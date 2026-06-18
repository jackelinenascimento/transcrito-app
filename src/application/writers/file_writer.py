from pathlib import Path

from src.application.safe_paths import UnsafePathError, resolve_inside_base
from src.application.writers.base_writer import TextWriter
from src.application.writers.errors import FileWriteError


class FileWriter(TextWriter):

    def __init__(self, base_dir: Path | str | None = None):
        self.base_dir = Path.cwd() if base_dir is None else Path(base_dir)

    def write(self, content: str, output_path: Path):
        try:
            safe_output_path = resolve_inside_base(output_path, self.base_dir)

            with open(safe_output_path, "w", encoding="utf-8") as f:
                f.write(content)
        except UnsafePathError as exc:
            raise FileWriteError(str(exc)) from exc
        except OSError as exc:
            raise FileWriteError(f"Could not write to {output_path}: {exc}") from exc
