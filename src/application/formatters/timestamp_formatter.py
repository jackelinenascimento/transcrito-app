from src.application.formatters.base_formatter import TranscriptionFormatter
from src.domain.transcription import Transcription


def format_timestamp(seconds: float) -> str:
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

class TimestampFormatter(TranscriptionFormatter):

    def format(self, transcription: Transcription) -> str:
        lines = []

        for segment in transcription.segments:
            timestamp = format_timestamp(segment.start)
            lines.append(f"[{timestamp}]")
            lines.append(segment.text.strip())
            lines.append("")

        return "\n".join(lines)