import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch


class WhisperTranscriptionServiceTest(unittest.TestCase):

    def tearDown(self):
        sys.modules.pop("src.infrastructure.whisper_transcription_service", None)

    def test_loads_whisper_model_with_configured_device(self):
        model = Mock()
        fake_whisper = types.SimpleNamespace(load_model=Mock(return_value=model))

        with patch.dict(sys.modules, {"whisper": fake_whisper}):
            module = importlib.import_module("src.infrastructure.whisper_transcription_service")

            service = module.WhisperTranscriptionService("tiny", device="cuda")

        fake_whisper.load_model.assert_called_once_with("tiny", device="cuda")
        self.assertIs(service.model, model)

    def test_converts_whisper_result_to_domain_transcription_with_configured_language(self):
        model = Mock()
        model.transcribe.return_value = {
            "text": "Full text",
            "language": "pt",
            "segments": [
                {"start": 0.0, "end": 1.5, "text": " First "},
                {"start": 1.5, "end": 3.0, "text": "Second"},
            ],
        }
        fake_whisper = types.SimpleNamespace(load_model=Mock(return_value=model))

        with patch.dict(sys.modules, {"whisper": fake_whisper}):
            module = importlib.import_module("src.infrastructure.whisper_transcription_service")
            service = module.WhisperTranscriptionService("base", language="en")

            transcription = service.transcribe("video.mp4")

        model.transcribe.assert_called_once_with("video.mp4", language="en")
        self.assertEqual(transcription.text, "Full text")
        self.assertEqual(transcription.language, "pt")
        self.assertEqual(len(transcription.segments), 2)
        self.assertEqual(transcription.segments[0].text, "First")
        self.assertEqual(transcription.segments[0].start, 0.0)
        self.assertEqual(transcription.segments[0].end, 1.5)


if __name__ == "__main__":
    unittest.main()
