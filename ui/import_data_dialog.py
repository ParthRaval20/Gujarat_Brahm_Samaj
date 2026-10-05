"""
Modern Data Import & Upsert Dialog.
Allows importing members from Excel (.xlsx) and CSV (.csv) files.
Provides smart replacement strategies:
1. Match & Replace by Mobile Number OR Form Number (Recommended)
2. Match & Replace by Mobile Number only
3. Match & Replace by Form Number / Member Code only
4. Insert Only (Skip duplicates)
Includes pre-import safety backup, preview table, and sample template generators.
Fully localized for Gujarati and English (zero Gujarati in English mode).
"""

from __future__ import annotations

import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QRadioButton, QButtonGroup, QCheckBox,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QFrame, QScrollArea, QWidget, QProgressBar,
)

from app.config import (
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_BG,
    COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    COLOR_ACCENT_BLUE, COLOR_ACCENT_EMERALD,
    EXPORT_DIR,
)
from services.import_export_service import ImportExportService, ImportResult


class ImportDataDialog(QDialog):
    """Dialog for importing member data with smart deduplication and replacement."""

    import_finished = Signal(object)  # Emits ImportResult

    def __init__(self, parent=None, lang: str | None = None):
        super().__init__(parent)
        if lang is not None:
            self._current_lang = lang
        elif parent is not None and hasattr(parent, '_current_lang'):
            self._current_lang = getattr(parent, '_current_lang')
        else:
            self._current_lang = 'gu'

        self.setMinimumSize(880, 680)
        self.resize(920, 720)
        self.setStyleSheet(f"background-color: {COLOR_BG}; font-family: 'Noto Sans Gujarati', 'Segoe UI', sans-serif;")

        self._selected_file_path: str = ""
        self._parsed_rows: list[dict[str, str]] = []
        self._mapped_keys: list[str] = []
        self._raw_headers: list[str] = []

        self._setup_ui()
        self.set_language(self._current_lang)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # ── 1. Header Banner ──────────────────────────────────────────
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0F172A, stop:0.6 #1E3A8A, stop:1 #1D4ED8);
                border-radius: 12px;
                border: 1px solid #1E293B;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)
        hdr_layout = QHBoxLayout(hdr_frame)
        hdr_layout.setContentsMargins(18, 14, 18, 14)
        hdr_layout.setSpacing(14)

        icon_lbl = QLabel("📥")
        icon_lbl.setFixedSize(44, 44)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            font-size: 22px;
        """)
        hdr_layout.addWidget(icon_lbl)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(3)
        self.t_lbl = QLabel()
        self.t_lbl.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: 800;")
        self.s_lbl = QLabel()
        self.s_lbl.setStyleSheet("color: #BFDBFE; font-size: 11.5px; font-weight: 500;")
        title_vbox.addWidget(self.t_lbl)
        title_vbox.addWidget(self.s_lbl)
        hdr_layout.addLayout(title_vbox, stretch=1)

        main_layout.addWidget(hdr_frame)

        # ── Scroll Area for Controls ──────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(14)

        # ── Step 1: File Selection Card ──────────────────────────────
        f_card = QFrame()
        f_card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER};
                border-radius: 10px;
                padding: 12px;
            }}
        """)
        f_layout = QVBoxLayout(f_card)
        f_layout.setSpacing(10)

        f_hdr = QHBoxLayout()
        self.step1_lbl = QLabel()
        self.step1_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {COLOR_TEXT_MAIN};")
        f_hdr.addWidget(self.step1_lbl)
        f_hdr.addStretch()

        self.btn_dl_xlsx = QPushButton()
        self.btn_dl_xlsx.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_dl_xlsx.setFixedHeight(28)
        self.btn_dl_xlsx.setStyleSheet("""
            QPushButton {
                background-color: #EFF6FF; color: #1D4ED8;
                border: 1px solid #BFDBFE; border-radius: 6px;
                font-size: 11px; font-weight: 600; padding: 0 10px;
            }
            QPushButton:hover { background-color: #DBEAFE; }
        """)
        self.btn_dl_xlsx.clicked.connect(lambda: self._download_sample("xlsx"))

        self.btn_dl_csv = QPushButton()
        self.btn_dl_csv.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_dl_csv.setFixedHeight(28)
        self.btn_dl_csv.setStyleSheet("""
            QPushButton {
                background-color: #F8FAFC; color: #334155;
                border: 1px solid #CBD5E1; border-radius: 6px;
                font-size: 11px; font-weight: 600; padding: 0 10px;
            }
            QPushButton:hover { background-color: #F1F5F9; }
        """)
        self.btn_dl_csv.clicked.connect(lambda: self._download_sample("csv"))

        f_hdr.addWidget(self.btn_dl_xlsx)
        f_hdr.addWidget(self.btn_dl_csv)
        f_layout.addLayout(f_hdr)

        pick_row = QHBoxLayout()
        pick_row.setSpacing(10)
        self.edit_file_path = QLineEdit()
        self.edit_file_path.setReadOnly(True)
        self.edit_file_path.setFixedHeight(36)
        self.edit_file_path.setStyleSheet(f"""
            QLineEdit {{
                background-color: #F8FAFC;
                color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER}; border-radius: 8px;
                padding: 0 12px; font-size: 12px;
            }}
        """)
        pick_row.addWidget(self.edit_file_path, stretch=1)

        self.btn_browse = QPushButton()
        self.btn_browse.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_browse.setFixedHeight(36)
        self.btn_browse.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT_BLUE}; color: white;
                border: none; border-radius: 8px;
                font-size: 12px; font-weight: 700; padding: 0 16px;
            }}
            QPushButton:hover {{ background-color: {COLOR_PRIMARY_DARK}; }}
        """)
        self.btn_browse.clicked.connect(self._browse_file)
        pick_row.addWidget(self.btn_browse)
        f_layout.addLayout(pick_row)

        c_layout.addWidget(f_card)

        # ── Step 2: Replacement Strategy Card ────────────────────────
        s_card = QFrame()
        s_card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER};
                border-radius: 10px;
                padding: 12px;
            }}
        """)
        s_layout = QVBoxLayout(s_card)
        s_layout.setSpacing(10)

        self.step2_lbl = QLabel()
        self.step2_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {COLOR_TEXT_MAIN};")
        s_layout.addWidget(self.step2_lbl)

        self.strategy_group = QButtonGroup(self)

        # Option 1: Both (Recommended)
        self.rb_both = QRadioButton()
        self.rb_both.setChecked(True)
        self.rb_both.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {COLOR_TEXT_MAIN};")
        self.strategy_group.addButton(self.rb_both, 1)

        self.desc_both = QLabel()
        self.desc_both.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_MUTED}; margin-bottom: 4px;")

        # Option 2: Mobile only
        self.rb_mobile = QRadioButton()
        self.rb_mobile.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {COLOR_TEXT_MAIN};")
        self.strategy_group.addButton(self.rb_mobile, 2)

        self.desc_mobile = QLabel()
        self.desc_mobile.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_MUTED}; margin-bottom: 4px;")

        # Option 3: Form number only
        self.rb_code = QRadioButton()
        self.rb_code.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {COLOR_TEXT_MAIN};")
        self.strategy_group.addButton(self.rb_code, 3)

        self.desc_code = QLabel()
        self.desc_code.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_MUTED}; margin-bottom: 4px;")

        # Option 4: Insert only
        self.rb_insert = QRadioButton()
        self.rb_insert.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {COLOR_TEXT_MAIN};")
        self.strategy_group.addButton(self.rb_insert, 4)

        self.desc_insert = QLabel()
        self.desc_insert.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_MUTED};")

        s_layout.addWidget(self.rb_both)
        s_layout.addWidget(self.desc_both)
        s_layout.addWidget(self.rb_mobile)
        s_layout.addWidget(self.desc_mobile)
        s_layout.addWidget(self.rb_code)
        s_layout.addWidget(self.desc_code)
        s_layout.addWidget(self.rb_insert)
        s_layout.addWidget(self.desc_insert)

        # Options check boxes
        opt_box = QHBoxLayout()
        opt_box.setSpacing(20)

        self.cb_keep_blank = QCheckBox()
        self.cb_keep_blank.setChecked(True)
        self.cb_keep_blank.setStyleSheet(f"font-size: 11.5px; font-weight: 600; color: {COLOR_TEXT_MAIN};")

        self.cb_safety_backup = QCheckBox()
        self.cb_safety_backup.setChecked(True)
        self.cb_safety_backup.setStyleSheet(f"font-size: 11.5px; font-weight: 600; color: {COLOR_TEXT_MAIN};")

        opt_box.addWidget(self.cb_keep_blank)
        opt_box.addWidget(self.cb_safety_backup)
        s_layout.addSpacing(6)
        s_layout.addLayout(opt_box)

        c_layout.addWidget(s_card)

        # ── Step 3: Live Data Preview Card ───────────────────────────
        p_card = QFrame()
        p_card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER};
                border-radius: 10px;
                padding: 12px;
            }}
        """)
        p_layout = QVBoxLayout(p_card)
        p_layout.setSpacing(8)

        p_hdr = QHBoxLayout()
        self.step3_lbl = QLabel()
        self.step3_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {COLOR_TEXT_MAIN};")
        p_hdr.addWidget(self.step3_lbl)

        self.lbl_stats = QLabel()
        self.lbl_stats.setStyleSheet("""
            background-color: #F1F5F9; color: #475569;
            border-radius: 12px; padding: 3px 10px;
            font-size: 11px; font-weight: 600;
        """)
        p_hdr.addWidget(self.lbl_stats)
        p_hdr.addStretch()
        p_layout.addLayout(p_hdr)

        self.preview_table = QTableWidget(0, 0)
        self.preview_table.setFixedHeight(160)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER};
                gridline-color: #F1F5F9;
                font-size: 11px;
            }}
            QHeaderView::section {{
                background-color: #0F172A;
                color: #FFFFFF;
                font-weight: 700;
                font-size: 11px;
                padding: 4px;
                border: none;
            }}
        """)
        self.preview_table.horizontalHeader().setStretchLastSection(True)
        p_layout.addWidget(self.preview_table)

        c_layout.addWidget(p_card)

        scroll.setWidget(content)
        main_layout.addWidget(scroll, stretch=1)

        # ── Progress Bar ─────────────────────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #E2E8F0;
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {COLOR_ACCENT_BLUE};
                border-radius: 4px;
            }}
        """)
        main_layout.addWidget(self.progress_bar)

        # ── Bottom Action Buttons ────────────────────────────────────
        act_row = QHBoxLayout()
        act_row.setSpacing(12)

        self.btn_cancel = QPushButton()
        self.btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_cancel.setFixedHeight(38)
        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF; color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER}; border-radius: 8px;
                font-size: 12px; font-weight: 600; padding: 0 18px;
            }}
            QPushButton:hover {{ background-color: #F8FAFC; }}
        """)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_start = QPushButton()
        self.btn_start.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_start.setFixedHeight(38)
        self.btn_start.setEnabled(False)
        self.btn_start.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT_EMERALD}; color: white;
                border: none; border-radius: 8px;
                font-size: 12px; font-weight: 700; padding: 0 24px;
            }}
            QPushButton:hover {{ background-color: #059669; }}
            QPushButton:disabled {{ background-color: #94A3B8; color: #E2E8F0; }}
        """)
        self.btn_start.clicked.connect(self._run_import)

        act_row.addStretch()
        act_row.addWidget(self.btn_cancel)
        act_row.addWidget(self.btn_start)
        main_layout.addLayout(act_row)

    def set_language(self, lang: str):
        self._current_lang = lang
        is_en = (lang == 'en')

        self.setWindowTitle("Data Import & Smart Upsert" if is_en else "ડેટા આયાત અને સ્માર્ટ અપડેટ")
        self.t_lbl.setText("Member Data Import & Smart Upsert" if is_en else "સભ્ય ડેટા આયાત અને સ્માર્ટ અપડેટ")
        self.s_lbl.setText(
            "Add members from Excel or CSV file. If mobile number or form number already exists in database, data will automatically be updated/replaced."
            if is_en else
            "Excel અથવા CSV ફાઇલમાંથી સભ્યો ઉમેરો. જો મોબાઇલ નંબર અથવા ફોર્મ નંબર ડેટાબેઝમાં પહેલેથી હોય તો ડેટા આપમેળે બદલાઈ (Replace) જશે."
        )

        self.step1_lbl.setText("1. Select Excel or CSV File" if is_en else "૧. એક્સેલ અથવા CSV ફાઇલ પસંદ કરો")
        self.btn_dl_xlsx.setText("📄 Download Sample Excel" if is_en else "📄 સેમ્પલ Excel ડાઉનલોડ")
        self.btn_dl_csv.setText("📄 Download Sample CSV" if is_en else "📄 સેમ્પલ CSV ડાઉનલોડ")
        self.edit_file_path.setPlaceholderText("No file selected... (.xlsx, .xls or .csv)" if is_en else "કોઈ ફાઇલ પસંદ કરેલ નથી... (.xlsx, .xls અથવા .csv)")
        self.btn_browse.setText("📁 Browse File" if is_en else "📁 ફાઇલ પસંદ કરો")

        self.step2_lbl.setText("2. Replacement & Matching Strategy When Data Exists" if is_en else "૨. ડેટા સરખો હોય ત્યારે બદલવાની પદ્ધતિ")
        self.rb_both.setText("⚡ Match by Form Number OR Mobile Number (Recommended)" if is_en else "⚡ મોબાઇલ અથવા ફોર્મ નંબર બંને દ્વારા સરખામણી કરી બદલો — ભલામણ કરેલ")
        self.desc_both.setText(
            "     → If form number matches, existing member is updated; otherwise matches mobile number. If neither matches, a new member is added."
            if is_en else
            "     → જો ફોર્મ નંબર મળે તો તે સભ્ય બદલાશે; જો ફોર્મ નંબર ન હોય તો મોબાઇલ નંબર દ્વારા મેચિંગ થશે. ડેટાબેઝમાં ન હોય તો નવો સભ્ય ઉમેરાશે."
        )

        self.rb_mobile.setText("📱 Match by Mobile Number only" if is_en else "📱 માત્ર મોબાઇલ નંબર દ્વારા બદલો")
        self.desc_mobile.setText(
            "     → If the provided mobile number is already registered, that member's details will be updated. A new mobile number creates a new member."
            if is_en else
            "     → જો આપેલો મોબાઇલ નંબર ડેટાબેઝમાં પહેલેથી નોંધાયેલ હશે, તો તે સભ્યની બાકીની વિગતો બદલાશે. નવો મોબાઇલ હોય તો નવો સભ્ય બનશે."
        )

        self.rb_code.setText("📋 Match by Form Number / Member Code only" if is_en else "📋 માત્ર ફોર્મ નંબર / સભ્ય કોડ દ્વારા બદલો")
        self.desc_code.setText(
            "     → If the member code (e.g. GBS-000045 or 45) matches, the existing record will be updated. A new code creates a new member."
            if is_en else
            "     → સભ્ય કોડ (જેમ કે GBS-000045 અથવા 45) સરખો હોય તો જૂના સભ્યનો ડેટા બદલાશે. નવો કોડ હોય તો નવો સભ્ય ઉમેરાશે."
        )

        self.rb_insert.setText("➕ Insert Only (Skip duplicates)" if is_en else "➕ માત્ર નવા સભ્યો ઉમેરો (ડુપ્લિકેટ હોય તો છોડી દો)")
        self.desc_insert.setText(
            "     → No existing member data will be modified; only completely new members will be added to the system."
            if is_en else
            "     → કોઈ પણ જૂના સભ્યનો ડેટા બદલવામાં આવશે નહીં; માત્ર તદ્દન નવા સભ્યો જ સિસ્ટમમાં ઉમેરાશે."
        )

        self.cb_keep_blank.setText("Keep existing values if Excel column is blank" if is_en else "જૂની વિગતો સાચવી રાખો જો એક્સેલમાં કોલમ ખાલી હોય")
        self.cb_safety_backup.setText("Automatic safety backup before import" if is_en else "આયાત કરતાં પહેલાં આપમેળે સુરક્ષા બેકઅપ લો")

        self.step3_lbl.setText("3. File Preview & Mapped Columns" if is_en else "૩. ફાઇલ પ્રીવ્યુ અને મેપ કરેલ કોલમ")
        if not self._parsed_rows:
            self.lbl_stats.setText("No file selected" if is_en else "ફાઇલ પસંદ થયેલ નથી")
        else:
            self.lbl_stats.setText(
                f"✓ {len(self._parsed_rows)} records found • {len(self._mapped_keys)} columns identified"
                if is_en else
                f"✓ {len(self._parsed_rows)} રેકોર્ડ્સ મળ્યા • {len(self._mapped_keys)} કોલમ ઓળખાઈ"
            )

        self.btn_cancel.setText("Close" if is_en else "બંધ કરો")
        self.btn_start.setText("📥  Start Data Import" if is_en else "📥  ડેટા આયાત શરૂ કરો")

        if self._parsed_rows:
            self._update_preview_table()

    def _browse_file(self):
        is_en = (self._current_lang == 'en')
        filt = (
            "Data Files (*.xlsx *.xls *.csv);;Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*.*)"
            if is_en else
            "ડેટા ફાઇલ્સ (*.xlsx *.xls *.csv);;Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*.*)"
        )
        title = "Select File to Import" if is_en else "આયાત કરવા માટે ફાઇલ પસંદ કરો"
        path, _ = QFileDialog.getOpenFileName(
            self,
            title,
            EXPORT_DIR,
            filt,
        )
        if not path:
            return

        self._selected_file_path = path
        self.edit_file_path.setText(path)
        self._load_and_preview(path)

    def _update_preview_table(self):
        is_en = (self._current_lang == 'en')
        preview_cols = [
            ("Member Code" if is_en else "સભ્ય કોડ", "member_code"),
            ("Full Name" if is_en else "નામ", "full_name"),
            ("Mobile Number" if is_en else "મોબાઈલ નંબર", "mobile"),
            ("City" if is_en else "શહેર", "city"),
            ("Occupation" if is_en else "વ્યવસાય", "occupation"),
        ]
        self.preview_table.setColumnCount(len(preview_cols))
        self.preview_table.setHorizontalHeaderLabels([c[0] for c in preview_cols])

        preview_count = min(5, len(self._parsed_rows))
        self.preview_table.setRowCount(preview_count)
        for r_idx in range(preview_count):
            row_data = self._parsed_rows[r_idx]
            for c_idx, (_, field_key) in enumerate(preview_cols):
                val = row_data.get(field_key, "")
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.preview_table.setItem(r_idx, c_idx, item)

        self.preview_table.resizeColumnsToContents()

    def _load_and_preview(self, path: str):
        is_en = (self._current_lang == 'en')
        try:
            rows, keys, raw_headers = ImportExportService.read_file(path)
            self._parsed_rows = rows
            self._mapped_keys = keys
            self._raw_headers = raw_headers

            if not rows:
                self.lbl_stats.setText("⚠️ No data found in file" if is_en else "⚠️ ફાઇલમાં કોઈ ડેટા મળ્યો નથી")
                self.lbl_stats.setStyleSheet("background-color: #FEF3C7; color: #B45309; border-radius: 12px; padding: 3px 10px; font-size: 11px; font-weight: 600;")
                self.btn_start.setEnabled(False)
                self.preview_table.setRowCount(0)
                self.preview_table.setColumnCount(0)
                return

            self.lbl_stats.setText(
                f"✓ {len(rows)} records found • {len(keys)} columns identified"
                if is_en else
                f"✓ {len(rows)} રેકોર્ડ્સ મળ્યા • {len(keys)} કોલમ ઓળખાઈ"
            )
            self.lbl_stats.setStyleSheet("background-color: #ECFDF5; color: #047857; border-radius: 12px; padding: 3px 10px; font-size: 11px; font-weight: 700;")
            self.btn_start.setEnabled(True)

            self._update_preview_table()

        except Exception as e:
            title = "Error Reading File" if is_en else "ફાઇલ વાંચવામાં ક્ષતિ"
            msg = f"Could not read file:\n{str(e)}" if is_en else f"ફાઇલ વાંચી શકાઈ નથી:\n{str(e)}"
            QMessageBox.critical(self, title, msg)
            self.btn_start.setEnabled(False)

    def _download_sample(self, format_type: str):
        is_en = (self._current_lang == 'en')
        ext = ".xlsx" if format_type == "xlsx" else ".csv"
        filter_str = f"{'Excel' if format_type == 'xlsx' else 'CSV'} Files (*{ext})"
        default_name = os.path.join(EXPORT_DIR, f"sample_members_template{ext}")

        dialog_title = f"Save Sample {format_type.upper()} Template" if is_en else f"સેમ્પલ {format_type.upper()} ટેમ્પલેટ સેવ કરો"
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            dialog_title,
            default_name,
            filter_str,
        )
        if not save_path:
            return

        try:
            out_file = ImportExportService.generate_sample_template(save_path, format_type)
            succ_title = "Template Downloaded" if is_en else "ટેમ્પલેટ ડાઉનલોડ સફળ"
            succ_msg = (
                f"Sample template saved successfully:\n\n{out_file}\n\nYou can fill in member details and import it."
                if is_en else
                f"નમૂના (Sample) ટેમ્પલેટ સફળતાપૂર્વક સાચવવામાં આવી છે:\n\n{out_file}\n\nઆ ફાઇલમાં તમારા સભ્યોની વિગતો ભરીને આયાત કરી શકો છો."
            )
            QMessageBox.information(self, succ_title, succ_msg)
        except Exception as e:
            err_title = "Error" if is_en else "ક્ષતિ"
            err_msg = f"Failed to generate template:\n{str(e)}" if is_en else f"ટેમ્પલેટ બનાવવામાં ક્ષતિ આવી:\n{str(e)}"
            QMessageBox.critical(self, err_title, err_msg)

    def _get_selected_strategy(self) -> str:
        if self.rb_both.isChecked():
            return "both"
        elif self.rb_mobile.isChecked():
            return "mobile"
        elif self.rb_code.isChecked():
            return "code"
        elif self.rb_insert.isChecked():
            return "insert_only"
        return "both"

    def _run_import(self):
        is_en = (self._current_lang == 'en')
        if not self._selected_file_path or not os.path.exists(self._selected_file_path):
            warn_title = "Warning" if is_en else "ચેતવણી"
            warn_msg = "Please select a valid file first." if is_en else "કૃપા કરીને પહેલાં માન્ય ફાઇલ પસંદ કરો."
            QMessageBox.warning(self, warn_title, warn_msg)
            return

        strat = self._get_selected_strategy()
        keep_blank = self.cb_keep_blank.isChecked()
        safety_backup = self.cb_safety_backup.isChecked()

        if is_en:
            strat_name_map = {
                "both": "Match by Form No OR Mobile (Recommended)",
                "mobile": "Match by Mobile Number only",
                "code": "Match by Form Number only",
                "insert_only": "Insert Only (Skip duplicates)",
            }
            confirm_title = "Confirm Import"
            confirm_msg = (
                f"You are about to import {len(self._parsed_rows)} member records with the following configuration:\n\n"
                f"• Strategy: {strat_name_map.get(strat, strat)}\n"
                f"• Safety Backup: {'Yes' if safety_backup else 'No'}\n\n"
                f"Do you want to proceed?"
            )
        else:
            strat_name_map = {
                "both": "મોબાઈલ અથવા ફોર્મ નંબર બંને દ્વારા",
                "mobile": "માત્ર મોબાઇલ નંબર દ્વારા",
                "code": "માત્ર ફોર્મ નંબર દ્વારા",
                "insert_only": "માત્ર નવા ઉમેરો",
            }
            confirm_title = "આયાતની ખાતરી"
            confirm_msg = (
                f"તમે નીચેની પદ્ધતિ સાથે {len(self._parsed_rows)} સભ્યોનો ડેટા આયાત કરવા માંગો છો:\n\n"
                f"• પદ્ધતિ: {strat_name_map.get(strat, strat)}\n"
                f"• સુરક્ષા બેકઅપ: {'હા' if safety_backup else 'ના'}\n\n"
                f"શું તમે આગળ વધવા માંગો છો?"
            )

        reply = QMessageBox.question(
            self,
            confirm_title,
            confirm_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Disable buttons and run
        self.btn_start.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # indeterminate pulse

        result: ImportResult = ImportExportService.import_members(
            file_path=self._selected_file_path,
            match_strategy=strat,
            keep_existing_on_blank=keep_blank,
            create_safety_backup=safety_backup,
        )

        self.progress_bar.setVisible(False)
        self.btn_cancel.setEnabled(True)
        self.btn_start.setEnabled(True)

        if not result.success:
            fail_title = "Import Failed" if is_en else "આયાત નિષ્ફળ"
            QMessageBox.critical(self, fail_title, result.message)
            return

        # Show detailed result dialog
        self._show_result_summary(result)
        self.import_finished.emit(result)
        self.accept()

    def _show_result_summary(self, res: ImportResult):
        is_en = (self._current_lang == 'en')
        dialog = QDialog(self)
        dialog.setWindowTitle("Data Import Summary" if is_en else "ડેટા આયાત સારાંશ")
        dialog.setMinimumSize(560, 420)
        dialog.setStyleSheet(f"background-color: {COLOR_BG}; font-family: 'Noto Sans Gujarati', 'Segoe UI', sans-serif;")

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 20, 20, 20)
        d_layout.setSpacing(14)

        # Success banner
        top_text = "🎉 Data import process completed successfully!" if is_en else "🎉 ડેટા આયાત પ્રક્રિયા સફળતાપૂર્વક પૂર્ણ થઈ!"
        top = QLabel(top_text)
        top.setStyleSheet(f"font-size: 15px; font-weight: 800; color: {COLOR_ACCENT_EMERALD};")
        d_layout.addWidget(top)

        # Stats Cards
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER};
                border-radius: 10px;
                padding: 14px;
            }}
        """)
        c_grid = QVBoxLayout(card)
        c_grid.setSpacing(8)

        def make_stat_row(label: str, val: str, color_hex: str):
            r = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet(f"font-size: 12.5px; font-weight: 600; color: {COLOR_TEXT_MAIN};")
            v = QLabel(val)
            v.setStyleSheet(f"font-size: 13px; font-weight: 800; color: {color_hex};")
            r.addWidget(lbl)
            r.addStretch()
            r.addWidget(v)
            return r

        if is_en:
            c_grid.addLayout(make_stat_row("Total Processed Records:", str(res.total_rows), COLOR_TEXT_MAIN))
            c_grid.addLayout(make_stat_row("➕ New Members Inserted:", str(res.inserted_count), COLOR_ACCENT_EMERALD))
            c_grid.addLayout(make_stat_row("🔄 Existing Members Updated:", str(res.updated_count), COLOR_ACCENT_BLUE))
            c_grid.addLayout(make_stat_row("⚠️ Skipped Records / Errors:", str(res.skipped_count), "#D97706"))
            if res.backup_path:
                b_lbl = QLabel(f"🛡️ Automatic safety backup created:\n{res.backup_path}")
                b_lbl.setStyleSheet("font-size: 11px; color: #64748B; background-color: #F8FAFC; border-radius: 6px; padding: 6px;")
                c_grid.addWidget(b_lbl)
        else:
            c_grid.addLayout(make_stat_row("કુલ પ્રોસેસ થયેલા રેકોર્ડ્સ:", str(res.total_rows), COLOR_TEXT_MAIN))
            c_grid.addLayout(make_stat_row("➕ નવા સભ્યો ઉમેરાયા:", str(res.inserted_count), COLOR_ACCENT_EMERALD))
            c_grid.addLayout(make_stat_row("🔄 જૂના સભ્યો બદલાયા:", str(res.updated_count), COLOR_ACCENT_BLUE))
            c_grid.addLayout(make_stat_row("⚠️ છોડી દીધેલા રેકોર્ડ્સ:", str(res.skipped_count), "#D97706"))
            if res.backup_path:
                b_lbl = QLabel(f"🛡️ આપમેળે સુરક્ષા બેકઅપ લેવાયો:\n{res.backup_path}")
                b_lbl.setStyleSheet("font-size: 11px; color: #64748B; background-color: #F8FAFC; border-radius: 6px; padding: 6px;")
                c_grid.addWidget(b_lbl)

        d_layout.addWidget(card)

        # If errors occurred, show error table
        if res.errors:
            err_title = QLabel("Error Details:" if is_en else "વિગતવાર ભૂલો:")
            err_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #DC2626;")
            d_layout.addWidget(err_title)

            err_table = QTableWidget(len(res.errors), 3)
            headers = ["Row #", "Name / Mobile", "Reason / Error"] if is_en else ["રો નં", "નામ / મોબાઇલ", "કારણ / ક્ષતિ"]
            err_table.setHorizontalHeaderLabels(headers)
            err_table.setStyleSheet("font-size: 11px;")
            for e_idx, err in enumerate(res.errors):
                err_table.setItem(e_idx, 0, QTableWidgetItem(str(err.row_num)))
                err_table.setItem(e_idx, 1, QTableWidgetItem(f"{err.name} ({err.mobile})"))
                err_table.setItem(e_idx, 2, QTableWidgetItem(err.error))
            err_table.horizontalHeader().setStretchLastSection(True)
            d_layout.addWidget(err_table, stretch=1)

        btn_ok = QPushButton("OK" if is_en else "ઠીક છે")
        btn_ok.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_ok.setFixedHeight(36)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT_BLUE}; color: white;
                border: none; border-radius: 8px;
                font-size: 12px; font-weight: 700; padding: 0 20px;
            }}
            QPushButton:hover {{ background-color: {COLOR_PRIMARY_DARK}; }}
        """)
        btn_ok.clicked.connect(dialog.accept)
        d_layout.addWidget(btn_ok, alignment=Qt.AlignmentFlag.AlignRight)

        dialog.exec()
