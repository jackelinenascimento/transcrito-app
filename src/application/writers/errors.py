class WriteError(Exception):
    """Base error for output writing failures."""


class FileWriteError(WriteError):
    """Raised when a local file cannot be written."""
