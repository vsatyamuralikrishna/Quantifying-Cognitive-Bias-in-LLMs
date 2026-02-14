"""Utility helpers for analytics."""


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division that returns default on zero denominator."""
    return round(numerator / denominator, 3) if denominator else default
