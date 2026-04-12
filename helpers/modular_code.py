from typing import Any


def safe_float(value: Any) -> float | None:
    """
    Convert value to float if possible, otherwise return None.
    Use this before numeric comparisons to avoid 'None < number' errors.
    """
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
    