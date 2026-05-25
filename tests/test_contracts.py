import unittest

from src.application.formatters.base_formatter import TranscriptionFormatter
from src.application.writers.base_writer import TextWriter
from src.domain.transcription import Transcription
from src.domain.transcription_service import TranscriptionService


class ConcreteFormatter(TranscriptionFormatter):

    def format(self, transcription: Transcription) -> str:
        return TranscriptionFormatter.format(self, transcription)


class ConcreteTranscriptionService(TranscriptionService):

    def transcribe(self, video_path: str) -> Transcription:
        return TranscriptionService.transcribe(self, video_path)


class ConcreteTextWriter(TextWriter):

    def write(self, content: str, output_path):
        return TextWriter.write(self, content, output_path)


class ContractsTest(unittest.TestCase):

    def test_formatter_contract_is_abstract(self):
        with self.assertRaises(TypeError):
            TranscriptionFormatter()

    def test_transcription_service_contract_is_abstract(self):
        with self.assertRaises(TypeError):
            TranscriptionService()

    def test_text_writer_contract_is_abstract(self):
        with self.assertRaises(TypeError):
            TextWriter()

    def test_default_abstract_methods_return_none_when_called_by_subclass(self):
        transcription = Transcription(text="", segments=[])

        self.assertIsNone(ConcreteFormatter().format(transcription))
        self.assertIsNone(ConcreteTranscriptionService().transcribe("video.mp4"))
        self.assertIsNone(ConcreteTextWriter().write("content", "output.txt"))


if __name__ == "__main__":
    unittest.main()
