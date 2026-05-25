import tempfile
import unittest
from pathlib import Path

from src.application.writers.file_writer import FileWriter


class FileWriterTest(unittest.TestCase):

    def test_writes_text_file_with_utf8_encoding(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "transcription.txt"

            FileWriter().write("Transcricao: acao", output_path)

            self.assertEqual(output_path.read_text(encoding="utf-8"), "Transcricao: acao")


if __name__ == "__main__":
    unittest.main()
