# vwrconf/models/custom_errors.py


class ReadOnlyError(Exception):
    """Raised when trying to write or restore on a readonly host."""

    pass


class UnknownHostError(Exception):
    """Raised when a host_id does not match any config client."""

    pass
