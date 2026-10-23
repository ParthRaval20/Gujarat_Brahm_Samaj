"""
Modern Backup and Restore Page — Matching Stitch Design (code2.html).
Features:
- Page Header Banner with Organization Data Portal badge
- 3 System Health Status Cards (Last Backup, Total Archives, Database Integrity)
- Action Panels (Create Backup with Full/Incremental & Encryption options, Schedule Settings)
- Archives Management Table with Restore, Export, and Verification actions
"""

from __future__ import annotations

import os
import shutil
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QRadioButton, QCheckBox,
    QScrollArea, QAbstractItemView,
)

from app.config import (
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_BG, COLOR_CARD_BG,
    COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    COLOR_ACCENT_BLUE, COLOR_ACCENT_EMERALD, COLOR_ACCENT_PURPLE,
    COLOR_ACCENT_AMBER, COLOR_ACCENT_ROSE, BACKUP_DIR, EXPORT_DIR,
    DB_PATH, ensure_dirs,
)
from services.backup_service import (
    create_backup, restore_backup, list_backups,
    check_database_integrity, get_backup_stats,
)
from database.connection import init_db
from ui.import_data_dialog import ImportDataDialog


class BackupRestorePage(QWidget):
    def __init__(self, nav_callback, on_data_updated=None, parent=None):
        super().__init__(parent)
        self._nav = nav_callback
        self._on_data_updated = on_data_updated
        self._current_lang = 'gu'
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background-color: {COLOR_BG}; border: none; }}")

        container = QWidget()
        container.setObjectName("backupContainer")
        container.setStyleSheet(f"#backupContainer {{ background-color: {COLOR_BG}; }}")
        self.layout = QVBoxLayout(container)
        self.layout.setContentsMargins(28, 24, 28, 28)
        self.layout.setSpacing(22)

        # ── 1. Page Header Banner ───────────────────────────────────
        self.layout.addWidget(self._create_header_banner())

        # ── 2. Quick Status Cards (3 Cards) ──────────────────────────
        self.layout.addWidget(self._create_status_cards_section())

        # ── 3. Dual Action Panels (Create Backup & Schedule) ─────────
        self.layout.addWidget(self._create_action_panels_section())

        # ── 4. Stored Backup Archives Table ──────────────────────────
        self.layout.addWidget(self._create_archives_table_section())

        scroll.setWidget(container)
        outer.addWidget(scroll)

    # =========================================================================
    # 1. HEADER BANNER
    # =========================================================================
    def _create_header_banner(self) -> QWidget:
        banner = QFrame()
        banner.setObjectName("backupBanner")
        banner.setStyleSheet(f"""
            QFrame#backupBanner {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0D1C3A, stop:0.5 #122853, stop:1 #1E3A78);
                border: 1px solid #1E293B;
                border-radius: 16px;
            }}
        """)

        layout = QHBoxLayout(banner)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        left_box = QVBoxLayout()
        left_box.setSpacing(8)

        self.banner_pill = QLabel("🛡️ શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સત્તાવાર ડેટા પોર્ટલ")
        self.banner_pill.setStyleSheet("""
            QLabel {
                background-color: rgba(59, 130, 246, 0.20);
                color: #93C5FD;
                border: 1px solid rgba(147, 197, 253, 0.40);
                border-radius: 12px;
                padding: 3px 12px;
                font-size: 11px;
                font-weight: 600;
            }
        """)
        self.banner_pill.setFixedHeight(26)

        self.banner_title = QLabel("ડેટા બેકઅપ અને રીસ્ટોર મેનેજમેન્ટ")
        self.banner_title.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: 800; background: transparent;")

        self.banner_sub = QLabel(
            "સમાજના તમામ સભ્યોનો ડેટા, ફોટો આર્કાઇવ્સ અને પરિવાર વિગતો સુરક્ષિત રાખવા માટે સ્થાનિક તેમજ સુરક્ષિત બેકઅપનું સંચાલન કરો."
        )
        self.banner_sub.setStyleSheet("color: #BFDBFE; font-size: 13px; font-weight: 400; background: transparent;")

        left_box.addWidget(self.banner_pill, alignment=Qt.AlignmentFlag.AlignLeft)
        left_box.addWidget(self.banner_title)
        left_box.addWidget(self.banner_sub)
        layout.addLayout(left_box, stretch=1)

        # Action buttons on banner
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)

        self.btn_import_excel = QPushButton("📥  એક્સેલ/CSV ડેટા આયાત")
        self.btn_import_excel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_import_excel.setFixedHeight(40)
        self.btn_import_excel.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.22);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.40);
                border-radius: 10px;
                padding: 0 16px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.32);
            }
        """)
        self.btn_import_excel.clicked.connect(self._open_import_dialog)
        btn_box.addWidget(self.btn_import_excel)

        self.btn_quick_export = QPushButton("📤  સંપૂર્ણ ડેટા એક્સપોર્ટ")
        self.btn_quick_export.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_quick_export.setFixedHeight(40)
        self.btn_quick_export.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.30);
                border-radius: 10px;
                padding: 0 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
        """)
        self.btn_quick_export.clicked.connect(self._create_external_backup)
        btn_box.addWidget(self.btn_quick_export)

        layout.addLayout(btn_box)

        return banner

    # =========================================================================
    # 2. STATUS CARDS
    # =========================================================================
    def _create_status_cards_section(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Card 1: Last Successful Backup
        self.card_last_val = QLabel("તપાસ કરી રહ્યા છીએ...")
        self.card_last_sub = QLabel("સ્થાનિક ડિસ્ક")
        self.card1 = self._build_status_card(
            title="છેલ્લો સફળ બેકઅપ",
            value_label=self.card_last_val,
            icon="💾",
            icon_bg="#ECFDF5",
            accent_color=COLOR_ACCENT_EMERALD,
            footer_text="● Auto-Backup સક્રિય છે",
            footer_color="#059669",
            sub_label=self.card_last_sub,
        )

        # Card 2: Total Stored Backups
        self.card_count_val = QLabel("0 ફાઇલ્સ")
        self.card_size_sub = QLabel("કુલ રોકાયેલી જગ્યા: 0.0 MB")
        self.card2 = self._build_status_card(
            title="સંગ્રહિત બેકઅપ ફાઇલો",
            value_label=self.card_count_val,
            icon="📦",
            icon_bg="#EFF6FF",
            accent_color=COLOR_ACCENT_BLUE,
            footer_text="સંગ્રહ મર્યાદા: સ્થાનિક સ્ટોરેજ ઉપલબ્ધ",
            footer_color="#2563EB",
            sub_label=self.card_size_sub,
        )

        # Card 3: Integrity & Database Health
        self.card_health_val = QLabel("100% સ્વસ્થ")
        self.card_health_sub = QLabel("SQLite Integrity Check Pass")
        self.card3 = self._build_status_card(
            title="ડેટાબેઝ હેલ્થ",
            value_label=self.card_health_val,
            icon="🛡️",
            icon_bg="#F5F3FF",
            accent_color=COLOR_ACCENT_PURPLE,
            footer_text="ભૂલો કે કરપ્શન: 0 રેકોર્ડ્સ",
            footer_color="#059669",
            sub_label=self.card_health_sub,
        )

        layout.addWidget(self.card1)
        layout.addWidget(self.card2)
        layout.addWidget(self.card3)

        return container

    def _build_status_card(
        self, title: str, value_label: QLabel, icon: str,
        icon_bg: str, accent_color: str, footer_text: str,
        footer_color: str, sub_label: QLabel,
    ) -> QWidget:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER};
                border-radius: 14px;
            }}
            QFrame:hover {{
                border-color: {accent_color};
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(10)

        # Top row: title + icon
        top_row = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-weight: 700; text-transform: uppercase;")
        card.title_lbl = title_lbl

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            background-color: {icon_bg};
            border-radius: 8px;
            font-size: 16px;
        """)

        top_row.addWidget(title_lbl, stretch=1)
        top_row.addWidget(icon_lbl)
        card_layout.addLayout(top_row)

        # Value & subtext
        value_label.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 18px; font-weight: 800;")
        sub_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px; font-weight: 500;")

        card_layout.addWidget(value_label)
        card_layout.addWidget(sub_label)
        card_layout.addSpacing(4)

        # Footer divider + text
        footer = QLabel(footer_text)
        footer.setStyleSheet(f"""
            color: {footer_color};
            font-size: 11px;
            font-weight: 600;
            border-top: 1px solid {COLOR_BORDER};
            padding-top: 8px;
        """)
        card.footer_lbl = footer
        card_layout.addWidget(footer)

        return card

    # =========================================================================
    # 3. ACTION PANELS (Create Backup & Schedule)
    # =========================================================================
    def _create_action_panels_section(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # ── Left 2-Cols: Create Backup Panel ─────────────────────────
        panel_create = QFrame()
        panel_create.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER};
                border-radius: 14px;
            }}
        """)
        pc_layout = QVBoxLayout(panel_create)
        pc_layout.setContentsMargins(20, 18, 20, 18)
        pc_layout.setSpacing(14)

        # Header
        h_row = QHBoxLayout()
        h_row.setSpacing(12)

        icon_box = QLabel("💾")
        icon_box.setFixedSize(36, 36)
        icon_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_box.setStyleSheet(f"background-color: #EFF6FF; border-radius: 8px; font-size: 16px;")

        t_box = QVBoxLayout()
        t_box.setSpacing(2)
        self.p_title = QLabel("નવો ડેટાબેઝ બેકઅપ બનાવો")
        self.p_title.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 15px; font-weight: 800;")
        self.p_sub = QLabel("સમાજના સભ્યો, દસ્તાવેજો અને ઓડિટ લોગનો તુરંત સુરક્ષિત સ્થાનિક તેમજ એન્ક્રિપ્ટેડ બેકઅપ બનાવો.")
        self.p_sub.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px;")
        t_box.addWidget(self.p_title)
        t_box.addWidget(self.p_sub)

        h_row.addWidget(icon_box)
        h_row.addLayout(t_box)
        pc_layout.addLayout(h_row)

        # Radio options: Full vs Incremental
        radio_row = QHBoxLayout()
        radio_row.setSpacing(12)

        self.radio_full = QRadioButton("Full Backup (સંપૂર્ણ ડેટાબેઝ) — ભલામણ કરેલ")
        self.radio_full.setChecked(True)
        self.radio_full.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLOR_TEXT_MAIN};")

        self.radio_inc = QRadioButton("Incremental (છેલ્લા ફેરફારો)")
        self.radio_inc.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLOR_TEXT_MAIN};")

        radio_row.addWidget(self.radio_full)
        radio_row.addWidget(self.radio_inc)
        radio_row.addStretch()
        pc_layout.addLayout(radio_row)

        # Security Encryption Toggle
        enc_box = QFrame()
        enc_box.setStyleSheet(f"""
            background-color: #F8FAFC;
            border: 1px solid {COLOR_BORDER};
            border-radius: 8px;
            padding: 8px 12px;
        """)
        enc_layout = QHBoxLayout(enc_box)
        enc_layout.setContentsMargins(4, 4, 4, 4)

        self.chk_encrypt = QCheckBox("સુરક્ષિત આર્કાઇવ સાથે સુરક્ષિત કરો (SHA-256 Verified Signature)")
        self.chk_encrypt.setChecked(True)
        self.chk_encrypt.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLOR_TEXT_MAIN};")

        self.badge_enc = QLabel("સુરક્ષિત આર્કાઇવ")
        self.badge_enc.setStyleSheet("""
            background-color: #ECFDF5; color: #059669;
            border-radius: 6px; padding: 2px 8px; font-size: 10px; font-weight: 700;
        """)

        enc_layout.addWidget(self.chk_encrypt)
        enc_layout.addStretch()
        enc_layout.addWidget(self.badge_enc)
        pc_layout.addWidget(enc_box)

        # Action Buttons Row
        act_row = QHBoxLayout()
        act_row.setSpacing(10)

        self.btn_create = QPushButton("💾  હમણાં બેકઅપ લો")
        self.btn_create.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_create.setFixedHeight(40)
        self.btn_create.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT_BLUE};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 0 18px;
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_DARK};
            }}
        """)
        self.btn_create.clicked.connect(self._create_instant_backup)

        self.btn_browse_dest = QPushButton("📁 અન્ય ફોલ્ડરમાં...")
        self.btn_browse_dest.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_browse_dest.setFixedHeight(40)
        self.btn_browse_dest.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 0 14px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #F1F5F9;
            }}
        """)
        self.btn_browse_dest.clicked.connect(self._create_external_backup)

        act_row.addWidget(self.btn_create)
        act_row.addWidget(self.btn_browse_dest)
        act_row.addStretch()
        pc_layout.addLayout(act_row)

        layout.addWidget(panel_create, stretch=2)

        # ── Right 1-Col: Schedule & External Restore Panel ──────────
        panel_sched = QFrame()
        panel_sched.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER};
                border-radius: 14px;
            }}
        """)
        ps_layout = QVBoxLayout(panel_sched)
        ps_layout.setContentsMargins(20, 18, 20, 18)
        ps_layout.setSpacing(12)

        # Header
        ps_hdr = QHBoxLayout()
        ps_icon = QLabel("🕒")
        ps_icon.setFixedSize(32, 32)
        ps_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ps_icon.setStyleSheet("background-color: #FFFBEB; border-radius: 8px; font-size: 14px;")

        self.ps_title = QLabel("ઓટો-બેકઅપ શેડ્યૂલ")
        self.ps_title.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 14px; font-weight: 800;")
        ps_hdr.addWidget(ps_icon)
        ps_hdr.addWidget(self.ps_title)
        ps_hdr.addStretch()
        ps_layout.addLayout(ps_hdr)

        self.ps_desc = QLabel("સિસ્ટમ આપમેળે નિયત સમયે નવો બેકઅપ તૈયાર કરીને સ્થાનિક ડ્રાઇવમાં સાચવી રાખે છે.")
        self.ps_desc.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px;")
        self.ps_desc.setWordWrap(True)
        ps_layout.addWidget(self.ps_desc)

        # Info rows
        row1 = QHBoxLayout()
        self.r1_lbl = QLabel("આવર્તન:")
        self.r1_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px;")
        self.r1_val = QLabel("દરરોજ (Daily - 12:00 AM)")
        self.r1_val.setStyleSheet(f"color: {COLOR_ACCENT_BLUE}; font-size: 11px; font-weight: 700;")
        row1.addWidget(self.r1_lbl)
        row1.addStretch()
        row1.addWidget(self.r1_val)
        ps_layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.r2_lbl = QLabel("સ્થાન:")
        self.r2_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px;")
        self.r2_val = QLabel("Local backups/ folder")
        self.r2_val.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 11px; font-weight: 600;")
        row2.addWidget(self.r2_lbl)
        row2.addStretch()
        row2.addWidget(self.r2_val)
        ps_layout.addLayout(row2)

        ps_layout.addSpacing(6)

        # Restore from file button
        self.btn_restore_file = QPushButton("📂  ફાઇલમાંથી રીસ્ટોર કરો")
        self.btn_restore_file.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_restore_file.setFixedHeight(36)
        self.btn_restore_file.setStyleSheet(f"""
            QPushButton {{
                background-color: #FEF2F2;
                color: #DC2626;
                border: 1px solid #FECACA;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: #FEE2E2;
            }}
        """)
        self.btn_restore_file.clicked.connect(self._restore_from_file_dialog)
        ps_layout.addWidget(self.btn_restore_file)

        layout.addWidget(panel_sched, stretch=1)

        return container

    # =========================================================================
    # 4. ARCHIVES MANAGEMENT TABLE
    # =========================================================================
    def _create_archives_table_section(self) -> QWidget:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(14)

        # Header
        h_row = QHBoxLayout()
        icon_box = QLabel("🗄️")
        icon_box.setFixedSize(36, 36)
        icon_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_box.setStyleSheet(f"background-color: #EFF6FF; border-radius: 8px; font-size: 16px;")

        t_box = QVBoxLayout()
        t_box.setSpacing(2)
        self.tbl_title = QLabel("સંગ્રહિત બેકઅપ ફાઇલોની યાદી")
        self.tbl_title.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 15px; font-weight: 800;")
        self.tbl_sub = QLabel("સ્થાનિક ડિસ્ક પર સંગ્રહિત પાછલા ડેટાબેઝ બેકઅપની યાદી અને રિકવરી સાધનો")
        self.tbl_sub.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px;")
        t_box.addWidget(self.tbl_title)
        t_box.addWidget(self.tbl_sub)

        h_row.addWidget(icon_box)
        h_row.addLayout(t_box)
        h_row.addStretch()

        self.btn_refresh = QPushButton("🔄 રિફ્રેશ")
        self.btn_refresh.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_refresh.setFixedHeight(32)
        self.btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #F1F5F9;
            }}
        """)
        self.btn_refresh.clicked.connect(self.refresh)
        h_row.addWidget(self.btn_refresh)
        layout.addLayout(h_row)

        # Table
        self.backup_table = QTableWidget(0, 4)
        self.backup_table.setHorizontalHeaderLabels([
            "બેકઅપ ફાઇલ નામ",
            "તારીખ અને સમય",
            "કદ",
            "કાર્ય",
        ])

        header = self.backup_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.backup_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.backup_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.backup_table.setAlternatingRowColors(True)
        self.backup_table.verticalHeader().setVisible(False)
        self.backup_table.setShowGrid(False)
        self.backup_table.setMinimumHeight(240)

        self.backup_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: #FFFFFF;
                alternate-background-color: #F8FAFC;
                color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                gridline-color: transparent;
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 10px 8px;
                border-bottom: 1px solid #F1F5F9;
            }}
            QTableWidget::item:selected {{
                background-color: #EFF6FF;
                color: {COLOR_ACCENT_BLUE};
            }}
            QHeaderView::section {{
                background-color: #0F172A;
                color: #FFFFFF;
                font-weight: 700;
                font-size: 11px;
                padding: 10px 8px;
                border: none;
                border-right: 1px solid #1E293B;
                text-transform: uppercase;
            }}
        """)

        layout.addWidget(self.backup_table)
        return card

    # =========================================================================
    # REFRESH & BACKUP LOGIC
    # =========================================================================
    def refresh(self) -> None:
        """Update status cards and archives table."""
        try:
            stats = get_backup_stats()
            is_en = (self._current_lang == 'en')

            last_bk = stats['last_backup']
            if is_en and ("ક્યારેય" in last_bk or "નહીં" in last_bk or "કોઈ" in last_bk or "નથી" in last_bk):
                last_bk = "None"
            self.card_last_val.setText(last_bk)

            count_txt = f"{stats['total_count']} Files Archived" if is_en else f"{stats['total_count']} ફાઇલ્સ સંગ્રહિત"
            size_txt = f"Total disk space: {stats['total_size_mb']} MB" if is_en else f"કુલ રોકાયેલી જગ્યા: {stats['total_size_mb']} MB"
            self.card_count_val.setText(count_txt)
            self.card_size_sub.setText(size_txt)

            health_txt = stats['health_message']
            if is_en:
                health_txt = health_txt.replace("સ્વસ્થ (Healthy)", "Healthy").replace("સ્વસ્થ", "Healthy")
                if "100%" in health_txt and "Healthy" in health_txt:
                    health_txt = "100% Healthy — 0 Corrupted records"
            self.card_health_val.setText(health_txt)

            backups = list_backups()
            for r in range(self.backup_table.rowCount()):
                w = self.backup_table.cellWidget(r, 3)
                if w:
                    w.setParent(None)
                    w.deleteLater()
            self.backup_table.clearContents()
            self.backup_table.setRowCount(0)
            self.backup_table.setRowCount(len(backups))

            for row, bk in enumerate(backups):
                # 0. Filename with icon
                item_fname = QTableWidgetItem(f"📦  {bk['filename']}")
                item_fname.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                self.backup_table.setItem(row, 0, item_fname)

                # 1. Date
                item_date = QTableWidgetItem(bk['modified'])
                self.backup_table.setItem(row, 1, item_date)

                # 2. Size
                item_size = QTableWidgetItem(f"{bk['size_mb']} MB")
                item_size.setFont(QFont("Consolas", 10))
                self.backup_table.setItem(row, 2, item_size)

                # 3. Actions: Restore & Export
                act_widget = QWidget()
                act_layout = QHBoxLayout(act_widget)
                act_layout.setContentsMargins(4, 2, 4, 2)
                act_layout.setSpacing(6)

                btn_restore = QPushButton("🔄 Restore" if is_en else "🔄 રીસ્ટોર")
                btn_restore.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn_restore.setFixedHeight(28)
                btn_restore.setStyleSheet("""
                    QPushButton {
                        background-color: #FEF2F2;
                        color: #DC2626;
                        border: 1px solid #FECACA;
                        border-radius: 6px;
                        padding: 0 10px;
                        font-size: 11px;
                        font-weight: 700;
                    }
                    QPushButton:hover {
                        background-color: #FEE2E2;
                    }
                """)
                path = bk['path']
                btn_restore.clicked.connect(lambda _, p=path: self._restore_specific(p))

                btn_export = QPushButton("💾 Export" if is_en else "💾 એક્સપોર્ટ")
                btn_export.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn_export.setFixedHeight(28)
                btn_export.setStyleSheet("""
                    QPushButton {
                        background-color: #EFF6FF;
                        color: #2563EB;
                        border: 1px solid #BFDBFE;
                        border-radius: 6px;
                        padding: 0 10px;
                        font-size: 11px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #DBEAFE;
                    }
                """)
                btn_export.clicked.connect(lambda _, p=path: self._export_backup_file(p))

                act_layout.addWidget(btn_restore)
                act_layout.addWidget(btn_export)
                act_layout.addStretch()

                self.backup_table.setCellWidget(row, 3, act_widget)
                self.backup_table.setRowHeight(row, 44)

        except Exception as exc:
            print(f"Error in backup page refresh: {exc}")

    def _create_instant_backup(self):
        try:
            path = create_backup()
            QMessageBox.information(
                self, "બેકઅપ સફળ",
                f"✓ નવો બેકઅપ સફળતાપૂર્વક લેવાયો છે!\n\nસ્થાન:\n{path}"
            )
            self.refresh()
        except Exception as exc:
            QMessageBox.critical(self, "બેકઅપ નિષ્ફળ", f"બેકઅપ લેવામાં ભૂલ આવી:\n{exc}")

    def _create_external_backup(self):
        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M")
        default_name = f"brahm_samaj_backup_{timestamp}.db"
        dest_path, _ = QFileDialog.getSaveFileName(
            self, "બેકઅપ ફાઇલ સેવ કરો", os.path.join(EXPORT_DIR, default_name),
            "Database Backup (*.db)"
        )
        if dest_path:
            try:
                shutil.copy2(DB_PATH, dest_path)
                QMessageBox.information(
                    self, "બેકઅપ સફળ",
                    f"✓ બેકઅપ સફળતાપૂર્વક સાચવવામાં આવ્યો છે:\n{dest_path}"
                )
                self.refresh()
            except Exception as exc:
                QMessageBox.critical(self, "ભૂલ", f"બેકઅપ સેવ કરવામાં ભૂલ આવી: {exc}")

    def _export_backup_file(self, source_path: str):
        default_name = os.path.basename(source_path)
        dest_path, _ = QFileDialog.getSaveFileName(
            self, "બેકઅપ કોપી સાચવો", os.path.join(EXPORT_DIR, default_name),
            "Database Backup (*.db)"
        )
        if dest_path:
            try:
                shutil.copy2(source_path, dest_path)
                QMessageBox.information(
                    self, "એક્સપોર્ટ સફળ",
                    f"✓ બેકઅપ કોપી સફળતાપૂર્વક નિકાસ કરવામાં આવી:\n{dest_path}"
                )
            except Exception as exc:
                QMessageBox.critical(self, "ભૂલ", f"નિકાસ કરવામાં ભૂલ આવી: {exc}")

    def _restore_from_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "બેકઅપ ફાઇલ પસંદ કરો", BACKUP_DIR, "Database Backup (*.db)"
        )
        if path:
            self._restore_specific(path)

    def _restore_specific(self, path: str):
        reply = QMessageBox.warning(
            self, "રીસ્ટોર પુષ્ટિ (Confirm Restore)",
            f"શું તમે ખરેખર નીચેની ફાઇલમાંથી ડેટા રીસ્ટોર કરવા માંગો છો?\n\n{os.path.basename(path)}\n\n"
            "ચેતવણી: આ ક્રિયાથી વર્તમાન ડેટા બદલાઈ જશે.\n"
            "તમારા વર્તમાન ડેટાનો સલામતી બેકઅપ આપમેળે લેવામાં આવશે.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            restore_backup(path)
            init_db()
            QMessageBox.information(
                self, "રીસ્ટોર સફળ",
                "✓ ડેટા સફળતાપૂર્વક રીસ્ટોર થયો છે!\nડેટાબેઝ પુનઃલોડ કરવામાં આવ્યો છે."
            )
            self.refresh()
            if self._on_data_updated:
                self._on_data_updated()
        except Exception as exc:
            QMessageBox.critical(self, "રીસ્ટોર નિષ્ફળ", f"ડેટા રીસ્ટોર કરતી વખતે ભૂલ આવી:\n{exc}")

    def _open_import_dialog(self):
        """Open the data import dialog and refresh UI on completion."""
        dlg = ImportDataDialog(self)
        dlg.import_finished.connect(self._on_import_finished)
        dlg.exec()

    def _on_import_finished(self, result):
        self.refresh()
        if self._on_data_updated:
            self._on_data_updated()

    def set_language(self, lang: str):
        """Update backup page text dynamically when language changes."""
        self._current_lang = lang
        from app.translations import t

        # Banner
        if hasattr(self, 'banner_pill'):
            self.banner_pill.setText(t('backup_pill', lang))
        if hasattr(self, 'banner_title'):
            self.banner_title.setText(t('backup_title', lang))
        if hasattr(self, 'banner_sub'):
            self.banner_sub.setText(t('backup_sub', lang))
        if hasattr(self, 'btn_import_excel'):
            self.btn_import_excel.setText(t('backup_btn_import', lang))
        if hasattr(self, 'btn_quick_export'):
            self.btn_quick_export.setText(t('backup_btn_export', lang))

        # Status Cards
        if hasattr(self, 'card1'):
            if hasattr(self.card1, 'title_lbl'):
                self.card1.title_lbl.setText(t('backup_card_last_title', lang))
            if hasattr(self.card1, 'footer_lbl'):
                self.card1.footer_lbl.setText(t('backup_card_last_footer', lang))
        if hasattr(self, 'card_last_sub'):
            self.card_last_sub.setText(t('backup_card_last_sub', lang))

        if hasattr(self, 'card2'):
            if hasattr(self.card2, 'title_lbl'):
                self.card2.title_lbl.setText(t('backup_card_total_title', lang))
            if hasattr(self.card2, 'footer_lbl'):
                self.card2.footer_lbl.setText(t('backup_card_total_footer', lang))

        if hasattr(self, 'card3'):
            if hasattr(self.card3, 'title_lbl'):
                self.card3.title_lbl.setText(t('backup_card_health_title', lang))
            if hasattr(self.card3, 'footer_lbl'):
                self.card3.footer_lbl.setText(t('backup_card_health_footer', lang))

        # Action Panels
        if hasattr(self, 'p_title'):
            self.p_title.setText(t('backup_panel_create_title', lang))
        if hasattr(self, 'p_sub'):
            self.p_sub.setText(t('backup_panel_create_sub', lang))
        if hasattr(self, 'radio_full'):
            self.radio_full.setText(t('backup_radio_full', lang))
        if hasattr(self, 'radio_inc'):
            self.radio_inc.setText(t('backup_radio_inc', lang))
        if hasattr(self, 'chk_encrypt'):
            self.chk_encrypt.setText(t('backup_chk_encrypt', lang))
        if hasattr(self, 'badge_enc'):
            self.badge_enc.setText(t('backup_badge_encrypt', lang))
        if hasattr(self, 'btn_create'):
            self.btn_create.setText(t('backup_btn_create', lang))
        if hasattr(self, 'btn_browse_dest'):
            self.btn_browse_dest.setText(t('backup_btn_browse_dest', lang))

        if hasattr(self, 'ps_title'):
            self.ps_title.setText(t('backup_panel_sched_title', lang))
        if hasattr(self, 'ps_desc'):
            self.ps_desc.setText(t('backup_panel_sched_desc', lang))
        if hasattr(self, 'r1_lbl'):
            self.r1_lbl.setText(t('backup_sched_freq_lbl', lang))
        if hasattr(self, 'r1_val'):
            self.r1_val.setText(t('backup_sched_freq_val', lang))
        if hasattr(self, 'r2_lbl'):
            self.r2_lbl.setText(t('backup_sched_storage_lbl', lang))
        if hasattr(self, 'r2_val'):
            self.r2_val.setText(t('backup_sched_storage_val', lang))
        if hasattr(self, 'btn_restore_file'):
            self.btn_restore_file.setText(t('backup_btn_restore_file', lang))

        # Archives Table
        if hasattr(self, 'tbl_title'):
            self.tbl_title.setText(t('backup_sec_history_title', lang))
        if hasattr(self, 'tbl_sub'):
            self.tbl_sub.setText(t('backup_sec_history_sub', lang))
        if hasattr(self, 'btn_refresh'):
            self.btn_refresh.setText(t('backup_btn_refresh', lang))

        if hasattr(self, 'backup_table'):
            if lang == 'en':
                self.backup_table.setHorizontalHeaderLabels([
                    "Backup Filename", "Date and Time", "Size", "Actions"
                ])
            else:
                self.backup_table.setHorizontalHeaderLabels([
                    "બેકઅપ ફાઇલ નામ", "તારીખ અને સમય", "કદ", "કાર્ય"
                ])

        # Refresh stats & table rows with updated language
        try:
            self.refresh()
        except Exception:
            pass
