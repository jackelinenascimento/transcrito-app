import unittest

from src.application.formatters.timestamp_formatter import (
    TimestampFormatter,
    format_timestamp,
)
from src.domain.transcription import Transcription, TranscriptionSegment


class FormatTimestampTest(unittest.TestCase):

    def test_formats_seconds_as_minutes_and_seconds(self):
        self.assertEqual(format_timestamp(0), "00:00")
        self.assertEqual(format_timestamp(65.9), "01:05")
        self.assertEqual(format_timestamp(3599), "59:59")


class TimestampFormatterTest(unittest.TestCase):

    def test_formats_transcription_segments_with_timestamps(self):
        transcription = Transcription(
            text="Hello world",
            segments=[
                TranscriptionSegment(start=0, end=2.5, text=" First line ", speaker=None),
                TranscriptionSegment(start=65, end=70, text="Second line", speaker="Speaker 1"),
            ],
            language="en",
        )

        formatted = TimestampFormatter().format(transcription)

        self.assertEqual(
            formatted,
            "[00:00]\nFirst line\n\n[01:05]\nSpeaker 1:\nSecond line\n",
        )

    def test_formats_empty_transcription_as_empty_text(self):
        transcription = Transcription(text="", segments=[])

        self.assertEqual(TimestampFormatter().format(transcription), "")


if __name__ == "__main__":
    unittest.main()
