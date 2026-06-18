from pathlib import Path

from src.application.formatters.base_formatter import TranscriptionFormatter
from src.application.writers.base_writer import TextWriter
from src.domain.transcription_service import TranscriptionService
from src.domain.transcription import TranscriptionSegment
from src.application.speaker_assigner import SpeakerAssigner


class TranscribeVideo:

    def __init__(
            self,
            service: TranscriptionService,
            formatter: TranscriptionFormatter,
            writer: TextWriter,
            diarize: bool = False,
            gap_threshold: float = 1.5,
            max_speakers: int = 0,
            diarization_provider=None,
            speaker_assigner: SpeakerAssigner | None = None,
    ):
        self.service = service
        self.formatter = formatter
        self.writer = writer
        self.diarize = diarize
        self.diarization_provider = diarization_provider
        # If no assigner provided, create a default one with provided values
        self.speaker_assigner = speaker_assigner or SpeakerAssigner(gap_threshold, max_speakers)

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
                # delegate to the SpeakerAssigner
                self.speaker_assigner.assign(transcription.segments)

        formatted_text = self.formatter.format(transcription)

        output_file = output_dir / f"{Path(video_path).stem}.txt"

        self.writer.write(formatted_text, output_file)

        return output_file

    # speaker assignment logic extracted to src/application/speaker_assigner.py
