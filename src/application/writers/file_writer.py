from pathlib import Path

from src.application.writers.base_writer import TextWriter
from src.application.writers.errors import FileWriteError


class FileWriter(TextWriter):

    def write(self, content: str, output_path: Path):
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as exc:
            raise FileWriteError(f"Could not write to {output_path}: {exc}") from exc
