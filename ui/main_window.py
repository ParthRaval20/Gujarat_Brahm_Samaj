"""
Main application window with Stitch Modern UI Design.
Features:
- Dark Slate Navy Sidebar (#0F172A) with Gold Emblem & Admin Profile Card
- Top Global Navigation Header with Omni-Search (Ctrl+K), Language Toggle, Quick Add & Sync Status
- Stacked Page View with smooth switching & live member badge counts
"""

from __future__ import annotations

import os
import re

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QKeySequence, QShortcut, QCursor, QPixmap, QIcon, QDesktopServices
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame,
    QLineEdit, QMessageBox,
)

from app.config import (
    WINDOW_TITLE, SIDEBAR_WIDTH, MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT,
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_BG, COLOR_CARD_BG,
    COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    COLOR_SIDEBAR_BG, COLOR_SIDEBAR_HEADER, COLOR_SIDEBAR_FOOTER,
    COLOR_SIDEBAR_HOVER, COLOR_SIDEBAR_ACTIVE,
    APP_NAME, APP_VERSION, LOGO_PATH, APP_ICON_PATH,
    GAYATRI_LOGO_PATH, DEVELOPER_NAME, DEVELOPER_NAME_GU,
    DEVELOPER_WEBSITE, DEVELOPER_EMAIL,
)
from ui.dashboard import DashboardPage
from ui.member_form import MemberFormPage
from ui.member_list import MemberListPage
from ui.member_profile import MemberProfilePage
from ui.form_preview import FormPreviewPage
from ui.backup_restore import BackupRestorePage
from ui.system_settings import SystemSettingsPage
from services.member_service import MemberService


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        if os.path.exists(APP_ICON_PATH):
            self.setWindowIcon(QIcon(APP_ICON_PATH))
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self._member_svc = MemberService()
        self._current_lang = 'gu'
        self._nav_text_labels: dict[str, QLabel] = {}
        self._setup_ui()
        self._setup_shortcuts()
        self.on_settings_updated()
        self._nav_to('dashboard')

    def _setup_ui(self):
        central = QWidget()
        central.setStyleSheet(f"background-color: {COLOR_BG};")
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── 1. Left Sidebar ──────────────────────────────────────────
        self.sidebar = self._create_sidebar()
        root.addWidget(self.sidebar)

        # ── 2. Right Content Area (Top Nav + Stacked Pages) ──────────
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Top Navigation Header Bar
        self.top_header = self._create_top_header()
        right_layout.addWidget(self.top_header)

        # Stacked Pages
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {COLOR_BG}; border: none;")
        right_layout.addWidget(self.stack, stretch=1)

        # Global Footer (Shown on every page)
        self.footer = self._create_global_footer()
        right_layout.addWidget(self.footer)

        root.addWidget(right_container, stretch=1)

        # Instantiate pages
        self._dashboard_page      = DashboardPage(self._nav_to)
        self._member_form_page    = MemberFormPage(self._nav_to, on_data_updated=self.on_data_updated)
        self._member_list_page    = MemberListPage(self._nav_to, on_data_updated=self.on_data_updated)
        self._member_profile_page = MemberProfilePage(self._nav_to, on_data_updated=self.on_data_updated)
        self._form_preview_page   = FormPreviewPage(self._nav_to)
        self._backup_page         = BackupRestorePage(self._nav_to, on_data_updated=self.on_data_updated)
        self._settings_page       = SystemSettingsPage(self._nav_to, on_settings_updated=self.on_settings_updated)

        for page in (
            self._dashboard_page,
            self._member_form_page,
            self._member_list_page,
            self._member_profile_page,
            self._form_preview_page,
            self._backup_page,
            self._settings_page,
        ):
            self.stack.addWidget(page)

        self._page_map = {
            'dashboard':    (0, 'dashboard'),
            'add':          (1, 'add'),
            'list':         (2, 'list'),
            'profile':      (3, None),
            'form_preview': (4, None),
            'backup':       (5, 'backup'),
            'search':       (2, 'list'),   # navigates to list page with search active
            'edit':         (1, 'add'),
            'settings':     (6, 'settings'),   # System Settings page
        }

    # =========================================================================
    # SIDEBAR CREATION
    # =========================================================================
    def _create_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("appSidebar")
        sidebar.setFixedWidth(SIDEBAR_WIDTH)
        sidebar.setStyleSheet(f"""
            QFrame#appSidebar {{
                background-color: #FFFFFF;
                border-right: 1px solid {COLOR_BORDER};
            }}
            QFrame#appSidebar QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # ── Branding Header ──────────────────────────────────────────
        brand_frame = QFrame()
        brand_frame.setObjectName("brandHeader")
        brand_frame.setStyleSheet(f"""
            QFrame#brandHeader {{
                background-color: {COLOR_SIDEBAR_HEADER};
                border-bottom: 1px solid #1E293B;
            }}
            QFrame#brandHeader QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        bf_layout = QHBoxLayout(brand_frame)
        bf_layout.setContentsMargins(18, 16, 18, 16)
        bf_layout.setSpacing(12)

        # Official Logo Box
        self.sidebar_logo = QLabel()
        self.sidebar_logo.setFixedSize(46, 46)
        self.sidebar_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if os.path.exists(LOGO_PATH):
            pix = QPixmap(LOGO_PATH)
            if not pix.isNull():
                self.sidebar_logo.setPixmap(
                    pix.scaled(44, 44, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                )
        self.sidebar_logo.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1.5px solid #334155;
                padding: 1px;
            }
        """)

        # Brand Title & ERP Subtitle
        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)

        self.org_name = QLabel("ગુજરાત બ્રહ્મ સમાજ")
        self.org_name.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 800; border: none; background: transparent;")

        erp_row = QHBoxLayout()
        erp_row.setSpacing(6)
        self.erp_sub = QLabel("BRAHM SAMAJ ERP")
        self.erp_sub.setStyleSheet("color: #F59E0B; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; border: none; background: transparent;")

        dot_live = QLabel()
        dot_live.setFixedSize(6, 6)
        dot_live.setStyleSheet("background-color: #10B981; border-radius: 3px; border: none;")

        erp_row.addWidget(self.erp_sub)
        erp_row.addWidget(dot_live)
        erp_row.addStretch()

        title_vbox.addWidget(self.org_name)
        title_vbox.addLayout(erp_row)

        bf_layout.addWidget(self.sidebar_logo)
        bf_layout.addLayout(title_vbox)
        sidebar_layout.addWidget(brand_frame)

        # ── Navigation Items ─────────────────────────────────────────
        nav_container = QWidget()
        nav_container.setObjectName("navContainer")
        nav_container.setStyleSheet("background-color: #FFFFFF;")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(12, 16, 12, 16)
        nav_layout.setSpacing(4)

        # Section 1: Main Menu
        self.lbl_sec_main = QLabel("મુખ્ય મેનુ")
        self.lbl_sec_main.setStyleSheet("color: #475569; font-size: 11px; font-weight: 800; letter-spacing: 0.5px; padding: 6px 10px 2px 10px; border: none; background: transparent;")
        nav_layout.addWidget(self.lbl_sec_main)

        self._nav_buttons: dict[str, QPushButton] = {}

        # 1. Dashboard
        self.btn_nav_dash = self._create_nav_button("🏠", "ડેશબોર્ડ", "dashboard")
        nav_layout.addWidget(self.btn_nav_dash)

        # 2. Add Member
        self.btn_nav_add = self._create_nav_button("➕", "નવો સભ્ય", "add")
        nav_layout.addWidget(self.btn_nav_add)

        # 3. All Members (with live count badge)
        self.btn_nav_list = self._create_nav_button("👥", "બધા સભ્યો", "list", badge="0", is_count=True)
        nav_layout.addWidget(self.btn_nav_list)

        nav_layout.addSpacing(14)

        # Section 2: Tools & Docs
        self.lbl_sec_tools = QLabel("સાધનો & દસ્તાવેજ")
        self.lbl_sec_tools.setStyleSheet("color: #475569; font-size: 11px; font-weight: 800; letter-spacing: 0.5px; padding: 6px 10px 2px 10px; border: none; background: transparent;")
        nav_layout.addWidget(self.lbl_sec_tools)

        # 4. Backup & Restore
        self.btn_nav_backup = self._create_nav_button("💾", "બૅકઅપ અને રીસ્ટોર", "backup")
        nav_layout.addWidget(self.btn_nav_backup)

        # 5. System Settings
        self.btn_nav_settings = self._create_nav_button("⚙️", "સિસ્ટમ સેટિંગ્સ", "settings")
        nav_layout.addWidget(self.btn_nav_settings)

        nav_layout.addStretch()
        sidebar_layout.addWidget(nav_container, stretch=1)

        # ── Sidebar Footer User Profile Card ─────────────────────────
        user_footer = QFrame()
        user_footer.setObjectName("userFooter")
        user_footer.setFixedHeight(72)
        user_footer.setStyleSheet(f"""
            QFrame#userFooter {{
                background-color: {COLOR_SIDEBAR_FOOTER};
                border-top: 1px solid #1E293B;
            }}
            QFrame#userFooter QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        uf_layout = QHBoxLayout(user_footer)
        uf_layout.setContentsMargins(14, 12, 14, 12)
        uf_layout.setSpacing(10)

        # Avatar Badge (Dynamic Initials)
        self.uavatar = QLabel("VR")
        self.uavatar.setFixedSize(38, 38)
        self.uavatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.uavatar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #D97706, stop:1 #F59E0B);
            color: #0F172A;
            font-size: 13px;
            font-weight: 800;
            border-radius: 8px;
            border: none;
        """)

        user_info = QVBoxLayout()
        user_info.setSpacing(3)
        user_info.setContentsMargins(0, 0, 0, 0)

        self.uname = QLabel("પાર્થ રાવલ (Admin)")
        self.uname.setStyleSheet("color: #FFFFFF; font-size: 12px; font-weight: 700; border: none; background: transparent;")

        status_row = QHBoxLayout()
        status_row.setSpacing(6)
        status_row.setContentsMargins(0, 0, 0, 0)
        pulse_dot = QLabel()
        pulse_dot.setFixedSize(7, 7)
        pulse_dot.setStyleSheet("background-color: #10B981; border-radius: 3px; border: none;")

        self.ustatus = QLabel(f"Online • v{APP_VERSION}")
        self.ustatus.setStyleSheet("color: #10B981; font-size: 11px; font-weight: 600; border: none; background: transparent;")

        status_row.addWidget(pulse_dot)
        status_row.addWidget(self.ustatus)
        status_row.addStretch()

        user_info.addWidget(self.uname)
        user_info.addLayout(status_row)

        uf_layout.addWidget(self.uavatar)
        uf_layout.addLayout(user_info)
        sidebar_layout.addWidget(user_footer)

        return sidebar

    def _create_nav_button(
        self, icon: str, text: str, page_key: str,
        badge: str = "", is_count: bool = False
    ) -> QPushButton:
        btn = QPushButton()
        btn.setFixedHeight(44)
        btn.setCheckable(True)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setObjectName(f"nav_{page_key}")

        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: #F1F5F9;
            }}
            QPushButton:checked {{
                background-color: {COLOR_SIDEBAR_ACTIVE};
            }}
            QPushButton:checked:hover {{
                background-color: {COLOR_SIDEBAR_ACTIVE};
            }}
        """)

        btn_layout = QHBoxLayout(btn)
        btn_layout.setContentsMargins(12, 0, 12, 0)
        btn_layout.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        icon_lbl.setStyleSheet("color: #0F172A; font-size: 15px; background: transparent; border: none;")

        text_lbl = QLabel(text)
        text_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        text_lbl.setStyleSheet("color: #0F172A; font-size: 13px; font-weight: 700; background: transparent; border: none;")

        btn_layout.addWidget(icon_lbl)
        btn_layout.addWidget(text_lbl, stretch=1)

        badge_lbl = None
        if badge:
            badge_lbl = QLabel(badge)
            badge_lbl.setObjectName(f"badge_{page_key}")
            badge_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            badge_lbl.setFixedHeight(22)
            badge_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if is_count:
                badge_lbl.setStyleSheet("""
                    QLabel {
                        background-color: #E2E8F0;
                        color: #0F172A;
                        border: 1px solid #CBD5E1;
                        border-radius: 11px;
                        padding: 0 8px;
                        font-size: 11px;
                        font-weight: 700;
                    }
                """)
                self._badge_member_count = badge_lbl
            else:
                badge_lbl.setStyleSheet("""
                    QLabel {
                        background-color: #E2E8F0;
                        color: #0F172A;
                        border-radius: 6px;
                        padding: 1px 6px;
                        font-size: 10px;
                        font-weight: 700;
                    }
                """)
            btn_layout.addWidget(badge_lbl)

        # Dynamic high-contrast sync on toggled
        def on_btn_toggled(checked, i_lbl=icon_lbl, t_lbl=text_lbl, b_lbl=badge_lbl, is_c=is_count):
            if checked:
                i_lbl.setStyleSheet("color: #FFFFFF; font-size: 15px; background: transparent; border: none;")
                t_lbl.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: 700; background: transparent; border: none;")
                if b_lbl and is_c:
                    b_lbl.setStyleSheet("""
                        QLabel {
                            background-color: rgba(255, 255, 255, 0.28);
                            color: #FFFFFF;
                            border: none;
                            border-radius: 11px;
                            padding: 0 8px;
                            font-size: 11px;
                            font-weight: 700;
                        }
                    """)
                elif b_lbl:
                    b_lbl.setStyleSheet("""
                        QLabel {
                            background-color: rgba(255, 255, 255, 0.28);
                            color: #FFFFFF;
                            border: none;
                            border-radius: 6px;
                            padding: 1px 6px;
                            font-size: 10px;
                            font-weight: 700;
                        }
                    """)
            else:
                i_lbl.setStyleSheet("color: #0F172A; font-size: 15px; background: transparent; border: none;")
                t_lbl.setStyleSheet("color: #0F172A; font-size: 13px; font-weight: 700; background: transparent; border: none;")
                if b_lbl and is_c:
                    b_lbl.setStyleSheet("""
                        QLabel {
                            background-color: #E2E8F0;
                            color: #0F172A;
                            border: 1px solid #CBD5E1;
                            border-radius: 11px;
                            padding: 0 8px;
                            font-size: 11px;
                            font-weight: 700;
                        }
                    """)
                elif b_lbl:
                    b_lbl.setStyleSheet("""
                        QLabel {
                            background-color: #E2E8F0;
                            color: #0F172A;
                            border-radius: 6px;
                            padding: 1px 6px;
                            font-size: 10px;
                            font-weight: 700;
                        }
                    """)

        btn.toggled.connect(on_btn_toggled)
        btn.clicked.connect(lambda _, k=page_key: self._nav_to(k))
        self._nav_buttons[page_key] = btn
        self._nav_text_labels[page_key] = text_lbl
        return btn

    # =========================================================================
    # TOP HEADER BAR CREATION
    # =========================================================================
    def _create_top_header(self) -> QWidget:
        header = QFrame()
        header.setFixedHeight(64)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-bottom: 1px solid {COLOR_BORDER};
            }}
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(16)

        # Omni-Search Bar with Ctrl+K
        search_box = QFrame()
        search_box.setObjectName("omniSearchBox")
        search_box.setStyleSheet(f"""
            QFrame#omniSearchBox {{
                background-color: #F8FAFC;
                border: 1px solid {COLOR_BORDER};
                border-radius: 10px;
            }}
            QFrame#omniSearchBox:focus-within {{
                border-color: {COLOR_PRIMARY};
                background-color: #FFFFFF;
            }}
        """)
        search_box.setMinimumWidth(380)
        search_box.setMaximumWidth(580)
        sb_layout = QHBoxLayout(search_box)
        sb_layout.setContentsMargins(12, 4, 10, 4)
        sb_layout.setSpacing(8)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("color: #94A3B8; font-size: 13px; border: none; background: transparent;")

        self.omni_search = QLineEdit()
        self.omni_search.setPlaceholderText("નામ, મોબાઈલ નંબર, સભ્ય કોડ (GBS-XXXX), ગામ અથવા શહેર દ્વારા શોધો...")
        self.omni_search.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #0F172A;
                font-size: 12px;
            }
        """)
        self.omni_search.returnPressed.connect(self._on_omni_search_submit)

        shortcut_kbd = QLabel("Ctrl + K")
        shortcut_kbd.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                color: #94A3B8;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 2px 6px;
                font-size: 10px;
                font-family: monospace;
                font-weight: 600;
            }
        """)

        sb_layout.addWidget(search_icon)
        sb_layout.addWidget(self.omni_search, stretch=1)
        sb_layout.addWidget(shortcut_kbd)
        layout.addWidget(search_box, stretch=1)

        # Language Toggle Pill
        lang_pill = QFrame()
        lang_pill.setStyleSheet("""
            QFrame {
                background-color: #F1F5F9;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }
        """)
        lang_layout = QHBoxLayout(lang_pill)
        lang_layout.setContentsMargins(3, 3, 3, 3)
        lang_layout.setSpacing(2)

        self.btn_lang_gu = QPushButton("ગુજરાતી")
        self.btn_lang_gu.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_lang_gu.setFixedHeight(26)
        self.btn_lang_gu.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #0F172A;
                border: none;
                border-radius: 6px;
                padding: 0 10px;
                font-size: 11px;
                font-weight: 700;
            }
        """)

        self.btn_lang_en = QPushButton("English")
        self.btn_lang_en.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_lang_en.setFixedHeight(26)
        self.btn_lang_en.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #64748B;
                border: none;
                border-radius: 6px;
                padding: 0 10px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                color: #0F172A;
            }
        """)

        self.btn_lang_gu.clicked.connect(lambda: self._set_language('gu'))
        self.btn_lang_en.clicked.connect(lambda: self._set_language('en'))

        lang_layout.addWidget(self.btn_lang_gu)
        lang_layout.addWidget(self.btn_lang_en)
        layout.addWidget(lang_pill)

        # Quick Add Member Button
        self.btn_quick_add = QPushButton("➕  નવો સભ્ય")
        self.btn_quick_add.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_quick_add.setFixedHeight(36)
        self.btn_quick_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_DARK};
            }}
        """)
        self.btn_quick_add.clicked.connect(lambda: self._nav_to('add'))
        layout.addWidget(self.btn_quick_add)

        # Notification Bell
        self.btn_notif = QPushButton("🔔")
        self.btn_notif.setToolTip("સૂચનાઓ")
        self.btn_notif.setFixedSize(36, 36)
        self.btn_notif.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_notif.setStyleSheet(f"""
            QPushButton {{
                background-color: #F8FAFC;
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #F1F5F9;
            }}
        """)
        self.btn_notif.clicked.connect(self._show_notifications)
        layout.addWidget(self.btn_notif)

        # Sync Health Pill
        self.sync_pill = QLabel("✓ ડેટા સુરક્ષિત")
        self.sync_pill.setStyleSheet("""
            QLabel {
                background-color: #ECFDF5;
                color: #059669;
                border: 1px solid #A7F3D0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: 600;
            }
        """)
        layout.addWidget(self.sync_pill)

        return header

    # =========================================================================
    # GLOBAL FOOTER CREATION
    # =========================================================================
    def _create_global_footer(self) -> QWidget:
        footer = QFrame()
        footer.setObjectName("appFooter")
        footer.setFixedHeight(48)
        footer.setStyleSheet(f"""
            QFrame#appFooter {{
                background-color: #FFFFFF;
                border-top: 1px solid {COLOR_BORDER};
            }}
            QFrame#appFooter QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(24, 0, 24, 0)
        f_layout.setSpacing(12)

        # Company Logo (Gayatri Technology)
        self.footer_logo = QLabel()
        self.footer_logo.setFixedSize(30, 30)
        self.footer_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_logo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.footer_logo.setToolTip(DEVELOPER_WEBSITE)
        self.footer_logo.mousePressEvent = lambda e: QDesktopServices.openUrl(QUrl(DEVELOPER_WEBSITE))
        self.footer_logo.setStyleSheet(f"""
            QLabel {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 1px;
            }}
            QLabel:hover {{
                border-color: {COLOR_PRIMARY};
            }}
        """)
        if os.path.exists(GAYATRI_LOGO_PATH):
            pix = QPixmap(GAYATRI_LOGO_PATH)
            if not pix.isNull():
                self.footer_logo.setPixmap(
                    pix.scaled(26, 26, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                )

        f_layout.addWidget(self.footer_logo)

        # Developer Attribution Label
        from app.translations import t
        self.lbl_footer_dev = QLabel()
        self.lbl_footer_dev.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px;")
        self.lbl_footer_dev.setMinimumWidth(260)
        built_by = t('footer_built_by', self._current_lang)
        comp_name = t('footer_company_name', self._current_lang)
        self.lbl_footer_dev.setText(f"{built_by}<b>{comp_name}</b>")
        f_layout.addWidget(self.lbl_footer_dev)

        f_layout.addSpacing(4)

        # Website Link Button
        self.btn_footer_web = QPushButton("🌐  gayatritechnology.in")
        self.btn_footer_web.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_footer_web.setFixedHeight(28)
        self.btn_footer_web.setToolTip(DEVELOPER_WEBSITE)
        self.btn_footer_web.setStyleSheet(f"""
            QPushButton {{
                background-color: #EFF6FF;
                color: {COLOR_PRIMARY};
                border: 1px solid #DBEAFE;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                padding: 0 10px;
            }}
            QPushButton:hover {{
                background-color: #DBEAFE;
                color: {COLOR_PRIMARY_DARK};
                border-color: #93C5FD;
            }}
        """)
        self.btn_footer_web.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(DEVELOPER_WEBSITE)))
        f_layout.addWidget(self.btn_footer_web)

        # Email Link Button
        self.btn_footer_email = QPushButton(f"✉️  {DEVELOPER_EMAIL}")
        self.btn_footer_email.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_footer_email.setFixedHeight(28)
        self.btn_footer_email.setToolTip(f"Email {DEVELOPER_EMAIL}")
        self.btn_footer_email.setStyleSheet(f"""
            QPushButton {{
                background-color: #F8FAFC;
                color: #475569;
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                padding: 0 10px;
            }}
            QPushButton:hover {{
                background-color: #F1F5F9;
                color: {COLOR_TEXT_MAIN};
                border-color: #CBD5E1;
            }}
        """)
        self.btn_footer_email.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(f"mailto:{DEVELOPER_EMAIL}")))
        f_layout.addWidget(self.btn_footer_email)

        f_layout.addStretch()

        # Right: Version & Rights Label
        rights = t('footer_rights', self._current_lang)
        self.lbl_footer_ver = QLabel(f"v{APP_VERSION} • {rights}")
        self.lbl_footer_ver.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_footer_ver.setMinimumWidth(190)
        self.lbl_footer_ver.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600;")
        f_layout.addWidget(self.lbl_footer_ver)

        return footer

    # =========================================================================
    # SHORTCUTS & ACTIONS
    # =========================================================================
    def _setup_shortcuts(self):
        # Global Ctrl+K to jump to Omni-search
        shortcut_k = QShortcut(QKeySequence("Ctrl+K"), self)
        shortcut_k.activated.connect(self.focus_omni_search)

    def focus_omni_search(self):
        self.omni_search.setFocus()
        self.omni_search.selectAll()

    def _on_omni_search_submit(self):
        text = self.omni_search.text().strip()
        if text:
            self._nav_to('list')
            self._member_list_page.search_edit.setText(text)

    def set_language(self, lang: str):
        """Public alias to set language across the application."""
        self._set_language(lang)

    def _set_language(self, lang: str):
        self._current_lang = lang
        from app.translations import t

        if lang == 'gu':
            self.btn_lang_gu.setText("ગુજરાતી")
            self.btn_lang_gu.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF; color: #0F172A;
                    border: 1px solid #CBD5E1; border-radius: 6px; padding: 0 10px;
                    font-size: 11px; font-weight: 700;
                }
            """)
            self.btn_lang_en.setStyleSheet("""
                QPushButton {
                    background-color: transparent; color: #64748B;
                    border: none; border-radius: 6px; padding: 0 10px;
                    font-size: 11px; font-weight: 500;
                }
                QPushButton:hover {
                    color: #0F172A;
                    background-color: rgba(255, 255, 255, 0.6);
                }
            """)
        else:
            self.btn_lang_gu.setText("Gujarati")
            self.btn_lang_en.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF; color: #0F172A;
                    border: 1px solid #CBD5E1; border-radius: 6px; padding: 0 10px;
                    font-size: 11px; font-weight: 700;
                }
            """)
            self.btn_lang_gu.setStyleSheet("""
                QPushButton {
                    background-color: transparent; color: #64748B;
                    border: none; border-radius: 6px; padding: 0 10px;
                    font-size: 11px; font-weight: 500;
                }
                QPushButton:hover {
                    color: #0F172A;
                    background-color: rgba(255, 255, 255, 0.6);
                }
            """)

        # 1. Window Title
        self.setWindowTitle(t('window_title', lang))

        # 2. Header Elements
        if hasattr(self, 'omni_search'):
            self.omni_search.setPlaceholderText(t('search_placeholder', lang))
        if hasattr(self, 'btn_quick_add'):
            self.btn_quick_add.setText(t('quick_add', lang))
        if hasattr(self, 'sync_pill'):
            self.sync_pill.setText(t('sync_status', lang))

        if hasattr(self, 'btn_notif'):
            self.btn_notif.setToolTip("Notifications" if lang == 'en' else "સૂચનાઓ")

        # 3. Sidebar Elements
        if hasattr(self, 'org_name'):
            try:
                from services.settings_service import SettingsService
                custom_name = SettingsService().get('org_name_' + lang)
                self.org_name.setText(custom_name if custom_name else t('org_name', lang))
            except Exception:
                self.org_name.setText(t('org_name', lang))
        if hasattr(self, 'lbl_sec_main'):
            self.lbl_sec_main.setText(t('sec_main', lang))
        if hasattr(self, 'lbl_sec_tools'):
            self.lbl_sec_tools.setText(t('sec_tools', lang))
        if hasattr(self, 'uname'):
            try:
                from services.settings_service import SettingsService
                custom_admin = SettingsService().get('admin_name')
                default_names = {
                    'પાર્થ રાવલ (Admin)', 'પાર્થ રાવલ (એડમિન)', 'Parth Raval (Admin)',
                    'સંચાલક (Admin)', 'સંચાલક (એડમિન)', 'Administrator',
                }
                if not custom_admin or custom_admin in default_names:
                    admin_display = t('admin_name', lang)
                else:
                    admin_display = custom_admin
                self.uname.setText(admin_display)
                self._update_user_avatar(admin_display)
            except Exception:
                admin_display = t('admin_name', lang)
                self.uname.setText(admin_display)
                self._update_user_avatar(admin_display)
        if hasattr(self, 'ustatus'):
            self.ustatus.setText(t('online_status', lang))

        # 4. Sidebar Nav Buttons
        nav_keys = {
            'dashboard': 'nav_dashboard',
            'add': 'nav_add',
            'list': 'nav_list',
            'backup': 'nav_backup',
            'settings': 'nav_settings',
        }
        for k, tr_k in nav_keys.items():
            if k in self._nav_text_labels:
                self._nav_text_labels[k].setText(t(tr_k, lang))

        # 5. Stacked Pages
        for page in (
            self._dashboard_page,
            self._member_list_page,
            self._member_form_page,
            self._member_profile_page,
            self._form_preview_page,
            self._backup_page,
            self._settings_page,
        ):
            if hasattr(page, 'set_language'):
                try:
                    page.set_language(lang)
                except Exception:
                    pass

        # 6. Global Footer Attribution
        if hasattr(self, 'lbl_footer_dev'):
            dev_text = t('footer_built_by', lang)
            comp_name = t('footer_company_name', lang)
            self.lbl_footer_dev.setText(f"{dev_text}<b>{comp_name}</b>")
        if hasattr(self, 'lbl_footer_ver'):
            rights = t('footer_rights', lang)
            self.lbl_footer_ver.setText(f"v{APP_VERSION} • {rights}")

        # 7. Persist to settings
        try:
            from services.settings_service import SettingsService
            SettingsService().set('default_language', lang)
        except Exception:
            pass

    def _show_notifications(self):
        from app.translations import t
        QMessageBox.information(
            self, t("notif_title", self._current_lang),
            t("notif_msg", self._current_lang)
        )

    def update_member_badge(self):
        """Update total members count badge on the sidebar."""
        try:
            count = self._member_svc.count()
            if hasattr(self, '_badge_member_count') and self._badge_member_count:
                self._badge_member_count.setText(f"{count:,}")
        except Exception:
            pass

    def on_data_updated(self):
        """Immediately refresh all data views, counters, and statistics across the app."""
        self.update_member_badge()
        if hasattr(self, '_dashboard_page') and self._dashboard_page:
            try:
                self._dashboard_page.refresh_stats()
            except Exception:
                pass
        if hasattr(self, '_member_list_page') and self._member_list_page:
            try:
                self._member_list_page.load_members()
            except Exception:
                pass
        if hasattr(self, '_settings_page') and self._settings_page:
            try:
                self._settings_page._refresh_diagnostics()
            except Exception:
                pass
        if hasattr(self, '_backup_page') and self._backup_page:
            try:
                self._backup_page.refresh()
            except Exception:
                pass

    def on_settings_updated(self):
        """Immediately update all UI components when system settings change."""
        try:
            from services.settings_service import SettingsService
            from app.translations import t
            settings = SettingsService().get_all()

            # 1. Update Sidebar Branding
            org_name = settings.get('org_name_' + self._current_lang) or settings.get('org_name_gu', 'ગુજરાત બ્રહ્મ સમાજ')
            org_subtitle = settings.get('erp_subtitle', 'BRAHM SAMAJ ERP')
            admin_name = settings.get('admin_name')
            default_names = {
                'પાર્થ રાવલ (Admin)', 'પાર્થ રાવલ (એડમિન)', 'Parth Raval (Admin)',
                'સંચાલક (Admin)', 'સંચાલક (એડમિન)', 'Administrator',
            }
            if not admin_name or admin_name in default_names:
                admin_name = t('admin_name', self._current_lang)

            if hasattr(self, 'org_name') and self.org_name:
                self.org_name.setText(org_name)
            if hasattr(self, 'erp_sub') and self.erp_sub:
                self.erp_sub.setText(org_subtitle)
            if hasattr(self, 'uname') and self.uname:
                self.uname.setText(admin_name)
                self._update_user_avatar(admin_name)

            # 2. Update runtime config prefix
            prefix = settings.get('member_code_prefix', 'GBS-')
            import app.config
            app.config.MEMBER_CODE_PREFIX = prefix

            # 3. Update records per page
            rpp = settings.get('rows_per_page', '50')
            try:
                if hasattr(self, '_member_list_page') and self._member_list_page:
                    self._member_list_page.PAGE_SIZE = int(rpp)
            except Exception:
                pass

            # 4. Always ensure active language is applied across all views
            lang = settings.get('default_language', self._current_lang)
            self._set_language(lang)

            # 5. Refresh all views and statistics
            self.on_data_updated()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning("Error refreshing UI on settings update: %s", e)

    # =========================================================================
    # AVATAR INITIALS HELPER
    # =========================================================================
    @staticmethod
    def _compute_initials(name: str) -> str:
        """
        Extract 1-2 letter uppercase initials dynamically from admin or user name.
        Handles English, Gujarati names, parenthesized roles (Admin), prefixes, etc.
        e.g.:
          'Vishnu Raval (Admin)' -> 'VR'
          'Vishnu Raval'         -> 'VR'
          'Parth Raval'          -> 'PR'
          'Administrator'        -> 'AD'
          'Admin'                -> 'AD'
          'વિષ્ણુ રાવલ'          -> 'VR'
        """
        if not name or not name.strip():
            return "AD"

        # 1. Clean brackets and parentheses like (Admin), [Staff], (સંચાલક)
        cleaned = re.sub(r'[\(\[\{][^\)\]\}]*[\)\]\}]', '', name).strip()
        # 2. Clean trailing role labels separated by -, |, /, :
        cleaned = re.sub(r'[\-|/:]\s*(admin|administrator|સંચાલક|એડમિન).*$', '', cleaned, flags=re.IGNORECASE).strip()

        # Split into words
        words = [w for w in re.split(r'[\s\-_\.,/]+', cleaned) if w]
        if not words:
            words = [w for w in re.split(r'[\s\-_\.,/()\[\]{}]+', name) if w]

        # Filter out standalone role words if multiple words exist
        roles = {'admin', 'administrator', 'એડમિન', 'સંચાલક', 'user', 'manager'}
        if len(words) > 1:
            non_role = [w for w in words if w.lower() not in roles]
            if non_role:
                words = non_role

        def word_to_initial(word: str) -> str:
            for ch in word:
                if ch.isalpha() and ch.isascii():
                    return ch.upper()
            try:
                from utils.gujarati_search import gujarati_to_phonetic_english
                phonetic = gujarati_to_phonetic_english(word)
                for ch in phonetic:
                    if ch.isalpha() and ch.isascii():
                        return ch.upper()
            except Exception:
                pass
            return word[0].upper() if word else ""

        if len(words) >= 2:
            c1 = word_to_initial(words[0])
            c2 = word_to_initial(words[-1])
            initials = (c1 + c2).strip()
            if initials:
                return initials
        elif len(words) == 1:
            w = words[0]
            ascii_letters = [ch.upper() for ch in w if ch.isalpha() and ch.isascii()]
            if len(ascii_letters) >= 2:
                return "".join(ascii_letters[:2])
            elif len(ascii_letters) == 1:
                return ascii_letters[0]
            else:
                try:
                    from utils.gujarati_search import gujarati_to_phonetic_english
                    phonetic = gujarati_to_phonetic_english(w)
                    p_letters = [ch.upper() for ch in phonetic if ch.isalpha() and ch.isascii()]
                    if len(p_letters) >= 2:
                        return "".join(p_letters[:2])
                    elif len(p_letters) == 1:
                        return p_letters[0]
                except Exception:
                    pass

        return "AD"

    def _update_user_avatar(self, name: str) -> None:
        """Update sidebar footer avatar badge with dynamic initials and tooltip."""
        if hasattr(self, 'uavatar') and self.uavatar:
            initials = self._compute_initials(name)
            self.uavatar.setText(initials)
            self.uavatar.setToolTip(name)

    # =========================================================================
    # NAVIGATION ROUTER
    # =========================================================================
    def _nav_to(self, page: str, **kwargs) -> None:
        """Navigate to a page by key."""
        idx, nav_key = self._page_map.get(page, (0, 'dashboard'))

        # Update button checked states
        for key, btn in self._nav_buttons.items():
            btn.setChecked(key == nav_key)

        if page == 'add':
            self._member_form_page.reset()
        elif page == 'edit':
            mid = kwargs.get('member_id')
            if mid is not None:
                member = self._member_svc.get_member(mid)
                if member:
                    self._member_form_page.load_for_edit(member)
        elif page == 'profile':
            mid = kwargs.get('member_id')
            if mid:
                self._member_profile_page.load_member(mid)
        elif page == 'form_preview':
            mid = kwargs.get('member_id')
            if mid:
                self._form_preview_page.load_member(mid)
            else:
                # If navigating to form preview with no mid, load first available or keep existing
                recent = self._member_svc.get_recent(1)
                if recent:
                    self._form_preview_page.load_member(recent[0].id)
        elif page in ('list', 'search'):
            self._member_list_page.load_members()
            if page == 'search':
                self._member_list_page.search_edit.setFocus()
        elif page == 'backup':
            self._backup_page.refresh()
        elif page == 'settings':
            self._settings_page.load_settings()
        elif page == 'dashboard':
            self._dashboard_page.refresh_stats()

        self.update_member_badge()
        self.stack.setCurrentIndex(idx)
