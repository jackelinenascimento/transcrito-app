import tempfile
import unittest
from pathlib import Path

from src.application.transcribe_video import TranscribeVideo
from src.domain.transcription import Transcription, TranscriptionSegment


class FakeTranscriptionService:

    def __init__(self):
        self.video_path = None

    def transcribe(self, video_path: str) -> Transcription:
        self.video_path = video_path
        return Transcription(
            text="Full text",
            segments=[TranscriptionSegment(start=1, end=2, text="Segment text")],
            language="en",
        )


class FakeFormatter:

    def __init__(self):
        self.transcription = None

    def format(self, transcription: Transcription) -> str:
        self.transcription = transcription
        return "formatted text"


class FakeWriter:

    def __init__(self):
        self.content = None
        self.output_path = None

    def write(self, content: str, output_path: Path):
        self.content = content
        self.output_path = output_path


class TranscribeVideoTest(unittest.TestCase):

    def test_transcribes_formats_writes_and_returns_output_path(self):
        service = FakeTranscriptionService()
        formatter = FakeFormatter()
        writer = FakeWriter()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            output_path = TranscribeVideo(service, formatter, writer).execute(
                "videos/example.video.mp4",
                output_dir,
            )

        self.assertEqual(service.video_path, "videos/example.video.mp4")
        self.assertEqual(formatter.transcription.language, "en")
        self.assertEqual(writer.content, "formatted text")
        self.assertEqual(writer.output_path, output_path)
        self.assertEqual(output_path.name, "example.video.txt")


if __name__ == "__main__":
    unittest.main()
