import unittest

from src.application.formatters.srt_formatter import SrtFormatter
from src.domain.transcription import Transcription, TranscriptionSegment


class SrtFormatterTest(unittest.TestCase):

    def test_formats_segments_as_srt_with_speakers(self):
        transcription = Transcription(
            text="",
            segments=[
                TranscriptionSegment(start=0.0, end=1.5, text="Hello", speaker="Speaker 1"),
                TranscriptionSegment(start=2.0, end=3.0, text="Reply", speaker="Speaker 2"),
            ],
        )

        formatted = SrtFormatter().format(transcription)

        # basic checks
        self.assertIn("1", formatted)
        self.assertIn("00:00:00,000 --> 00:00:01,500", formatted)
        self.assertIn("Speaker 1: Hello", formatted)
        self.assertIn("Speaker 2: Reply", formatted)


if __name__ == "__main__":
    unittest.main()
