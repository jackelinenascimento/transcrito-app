import unittest

from src.application.speaker_assigner import SpeakerAssigner
from src.domain.transcription import TranscriptionSegment


class SpeakerAssignerTest(unittest.TestCase):

    def test_assign_with_no_segments_does_nothing(self):
        assigner = SpeakerAssigner()
        segments: list[TranscriptionSegment] = []
        # should not raise
        assigner.assign(segments)
        self.assertEqual(segments, [])

    def test_assign_labels_by_pause(self):
        assigner = SpeakerAssigner(gap_threshold=1.0)
        segments = [
            TranscriptionSegment(start=0, end=1, text="a"),
            TranscriptionSegment(start=2.5, end=3.0, text="b"),
            TranscriptionSegment(start=4.5, end=5.0, text="c"),
        ]
        assigner.assign(segments)
        self.assertEqual(segments[0].speaker, "Speaker 1")
        self.assertEqual(segments[1].speaker, "Speaker 2")
        self.assertEqual(segments[2].speaker, "Speaker 3")

    def test_respects_max_speakers(self):
        assigner = SpeakerAssigner(gap_threshold=1.0, max_speakers=2)
        segments = [
            TranscriptionSegment(start=0, end=1, text="a"),
            TranscriptionSegment(start=2.5, end=3.0, text="b"),
            TranscriptionSegment(start=4.5, end=5.0, text="c"),
        ]
        assigner.assign(segments)
        self.assertEqual(segments[0].speaker, "Speaker 1")
        self.assertEqual(segments[1].speaker, "Speaker 2")
        # because max_speakers=2, the third stays Speaker 2
        self.assertEqual(segments[2].speaker, "Speaker 2")


if __name__ == "__main__":
    unittest.main()
