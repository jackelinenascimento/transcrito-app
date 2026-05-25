class TranscriptionServiceError(Exception):
    """Base error for transcription service failures."""


class ModelLoadError(TranscriptionServiceError):
    """Raised when a transcription model cannot be loaded."""


class TranscriptionExecutionError(TranscriptionServiceError):
    """Raised when transcription fails after the service is available."""
