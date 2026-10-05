"""File name helpers."""

from __future__ import annotations
import re


def safe_filename(text: str) -> str:
    """Replace characters unsafe for filenames."""
    return re.sub(r'[\\/:*?"<>|]', '_', text)


def get_pdf_filename(full_name: str, member_code: str) -> str:
    """Return a safe PDF filename like 'RavalParth_GBS-000001.pdf'."""
    name_part = safe_filename(full_name.replace(' ', '_'))
    code_part = safe_filename(member_code)
    return f'{name_part}_{code_part}.pdf'
