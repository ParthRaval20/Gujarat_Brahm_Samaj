"""
Modern Dashboard Page — Matching the Stitch UI Design Revamp.
Displays:
1. Cultural Welcome Banner (નમસ્તે, પ્રમુખ શ્રી - Admin Portal)
2. 4 Key Metrics KPI Cards (Total Members, Added Today, Families, ID Cards)
3. 3 Quick Launchpad Action Cards (Add Member, View Directory, Backup/Restore)
4. Recent Registrations Interactive Data Table with Search and City Filters
"""

from __future__ import annotations

import csv
import os
from datetime import datetime
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QCursor, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox,
    QScrollArea, QAbstractItemView, QFileDialog, QMessageBox,
)

from app.config import (
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_BG, COLOR_CARD_BG,
    COLOR_BORDER, COLOR_BORDER_LIGHT, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    COLOR_ACCENT_BLUE, COLOR_ACCENT_EMERALD, COLOR_ACCENT_PURPLE,
    COLOR_ACCENT_AMBER, COLOR_ACCENT_GOLD, COLOR_SIDEBAR_BG,
    EXPORT_DIR, ensure_dirs,
)
from services.member_service import MemberService
from services.family_service import FamilyService

CITY_TRANSLATIONS = {
    'અમદાવાદ': 'Ahmedabad',
    'આણંદ': 'Anand',
    'ઈડર': 'Idar',
    'ઇડર': 'Idar',
    'ગાંધીનગર': 'Gandhinagar',
    'જામનગર સિટી': 'Jamnagar City',
    'જામનગર': 'Jamnagar',
    'જુનાગઢ': 'Junagadh',
    'જૂનાગઢ': 'Junagadh',
    'નડિયાદ': 'Nadiad',
    'ભાવનગર': 'Bhavnagar',
    'રાજકોટ': 'Rajkot',
    'વડોદરા': 'Vadodara',
    'સુરત': 'Surat',
    'મહેસાણા': 'Mehsana',
    'હિંમતનગર': 'Himatnagar',
    'પ્રાંતિજ': 'Prantij',
    'તલોદ': 'Talod',
    'મોડાસા': 'Modasa',
    'ખેડબ્રહ્મા': 'Khedbrahma',
    'વડાલી': 'Vadali',
    'વિજયનગર': 'Vijaynagar',
    'પોશીના': 'Poshina',
    'પાટણ': 'Patan',
    'પાલનપુર': 'Palanpur',
    'પોરબંદર': 'Porbandar',
    'મોરબી': 'Morbi',
    'ભરૂચ': 'Bharuch',
    'નવસારી': 'Navsari',
    'વલસાડ': 'Valsad',
    'સાબરકાંઠા': 'Sabarkantha',
    'ગુજરાત': 'Gujarat',
}


