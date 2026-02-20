import whisper
from src.domain.transcription_service import TranscriptionService
from src.domain.transcription import Transcription, TranscriptionSegment


class WhisperTranscriptionService(TranscriptionService):

    def __init__(self, model_name: str = "base"):
        self.model = whisper.load_model(model_name, device="cpu")

    def transcribe(self, video_path: str) -> Transcription:
        result = self.model.transcribe(video_path, language="pt")

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