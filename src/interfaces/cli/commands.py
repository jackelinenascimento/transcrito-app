import argparse
import shutil
import time
from pathlib import Path

from src.application.formatters.timestamp_formatter import TimestampFormatter
from src.application.transcribe_video import TranscribeVideo
from src.application.writers.file_writer import FileWriter
from src.application.writers.errors import WriteError
from src.application.utils.time_formatter import format_duration
from src.domain.transcription_errors import ModelLoadError, TranscriptionExecutionError


def _create_service(service_factory, model_name: str, device: str, language: str):
    # If a class was passed (e.g. WhisperTranscriptionService), instantiate it.
    # If a factory function was passed, call it. If an instance was passed,
    # return it directly.
    from inspect import isclass

    if isclass(service_factory):
        return service_factory(model_name=model_name, device=device, language=language)

    if callable(service_factory) and not hasattr(service_factory, "transcribe"):
        # factory function
        return service_factory(model_name=model_name, device=device, language=language)

    # assume it's already an instance with a `transcribe` method
    return service_factory


def run(service_factory):
    parser = argparse.ArgumentParser(prog="transcrito")
    parser.add_argument("video", help="Path to the video file")
    parser.add_argument("--out", default="outputs", help="Path to the output directory")
    parser.add_argument("--model", default="base", help="Whisper model name")
    parser.add_argument("--device", default="cpu", help="Device used by Whisper")
    parser.add_argument("--language", default="pt", help="Transcription language")
    parser.add_argument("--format", default="txt", choices=["txt", "srt"], help="Output format")
    parser.add_argument("--diarize", action="store_true", help="Request diarization from the transcription service or enable heuristic speaker separation")
    parser.add_argument("--gap-threshold", type=float, default=1.5, help="Gap threshold in seconds to consider a new speaker when using heuristic")
    parser.add_argument("--max-speakers", type=int, default=0, help="Maximum number of speakers to assign with heuristic (0 = unlimited)")

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

    try:
        service = _create_service(service_factory, args.model, args.device, args.language)
    except ModelLoadError as exc:
        print(f"❌ Could not load transcription model: {exc}")
        return

    if args.format == "srt":
        from src.application.formatters.srt_formatter import SrtFormatter

        formatter = SrtFormatter()
    else:
        formatter = TimestampFormatter()
    writer = FileWriter()
    diarization_provider = None
    if args.diarize:
        try:
            from src.infrastructure.diarization_provider import StubDiarizationProvider

            diarization_provider = StubDiarizationProvider()
        except Exception:
            diarization_provider = None

    use_case = TranscribeVideo(
        service,
        formatter,
        writer,
        diarize=args.diarize,
        gap_threshold=args.gap_threshold,
        max_speakers=args.max_speakers,
        diarization_provider=diarization_provider,
    )

    try:
        output_file = use_case.execute(str(video_path), output_dir)
    except TranscriptionExecutionError as exc:
        print(f"❌ Transcription failed: {exc}")
        return
    except WriteError as exc:
        print(f"❌ Could not write output file: {exc}")
        return

    duration = time.perf_counter() - start_time

    print("\n────────────────────────")
    print("✅ Done")
    print(f"⏱ Total time: {format_duration(duration)}")
    print(f"📄 Output: {output_file}\n")
