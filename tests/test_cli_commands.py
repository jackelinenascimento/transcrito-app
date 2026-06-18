import io
import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from src.application.writers.errors import FileWriteError
from src.domain.transcription_errors import ModelLoadError, TranscriptionExecutionError
from src.domain.transcription import Transcription, TranscriptionSegment
from src.interfaces.cli.commands import run


@contextmanager
def temporary_cwd():
    current_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        try:
            yield Path(temp_dir)
        finally:
            os.chdir(current_dir)


class FakeTranscriptionService:

    def __init__(self):
        self.video_path = None

    def transcribe(self, video_path: str) -> Transcription:
        self.video_path = video_path
        return Transcription(
            text="Full text",
            segments=[TranscriptionSegment(start=0, end=1, text="Segment text")],
            language="en",
        )


class FakeTranscriptionServiceFactory:

    def __init__(self):
        self.created_service = None
        self.init_kwargs = None

    def __call__(self, **kwargs):
        self.init_kwargs = kwargs
        self.created_service = FakeTranscriptionService()
        return self.created_service


class FailingTranscriptionService:

    def transcribe(self, video_path: str) -> Transcription:
        raise TranscriptionExecutionError("engine unavailable")


class FailingTranscriptionServiceFactory:

    def __call__(self, **kwargs):
        raise ModelLoadError("model unavailable")


