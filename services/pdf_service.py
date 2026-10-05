"""
PDF service — Exact vector reproduction of the official
'સભ્ય નોંધણી ફોર્મ' of 'શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સા.કાં.'

Uses QPdfWriter and FormRenderer with full HarfBuzz Gujarati complex script shaping
to guarantee 100% visual fidelity matching the master physical form reference.
"""

from __future__ import annotations

import os
import sys
from typing import Any

from PySide6.QtCore import QMarginsF
from PySide6.QtGui import QGuiApplication, QPdfWriter, QPainter, QPageSize

from app.config import EXPORT_DIR, ensure_dirs
from services.form_renderer import FormRenderer
from utils.file_utils import get_pdf_filename


def generate_form_pdf(form_data: dict[str, Any], output_path: str | None = None) -> str:
    """
    Generate the official form PDF and return the saved file path.

    :param form_data:   Dictionary with form fields (built via form_service.build_form_data).
    :param output_path: Optional explicit output path. Defaults to exports/<filename>.pdf.
    :return: Absolute or relative path to the generated PDF.
    """
    ensure_dirs()

    if output_path is None:
        filename = get_pdf_filename(
            form_data.get('full_name', 'member'),
            form_data.get('form_number', 'GBS'),
        )
        output_path = os.path.join(EXPORT_DIR, filename)

    # Ensure parent dir exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Ensure a Qt application instance exists for font loading & text shaping
    app = QGuiApplication.instance()
    created_app = False
    if app is None:
        app = QGuiApplication(sys.argv if sys.argv else [''])
        created_app = True

    writer = QPdfWriter(output_path)
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setPageMargins(QMarginsF(0, 0, 0, 0))
    writer.setResolution(300)  # High-definition 300 DPI for print-grade output

    painter = QPainter(writer)
    FormRenderer.draw_form(
        painter,
        form_data=form_data,
        width=writer.width(),
        height=writer.height(),
        draw_background=True,
        draw_labels_and_lines=True,
        draw_values=True,
    )
    painter.end()

    return output_path


def get_pdf_path_for_member(full_name: str, member_code: str) -> str:
    """Return expected PDF output path without generating."""
    ensure_dirs()
    filename = get_pdf_filename(full_name, member_code)
    return os.path.join(EXPORT_DIR, filename)
