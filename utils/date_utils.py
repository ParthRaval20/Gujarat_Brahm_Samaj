"""Date and age utilities."""

from __future__ import annotations
from datetime import date


def calculate_age(birth_date_str: str) -> int | None:
    """Compute age from a YYYY-MM-DD string. Returns None if input is falsy."""
    if not birth_date_str:
        return None
    try:
        birth = date.fromisoformat(birth_date_str)
    except ValueError:
        return None
    today = date.today()
    age = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    return age


def format_date_display(date_str: str) -> str:
    """Convert YYYY-MM-DD to DD/MM/YYYY for UI display."""
    if not date_str:
        return ''
    try:
        d = date.fromisoformat(date_str)
        return d.strftime('%d/%m/%Y')
    except ValueError:
        return date_str


def parse_display_date(display: str) -> str:
    """Convert DD/MM/YYYY back to YYYY-MM-DD for storage."""
    if not display:
        return ''
    try:
        d = date(int(display[6:]), int(display[3:5]), int(display[:2]))
        return d.isoformat()
    except Exception:
        return display
