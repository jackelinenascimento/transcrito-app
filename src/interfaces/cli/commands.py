import argparse
import shutil
import time
from pathlib import Path

from src.application.formatters.timestamp_formatter import TimestampFormatter
from src.application.transcribe_video import TranscribeVideo
from src.application.writers.file_writer import FileWriter
from src.application.utils.time_formatter import format_duration


def _create_service(service_factory, model_name: str, device: str, language: str):
    if hasattr(service_factory, "transcribe"):
        return service_factory
    return service_factory(model_name=model_name, device=device, language=language)


def run(service_factory):
    parser = argparse.ArgumentParser(prog="transcrito")
    parser.add_argument("video", help="Path to the video file")
    parser.add_argument("--out", default="outputs", help="Path to the output directory")
    parser.add_argument("--model", default="base", help="Whisper model name")
    parser.add_argument("--device", default="cpu", help="Device used by Whisper")
    parser.add_argument("--language", default="pt", help="Transcription language")
    parser.add_argument("--format", default="txt", choices=["txt"], help="Output format")

    args = parser.parse_args()

    video_path = Path(args.video)

    if not video_path.exists():
        print(f"❌ Video not found: {video_path}")
        return

    if shutil.which("ffmpeg") is None:
        print("❌ ffmpeg not found. Install ffmpeg before transcribing.")
        return

    output_dir = Path(args.out)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"❌ Could not create output directory: {exc}")
        return

    print("\n🎬 Transcrito App")
    print("────────────────────────")
    print(f"📂 Video: {video_path}")
    print(f"🧠 Engine: Whisper ({args.model} | {args.device})")
    print(f"🌐 Language: {args.language}")
    print(f"📄 Format: {args.format}\n")

    print("⏳ Transcribing...")

    start_time = time.perf_counter()

    service = _create_service(service_factory, args.model, args.device, args.language)
    formatter = TimestampFormatter()
    writer = FileWriter()
    use_case = TranscribeVideo(service, formatter, writer)

    try:
        output_file = use_case.execute(str(video_path), output_dir)
    except Exception as exc:
        print(f"❌ Transcription failed: {exc}")
        return

    duration = time.perf_counter() - start_time

    print("\n────────────────────────")
    print("✅ Done")
    print(f"⏱ Total time: {format_duration(duration)}")
    print(f"📄 Output: {output_file}\n")
