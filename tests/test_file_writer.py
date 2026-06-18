import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.application.writers.errors import FileWriteError
from src.application.writers.file_writer import FileWriter


class FileWriterTest(unittest.TestCase):

    def test_writes_text_file_with_utf8_encoding(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "transcription.txt"

            FileWriter(base_dir=temp_dir).write("Transcricao: acao", output_path)

            self.assertEqual(output_path.read_text(encoding="utf-8"), "Transcricao: acao")

    def test_rejects_output_path_outside_base_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / ".." / "transcription.txt"

            with self.assertRaises(FileWriteError) as context:
                FileWriter(base_dir=temp_dir).write("content", output_path)

        self.assertIn("Path must stay inside", str(context.exception))

    def test_wraps_os_error_in_file_write_error(self):
        with self.assertRaises(FileWriteError) as context, patch(
            "builtins.open",
            side_effect=OSError("permission denied"),
        ):
            FileWriter().write("content", Path("output.txt"))

        self.assertIn("Could not write to output.txt", str(context.exception))
        self.assertIsInstance(context.exception.__cause__, OSError)


if __name__ == "__main__":
    unittest.main()
