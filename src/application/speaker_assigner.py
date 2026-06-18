from typing import List

from src.domain.transcription import TranscriptionSegment


class SpeakerAssigner:
    """Encapsulates the heuristic to assign speaker labels by pauses between segments.

    This class replaces the former helper method inside TranscribeVideo so the
    behavior can be tested and reused independently.
    """

    def __init__(self, gap_threshold: float = 1.5, max_speakers: int = 0):
        self.gap_threshold = gap_threshold
        self.max_speakers = max_speakers

    def assign(self, segments: List[TranscriptionSegment]) -> None:
        if not segments:
            return

        current_speaker = 1
        segments[0].speaker = f"Speaker {current_speaker}"
        prev_end = segments[0].end

        for seg in segments[1:]:
            gap = max(0.0, seg.start - prev_end)
            if gap > self.gap_threshold:
                next_speaker = current_speaker + 1
                if self.max_speakers and next_speaker > self.max_speakers:
                    current_speaker = self.max_speakers
                else:
                    current_speaker = next_speaker
            seg.speaker = f"Speaker {current_speaker}"
            prev_end = seg.end
