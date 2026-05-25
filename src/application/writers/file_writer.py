from pathlib import Path

from src.application.writers.base_writer import TextWriter


class FileWriter(TextWriter):

    def write(self, content: str, output_path: Path):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