class CliRunTest(unittest.TestCase):

    def test_returns_without_transcribing_when_video_does_not_exist(self):
        service = FakeTranscriptionService()

        with patch("sys.argv", ["transcrito", "missing.mp4"]), patch(
            "sys.stdout",
            new_callable=io.StringIO,
        ) as stdout:
            run(service)

        self.assertIsNone(service.video_path)
        self.assertIn("Video not found", stdout.getvalue())

    def test_transcribes_existing_video_to_output_directory(self):
        service = FakeTranscriptionService()

        with temporary_cwd() as temp_path:
            video_path = Path("sample.mp4")
            output_dir = Path("outputs")
            video_path.write_text("not a real video", encoding="utf-8")

            with patch(
                "sys.argv",
                ["transcrito", str(video_path), "--out", str(output_dir)],
            ), patch("time.perf_counter", side_effect=[10.0, 72.0]), patch(
                "shutil.which",
                return_value="/usr/bin/ffmpeg",
            ), patch(
                "sys.stdout",
                new_callable=io.StringIO,
            ) as stdout:
                run(service)

            output_file = temp_path / output_dir / "sample.txt"

            self.assertEqual(service.video_path, str(temp_path / video_path))
            self.assertEqual(output_file.read_text(encoding="utf-8"), "[00:00]\nSpeaker 1:\nSegment text\n")
            self.assertIn("Done", stdout.getvalue())
            self.assertIn(str(output_file), stdout.getvalue())

    def test_builds_service_from_cli_configuration(self):
        service_factory = FakeTranscriptionServiceFactory()

        with temporary_cwd() as temp_path:
            video_path = Path("sample.mp4")
            output_dir = Path("nested") / "outputs"
            video_path.write_text("not a real video", encoding="utf-8")

            with patch(
                "sys.argv",
                [
                    "transcrito",
                    str(video_path),
                    "--out",
                    str(output_dir),
                    "--model",
                    "small",
                    "--device",
                    "cuda",
                    "--language",
                    "en",
                ],
            ), patch("time.perf_counter", side_effect=[1.0, 2.0]), patch(
                "shutil.which",
                return_value="/usr/bin/ffmpeg",
            ), patch(
                "sys.stdout",
                new_callable=io.StringIO,
            ) as stdout:
                run(service_factory)

            self.assertEqual(
                service_factory.init_kwargs,
                {"model_name": "small", "device": "cuda", "language": "en"},
            )
            self.assertEqual(service_factory.created_service.video_path, str(temp_path / video_path))
            self.assertTrue((temp_path / output_dir / "sample.txt").exists())
            self.assertIn("Whisper (small | cuda)", stdout.getvalue())

    def test_returns_when_ffmpeg_is_missing(self):
        service = FakeTranscriptionService()

        with temporary_cwd():
            video_path = Path("sample.mp4")
            video_path.write_text("not a real video", encoding="utf-8")

            with patch("sys.argv", ["transcrito", str(video_path)]), patch(
                "shutil.which",
                return_value=None,
            ), patch(
                "sys.stdout",
                new_callable=io.StringIO,
            ) as stdout:
                run(service)

        self.assertIsNone(service.video_path)
        self.assertIn("ffmpeg not found", stdout.getvalue())

    def test_returns_when_output_directory_cannot_be_created(self):
        service = FakeTranscriptionService()

        with temporary_cwd():
            video_path = Path("sample.mp4")
            video_path.write_text("not a real video", encoding="utf-8")

            with patch(
                "sys.argv",
                ["transcrito", str(video_path), "--out", "outputs"],
            ), patch("shutil.which", return_value="/usr/bin/ffmpeg"), patch.object(
                Path,
                "mkdir",
                side_effect=OSError("permission denied"),
            ), patch(
                "sys.stdout",
                new_callable=io.StringIO,
            ) as stdout:
                run(service)

        self.assertIsNone(service.video_path)
        self.assertIn("Could not create output directory", stdout.getvalue())

    def test_returns_when_transcription_fails(self):
        with temporary_cwd():
            video_path = Path("sample.mp4")
            video_path.write_text("not a real video", encoding="utf-8")

            with patch("sys.argv", ["transcrito", str(video_path)]), patch(
                "shutil.which",
                return_value="/usr/bin/ffmpeg",
            ), patch(
                "time.perf_counter",
                return_value=1.0,
            ), patch(
                "sys.stdout",
                new_callable=io.StringIO,
            ) as stdout:
                run(FailingTranscriptionService())

        self.assertIn("Transcription failed: engine unavailable", stdout.getvalue())

    def test_returns_when_model_cannot_be_loaded(self):
        with temporary_cwd():
            video_path = Path("sample.mp4")
            video_path.write_text("not a real video", encoding="utf-8")

            with patch("sys.argv", ["transcrito", str(video_path)]), patch(
                "shutil.which",
                return_value="/usr/bin/ffmpeg",
            ), patch(
                "time.perf_counter",
                return_value=1.0,
            ), patch(
                "sys.stdout",
                new_callable=io.StringIO,
            ) as stdout:
                run(FailingTranscriptionServiceFactory())

        self.assertIn("Could not load transcription model: model unavailable", stdout.getvalue())

    def test_returns_when_output_file_cannot_be_written(self):
        service = FakeTranscriptionService()

        with temporary_cwd():
            video_path = Path("sample.mp4")
            video_path.write_text("not a real video", encoding="utf-8")

            with patch("sys.argv", ["transcrito", str(video_path)]), patch(
                "shutil.which",
                return_value="/usr/bin/ffmpeg",
            ), patch(
                "time.perf_counter",
                return_value=1.0,
            ), patch(
                "src.application.writers.file_writer.FileWriter.write",
                side_effect=FileWriteError("permission denied"),
            ), patch(
                "sys.stdout",
                new_callable=io.StringIO,
            ) as stdout:
                run(service)

        self.assertIn("Could not write output file: permission denied", stdout.getvalue())

    def test_returns_when_video_path_escapes_working_directory(self):
        service = FakeTranscriptionService()

        with temporary_cwd(), patch(
            "sys.argv",
            ["transcrito", "../sample.mp4"],
        ), patch(
            "sys.stdout",
            new_callable=io.StringIO,
        ) as stdout:
            run(service)

        self.assertIsNone(service.video_path)
        self.assertIn("Unsafe path", stdout.getvalue())

    def test_returns_when_output_path_escapes_working_directory(self):
        service = FakeTranscriptionService()

        with temporary_cwd():
            video_path = Path("sample.mp4")
            video_path.write_text("not a real video", encoding="utf-8")

            with patch(
                "sys.argv",
                ["transcrito", str(video_path), "--out", "../outputs"],
            ), patch(
                "sys.stdout",
                new_callable=io.StringIO,
            ) as stdout:
                run(service)

        self.assertIsNone(service.video_path)
        self.assertIn("Unsafe path", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
