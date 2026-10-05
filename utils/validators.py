"""Utility: field validators."""

from __future__ import annotations
import re
from datetime import date

from app.config import BLOOD_GROUPS


def validate_full_name(name: str) -> str | None:
    """Return error message or None if valid."""
    if not name or len(name.strip()) < 2:
        return 'Full name is required (minimum 2 characters).'
    return None


def validate_mobile(mobile: str) -> str | None:
    if not mobile:
        return None   # optional
    digits = re.sub(r'\D', '', mobile)
    if len(digits) != 10:
        return 'Mobile number must be exactly 10 digits.'
    return None


def validate_phone_landline(phone: str) -> str | None:
    if not phone:
        return None   # optional
    allowed = re.sub(r'[\d\-+() ]', '', phone)
    if allowed:
        return 'Phone number may only contain digits, hyphens, and spaces.'
    return None


def validate_pincode(pincode: str) -> str | None:
    if not pincode:
        return None   # optional
    if not re.fullmatch(r'\d{6}', pincode):
        return 'PIN code must be exactly 6 digits.'
    return None


def validate_blood_group(bg: str) -> str | None:
    if not bg:
        return None   # optional
    if bg not in BLOOD_GROUPS:
        return f'Blood group must be one of: {", ".join(g for g in BLOOD_GROUPS if g)}.'
    return None


def validate_birth_date(birth_date_str: str) -> str | None:
    if not birth_date_str:
        return None   # optional
    try:
        bd = date.fromisoformat(birth_date_str)
    except ValueError:
        return 'Date of birth must be in YYYY-MM-DD format.'
    if bd >= date.today():
        return 'Date of birth cannot be today or in the future.'
    return None


def validate_family_member_age(age_val) -> str | None:
    if age_val is None or age_val == '':
        return None
    try:
        a = int(age_val)
    except (TypeError, ValueError):
        return 'Age must be a whole number.'
    if not (0 <= a <= 120):
        return 'Age must be between 0 and 120.'
    return None
