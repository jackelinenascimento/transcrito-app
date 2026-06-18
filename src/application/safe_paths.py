from pathlib import Path


class UnsafePathError(ValueError):
    """Raised when a path resolves outside its allowed base directory."""


def resolve_inside_base(path: Path | str, base_dir: Path | str) -> Path:
    base_path = Path(base_dir).expanduser().resolve()
    candidate_path = Path(path).expanduser()

    if not candidate_path.is_absolute():
        candidate_path = base_path / candidate_path

    resolved_path = candidate_path.resolve(strict=False)

    try:
        resolved_path.relative_to(base_path)
    except ValueError as exc:
        raise UnsafePathError(f"Path must stay inside {base_path}: {path}") from exc

    return resolved_path
