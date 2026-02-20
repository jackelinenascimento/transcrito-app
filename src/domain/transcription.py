from dataclasses import dataclass
from typing import List


@dataclass
class TranscriptionSegment:
    start: float
    end: float
    text: str


@dataclass
class Transcription:
    text: str
    segments: List[TranscriptionSegment]
    language: str | None = None