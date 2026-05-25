from abc import ABC, abstractmethod
from pathlib import Path


class TextWriter(ABC):

    @abstractmethod
    def write(self, content: str, output_path: Path):
        pass
