import runpy
import sys
import types
import unittest


class MainTest(unittest.TestCase):

    def tearDown(self):
        sys.modules.pop("src.main", None)
        sys.modules.pop("src.infrastructure.whisper_transcription_service", None)
        sys.modules.pop("src.interfaces.cli.commands", None)

    def test_module_entrypoint_passes_service_factory_to_cli(self):
        calls = []

        class FakeWhisperTranscriptionService:

            pass

        def fake_run(service_factory):
            calls.append(("run", service_factory))

        fake_infrastructure_module = types.SimpleNamespace(
            WhisperTranscriptionService=FakeWhisperTranscriptionService,
        )
        fake_cli_module = types.SimpleNamespace(run=fake_run)

        sys.modules["src.infrastructure.whisper_transcription_service"] = fake_infrastructure_module
        sys.modules["src.interfaces.cli.commands"] = fake_cli_module

        runpy.run_module("src.main", run_name="__main__")

        self.assertEqual(calls, [("run", FakeWhisperTranscriptionService)])


if __name__ == "__main__":
    unittest.main()
