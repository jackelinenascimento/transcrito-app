from abc import ABC, abstractmethod
from src.domain.transcription import Transcription


class TranscriptionService(ABC):

    @abstractmethod
    def transcribe(self, video_path: str) -> Transcription:
        pass