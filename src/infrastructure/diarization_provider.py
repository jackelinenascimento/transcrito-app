from typing import List

from src.domain.transcription import Transcription, TranscriptionSegment


class DiarizationProvider:
    """Contract for diarization providers.

    Concrete providers should implement `diarize` to take a video path and
    optionally the current transcription and attach speaker labels to the
    transcription.segments or return a new list of speakers.
    """

    def diarize(self, video_path: str, transcription: Transcription) -> None:
        raise NotImplementedError()


class StubDiarizationProvider(DiarizationProvider):
    """A tiny stub provider for testing and demonstration.

    It assigns speaker labels deterministically: alternating Speaker 1,
    Speaker 2, ... across segments. This simulates a provider that would
    normally run an external diarization model.
    """

    def diarize(self, video_path: str, transcription: Transcription) -> None:
        for i, seg in enumerate(transcription.segments, start=1):
            seg.speaker = f"Speaker {((i - 1) % 3) + 1}"
