from src.application.formatters.base_formatter import TranscriptionFormatter
from src.domain.transcription import Transcription


def _format_srt_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


class SrtFormatter(TranscriptionFormatter):

    def format(self, transcription: Transcription) -> str:
        lines = []
        for i, seg in enumerate(transcription.segments, start=1):
            start_ts = _format_srt_timestamp(seg.start)
            end_ts = _format_srt_timestamp(seg.end)
            lines.append(str(i))
            # timestamp line
            lines.append(f"{start_ts} --> {end_ts}")
            if getattr(seg, "speaker", None):
                lines.append(f"{seg.speaker}: {seg.text.strip()}")
            else:
                lines.append(seg.text.strip())
            lines.append("")

        return "\n".join(lines)
