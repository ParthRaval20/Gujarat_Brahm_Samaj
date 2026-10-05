"""
Modern System Settings Page — Matching Stitch Design.
Allows users to configure:
1. Organization details (Name in Gujarati/English, Subtitle, Prefix, Admin Name, Address, Contact)
2. Application preferences (Language, Date Format, Rows Per Page, Export Directory, Auto-Backup)
3. Database diagnostics and maintenance (Optimize / VACUUM, Explore Data Folder)
"""

from __future__ import annotations

import os
import subprocess
import platform

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QCheckBox, QFrame, QScrollArea,
    QFileDialog, QMessageBox, QGridLayout,
)

from app.config import (
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_BG, COLOR_CARD_BG,
    COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    COLOR_ACCENT_BLUE, COLOR_ACCENT_EMERALD, COLOR_ACCENT_AMBER,
    DATA_DIR, EXPORT_DIR, BACKUP_DIR, APP_VERSION,
)
from services.settings_service import SettingsService


class SystemSettingsPage(QWidget):
    def __init__(self, nav_callback, on_settings_updated=None, parent=None):
        super().__init__(parent)
        self._nav = nav_callback
        self._on_settings_updated = on_settings_updated
        self._settings_svc = SettingsService()
        self._current_lang = 'gu'
        self._setup_ui()
        self.load_settings()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background-color: {COLOR_BG}; border: none; }}")

        container = QWidget()
        container.setStyleSheet(f"background-color: {COLOR_BG};")
        self.layout = QVBoxLayout(container)
        self.layout.setContentsMargins(28, 24, 28, 28)
        self.layout.setSpacing(20)

        # ── 1. Page Header Banner ───────────────────────────────────
        self.layout.addWidget(self._create_header_banner())

        # ── 2. Top Save / Action Bar ─────────────────────────────────
        self.layout.addWidget(self._create_top_action_bar())

        # ── 3. Organization Profile Card ─────────────────────────────
        self.layout.addWidget(self._create_org_settings_card())

        # ── 4. App Preferences Card ──────────────────────────────────
        self.layout.addWidget(self._create_app_preferences_card())

        # ── 5. Database Diagnostics & Maintenance Card ───────────────
        self.layout.addWidget(self._create_database_maintenance_card())

        # ── 6. Bottom Save Bar ───────────────────────────────────────
        self.layout.addWidget(self._create_bottom_action_bar())

        scroll.setWidget(container)
        outer.addWidget(scroll)

    # =========================================================================
    # 1. HEADER BANNER
    # =========================================================================
    def _create_header_banner(self) -> QWidget:
        banner = QFrame()
        banner.setObjectName("settingsBanner")
        banner.setStyleSheet("""
            QFrame#settingsBanner {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0D1C3A, stop:0.5 #122853, stop:1 #1E3A78);
                border: 1px solid #1E293B;
                border-radius: 16px;
            }
        """)

        layout = QHBoxLayout(banner)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(20)

        left_box = QVBoxLayout()
        left_box.setSpacing(6)

        self.banner_pill = QLabel("⚙️ સિસ્ટમ અને સોફ્ટવેર કન્ફિગરેશન")
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

        self.banner_title = QLabel("સિસ્ટમ સેટિંગ્સ સંચાલન")
        self.banner_title.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: 800; background: transparent;")

        self.banner_sub = QLabel(
            "સંસ્થાનું નામ, સભ્ય પ્રીફિક્સ કોડ, ભાષા, ડિફૉલ્ટ એક્સપોર્ટ પાથ અને ડેટાબેઝ કામગીરીનું અહીંથી સંચાલન કરો."
        )
        self.banner_sub.setStyleSheet("color: #BFDBFE; font-size: 12px; font-weight: 400; background: transparent;")

        left_box.addWidget(self.banner_pill)
        left_box.addWidget(self.banner_title)
        left_box.addWidget(self.banner_sub)
        layout.addLayout(left_box, stretch=1)

        icon_card = QLabel("⚙️")
        icon_card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_card.setFixedSize(60, 60)
        icon_card.setStyleSheet("""
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.20);
            border-radius: 14px;
            font-size: 28px;
        """)
        layout.addWidget(icon_card)

        return banner

    # =========================================================================
    # ACTION BARS
    # =========================================================================
    def _create_top_action_bar(self) -> QWidget:
        bar = QFrame()
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_CARD_BG};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
            }}
        """)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(12)

        self.lbl_top_info = QLabel("ℹ️ નીચે આપેલા ફીલ્ડ્સમાં ફેરફાર કરી 'સેવ સેટિંગ્સ' પર ક્લિક કરો.")
        self.lbl_top_info.setStyleSheet("color: #475569; font-size: 12px; font-weight: 600;")
        layout.addWidget(self.lbl_top_info)
        layout.addStretch()

        self.btn_save_top = QPushButton("💾  સેવ સેટિંગ્સ")
        self.btn_save_top.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_save_top.setFixedHeight(36)
        self.btn_save_top.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 0 20px;
                font-size: 12px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_DARK};
            }}
        """)
        self.btn_save_top.clicked.connect(self.save_settings)
        layout.addWidget(self.btn_save_top)

        return bar

    def _create_bottom_action_bar(self) -> QWidget:
        bar = QFrame()
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_CARD_BG};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
            }}
        """)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(12)

        self.btn_reset = QPushButton("🔄  ડિફૉલ્ટ રીસેટ કરો")
        self.btn_reset.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_reset.setFixedHeight(36)
        self.btn_reset.setStyleSheet(f"""
            QPushButton {{
                background-color: #F8FAFC;
                color: #475569;
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #F1F5F9;
                color: #0F172A;
            }}
        """)
        self.btn_reset.clicked.connect(self.reset_defaults)
        layout.addWidget(self.btn_reset)

        layout.addStretch()

        self.btn_save_bottom = QPushButton("💾  સેવ સેટિંગ્સ")
        self.btn_save_bottom.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_save_bottom.setFixedHeight(36)
        self.btn_save_bottom.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 0 24px;
                font-size: 12px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_DARK};
            }}
        """)
        self.btn_save_bottom.clicked.connect(self.save_settings)
        layout.addWidget(self.btn_save_bottom)

        return bar

    # =========================================================================
    # 2. ORGANIZATION SETTINGS CARD
    # =========================================================================
    def _create_org_settings_card(self) -> QWidget:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_CARD_BG};
                border: 1px solid {COLOR_BORDER};
                border-radius: 14px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(16)

        # Card Title
        head = QHBoxLayout()
        icon = QLabel("🏛️")
        icon.setStyleSheet("font-size: 18px;")
        self.lbl_card1_title = QLabel("સમાજ અને સંસ્થા વિગતો")
        self.lbl_card1_title.setStyleSheet("color: #0F172A; font-size: 15px; font-weight: 800;")
        head.addWidget(icon)
        head.addWidget(self.lbl_card1_title)
        head.addStretch()
        layout.addLayout(head)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(14)

        # 1. Org Name Gujarati
        self.lbl_org_gu = QLabel("સંસ્થાનું નામ (ગુજરાતી) *")
        self.lbl_org_gu.setStyleSheet("color: #334155; font-size: 12px; font-weight: 700;")
        self.edit_org_gu = QLineEdit()
        self._style_input(self.edit_org_gu)
        grid.addWidget(self.lbl_org_gu, 0, 0)
        grid.addWidget(self.edit_org_gu, 1, 0)

        # 2. Org Name English
        self.lbl_org_en = QLabel("સંસ્થાનું નામ (અંગ્રેજી) *")
        self.lbl_org_en.setStyleSheet("color: #334155; font-size: 12px; font-weight: 700;")
        self.edit_org_en = QLineEdit()
        self._style_input(self.edit_org_en)
        grid.addWidget(self.lbl_org_en, 0, 1)
        grid.addWidget(self.edit_org_en, 1, 1)

        # 3. ERP Subtitle
        self.lbl_sub = QLabel("પોર્ટલ સબટાઇટલ")
        self.lbl_sub.setStyleSheet("color: #334155; font-size: 12px; font-weight: 700;")
        self.edit_sub = QLineEdit()
        self._style_input(self.edit_sub)
        grid.addWidget(self.lbl_sub, 2, 0)
        grid.addWidget(self.edit_sub, 3, 0)

        # 4. Member Code Prefix
        self.lbl_prefix = QLabel("સભ્ય કોડ પ્રીફિક્સ (દા.ત. GBS)")
        self.lbl_prefix.setStyleSheet("color: #334155; font-size: 12px; font-weight: 700;")
        self.edit_prefix = QLineEdit()
        self._style_input(self.edit_prefix)
        grid.addWidget(self.lbl_prefix, 2, 1)
        grid.addWidget(self.edit_prefix, 3, 1)

        # 5. Admin / President Name
        self.lbl_admin = QLabel("સંચાલક / પ્રમુખ નામ")
        self.lbl_admin.setStyleSheet("color: #334155; font-size: 12px; font-weight: 700;")
        self.edit_admin = QLineEdit()
        self._style_input(self.edit_admin)
        grid.addWidget(self.lbl_admin, 4, 0)
        grid.addWidget(self.edit_admin, 5, 0)

        # 6. Helpline Phone
        self.lbl_phone = QLabel("સંપર્ક હેલ્પલાઇન નંબર")
        self.lbl_phone.setStyleSheet("color: #334155; font-size: 12px; font-weight: 700;")
        self.edit_phone = QLineEdit()
        self._style_input(self.edit_phone)
        grid.addWidget(self.lbl_phone, 4, 1)
        grid.addWidget(self.edit_phone, 5, 1)

        # 7. Office Address
        self.lbl_addr = QLabel("મુખ્ય કાર્યાલય સરનામું")
        self.lbl_addr.setStyleSheet("color: #334155; font-size: 12px; font-weight: 700;")
        self.edit_addr = QLineEdit()
        self._style_input(self.edit_addr)
        grid.addWidget(self.lbl_addr, 6, 0)
        grid.addWidget(self.edit_addr, 7, 0)

        # 8. Email
        self.lbl_email = QLabel("સત્તાવાર ઇમેઇલ")
        self.lbl_email.setStyleSheet("color: #334155; font-size: 12px; font-weight: 700;")
        self.edit_email = QLineEdit()
        self._style_input(self.edit_email)
        grid.addWidget(self.lbl_email, 6, 1)
        grid.addWidget(self.edit_email, 7, 1)

        layout.addLayout(grid)
        return card

    # =========================================================================
    # 3. APP PREFERENCES CARD
    # =========================================================================
    def _create_app_preferences_card(self) -> QWidget:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_CARD_BG};
                border: 1px solid {COLOR_BORDER};
                border-radius: 14px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(16)

        head = QHBoxLayout()
        icon = QLabel("🛠️")
        icon.setStyleSheet("font-size: 18px;")
        self.lbl_card2_title = QLabel("એપ્લિકેશન સેટિંગ્સ અને પસંદગીઓ")
        self.lbl_card2_title.setStyleSheet("color: #0F172A; font-size: 15px; font-weight: 800;")
        head.addWidget(icon)
        head.addWidget(self.lbl_card2_title)
        head.addStretch()
        layout.addLayout(head)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(14)

        # 1. Default Language
        self.lbl_lang = QLabel("ડિફૉલ્ટ ભાષા")
        self.lbl_lang.setStyleSheet("color: #334155; font-size: 12px; font-weight: 700;")
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["ગુજરાતી", "English"])
        self._style_input(self.combo_lang)
        grid.addWidget(self.lbl_lang, 0, 0)
        grid.addWidget(self.combo_lang, 1, 0)

        # 2. Date Format
        self.lbl_df = QLabel("તારીખ ફોર્મેટ")
        self.lbl_df.setStyleSheet("color: #334155; font-size: 12px; font-weight: 700;")
        self.combo_df = QComboBox()
        self.combo_df.addItems(["DD/MM/YYYY", "YYYY-MM-DD", "DD-MM-YYYY"])
        self._style_input(self.combo_df)
        grid.addWidget(self.lbl_df, 0, 1)
        grid.addWidget(self.combo_df, 1, 1)

        # 3. Rows per page
        self.lbl_rpp = QLabel("પ્રતિ પાનું સભ્યો સંખ્યા")
        self.lbl_rpp.setStyleSheet("color: #334155; font-size: 12px; font-weight: 700;")
        self.combo_rpp = QComboBox()
        self.combo_rpp.addItems(["25", "50", "100", "200"])
        self._style_input(self.combo_rpp)
        grid.addWidget(self.lbl_rpp, 2, 0)
        grid.addWidget(self.combo_rpp, 3, 0)

        # 4. Auto Backup on exit
        self.lbl_ab = QLabel("સ્વચાલિત બેકઅપ")
        self.lbl_ab.setStyleSheet("color: #334155; font-size: 12px; font-weight: 700;")
        self.chk_autobackup = QCheckBox("એપ્લિકેશન બંધ કરતી વખતે સ્વચાલિત બેકઅપ લો")
        self.chk_autobackup.setStyleSheet("""
            QCheckBox {
                color: #0F172A;
                font-size: 12px;
                font-weight: 600;
                spacing: 8px;
            }
        """)
        grid.addWidget(self.lbl_ab, 2, 1)
        grid.addWidget(self.chk_autobackup, 3, 1)

        # 5. Default Export Directory (Full row)
        self.lbl_exp = QLabel("ડિફૉલ્ટ નિકાસ ફોલ્ડર")
        self.lbl_exp.setStyleSheet("color: #334155; font-size: 12px; font-weight: 700;")

        exp_row = QHBoxLayout()
        exp_row.setSpacing(8)
        self.edit_export_path = QLineEdit()
        self._style_input(self.edit_export_path)

        self.btn_browse_exp = QPushButton("📁 બ્રાઉઝ")
        self.btn_browse_exp.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_browse_exp.setFixedHeight(38)
        self.btn_browse_exp.setStyleSheet(f"""
            QPushButton {{
                background-color: #F1F5F9;
                color: #0F172A;
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #E2E8F0;
            }}
        """)
        self.btn_browse_exp.clicked.connect(self._browse_export_dir)

        exp_row.addWidget(self.edit_export_path, stretch=1)
        exp_row.addWidget(self.btn_browse_exp)

        grid.addWidget(self.lbl_exp, 4, 0, 1, 2)
        grid.addLayout(exp_row, 5, 0, 1, 2)

        layout.addLayout(grid)
        return card

    # =========================================================================
    # 4. DATABASE & SYSTEM DIAGNOSTICS CARD
    # =========================================================================
    def _create_database_maintenance_card(self) -> QWidget:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_CARD_BG};
                border: 1px solid {COLOR_BORDER};
                border-radius: 14px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(16)

        head = QHBoxLayout()
        icon = QLabel("💾")
        icon.setStyleSheet("font-size: 18px;")
        self.lbl_card3_title = QLabel("ડેટાબેઝ સંચાલન અને સિસ્ટમ સ્થિતિ")
        self.lbl_card3_title.setStyleSheet("color: #0F172A; font-size: 15px; font-weight: 800;")
        head.addWidget(icon)
        head.addWidget(self.lbl_card3_title)
        head.addStretch()
        layout.addLayout(head)

        # Metrics Row
        info_row = QHBoxLayout()
        info_row.setSpacing(12)

        self.pill_members = self._create_info_pill("👥 કુલ નોંધણી", "...", "#2563EB")
        self.pill_dbsize = self._create_info_pill("📊 ડેટાબેઝ સાઈઝ", "...", "#10B981")
        self.pill_version = self._create_info_pill("🚀 સિસ્ટમ વર્ઝન", f"v{APP_VERSION}", "#8B5CF6")

        info_row.addWidget(self.pill_members)
        info_row.addWidget(self.pill_dbsize)
        info_row.addWidget(self.pill_version)
        layout.addLayout(info_row)

        # Maintenance Buttons Row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_optimize = QPushButton("⚡ ડેટાબેઝ ઓપ્ટિમાઇઝ કરો")
        self.btn_optimize.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_optimize.setFixedHeight(38)
        self.btn_optimize.setStyleSheet("""
            QPushButton {
                background-color: #ECFDF5;
                color: #065F46;
                border: 1px solid #A7F3D0;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #D1FAE5;
            }
        """)
        self.btn_optimize.clicked.connect(self._optimize_db)

        self.btn_open_data = QPushButton("📁 ડેટા ફોલ્ડર ખોલો")
        self.btn_open_data.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_open_data.setFixedHeight(38)
        self.btn_open_data.setStyleSheet(f"""
            QPushButton {{
                background-color: #F8FAFC;
                color: #334155;
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #F1F5F9;
            }}
        """)
        self.btn_open_data.clicked.connect(self._open_data_folder)

        btn_row.addWidget(self.btn_optimize)
        btn_row.addWidget(self.btn_open_data)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        return card

    def _create_info_pill(self, label: str, val: str, color_hex: str) -> QFrame:
        pill = QFrame()
        pill.setStyleSheet(f"""
            QFrame {{
                background-color: #F8FAFC;
                border: 1px solid {COLOR_BORDER};
                border-radius: 10px;
                padding: 10px 14px;
            }}
        """)
        v = QVBoxLayout(pill)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)

        lbl = QLabel(label)
        lbl.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 600;")
        val_lbl = QLabel(val)
        val_lbl.setObjectName("val")
        val_lbl.setStyleSheet(f"color: {color_hex}; font-size: 15px; font-weight: 800;")

        v.addWidget(lbl)
        v.addWidget(val_lbl)
        pill.lbl_title = lbl
        return pill

    # =========================================================================
    # HELPERS & LOGIC
    # =========================================================================
    def _style_input(self, widget: QWidget):
        widget.setFixedHeight(38)
        widget.setStyleSheet(f"""
            QLineEdit, QComboBox {{
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 0 12px;
                font-size: 12px;
                font-weight: 500;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1.5px solid {COLOR_PRIMARY};
                background-color: #FAFAFA;
            }}
        """)

    def load_settings(self):
        """Populate UI from database."""
        all_s = self._settings_svc.get_all()

        self.edit_org_gu.setText(all_s.get('org_name_gu', 'ગુજરાત બ્રહ્મ સમાજ'))
        self.edit_org_en.setText(all_s.get('org_name_en', 'Gujarat Brahm Samaj'))
        self.edit_sub.setText(all_s.get('erp_subtitle', 'BRAHM SAMAJ ERP'))
        self.edit_prefix.setText(all_s.get('member_code_prefix', 'GBS'))
        self.edit_admin.setText(all_s.get('admin_name', 'સંચાલક (Admin)'))
        self.edit_phone.setText(all_s.get('helpline_phone', '+91 98765 43210'))
        self.edit_addr.setText(all_s.get('office_address', 'અમદાવાદ, ગુજરાત'))
        self.edit_email.setText(all_s.get('contact_email', 'contact@brahmsamaj.org'))

        lang = all_s.get('default_language', 'gu')
        self.combo_lang.setCurrentIndex(0 if lang == 'gu' else 1)

        df = all_s.get('date_format', 'DD/MM/YYYY')
        idx_df = self.combo_df.findText(df)
        if idx_df >= 0:
            self.combo_df.setCurrentIndex(idx_df)

        rpp = all_s.get('rows_per_page', '50')
        idx_rpp = self.combo_rpp.findText(rpp)
        if idx_rpp >= 0:
            self.combo_rpp.setCurrentIndex(idx_rpp)

        ab = all_s.get('auto_backup_on_exit', 'True')
        self.chk_autobackup.setChecked(ab.lower() in ('true', '1', 'yes'))

        exp_dir = all_s.get('default_export_dir', EXPORT_DIR)
        self.edit_export_path.setText(exp_dir)

        # Update diagnostics
        self._refresh_diagnostics()

    def _refresh_diagnostics(self):
        sys_info = self._settings_svc.get_system_info()
        tot = sys_info.get('member_count', 0)
        fam = sys_info.get('family_count', 0)
        lang = getattr(self, '_current_lang', 'gu')
        if lang == 'en':
            self.pill_members.findChild(QLabel, "val").setText(f"{tot:,} Members ({fam} Families)")
        else:
            self.pill_members.findChild(QLabel, "val").setText(f"{tot:,} સભ્યો ({fam} પરિવાર)")

        size_kb = sys_info.get('db_size_kb', 0)
        if size_kb > 1024:
            self.pill_dbsize.findChild(QLabel, "val").setText(f"{round(size_kb/1024, 2)} MB")
        else:
            self.pill_dbsize.findChild(QLabel, "val").setText(f"{size_kb} KB")

    def save_settings(self):
        """Save form data to settings table."""
        payload = {
            'org_name_gu': self.edit_org_gu.text().strip(),
            'org_name_en': self.edit_org_en.text().strip(),
            'erp_subtitle': self.edit_sub.text().strip(),
            'member_code_prefix': self.edit_prefix.text().strip().upper(),
            'admin_name': self.edit_admin.text().strip(),
            'helpline_phone': self.edit_phone.text().strip(),
            'office_address': self.edit_addr.text().strip(),
            'contact_email': self.edit_email.text().strip(),
            'default_language': 'gu' if self.combo_lang.currentIndex() == 0 else 'en',
            'date_format': self.combo_df.currentText(),
            'rows_per_page': self.combo_rpp.currentText(),
            'auto_backup_on_exit': str(self.chk_autobackup.isChecked()),
            'default_export_dir': self.edit_export_path.text().strip(),
        }

        try:
            self._settings_svc.set_many(payload)
            if self._on_settings_updated:
                self._on_settings_updated()
            lang = getattr(self, '_current_lang', 'gu')
            if lang == 'en':
                QMessageBox.information(
                    self, "Settings Saved",
                    "✓ All system settings have been saved successfully.\n"
                    "Changes are applied immediately."
                )
            else:
                QMessageBox.information(
                    self, "સેવ સેટિંગ્સ",
                    "✓ તમામ સિસ્ટમ સેટિંગ્સ સફળતાપૂર્વક સાચવવામાં આવ્યા છે.\n"
                    "નવા સેટિંગ્સ એપ્લિકેશનમાં તરત જ લાગુ થયા છે."
                )
            self._refresh_diagnostics()
        except Exception as exc:
            lang = getattr(self, '_current_lang', 'gu')
            title = "Error" if lang == 'en' else "ભૂલ"
            msg = f"Failed to save settings:\n{exc}" if lang == 'en' else f"સેટિંગ્સ સાચવવામાં સમસ્યા આવી:\n{exc}"
            QMessageBox.critical(self, title, msg)

    def reset_defaults(self):
        """Reset inputs to defaults."""
        lang = getattr(self, '_current_lang', 'gu')
        title = "Reset to Defaults" if lang == 'en' else "ડિફૉલ્ટ રીસેટ"
        prompt = "Are you sure you want to reset all settings to system defaults?" if lang == 'en' else "શું તમે ખરેખર તમામ સેટિંગ્સ મૂળભૂત (Default) સેટિંગ્સમાં ફેરવવા માંગો છો?"
        res = QMessageBox.question(
            self, title,
            prompt,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if res == QMessageBox.StandardButton.Yes:
            from services.settings_service import DEFAULT_SETTINGS
            self._settings_svc.set_many(DEFAULT_SETTINGS)
            self.load_settings()
            if self._on_settings_updated:
                self._on_settings_updated()
            msg = "All settings have been reset to defaults." if lang == 'en' else "તમામ સેટિંગ્સ ડિફૉલ્ટમાં રીસેટ થયા છે."
            succ = "Success" if lang == 'en' else "સફળ"
            QMessageBox.information(self, succ, msg)

    def _browse_export_dir(self):
        curr = self.edit_export_path.text() or EXPORT_DIR
        lang = getattr(self, '_current_lang', 'gu')
        title = "Select Export Folder" if lang == 'en' else "એક્સપોર્ટ ફોલ્ડર પસંદ કરો"
        chosen = QFileDialog.getExistingDirectory(self, title, curr)
        if chosen:
            self.edit_export_path.setText(chosen)

    def _optimize_db(self):
        ok, msg = self._settings_svc.optimize_database()
        lang = getattr(self, '_current_lang', 'gu')
        if ok:
            title = "Database Optimization" if lang == 'en' else "ડેટાબેઝ ઓપ્ટિમાઇઝેશન"
            QMessageBox.information(self, title, f"✓ {msg}")
            self._refresh_diagnostics()
        else:
            title = "Warning" if lang == 'en' else "ચેતવણી"
            QMessageBox.warning(self, title, msg)

    def _open_data_folder(self):
        try:
            if platform.system() == 'Windows':
                os.startfile(DATA_DIR)
            elif platform.system() == 'Darwin':
                subprocess.Popen(['open', DATA_DIR])
            else:
                subprocess.Popen(['xdg-open', DATA_DIR])
        except Exception as exc:
            lang = getattr(self, '_current_lang', 'gu')
            title = "Error" if lang == 'en' else "ભૂલ"
            msg = f"Could not open directory: {exc}" if lang == 'en' else f"ફોલ્ડર ખોલી શકાયું નથી: {exc}"
            QMessageBox.warning(self, title, msg)

    def set_language(self, lang: str):
        """Update system settings page dynamically when language changes."""
        from app.translations import t
        self._current_lang = lang

        if hasattr(self, 'banner_title'):
            self.banner_title.setText(t('settings_title', lang))
        if hasattr(self, 'banner_sub'):
            self.banner_sub.setText(t('settings_sub', lang))
        if hasattr(self, 'banner_pill'):
            self.banner_pill.setText(t('settings_pill', lang))
        if hasattr(self, 'lbl_top_info'):
            self.lbl_top_info.setText(t('settings_top_info', lang))
        if hasattr(self, 'btn_save_top'):
            self.btn_save_top.setText(t('settings_btn_save', lang))
        if hasattr(self, 'btn_reset'):
            self.btn_reset.setText(t('settings_btn_reset', lang))
        if hasattr(self, 'btn_save_bottom'):
            self.btn_save_bottom.setText(t('settings_btn_save', lang))

        # Card 1: Org Details
        if hasattr(self, 'lbl_card1_title'):
            self.lbl_card1_title.setText(t('settings_card_org_title', lang))
        if hasattr(self, 'lbl_org_gu'):
            self.lbl_org_gu.setText(t('settings_lbl_org_gu', lang))
        if hasattr(self, 'lbl_org_en'):
            self.lbl_org_en.setText(t('settings_lbl_org_en', lang))
        if hasattr(self, 'lbl_sub'):
            self.lbl_sub.setText(t('settings_lbl_sub', lang))
        if hasattr(self, 'lbl_prefix'):
            self.lbl_prefix.setText(t('settings_lbl_prefix', lang))
        if hasattr(self, 'lbl_admin'):
            self.lbl_admin.setText(t('settings_lbl_admin', lang))
        if hasattr(self, 'lbl_phone'):
            self.lbl_phone.setText(t('settings_lbl_phone', lang))
        if hasattr(self, 'lbl_addr'):
            self.lbl_addr.setText(t('settings_lbl_addr', lang))
        if hasattr(self, 'lbl_email'):
            self.lbl_email.setText(t('settings_lbl_email', lang))

        # Card 2: App Preferences
        if hasattr(self, 'lbl_card2_title'):
            self.lbl_card2_title.setText(t('settings_card_pref_title', lang))
        if hasattr(self, 'lbl_lang'):
            self.lbl_lang.setText(t('settings_lbl_lang', lang))
        if hasattr(self, 'lbl_df'):
            self.lbl_df.setText(t('settings_lbl_df', lang))
        if hasattr(self, 'lbl_rpp'):
            self.lbl_rpp.setText(t('settings_lbl_rpp', lang))
        if hasattr(self, 'lbl_ab'):
            self.lbl_ab.setText(t('settings_lbl_ab', lang))
        if hasattr(self, 'chk_autobackup'):
            self.chk_autobackup.setText(t('settings_chk_ab', lang))
        if hasattr(self, 'lbl_exp'):
            self.lbl_exp.setText(t('settings_lbl_exp', lang))
        if hasattr(self, 'btn_browse_exp'):
            self.btn_browse_exp.setText(t('settings_btn_browse', lang))
        if hasattr(self, 'combo_lang'):
            self.combo_lang.setItemText(0, "ગુજરાતી" if lang == 'gu' else "Gujarati")
            self.combo_lang.setItemText(1, "English")
            self.combo_lang.setCurrentIndex(0 if lang == 'gu' else 1)

        # Card 3: Database & Diagnostics
        if hasattr(self, 'lbl_card3_title'):
            self.lbl_card3_title.setText(t('settings_card_diag_title', lang))
        if hasattr(self, 'pill_members') and hasattr(self.pill_members, 'lbl_title'):
            self.pill_members.lbl_title.setText(t('settings_pill_members', lang))
        if hasattr(self, 'pill_dbsize') and hasattr(self.pill_dbsize, 'lbl_title'):
            self.pill_dbsize.lbl_title.setText(t('settings_pill_dbsize', lang))
        if hasattr(self, 'pill_version') and hasattr(self.pill_version, 'lbl_title'):
            self.pill_version.lbl_title.setText(t('settings_pill_version', lang))
        if hasattr(self, 'btn_optimize'):
            self.btn_optimize.setText(t('settings_btn_optimize', lang))
        if hasattr(self, 'btn_open_data'):
            self.btn_open_data.setText(t('settings_btn_open_data', lang))

        self._refresh_diagnostics()
