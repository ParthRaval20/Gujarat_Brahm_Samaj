"""Gujarati Unicode helpers."""

from __future__ import annotations
import unicodedata


def normalize_gujarati(text: str) -> str:
    """NFC-normalize a string (important for Gujarati Unicode)."""
    if not text:
        return ''
    return unicodedata.normalize('NFC', text)


def safe_gujarati(text: str | None) -> str:
    """Return normalized string or empty string for None."""
    return normalize_gujarati(text or '')
