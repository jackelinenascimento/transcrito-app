from pathlib import Path

from src.application.formatters.base_formatter import TranscriptionFormatter
from src.application.writers.base_writer import TextWriter
from src.domain.transcription_service import TranscriptionService
from src.domain.transcription import TranscriptionSegment


class TranscribeVideo:

    def __init__(
            self,
            service: TranscriptionService,
            formatter: TranscriptionFormatter,
            writer: TextWriter
            ,
            diarize: bool = False,
            gap_threshold: float = 1.5,
            max_speakers: int = 0,
            diarization_provider=None,
    ):
        self.service = service
        self.formatter = formatter
        self.writer = writer
        self.diarize = diarize
        self.gap_threshold = gap_threshold
        self.max_speakers = max_speakers
        self.diarization_provider = diarization_provider

    def execute(self, video_path: str, output_dir: Path) -> Path:
        transcription = self.service.transcribe(video_path)

        # If diarization is requested, attempt to rely on service-provided
        # speaker labels. If the service does not provide them and diarize is
        # True, fall back to heuristic. If diarize is False, still run the
        # heuristic to provide a sensible default separation.
        if transcription.segments and not any(getattr(s, "speaker", None) for s in transcription.segments):
            # Prefer provider-provided labels when diarize requested.
            if self.diarize and self.diarization_provider is not None:
                try:
                    self.diarization_provider.diarize(video_path, transcription)
                except Exception:
                    # provider errors should not break the main flow; fall
                    # back to heuristic below
                    pass

            # If after provider there are still no speakers, or no provider
            # was available, apply heuristic as fallback (or as default when
            # diarize is False).
            if not any(getattr(s, "speaker", None) for s in transcription.segments):
                self._assign_speakers_by_pause(
                    transcription.segments,
                    gap_threshold=self.gap_threshold,
                )

        formatted_text = self.formatter.format(transcription)

        output_file = output_dir / f"{Path(video_path).stem}.txt"

        self.writer.write(formatted_text, output_file)

        return output_file

    def _assign_speakers_by_pause(self, segments: list[TranscriptionSegment], gap_threshold: float = 1.5) -> None:
        """
        Assign speaker labels to segments in-place.

        Simple heuristic: start with Speaker 1. For each next segment, if the
        gap between the current segment start and previous segment end is
        greater than gap_threshold (seconds), toggle to the next speaker
        (Speaker 2, then Speaker 1, ...). This is a minimal, local heuristic
        that gives a sensible default speaker separation when diarization is
        not available from the transcription engine.
        """
        if not segments:
            return

        current_speaker = 1
        segments[0].speaker = f"Speaker {current_speaker}"
        prev_end = segments[0].end

        for seg in segments[1:]:
            gap = max(0.0, seg.start - prev_end)
            if gap > gap_threshold:
                # consider this a new speaker and increment speaker id
                next_speaker = current_speaker + 1
                if self.max_speakers and next_speaker > self.max_speakers:
                    # if we've reached the configured maximum, keep using the
                    # last speaker id (do not create new labeled speakers)
                    current_speaker = self.max_speakers
                else:
                    current_speaker = next_speaker
            seg.speaker = f"Speaker {current_speaker}"
            prev_end = seg.end
