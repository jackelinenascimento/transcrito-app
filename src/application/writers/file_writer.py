from pathlib import Path


class FileWriter:

    def write(self, content: str, output_path: Path):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)