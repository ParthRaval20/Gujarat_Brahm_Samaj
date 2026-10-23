"""
Form preview page — generates PDF and shows instant authentic preview + print/save actions.
"""

from __future__ import annotations

import os
from typing import Any

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QImage, QPainter, QCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QFileDialog, QMessageBox, QProgressBar,
)
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

from app.config import COLOR_PRIMARY, COLOR_PRIMARY_DARK, EXPORT_DIR
from services.member_service import MemberService
from services.family_service import FamilyService
from services.form_service import build_form_data
from services.form_renderer import FormRenderer, CANVAS_W, CANVAS_H
from services.pdf_service import generate_form_pdf
from utils.file_utils import get_pdf_filename


class PdfGeneratorThread(QThread):
    """Generate PDF in a background thread."""
    finished = Signal(str)   # emits output path
    error    = Signal(str)   # emits error message

    def __init__(self, form_data: dict, output_path: str):
        super().__init__()
        self._form_data   = form_data
        self._output_path = output_path

    def run(self):
        try:
            path = generate_form_pdf(self._form_data, self._output_path)
            self.finished.emit(path)
        except Exception as e:
            self.error.emit(str(e))


class FormPreviewPage(QWidget):
    def __init__(self, nav_callback, parent=None):
        super().__init__(parent)
        self._nav          = nav_callback
        self._pdf_path     = None
        self._member_id    = None
        self._form_data    = {}
        self._thread       = None
        self._current_lang = 'gu'
        self._setup_ui()

    def set_language(self, lang: str):
        self._current_lang = lang
        is_en = (lang == 'en')
        if hasattr(self, 'back_btn'):
            self.back_btn.setText('← Back to Profile' if is_en else '← પ્રોફાઇલ પર પાછા જાઓ')
        if hasattr(self, 'print_btn'):
            self.print_btn.setText('🖨  Print Form' if is_en else '🖨  ફોર્મ પ્રિન્ટ કરો')
        if hasattr(self, 'save_btn'):
            self.save_btn.setText('💾  Save PDF As...' if is_en else '💾  પીડીએફ સાચવો...')
        if hasattr(self, 'open_btn'):
            self.open_btn.setText('📂  Open PDF' if is_en else '📂  પીડીએફ ખોલો')
        if hasattr(self, 'regen_btn'):
            self.regen_btn.setText('🔄  Regenerate' if is_en else '🔄  ફરીથી બનાવો')
        if hasattr(self, 'title_label') and self._member_id is not None:
            member = MemberService().get_member(self._member_id)
            if member:
                prefix = '📄  Member Registration Form — ' if is_en else '📄  સભ્ય નોંધણી ફોર્મ — '
                self.title_label.setText(f'{prefix}{member.full_name}  ({member.member_code})')
            else:
                self.title_label.setText('📄  Member Registration Form — Preview' if is_en else '📄  સભ્ય નોંધણી ફોર્મ — પ્રીવ્યૂ')
        elif hasattr(self, 'title_label'):
            self.title_label.setText('📄  Member Registration Form — Preview' if is_en else '📄  સભ્ય નોંધણી ફોર્મ — પ્રીવ્યૂ')

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        # Header
        hdr = QHBoxLayout()
        hdr.setSpacing(12)
        self.back_btn = QPushButton('← Back to Profile' if self._current_lang == 'en' else '← પ્રોફાઇલ પર પાછા જાઓ')
        self.back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_btn.setFixedHeight(36)
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: {COLOR_PRIMARY};
                border: 1.5px solid {COLOR_PRIMARY};
                border-radius: 8px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: #EFF6FF;
                border-color: {COLOR_PRIMARY_DARK};
                color: {COLOR_PRIMARY_DARK};
            }}
            QPushButton:pressed {{
                background-color: #DBEAFE;
            }}
        """)
        self.back_btn.clicked.connect(lambda: self._nav('profile', member_id=self._member_id))

        self.title_label = QLabel('📄  સભ્ય નોંધણી ફોર્મ — પ્રીવ્યૂ')
        self.title_label.setStyleSheet(f'font-size: 20px; font-weight: 800; color: {COLOR_PRIMARY};')

        hdr.addWidget(self.back_btn)
        hdr.addWidget(self.title_label)
        hdr.addStretch()
        layout.addLayout(hdr)

        # Action buttons
        act = QHBoxLayout()
        act.setSpacing(10)
        self.print_btn = QPushButton('🖨️  Print Form' if self._current_lang == 'en' else '🖨️  ફોર્મ પ્રિન્ટ કરો')
        self.save_btn  = QPushButton('💾  Save PDF As...' if self._current_lang == 'en' else '💾  પીડીએફ સાચવો...')
        self.open_btn  = QPushButton('📂  Open PDF' if self._current_lang == 'en' else '📂  પીડીએફ ખોલો')
        self.regen_btn = QPushButton('🔄  Regenerate' if self._current_lang == 'en' else '🔄  ફરીથી બનાવો')

        colors_map = [
            (self.print_btn, '#10B981', '#059669', '#047857'),
            (self.save_btn,  COLOR_PRIMARY, COLOR_PRIMARY_DARK, '#0E1848'),
            (self.open_btn,  '#2563EB', '#1D4ED8', '#1E40AF'),
            (self.regen_btn, '#64748B', '#475569', '#334155'),
        ]
        for btn, bg, hover, pressed in colors_map:
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFixedHeight(38)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg}; color: white;
                    border: none; border-radius: 8px;
                    font-size: 12px; font-weight: 700; padding: 0 16px;
                }}
                QPushButton:hover {{ background-color: {hover}; }}
                QPushButton:pressed {{ background-color: {pressed}; }}
                QPushButton:disabled {{ background-color: #E2E8F0; color: #94A3B8; border: 1px solid #CBD5E1; }}
            """)
            act.addWidget(btn)
        act.addStretch()
        layout.addLayout(act)

        self.print_btn.clicked.connect(self._print_form)
        self.save_btn.clicked.connect(self._save_as)
        self.open_btn.clicked.connect(self._open_pdf)
        self.regen_btn.clicked.connect(lambda: self.load_member(self._member_id) if self._member_id is not None else None)

        # Disable until PDF ready
        for btn in (self.print_btn, self.save_btn, self.open_btn):
            btn.setEnabled(False)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(6)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                border: none; background: #E8ECF8; border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background: {COLOR_PRIMARY}; border-radius: 3px;
            }}
        """)
        self.progress.hide()
        layout.addWidget(self.progress)

        # Status label
        self.status_label = QLabel('')
        self.status_label.setStyleSheet('font-size: 13px; color: #555;')
        layout.addWidget(self.status_label)

        # Preview area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.Box)
        scroll.setStyleSheet('QScrollArea { border: 1px solid #D0D5E8; background: #E8ECF8; }')

        self.preview_container = QWidget()
        self.preview_container.setObjectName("previewContainer")
        self.preview_container.setStyleSheet("#previewContainer { background: #E8ECF8; }")
        preview_layout = QVBoxLayout(self.preview_container)
        preview_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # A4 Paper sheet card for preview
        self.paper_frame = QFrame()
        self.paper_frame.setObjectName("paperFrame")
        self.paper_frame.setStyleSheet("#paperFrame { background: white; border: 1px solid #B0B8D8; }")
        pf_layout = QVBoxLayout(self.paper_frame)
        pf_layout.setContentsMargins(0, 0, 0, 0)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pf_layout.addWidget(self.preview_label)

        preview_layout.addWidget(self.paper_frame)
        scroll.setWidget(self.preview_container)
        layout.addWidget(scroll)

    def load_member(self, member_id: int) -> None:
        self._member_id = member_id
        self._pdf_path  = None
        is_en = (self._current_lang == 'en')

        member = MemberService().get_member(member_id)
        if not member:
            self.status_label.setText('Member not found.' if is_en else 'સભ્ય મળ્યા નથી.')
            return

        prefix = '📄  Member Registration Form — ' if is_en else '📄  સભ્ય નોંધણી ફોર્મ — '
        self.title_label.setText(f'{prefix}{member.full_name}  ({member.member_code})')

        family_members = FamilyService().get_family_members(member_id)
        self._form_data = build_form_data(member, family_members)

        filename    = get_pdf_filename(str(member.full_name), str(member.member_code))
        output_path = os.path.join(EXPORT_DIR, filename)

        self.status_label.setText('Generating PDF & Preview...' if is_en else 'પીડીએફ અને પ્રીવ્યૂ તૈયાર થઈ રહ્યું છે...')
        self.progress.show()

        # Render instant high-fidelity raster preview using FormRenderer
        self._render_canvas_preview(self._form_data)

        self._thread = PdfGeneratorThread(self._form_data, output_path)
        self._thread.finished.connect(self._on_pdf_ready)
        self._thread.error.connect(self._on_pdf_error)
        self._thread.start()

    def _render_canvas_preview(self, form_data: dict[str, Any]) -> None:
        """Render high-resolution preview directly using FormRenderer."""
        img = QImage(int(CANVAS_W), int(CANVAS_H), QImage.Format.Format_ARGB32)
        p = QPainter(img)
        FormRenderer.draw_form(
            p,
            form_data=form_data,
            width=CANVAS_W,
            height=CANVAS_H,
            draw_background=True,
            draw_labels_and_lines=True,
            draw_values=True,
        )
        p.end()

        pix = QPixmap.fromImage(img)
        self.preview_label.setPixmap(pix)
        self.paper_frame.setFixedSize(int(CANVAS_W), int(CANVAS_H))

    def _on_pdf_ready(self, path: str) -> None:
        self._pdf_path = path
        self.progress.hide()
        is_en = (self._current_lang == 'en')
        self.status_label.setText(
            f'✓ Official Form PDF ready: {os.path.basename(path)}'
            if is_en else
            f'✓ સત્તાવાર ફોર્મ પીડીએફ તૈયાર: {os.path.basename(path)}'
        )

        for btn in (self.print_btn, self.save_btn, self.open_btn):
            btn.setEnabled(True)

    def _on_pdf_error(self, message: str) -> None:
        self.progress.hide()
        self.status_label.setText(f'Error: {message}')
        QMessageBox.critical(self, 'PDF Error', f'Could not generate PDF:\n{message}')

    def _print_form(self) -> None:
        """Print the exact A4 form via QPrinter without UI navigation or buttons."""
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageSize(QPrinter.PageSize.A4)
        printer.setFullPage(True)
        is_en = (self._current_lang == 'en')

        dialog = QPrintDialog(printer, self)
        dialog.setWindowTitle('Print Member Registration Form' if is_en else 'સભ્ય નોંધણી ફોર્મ પ્રિન્ટ કરો')
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            p = QPainter(printer)
            FormRenderer.draw_form(
                p,
                form_data=self._form_data,
                width=printer.width(),
                height=printer.height(),
                draw_background=True,
                draw_labels_and_lines=True,
                draw_values=True,
            )
            p.end()
            title = 'Printed' if is_en else 'પ્રિન્ટ થયેલ'
            msg = 'Form sent to printer successfully.' if is_en else 'ફોર્મ સફળતાપૂર્વક પ્રિન્ટર પર મોકલવામાં આવ્યું છે.'
            QMessageBox.information(self, title, msg)

    def _open_pdf(self) -> None:
        if not self._pdf_path or not os.path.exists(self._pdf_path):
            QMessageBox.warning(self, 'No PDF', 'PDF not found. Please regenerate.')
            return
        try:
            os.startfile(self._pdf_path)
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def _save_as(self) -> None:
        if not self._pdf_path or not os.path.exists(self._pdf_path):
            QMessageBox.warning(self, 'No PDF', 'PDF not found. Please regenerate.')
            return
        dest, _ = QFileDialog.getSaveFileName(
            self, 'Save PDF As', self._pdf_path, 'PDF Files (*.pdf)'
        )
        if dest:
            import shutil
            shutil.copy2(self._pdf_path, dest)
            QMessageBox.information(self, 'Saved', f'PDF saved to:\n{dest}')