class DashboardPage(QWidget):
    def __init__(self, nav_callback, parent=None):
        super().__init__(parent)
        self._nav = nav_callback
        self._member_svc = MemberService()
        self._family_svc = FamilyService()
        self._recent_members = []
        self._current_lang = 'gu'
        self._setup_ui()
        self.refresh_stats()

    def _setup_ui(self):
        # Outer layout contains a smooth scroll area for modern look
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet(f"QScrollArea {{ background-color: {COLOR_BG}; border: none; }}")

        container = QWidget()
        container.setObjectName("dashboardContainer")
        container.setStyleSheet(f"#dashboardContainer {{ background-color: {COLOR_BG}; }}")
        self.layout = QVBoxLayout(container)
        self.layout.setContentsMargins(28, 24, 28, 28)
        self.layout.setSpacing(22)

        # ── 1. Hero Welcome Banner ───────────────────────────────────
        self.layout.addWidget(self._create_hero_banner())

        # ── 2. Key Metrics KPI Cards (4 cards) ───────────────────────
        self.layout.addWidget(self._create_kpi_metrics_section())

        # ── 3. Quick Launchpad Action Cards ──────────────────────────
        self.layout.addWidget(self._create_quick_launchpad_section())

        # ── 4. Recent Registrations Data Table ───────────────────────
        self.layout.addWidget(self._create_recent_table_section())

        scroll_area.setWidget(container)
        outer_layout.addWidget(scroll_area)

    # =========================================================================
    # 1. HERO BANNER
    # =========================================================================
    def _create_hero_banner(self) -> QWidget:
        banner = QFrame()
        banner.setObjectName("heroBanner")
        banner.setStyleSheet(f"""
            QFrame#heroBanner {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0F172A, stop:0.5 #1E293B, stop:1 #1E3A8A);
                border: 1px solid #1E293B;
                border-radius: 16px;
            }}
        """)

        layout = QHBoxLayout(banner)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        # Left Info Block
        left_box = QVBoxLayout()
        left_box.setSpacing(8)

        # Official portal pill badge
        self.flag_badge = QLabel("🚩 શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સત્તાવાર પોર્ટલ")
        self.flag_badge.setStyleSheet("""
            QLabel {
                background-color: rgba(245, 158, 11, 0.15);
                color: #FBBF24;
                border: 1px solid rgba(245, 158, 11, 0.4);
                border-radius: 12px;
                padding: 3px 12px;
                font-size: 11px;
                font-weight: 600;
            }
        """)
        self.flag_badge.setFixedHeight(26)

        # Heading
        self.hero_title = QLabel("નમસ્તે, પ્રમુખ શ્રી (Admin Portal)")
        self.hero_title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 22px;
                font-weight: 800;
                letter-spacing: 0.2px;
                background: transparent;
            }
        """)

        # Subtitle
        self.hero_subtitle = QLabel("સમાજના તમામ સભ્યો, કુંટુંબ વિગતો અને આઈડી કાર્ડ વિતરણનું કેન્દ્રીય સંચાલન બોર્ડ.")
        self.hero_subtitle.setStyleSheet("""
            QLabel {
                color: #94A3B8;
                font-size: 13px;
                font-weight: 400;
                background: transparent;
            }
        """)

        left_box.addWidget(self.flag_badge, alignment=Qt.AlignmentFlag.AlignLeft)
        left_box.addWidget(self.hero_title)
        left_box.addWidget(self.hero_subtitle)
        layout.addLayout(left_box, stretch=1)

        # Right Action Buttons
        right_box = QHBoxLayout()
        right_box.setSpacing(12)

        # Download Report Button
        self.btn_download_report = QPushButton("📥  રિપોર્ટ ડાઉનલોડ")
        self.btn_download_report.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_download_report.setFixedHeight(42)
        self.btn_download_report.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.12);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 10px;
                padding: 0 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.20);
                border-color: rgba(255, 255, 255, 0.40);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.08);
            }
        """)
        self.btn_download_report.clicked.connect(self._export_summary_report)

        # Register Member Button
        self.btn_banner_register = QPushButton("➕  સભ્ય નોંધણી")
        self.btn_banner_register.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_banner_register.setFixedHeight(42)
        self.btn_banner_register.setStyleSheet("""
            QPushButton {
                background-color: #F59E0B;
                color: #0F172A;
                border: none;
                border-radius: 10px;
                padding: 0 20px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #D97706;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #B45309;
            }
        """)
        self.btn_banner_register.clicked.connect(lambda: self._nav("add"))

        right_box.addWidget(self.btn_download_report)
        right_box.addWidget(self.btn_banner_register)
        layout.addLayout(right_box)

        return banner

    # =========================================================================
    # 2. KEY METRICS KPI CARDS
    # =========================================================================
    def _create_kpi_metrics_section(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Card 1: Total Members (Blue)
        self.card_total_val = QLabel("0")
        self.card_total = self._build_kpi_card(
            title="કુલ નોંધાયેલ સભ્યો",
            value_label=self.card_total_val,
            icon_char="👥",
            badge_text="↑ 12.5%",
            badge_color="#10B981",
            badge_bg="#ECFDF5",
            subtext="ગત માસ કરતા વધુ",
            accent_color=COLOR_ACCENT_BLUE,
            icon_bg="#EFF6FF",
        )

        # Card 2: Added Today (Emerald)
        self.card_today_val = QLabel("0")
        self.card_today = self._build_kpi_card(
            title="આજે ઉમેરાયેલ (TODAY)",
            value_label=self.card_today_val,
            icon_char="📅",
            badge_text="લાઇવ અપડેટ",
            badge_color="#059669",
            badge_bg="#D1FAE5",
            subtext="સત્તાવાર દૈનિક નોંધણી",
            accent_color=COLOR_ACCENT_EMERALD,
            icon_bg="#ECFDF5",
        )

        # Card 3: Families (Purple)
        self.card_family_val = QLabel("0")
        self.card_family = self._build_kpi_card(
            title="કુલ કુટુંબ સંખ્યા (FAMILIES)",
            value_label=self.card_family_val,
            icon_char="👨‍👩‍👧",
            badge_text="સરેરાશ 3.8 સભ્ય/ઘર",
            badge_color="#7C3AED",
            badge_bg="#F5F3FF",
            subtext="સંપૂર્ણ પારિવારિક ડેટા ઉપલબ્ધ",
            accent_color=COLOR_ACCENT_PURPLE,
            icon_bg="#F5F3FF",
        )

        # Card 4: ID Cards Issued (Amber)
        self.card_issued_val = QLabel("0")
        self.card_issued = self._build_kpi_card(
            title="આઈડી કાર્ડ વિતરણ (ISSUED)",
            value_label=self.card_issued_val,
            icon_char="🪪",
            badge_text="QR કાર્ડ પ્રિન્ટેડ",
            badge_color="#D97706",
            badge_bg="#FFFBEB",
            subtext="ડિજિટલ સ્માર્ટ કાર્ડ ચકાસાયેલ",
            accent_color=COLOR_ACCENT_AMBER,
            icon_bg="#FFFBEB",
        )

        layout.addWidget(self.card_total)
        layout.addWidget(self.card_today)
        layout.addWidget(self.card_family)
        layout.addWidget(self.card_issued)

        return container

    def _build_kpi_card(
        self, title: str, value_label: QLabel, icon_char: str,
        badge_text: str, badge_color: str, badge_bg: str,
        subtext: str, accent_color: str, icon_bg: str,
    ) -> QWidget:
        card = QFrame()
        card.setObjectName("kpiCard")
        card.setFixedHeight(122)
        card.setStyleSheet(f"""
            QFrame#kpiCard {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER};
                border-radius: 14px;
            }}
            QFrame#kpiCard:hover {{
                border-color: {accent_color};
            }}
            QFrame#kpiCard QLabel {{
                border: none;
                background: transparent;
            }}
        """)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 16, 0)
        card_layout.setSpacing(14)

        # Left vertical accent stripe
        stripe = QFrame()
        stripe.setObjectName("kpiStripe")
        stripe.setFixedWidth(5)
        stripe.setStyleSheet(f"""
            QFrame#kpiStripe {{
                background-color: {accent_color};
                border: none;
                border-top-left-radius: 14px;
                border-bottom-left-radius: 14px;
            }}
        """)
        card_layout.addWidget(stripe)

        # Content area
        content = QVBoxLayout()
        content.setContentsMargins(0, 16, 0, 16)
        content.setSpacing(6)

        # Top row: Title + Icon
        top_row = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-weight: 700; text-transform: uppercase; border: none; background: transparent;")
        card.title_lbl = title_lbl

        icon_lbl = QLabel(icon_char)
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {icon_bg};
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }}
        """)

        top_row.addWidget(title_lbl, stretch=1)
        top_row.addWidget(icon_lbl)
        content.addLayout(top_row)

        # Middle row: Stat Value + Badge
        mid_row = QHBoxLayout()
        mid_row.setSpacing(8)

        value_label.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 26px; font-weight: 800; border: none; background: transparent;")

        badge = QLabel(badge_text)
        badge.setStyleSheet(f"""
            QLabel {{
                color: {badge_color};
                background-color: {badge_bg};
                border: none;
                border-radius: 6px;
                padding: 2px 8px;
                font-size: 11px;
                font-weight: 700;
            }}
        """)
        card.badge_lbl = badge

        mid_row.addWidget(value_label)
        mid_row.addWidget(badge)
        mid_row.addStretch()
        content.addLayout(mid_row)

        # Bottom subtext
        sub_lbl = QLabel(subtext)
        sub_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-weight: 500; border: none; background: transparent;")
        card.sub_lbl = sub_lbl
        content.addWidget(sub_lbl)

        card_layout.addLayout(content, stretch=1)
        return card

    # =========================================================================
    # 3. QUICK LAUNCHPAD ACTION CARDS
    # =========================================================================
    def _create_quick_launchpad_section(self) -> QWidget:
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Section Header
        hdr = QHBoxLayout()
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background-color: {COLOR_ACCENT_BLUE}; border-radius: 4px;")

        self.sec_launchpad_title = QLabel("ઝડપી સેવાઓ (Quick Launchpad)")
        self.sec_launchpad_title.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 15px; font-weight: 800;")

        self.sec_launchpad_sub = QLabel("વારંવાર ઉપયોગમાં લેવાતા મોડ્યુલ")
        self.sec_launchpad_sub.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px; font-weight: 500;")

        hdr.addWidget(dot)
        hdr.addWidget(self.sec_launchpad_title)
        hdr.addSpacing(8)
        hdr.addWidget(self.sec_launchpad_sub)
        hdr.addStretch()
        layout.addLayout(hdr)

        # 3 Launchpad Action Cards Grid
        grid = QHBoxLayout()
        grid.setSpacing(16)

        # Action 1: Add New Member (Emerald)
        self.launch_card1 = self._build_action_card(
            icon="➕",
            badge="નવું ફોર્મ",
            title="Add New Member",
            subtitle="નવા સભ્યની પ્રાથમિક અને કૌટુંબિક નોંધણી",
            gradient_css="qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #059669, stop:1 #047857)",
            click_handler=lambda: self._nav("add"),
        )

        # Action 2: View All Members (Blue)
        self.launch_card2 = self._build_action_card(
            icon="📇",
            badge="ડિરેક્ટરી",
            title="View All Members",
            subtitle="તમામ સભ્યોની યાદી, શોધ અને સુધારા",
            gradient_css="qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2563EB, stop:1 #1D4ED8)",
            click_handler=lambda: self._nav("list"),
        )

        # Action 3: Backup / Restore (Amber)
        self.launch_card3 = self._build_action_card(
            icon="💾",
            badge="સલામતી",
            title="Backup / Restore",
            subtitle="ડેટાબેઝ સ્થાનિક બેકઅપ અને સુરક્ષા",
            gradient_css="qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #D97706, stop:1 #B45309)",
            click_handler=lambda: self._nav("backup"),
        )

        grid.addWidget(self.launch_card1)
        grid.addWidget(self.launch_card2)
        grid.addWidget(self.launch_card3)
        layout.addLayout(grid)

        return section

    def _build_action_card(
        self, icon: str, badge: str, title: str, subtitle: str,
        gradient_css: str, click_handler,
    ) -> QWidget:
        btn = QPushButton()
        btn.setObjectName("launchCard")
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setFixedHeight(130)
        btn.setStyleSheet(f"""
            QPushButton#launchCard {{
                background: {gradient_css};
                border: none;
                border-radius: 14px;
                text-align: left;
                padding: 0px;
            }}
            QPushButton#launchCard:hover {{
                border: 2px solid rgba(255, 255, 255, 0.6);
            }}
            QPushButton#launchCard QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        btn.clicked.connect(click_handler)

        card_layout = QVBoxLayout(btn)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(8)

        # Top row: icon container + badge
        top_row = QHBoxLayout()

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.20);
                border: none;
                border-radius: 8px;
                font-size: 16px;
                color: #FFFFFF;
            }
        """)

        badge_lbl = QLabel(badge)
        badge_lbl.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0.25);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.30);
                border-radius: 10px;
                padding: 2px 10px;
                font-size: 10px;
                font-weight: 700;
            }
        """)

        top_row.addWidget(icon_lbl)
        top_row.addStretch()
        top_row.addWidget(badge_lbl)
        card_layout.addLayout(top_row)

        card_layout.addStretch()

        # Title & Subtitle
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #FFFFFF; font-size: 15px; font-weight: 800; background: transparent; border: none;")

        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet("color: rgba(255, 255, 255, 0.88); font-size: 11px; font-weight: 500; background: transparent; border: none;")

        card_layout.addWidget(title_lbl)
        card_layout.addWidget(sub_lbl)

        btn.title_lbl = title_lbl
        btn.sub_lbl = sub_lbl
        btn.badge_lbl = badge_lbl

        return btn

    # =========================================================================
    # 4. RECENT REGISTRATIONS DATA TABLE
    # =========================================================================
    def _create_recent_table_section(self) -> QWidget:
        card = QFrame()
        card.setObjectName("recentTableCard")
        card.setStyleSheet(f"""
            QFrame#recentTableCard {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER};
                border-radius: 16px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(14)

        # Header Bar with Controls
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        # Left Title
        left_title = QHBoxLayout()
        left_title.setSpacing(10)

        icon_box = QLabel("📋")
        icon_box.setFixedSize(36, 36)
        icon_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_box.setStyleSheet(f"""
            background-color: #EFF6FF;
            color: {COLOR_ACCENT_BLUE};
            border-radius: 8px;
            font-size: 16px;
        """)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)

        self.tbl_title = QLabel("તાજેતરના સભ્યો (Recent Registrations)")
        self.tbl_title.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 15px; font-weight: 800;")

        self.tbl_subtitle = QLabel("કુલ સભ્યોમાંથી છેલ્લા નોંધાયેલા સભ્યોની યાદી")
        self.tbl_subtitle.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-weight: 500;")

        title_vbox.addWidget(self.tbl_title)
        title_vbox.addWidget(self.tbl_subtitle)

        left_title.addWidget(icon_box)
        left_title.addLayout(title_vbox)
        header_row.addLayout(left_title, stretch=1)

        # Right Controls: Filter Input, City Dropdown, Filter Button
        controls = QHBoxLayout()
        controls.setSpacing(8)

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("🔍  આ યાદીમાં ફિલ્ટર કરો...")
        self.filter_input.setFixedHeight(34)
        self.filter_input.setFixedWidth(200)
        self.filter_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #F8FAFC;
                color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 0 10px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border-color: {COLOR_ACCENT_BLUE};
                background-color: #FFFFFF;
            }}
        """)
        self.filter_input.textChanged.connect(self._apply_table_filters)

        self.city_combo = QComboBox()
        self.city_combo.setFixedHeight(34)
        self.city_combo.setMinimumWidth(160)
        self.city_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #F8FAFC;
                color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 0 10px;
                font-size: 12px;
            }}
            QComboBox:focus {{
                border-color: {COLOR_ACCENT_BLUE};
            }}
            QComboBox QAbstractItemView {{
                background-color: #FFFFFF;
                color: {COLOR_TEXT_MAIN};
                selection-background-color: #EFF6FF;
                selection-color: {COLOR_ACCENT_BLUE};
            }}
        """)
        self.city_combo.currentIndexChanged.connect(self._apply_table_filters)

        self.btn_filters = QPushButton("ફિલ્ટર્સ")
        self.btn_filters.setFixedHeight(34)
        self.btn_filters.setStyleSheet(f"""
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
        self.btn_filters.clicked.connect(self._reset_table_filters)

        controls.addWidget(self.filter_input)
        controls.addWidget(self.city_combo)
        controls.addWidget(self.btn_filters)
        header_row.addLayout(controls)

        layout.addLayout(header_row)

        # Table Element
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "સભ્ય કોડ",
            "સભ્યનું પૂરું નામ",
            "પિતા / વાલીનું નામ",
            "મોબાઇલ નંબર",
            "શહેર",
            "સ્થિતિ",
            "કાર્ય",
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Interactive)

        self.table.setColumnWidth(0, 110)
        self.table.setColumnWidth(3, 125)
        self.table.setColumnWidth(4, 115)
        self.table.setColumnWidth(5, 125)
        self.table.setColumnWidth(6, 125)
        self.table.verticalHeader().setDefaultSectionSize(44)

        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(280)

        self.table.setStyleSheet(f"""
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

        layout.addWidget(self.table)
        return card

    # =========================================================================
    # REFRESH AND DATA LOGIC
    # =========================================================================
    def refresh_stats(self):
        """Update KPI stats and populate recent registrations from database."""
        try:
            total_members = self._member_svc.count()
            today_members = self._member_svc.count_today()
            total_families = self._family_svc.count_all()

            self.card_total_val.setText(f"{total_members:,}")
            self.card_today_val.setText(str(today_members))
            self.card_family_val.setText(f"{total_families:,}")
            self.card_issued_val.setText(f"{total_members:,}")

            # Populate City Filter Dropdown
            cities = self._member_svc.get_distinct_cities()
            curr_data = self.city_combo.currentData()
            self.city_combo.blockSignals(True)
            self.city_combo.clear()
            all_cities_label = "All Cities" if self._current_lang == 'en' else "તમામ શહેર"
            self.city_combo.addItem(all_cities_label, "")
            for c in cities:
                disp = CITY_TRANSLATIONS.get(c, c) if self._current_lang == 'en' else c
                self.city_combo.addItem(disp, c)
            if curr_data:
                idx = self.city_combo.findData(curr_data)
                if idx >= 0:
                    self.city_combo.setCurrentIndex(idx)
            self.city_combo.blockSignals(False)

            # Load recent 20 registrations
            self._recent_members = self._member_svc.get_recent(limit=20)
            if self._current_lang == 'en':
                self.tbl_subtitle.setText(f"List of recently registered members out of total {total_members:,} members")
            else:
                self.tbl_subtitle.setText(f"કુલ {total_members:,} સભ્યોમાંથી છેલ્લા નોંધાયેલા સભ્યોની યાદી")
            self._apply_table_filters()
        except Exception as exc:
            print(f"Error refreshing dashboard stats: {exc}")

    def _apply_table_filters(self):
        """Filter recent members table based on search input and selected city."""
        search_txt = self.filter_input.text().strip().lower()
        selected_city = self.city_combo.currentData()
        if selected_city is None:
            txt = self.city_combo.currentText()
            if txt in ("તમામ શહેર", "All Cities", "તમામ શહેર (All Cities)"):
                selected_city = ""
            else:
                selected_city = txt

        filtered = []
        for m in self._recent_members:
            if selected_city and (m.city or "").strip() != selected_city:
                continue
            if search_txt:
                haystack = f"{m.member_code} {m.full_name} {m.father_name or ''} {m.mobile or ''} {m.city or ''}".lower()
                if search_txt not in haystack:
                    continue
            filtered.append(m)

        self._populate_table(filtered)

    def _reset_table_filters(self):
        self.filter_input.clear()
        self.city_combo.setCurrentIndex(0)
        self._apply_table_filters()

    def _populate_table(self, members):
        # Cleanly unparent existing action cell widgets to prevent ghost floating widgets
        for r in range(self.table.rowCount()):
            w = self.table.cellWidget(r, 6)
            if w:
                w.setParent(None)
        self.table.setRowCount(0)
        self.table.setRowCount(len(members))

        is_en = (self._current_lang == 'en')

        for row_idx, m in enumerate(members):
            # 0. Code (Blue mono font)
            item_code = QTableWidgetItem(m.member_code)
            item_code.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            item_code.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
            item_code.setForeground(QColor("#2563EB"))
            self.table.setItem(row_idx, 0, item_code)

            # 1. Full Name
            name_text = m.full_name or ""
            if m.surname and m.surname not in name_text:
                name_text = f"{m.full_name} ({m.surname})"
            item_name = QTableWidgetItem(name_text)
            item_name.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            item_name.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            item_name.setForeground(QColor("#0F172A"))
            self.table.setItem(row_idx, 1, item_name)

            # 2. Father's Name
            item_father = QTableWidgetItem(m.father_name or "—")
            item_father.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            item_father.setFont(QFont("Segoe UI", 10))
            item_father.setForeground(QColor("#334155"))
            self.table.setItem(row_idx, 2, item_father)

            # 3. Mobile
            item_mobile = QTableWidgetItem(m.mobile or "—")
            item_mobile.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            item_mobile.setFont(QFont("Consolas", 10))
            item_mobile.setForeground(QColor("#334155"))
            self.table.setItem(row_idx, 3, item_mobile)

            # 4. City (Clean aligned native cell)
            default_city = "Gujarat" if is_en else "ગુજરાત"
            raw_city = m.city or default_city
            disp_city = CITY_TRANSLATIONS.get(raw_city, raw_city) if is_en else raw_city
            item_city = QTableWidgetItem(disp_city)
            item_city.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            item_city.setFont(QFont("Segoe UI", 10))
            item_city.setForeground(QColor("#334155"))
            self.table.setItem(row_idx, 4, item_city)

            # 5. Status (Emerald bold centered text)
            status_text = "●  Verified" if is_en else "●  ચકાસાયેલ"
            item_status = QTableWidgetItem(status_text)
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_status.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            item_status.setForeground(QColor("#059669"))
            self.table.setItem(row_idx, 5, item_status)

            # 6. Action buttons: 👁 View, ✏️ Edit, 🖨 Print
            act_widget = QWidget()
            act_layout = QHBoxLayout(act_widget)
            act_layout.setContentsMargins(4, 2, 4, 2)
            act_layout.setSpacing(6)
            act_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            tip_view = "View Member Details" if is_en else "સભ્ય વિગત જુઓ"
            tip_edit = "Edit Member" if is_en else "સુધારો કરો"
            tip_print = "Print Form / ID Card" if is_en else "ફોર્મ / આઈડી કાર્ડ છાપો"

            btn_view = QPushButton("👁")
            btn_view.setToolTip(tip_view)
            btn_view.setFixedSize(30, 30)
            btn_view.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_view.setStyleSheet("""
                QPushButton {
                    background-color: #EFF6FF;
                    color: #2563EB;
                    border: 1px solid #BFDBFE;
                    border-radius: 6px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #DBEAFE;
                }
                QToolTip {
                    background-color: #0F172A;
                    color: #FFFFFF;
                    border: 1px solid #334155;
                    border-radius: 6px;
                    padding: 5px 9px;
                    font-size: 11px;
                }
            """)
            btn_view.clicked.connect(lambda _, mid=m.id: self._nav("profile", member_id=mid))

            btn_edit = QPushButton("✏️")
            btn_edit.setToolTip(tip_edit)
            btn_edit.setFixedSize(30, 30)
            btn_edit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #ECFDF5;
                    color: #059669;
                    border: 1px solid #A7F3D0;
                    border-radius: 6px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #D1FAE5;
                }
                QToolTip {
                    background-color: #0F172A;
                    color: #FFFFFF;
                    border: 1px solid #334155;
                    border-radius: 6px;
                    padding: 5px 9px;
                    font-size: 11px;
                }
            """)
            btn_edit.clicked.connect(lambda _, mid=m.id: self._nav("edit", member_id=mid))

            btn_print = QPushButton("🖨")
            btn_print.setToolTip(tip_print)
            btn_print.setFixedSize(30, 30)
            btn_print.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_print.setStyleSheet("""
                QPushButton {
                    background-color: #F5F3FF;
                    color: #7C3AED;
                    border: 1px solid #DDD6FE;
                    border-radius: 6px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #EDE9FE;
                }
                QToolTip {
                    background-color: #0F172A;
                    color: #FFFFFF;
                    border: 1px solid #334155;
                    border-radius: 6px;
                    padding: 5px 9px;
                    font-size: 11px;
                }
            """)
            btn_print.clicked.connect(lambda _, mid=m.id: self._nav("form_preview", member_id=mid))

            act_layout.addWidget(btn_view)
            act_layout.addWidget(btn_edit)
            act_layout.addWidget(btn_print)
            act_layout.addStretch()

            self.table.setCellWidget(row_idx, 6, act_widget)
            self.table.setRowHeight(row_idx, 46)

    def _export_summary_report(self):
        """Export all registered members to CSV report."""
        ensure_dirs()
        members = self._member_svc.get_all(offset=0, limit=50000)
        is_en = (self._current_lang == 'en')
        if not members:
            msg = "No members available to export." if is_en else "કોઈ સભ્યો ઉપલબ્ધ નથી."
            QMessageBox.information(self, "Export Report" if is_en else "રિપોર્ટ ડાઉનલોડ", msg)
            return

        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M")
        default_path = os.path.join(EXPORT_DIR, f"Gujarat_Brahm_Samaj_Members_{timestamp}.csv")
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Member Report" if is_en else "સભ્ય રિપોર્ટ સેવ કરો",
            default_path,
            "CSV Files (*.csv)"
        )
        if not save_path:
            return

        try:
            with open(save_path, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                if is_en:
                    writer.writerow([
                        "Member Code", "Full Name", "Surname", "Father Name", "Mobile No",
                        "Address", "City", "District", "Pincode", "Blood Group",
                        "Occupation", "Education", "Samaj", "Membership Fee", "Registration Date"
                    ])
                else:
                    writer.writerow([
                        "સભ્ય કોડ", "પૂરું નામ", "અટક", "પિતાનું નામ", "મોબાઇલ નં.",
                        "સરનામું", "શહેર", "જિલ્લો", "પિનકોડ", "બ્લડ ગ્રૂપ",
                        "ધંધો/વ્યવસાય", "અભ્યાસ", "સમાજ", "સભ્ય ફી", "નોંધણી તારીખ"
                    ])
                for m in members:
                    writer.writerow([
                        m.member_code, m.full_name, m.surname or "", m.father_name or "",
                        m.mobile or "", m.address or "", m.city or "", m.district or "",
                        m.pincode or "", m.blood_group or "", m.occupation or "",
                        m.education or "", m.samaj or "", m.membership_fee or "",
                        m.created_at or ""
                    ])
            success_msg = (
                f"Member report downloaded successfully!\n\nPath:\n{save_path}"
                if is_en else
                f"સભ્ય રિપોર્ટ સફળતાપૂર્વક ડાઉનલોડ થયો છે!\n\nસ્થાન:\n{save_path}"
            )
            QMessageBox.information(
                self, "Report Downloaded" if is_en else "રિપોર્ટ સફળ",
                success_msg
            )
        except Exception as exc:
            err_title = "Error" if is_en else "ભૂલ"
            err_msg = f"Error saving report: {exc}" if is_en else f"રિપોર્ટ સેવ કરતી વખતે ભૂલ આવી: {exc}"
            QMessageBox.critical(self, err_title, err_msg)

    def set_language(self, lang: str):
        """Update dashboard text dynamically when language changes."""
        self._current_lang = lang
        from app.translations import t

        # Banner
        if hasattr(self, 'flag_badge'):
            self.flag_badge.setText(t('dash_welcome_badge', lang))
        if hasattr(self, 'hero_title'):
            self.hero_title.setText(t('dash_welcome_title', lang))
        if hasattr(self, 'hero_subtitle'):
            self.hero_subtitle.setText(t('dash_welcome_sub', lang))
        if hasattr(self, 'btn_download_report'):
            self.btn_download_report.setText(t('dash_btn_report', lang))
        if hasattr(self, 'btn_banner_register'):
            self.btn_banner_register.setText(t('dash_btn_register', lang))

        # KPI Cards (titles, badges, subtexts)
        if hasattr(self, 'card_total'):
            if hasattr(self.card_total, 'title_lbl'):
                self.card_total.title_lbl.setText(t('dash_kpi_total', lang))
            if hasattr(self.card_total, 'badge_lbl'):
                self.card_total.badge_lbl.setText(t('dash_badge_total', lang))
            if hasattr(self.card_total, 'sub_lbl'):
                self.card_total.sub_lbl.setText(t('dash_sub_total', lang))

        if hasattr(self, 'card_today'):
            if hasattr(self.card_today, 'title_lbl'):
                self.card_today.title_lbl.setText(t('dash_kpi_today', lang))
            if hasattr(self.card_today, 'badge_lbl'):
                self.card_today.badge_lbl.setText(t('dash_badge_today', lang))
            if hasattr(self.card_today, 'sub_lbl'):
                self.card_today.sub_lbl.setText(t('dash_sub_today', lang))

        if hasattr(self, 'card_family'):
            if hasattr(self.card_family, 'title_lbl'):
                self.card_family.title_lbl.setText(t('dash_kpi_families', lang))
            if hasattr(self.card_family, 'badge_lbl'):
                self.card_family.badge_lbl.setText(t('dash_badge_family', lang))
            if hasattr(self.card_family, 'sub_lbl'):
                self.card_family.sub_lbl.setText(t('dash_sub_family', lang))

        if hasattr(self, 'card_issued'):
            if hasattr(self.card_issued, 'title_lbl'):
                self.card_issued.title_lbl.setText(t('dash_kpi_idcards', lang))
            if hasattr(self.card_issued, 'badge_lbl'):
                self.card_issued.badge_lbl.setText(t('dash_badge_issued', lang))
            if hasattr(self.card_issued, 'sub_lbl'):
                self.card_issued.sub_lbl.setText(t('dash_sub_issued', lang))

        # Launchpad
        if hasattr(self, 'sec_launchpad_title'):
            self.sec_launchpad_title.setText(t('dash_quick_launchpad', lang))
        if hasattr(self, 'sec_launchpad_sub'):
            self.sec_launchpad_sub.setText(t('dash_quick_launchpad_sub', lang))

        if hasattr(self, 'launch_card1'):
            if hasattr(self.launch_card1, 'title_lbl'):
                self.launch_card1.title_lbl.setText(t('dash_action1_title', lang))
            if hasattr(self.launch_card1, 'sub_lbl'):
                self.launch_card1.sub_lbl.setText(t('dash_action1_sub', lang))
            if hasattr(self.launch_card1, 'badge_lbl'):
                self.launch_card1.badge_lbl.setText(t('dash_action1_badge', lang))

        if hasattr(self, 'launch_card2'):
            if hasattr(self.launch_card2, 'title_lbl'):
                self.launch_card2.title_lbl.setText(t('dash_action2_title', lang))
            if hasattr(self.launch_card2, 'sub_lbl'):
                self.launch_card2.sub_lbl.setText(t('dash_action2_sub', lang))
            if hasattr(self.launch_card2, 'badge_lbl'):
                self.launch_card2.badge_lbl.setText(t('dash_action2_badge', lang))

        if hasattr(self, 'launch_card3'):
            if hasattr(self.launch_card3, 'title_lbl'):
                self.launch_card3.title_lbl.setText(t('dash_action3_title', lang))
            if hasattr(self.launch_card3, 'sub_lbl'):
                self.launch_card3.sub_lbl.setText(t('dash_action3_sub', lang))
            if hasattr(self.launch_card3, 'badge_lbl'):
                self.launch_card3.badge_lbl.setText(t('dash_action3_badge', lang))

        # Table & Controls
        if hasattr(self, 'tbl_title'):
            self.tbl_title.setText(t('dash_recent_table_title', lang))
        if hasattr(self, 'filter_input'):
            self.filter_input.setPlaceholderText(t('dash_filter_placeholder', lang))
        if hasattr(self, 'btn_filters'):
            self.btn_filters.setText(t('dash_btn_filters', lang))

        if hasattr(self, 'city_combo'):
            cities = self._member_svc.get_distinct_cities()
            curr_data = self.city_combo.currentData()
            self.city_combo.blockSignals(True)
            self.city_combo.clear()
            self.city_combo.addItem(t('dash_all_cities', lang), "")
            for c in cities:
                disp = CITY_TRANSLATIONS.get(c, c) if lang == 'en' else c
                self.city_combo.addItem(disp, c)
            if curr_data:
                idx = self.city_combo.findData(curr_data)
                if idx >= 0:
                    self.city_combo.setCurrentIndex(idx)
            self.city_combo.blockSignals(False)

        if hasattr(self, 'table'):
            if lang == 'en':
                self.table.setHorizontalHeaderLabels([
                    "Member Code", "Full Name", "Father / Guardian",
                    "Mobile Number", "City", "Status", "Actions"
                ])
            else:
                self.table.setHorizontalHeaderLabels([
                    "સભ્ય કોડ", "સભ્યનું પૂરું નામ", "પિતા / વાલીનું નામ",
                    "મોબાઇલ નંબર", "શહેર", "સ્થિતિ", "કાર્ય"
                ])

        # Refresh subtitle and re-populate table to refresh cell values & action tooltips
        try:
            total_members = self._member_svc.count()
            if hasattr(self, 'tbl_subtitle'):
                if lang == 'en':
                    self.tbl_subtitle.setText(f"List of recently registered members out of total {total_members:,} members")
                else:
                    self.tbl_subtitle.setText(f"કુલ {total_members:,} સભ્યોમાંથી છેલ્લા નોંધાયેલા સભ્યોની યાદી")
            self._apply_table_filters()
        except Exception:
            pass
