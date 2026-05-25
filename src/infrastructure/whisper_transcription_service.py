import whisper

from src.domain.transcription_service import TranscriptionService
from src.domain.transcription import Transcription, TranscriptionSegment
from src.domain.transcription_errors import ModelLoadError, TranscriptionExecutionError


class WhisperTranscriptionService(TranscriptionService):

    def __init__(
            self,
            model_name: str = "base",
            device: str = "cpu",
            language: str = "pt"
    ):
        self.language = language
        try:
            self.model = whisper.load_model(model_name, device=device)
        except Exception as exc:
            raise ModelLoadError(
                f"Could not load Whisper model '{model_name}' on device '{device}': {exc}"
            ) from exc

    def transcribe(self, video_path: str) -> Transcription:
        try:
            result = self.model.transcribe(video_path, language=self.language)

            segments = [
                TranscriptionSegment(
                    start=s["start"],
                    end=s["end"],
                    text=s["text"].strip(),
                )
                for s in result["segments"]
            ]

            return Transcription(
                text=result["text"],
                segments=segments,
                language=result.get("language"),
            )
        except Exception as exc:
            raise TranscriptionExecutionError(
                f"Could not transcribe '{video_path}': {exc}"
            ) from exc
