from abc import ABC, abstractmethod

from src.domain.transcription import Transcription


class TranscriptionFormatter(ABC):

    @abstractmethod
    def format(self, transcription: Transcription) -> str:
        pass