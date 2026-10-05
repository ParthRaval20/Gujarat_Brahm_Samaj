"""
Member Registration & Edit Form — Authentically matching the official
'સભ્ય નોંધણી ફોર્મ' of 'શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સા.કાં.'

Layout & Fields:
- Official letterhead with logo, title, address, and centered 'સભ્ય નોંધણી ફોર્મ' banner
- Form Meta: ફોર્મ નં. (Form No.) & તારીખ (Date)
- Numbered Personal Info Section (૧ થી ૭ ક્રમાંકિત વિગતો):
    (૧) પુરુ નામ (અટક પહેલા લખવી)
    (૨) પત્ર વ્યવહારનું સરનામું (પીન કોડ નં. સહિત) + શહેર, જિલ્લો, રાજ્ય, પીનકોડ
    (૩) ઈ-મેઈલ  |  મોબાઈલ નં.  |  ફોન નં.
    (૪) ધંધો / વ્યવસાય
    (૫) અભ્યાસ  |  (૬) બ્લડ ગૃપ
    (૭) સમાજ
    સભ્ય ફી મળેલ છે  |  ફોર્મ ભરનારની સહી (Text + Signature Image)
- પરિવારની માહિતી Section:
    8-column official family members table (ક્રમ, નામ, સબંધ, ઉંમર, અભ્યાસ, બ્લડ ગૃપ, વ્યવસાય, કોન્ટેક નંબર)
- Action Bars:
    💾 સભ્ય સાચવો (Save)
    📄 પીડીએફ બનાવો (Generate PDF)
    🖨️ પ્રિન્ટ ફોર્મ (Print Form)
    👁️ ફોર્મ પ્રીવ્યૂ (Preview Form)
    ✖ રદ કરો (Cancel)
"""

from __future__ import annotations

import os
import shutil
from datetime import date
from typing import Any

from PySide6.QtCore import Qt, QDate, QRegularExpression
from PySide6.QtGui import (
    QPixmap, QCursor, QFont, QPainter, QPageSize,
    QRegularExpressionValidator,
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QPlainTextEdit, QComboBox, QDateEdit,
    QScrollArea, QFrame, QGridLayout, QMessageBox, QFileDialog,
    QCompleter,
)
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

from app.config import (
    BLOOD_GROUPS, COLOR_PRIMARY, COLOR_PRIMARY_DARK,
    COLOR_BG, COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    COLOR_ACCENT_BLUE, LOGO_PATH, EXPORT_DIR, DATA_DIR, ensure_dirs,
    EDUCATION_PRESETS_GU, EDUCATION_PRESETS_EN,
)
from database.connection import get_session
from database.models import AppSetting
from services.member_service import MemberService
from services.family_service import FamilyService
from services.form_service import build_form_data
from services.form_renderer import FormRenderer
from services.pdf_service import generate_form_pdf
from ui.widgets.family_table_widget import FamilyTableWidget
from utils.file_utils import get_pdf_filename

# 8 Official Talukas of Sabarkantha District
SABARKANTHA_TALUKAS: list[tuple[str, str]] = [
    ("ઇડર", "Idar"),
    ("હિંમતનગર", "Himatnagar"),
    ("પ્રાંતિજ", "Prantij"),
    ("તલોદ", "Talod"),
    ("ખેડબ્રહ્મા", "Khedbrahma"),
    ("વડાલી", "Vadali"),
    ("વિજયનગર", "Vijaynagar"),
    ("પોશીના", "Poshina"),
]


class MemberFormPage(QWidget):
    def __init__(self, nav_callback, on_data_updated=None, parent=None):
        super().__init__(parent)
        self._nav = nav_callback
        self._on_data_updated = on_data_updated
        self._current_lang: str = 'gu'
        self._editing_id: int | None = None
        self._signature_image_path: str = ''
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── 1. Top Action Bar ──────────────────────────────────────────
        top_bar = QFrame()
        top_bar.setFixedHeight(64)
        top_bar.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-bottom: 1px solid {COLOR_BORDER};
            }}
        """)
        tb_layout = QHBoxLayout(top_bar)
        tb_layout.setContentsMargins(28, 10, 28, 10)
        tb_layout.setSpacing(10)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)

        self.title_label = QLabel("➕  સભ્ય નોંધણી ફોર્મ (Add Member)")
        self.title_label.setStyleSheet(f"font-size: 16px; font-weight: 800; color: #1B2F8A; border: none;")

        self.subtitle_label = QLabel("શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સા.કાં. — સત્તાવાર સભ્યપદ નોંધણી")
        self.subtitle_label.setStyleSheet(f"font-size: 11px; font-weight: 500; color: {COLOR_TEXT_MUTED}; border: none;")

        title_vbox.addWidget(self.title_label)
        title_vbox.addWidget(self.subtitle_label)
        tb_layout.addLayout(title_vbox)

        tb_layout.addStretch()

        self.btn_top_cancel  = QPushButton("✖ રદ કરો")
        self.btn_top_preview = QPushButton("👁️  પ્રીવ્યૂ")
        self.btn_top_print   = QPushButton("🖨️  પ્રિન્ટ")
        self.btn_top_pdf     = QPushButton("📄  પીડીએફ")
        self.btn_top_save    = QPushButton("💾  સભ્ય સાચવો")

        for btn in (self.btn_top_cancel, self.btn_top_preview, self.btn_top_print, self.btn_top_pdf, self.btn_top_save):
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFixedHeight(38)

        self.btn_top_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF; color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER}; border-radius: 8px;
                padding: 0 14px; font-size: 12px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #F1F5F9; }}
        """)

        self.btn_top_preview.setStyleSheet("""
            QPushButton {
                background-color: #F5F3FF; color: #7C3AED;
                border: 1px solid #DDD6FE; border-radius: 8px;
                padding: 0 14px; font-size: 12px; font-weight: 700;
            }
            QPushButton:hover { background-color: #EDE9FE; }
        """)

        self.btn_top_print.setStyleSheet("""
            QPushButton {
                background-color: #ECFDF5; color: #059669;
                border: 1px solid #A7F3D0; border-radius: 8px;
                padding: 0 14px; font-size: 12px; font-weight: 700;
            }
            QPushButton:hover { background-color: #D1FAE5; }
        """)

        self.btn_top_pdf.setStyleSheet("""
            QPushButton {
                background-color: #EFF6FF; color: #2563EB;
                border: 1px solid #BFDBFE; border-radius: 8px;
                padding: 0 14px; font-size: 12px; font-weight: 700;
            }
            QPushButton:hover { background-color: #DBEAFE; }
        """)

        self.btn_top_save.setStyleSheet("""
            QPushButton {
                background-color: #1B2F8A; color: #FFFFFF;
                border: none; border-radius: 8px;
                padding: 0 20px; font-size: 12px; font-weight: 800;
            }
            QPushButton:hover { background-color: #142268; }
        """)

        tb_layout.addWidget(self.btn_top_cancel)
        tb_layout.addWidget(self.btn_top_preview)
        tb_layout.addWidget(self.btn_top_print)
        tb_layout.addWidget(self.btn_top_pdf)
        tb_layout.addWidget(self.btn_top_save)

        outer.addWidget(top_bar)

        # ── 2. Scroll Area for Form Sheet ────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background-color: {COLOR_BG}; border: none; }}")
        outer.addWidget(scroll)

        scroll_content = QWidget()
        scroll_content.setStyleSheet(f"background-color: {COLOR_BG};")
        scroll.setWidget(scroll_content)

        center_layout = QVBoxLayout(scroll_content)
        center_layout.setContentsMargins(28, 20, 28, 28)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # ── 3. Main Form Paper Sheet Card ────────────────────────────
        # Designed like the authentic physical document
        paper_card = QFrame()
        paper_card.setMinimumWidth(880)
        paper_card.setMaximumWidth(1060)
        paper_card.setStyleSheet("""
            QFrame#paper_card {
                background-color: #FFFFFF;
                border: 2px solid #1B2F8A;
                border-radius: 12px;
            }
        """)
        paper_card.setObjectName("paper_card")

        form_vbox = QVBoxLayout(paper_card)
        form_vbox.setContentsMargins(26, 22, 26, 26)
        form_vbox.setSpacing(16)

        # ── Letterhead Header ─────────────────────────────────────────
        hdr_frame = QFrame()
        hdr_frame.setObjectName("hdr_frame")
        hdr_frame.setStyleSheet("""
            QFrame#hdr_frame {
                background-color: #F8FAFC;
                border: 1px solid #D0D5E8;
                border-radius: 10px;
            }
        """)
        hdr_layout = QHBoxLayout(hdr_frame)
        hdr_layout.setContentsMargins(16, 12, 16, 12)
        hdr_layout.setSpacing(16)

        # Parshuram Logo (No clipping/cutting)
        logo_lbl = QLabel()
        logo_lbl.setFixedSize(85, 85)
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setContentsMargins(0, 0, 0, 0)
        if os.path.exists(LOGO_PATH):
            pix = QPixmap(LOGO_PATH)
            if not pix.isNull():
                logo_lbl.setPixmap(pix.scaled(85, 85, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_lbl.setStyleSheet("border: none; background: transparent; padding: 0px;")
        hdr_layout.addWidget(logo_lbl)

        # Org Title & Address & Banner
        title_box = QVBoxLayout()
        title_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_box.setSpacing(4)

        # Top Hanging Banner
        self.banner_lbl = QLabel("સભ્ય નોંધણી ફોર્મ")
        self.banner_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.banner_lbl.setFixedHeight(30)
        self.banner_lbl.setFixedWidth(240)
        self.banner_lbl.setStyleSheet("""
            background-color: #1B2F8A;
            color: #FFFFFF;
            font-size: 14px;
            font-weight: 800;
            border-radius: 6px;
            padding: 2px 10px;
        """)

        self.org_name_lbl = QLabel("શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સા.કાં.")
        self.org_name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.org_name_lbl.setStyleSheet("font-size: 19px; font-weight: 800; color: #1B2F8A; border: none;")

        self.org_addr_lbl = QLabel("એફ.એફ-૧૧૪, પહેલો માળ, શૈવ કૉમ્પ્લેક્સ, દામોદર એરિયા, સત્યમ હોસ્પિટલની સામે, ઇડર.")
        self.org_addr_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.org_addr_lbl.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {COLOR_TEXT_MUTED}; border: none;")

        b_center_h = QHBoxLayout()
        b_center_h.addStretch()
        b_center_h.addWidget(self.banner_lbl)
        b_center_h.addStretch()

        title_box.addLayout(b_center_h)
        title_box.addWidget(self.org_name_lbl)
        title_box.addWidget(self.org_addr_lbl)

        hdr_layout.addLayout(title_box)
        hdr_layout.addSpacing(80) # balance logo
        form_vbox.addWidget(hdr_frame)

        # ── Form Meta Bar: ફોર્મ ક્રમાંક & તારીખ (Line 1 of Official Form) ──
        meta_bar = QFrame()
        meta_bar.setStyleSheet("""
            QFrame {
                background-color: #EFF6FF;
                border: 1px solid #BFDBFE;
                border-radius: 8px;
                padding: 6px 16px;
            }
        """)
        mb_layout = QHBoxLayout(meta_bar)
        mb_layout.setContentsMargins(12, 6, 12, 6)
        mb_layout.setSpacing(20)

        self.fn_lbl = QLabel("ફોર્મ ક્રમાંક :")
        self.fn_lbl.setStyleSheet("font-size: 13px; font-weight: 800; color: #1B2F8A; border: none;")
        self.form_no_edit = QLineEdit()
        self.form_no_edit.setPlaceholderText("દા.ત. GBS-000001")
        self.form_no_edit.setFixedWidth(150)
        self.form_no_edit.setFixedHeight(34)
        self.form_no_edit.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF; color: #1B2F8A;
                font-weight: 800; font-size: 13px;
                border: 1px solid #93C5FD; border-radius: 6px;
                padding: 0 10px;
            }
        """)

        self.dt_lbl = QLabel("તારીખ :")
        self.dt_lbl.setStyleSheet("font-size: 13px; font-weight: 800; color: #1B2F8A; border: none;")
        self.form_date_edit = QDateEdit()
        self.form_date_edit.setCalendarPopup(True)
        self.form_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.form_date_edit.setDate(QDate.currentDate())
        self.form_date_edit.setFixedWidth(140)
        self.form_date_edit.setFixedHeight(34)
        self.form_date_edit.setStyleSheet("""
            QDateEdit {
                background-color: #FFFFFF; color: #1E293B;
                font-size: 12px; font-weight: 700;
                border: 1px solid #93C5FD; border-radius: 6px;
                padding: 0 10px;
            }
        """)

        mb_layout.addWidget(self.fn_lbl)
        mb_layout.addWidget(self.form_no_edit)
        mb_layout.addStretch()
        mb_layout.addWidget(self.dt_lbl)
        mb_layout.addWidget(self.form_date_edit)
        form_vbox.addWidget(meta_bar)

        # ── Helpers for form row builders ─────────────────────────────
        def f_label(text: str) -> QLabel:
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 12px; font-weight: 700; color: #1B2F8A;")
            return lbl

        def f_input(placeholder: str = "") -> QLineEdit:
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setFixedHeight(36)
            inp.setStyleSheet(f"""
                QLineEdit {{
                    background-color: #F8FAFC;
                    color: {COLOR_TEXT_MAIN};
                    border: 1px solid {COLOR_BORDER};
                    border-radius: 6px;
                    padding: 0 12px;
                    font-size: 12px;
                }}
                QLineEdit:focus {{
                    background-color: #FFFFFF;
                    border: 1.5px solid {COLOR_PRIMARY};
                }}
            """)
            return inp

        def f_badge(num_text: str) -> QLabel:
            b = QLabel(num_text)
            b.setFixedSize(22, 22)
            b.setAlignment(Qt.AlignmentFlag.AlignCenter)
            b.setStyleSheet("""
                QLabel {
                    background-color: #1B2F8A;
                    color: #FFFFFF;
                    font-size: 11px;
                    font-weight: 800;
                    border-radius: 11px;
                }
            """)
            return b

        def f_badged_label(badge_lbl: QLabel, text_lbl: QLabel, width: int = 190) -> QWidget:
            w = QWidget()
            w.setFixedWidth(width)
            w.setStyleSheet("background: transparent; border: none;")
            h = QHBoxLayout(w)
            h.setContentsMargins(0, 0, 0, 0)
            h.setSpacing(8)
            h.addWidget(badge_lbl)
            h.addWidget(text_lbl)
            h.addStretch()
            return w

        # ── SECTION 1: સભ્યની વ્યક્તિગત માહિતી (Member's Personal Information) ──
        sec1_frame = QFrame()
        sec1_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 10px;
            }
        """)
        sec1_layout = QVBoxLayout(sec1_frame)
        sec1_layout.setContentsMargins(18, 16, 18, 18)
        sec1_layout.setSpacing(14)

        sec1_hdr = QHBoxLayout()
        self.s1_title = QLabel("૧. સભ્યની વ્યક્તિગત માહિતી")
        self.s1_title.setFixedHeight(30)
        self.s1_title.setStyleSheet("""
            background-color: #1B2F8A;
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 800;
            border-radius: 6px;
            padding: 4px 14px;
        """)
        self.s1_req = QLabel("* ફરજિયાત ક્ષેત્ર")
        self.s1_req.setStyleSheet("font-size: 11px; font-weight: 600; color: #EF4444; border: none;")
        sec1_hdr.addWidget(self.s1_title)
        sec1_hdr.addStretch()
        sec1_hdr.addWidget(self.s1_req)
        sec1_layout.addLayout(sec1_hdr)

        grid1 = QGridLayout()
        grid1.setHorizontalSpacing(14)
        grid1.setVerticalSpacing(12)
        grid1.setColumnStretch(0, 0)
        grid1.setColumnStretch(1, 1)
        grid1.setColumnStretch(2, 0)
        grid1.setColumnStretch(3, 1)

        # Line 1: Badge ૧ + પૂર્ણ નામ (અટક પહેલાં લખવી)
        self.badge_1 = f_badge("૧")
        self.lbl_fullname = f_label("પૂર્ણ નામ (અટક પહેલાં લખવી) *")
        grid1.addWidget(f_badged_label(self.badge_1, self.lbl_fullname, width=190), 0, 0)
        self.fullname_edit = f_input("અટક પહેલાં લખવી — દા.ત. જોષી હર્ષદભાઈ રમણિકલાલ *")
        grid1.addWidget(self.fullname_edit, 0, 1, 1, 3)

        # Line 2: Badge ૨ + રહેઠાણનું સરનામું
        self.badge_2 = f_badge("૨")
        self.lbl_address = f_label("રહેઠાણનું સરનામું *")
        grid1.addWidget(f_badged_label(self.badge_2, self.lbl_address, width=190), 1, 0)
        self.address_edit = QPlainTextEdit()
        self.address_edit.setPlaceholderText("ઘર નં., ફ્લેટ/સોસાયટી, શેરી, વિસ્તાર... *")
        self.address_edit.setFixedHeight(64)
        self.address_edit.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: #F8FAFC;
                color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
            }}
            QPlainTextEdit:focus {{
                background-color: #FFFFFF;
                border: 1.5px solid {COLOR_PRIMARY};
            }}
        """)
        grid1.addWidget(self.address_edit, 1, 1, 1, 3)

        # Address Detail Helpers (Taluka Dropdown, Fixed Sabarkantha District, State, Pincode)
        self.lbl_city_dist = f_label("તાલુકો & જિલ્લો")
        self.lbl_city_dist.setFixedWidth(190)
        self.lbl_city_dist.setStyleSheet("font-size: 12px; font-weight: 700; color: #1B2F8A; padding-left: 30px;")
        grid1.addWidget(self.lbl_city_dist, 2, 0)
        addr_row1 = QHBoxLayout()
        addr_row1.setSpacing(10)

        # Taluka Dropdown with all 8 talukas of Sabarkantha
        self.taluka_combo = QComboBox()
        self.taluka_combo.setEditable(True)
        self.taluka_combo.setFixedHeight(36)
        self.taluka_combo.setMinimumWidth(130)
        self.taluka_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #F8FAFC;
                color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 0 10px;
                font-size: 12px;
                font-weight: 600;
            }}
            QComboBox:focus {{
                background-color: #FFFFFF;
                border: 1.5px solid {COLOR_PRIMARY};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid {COLOR_BORDER};
            }}
            QComboBox QAbstractItemView {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER};
                selection-background-color: {COLOR_PRIMARY};
                selection-color: #FFFFFF;
                font-size: 12px;
            }}
        """)
        self._populate_talukas(is_en=False, keep_current=False)
        self.city_edit = self.taluka_combo.lineEdit()

        # Fixed District: Sabarkantha / સાબરકાંઠા
        self.district_edit = f_input("જિલ્લો")
        self.district_edit.setText("સાબરકાંઠા")
        self.district_edit.setReadOnly(True)
        self.district_edit.setToolTip("જિલ્લો: સાબરકાંઠા (Fixed)")
        self.district_edit.setMinimumWidth(95)
        self.district_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: #F1F5F9;
                color: #1E293B;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 0 8px;
                font-size: 12px;
                font-weight: 700;
            }}
        """)

        addr_row1.addWidget(self.taluka_combo, stretch=3)
        addr_row1.addWidget(self.district_edit, stretch=2)
        grid1.addLayout(addr_row1, 2, 1)

        self.lbl_state_pin = f_label("રાજ્ય & પીન કોડ નં. *")
        self.lbl_state_pin.setFixedWidth(145)
        grid1.addWidget(self.lbl_state_pin, 2, 2)
        addr_row2 = QHBoxLayout()
        addr_row2.setSpacing(10)
        self.state_edit = f_input("રાજ્ય")
        self.state_edit.setText("ગુજરાત")
        self.state_edit.setReadOnly(True)
        self.state_edit.setMinimumWidth(85)
        self.state_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: #F1F5F9;
                color: #1E293B;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 0 8px;
                font-size: 12px;
                font-weight: 700;
            }}
        """)
        self.pincode_edit = f_input("પીન કોડ (૬ અંક) *")
        self.pincode_edit.setMaxLength(6)
        self.pincode_edit.setMinimumWidth(110)
        self.pincode_edit.setValidator(QRegularExpressionValidator(QRegularExpression(r"^\d{0,6}$")))
        addr_row2.addWidget(self.state_edit, stretch=2)
        addr_row2.addWidget(self.pincode_edit, stretch=3)
        grid1.addLayout(addr_row2, 2, 3)

        # Line 3: Badge ૩ + ગામનું સરનામું (Native Village Address)
        self.badge_3 = f_badge("૩")
        self.lbl_village_address = f_label("ગામનું સરનામું")
        grid1.addWidget(f_badged_label(self.badge_3, self.lbl_village_address, width=190), 3, 0)
        self.village_address_edit = f_input("ગામ / મૂળ વતનનું સરનામું")
        grid1.addWidget(self.village_address_edit, 3, 1, 1, 3)

        # Line 4: Badge ૪ + ઈ-મેલ આઈડી & Badge ૫ + શિક્ષણ
        self.badge_4 = f_badge("૪")
        self.lbl_email = f_label("ઈ-મેલ આઈડી")
        grid1.addWidget(f_badged_label(self.badge_4, self.lbl_email, width=190), 4, 0)
        self.email_edit = f_input("example@domain.com")
        grid1.addWidget(self.email_edit, 4, 1)

        self.badge_5 = f_badge("૫")
        self.lbl_edu = f_label("શિક્ષણ")
        grid1.addWidget(f_badged_label(self.badge_5, self.lbl_edu, width=145), 4, 2)

        # Education Dropdown with presets + smart autocomplete + free typing
        self.edu_combo = QComboBox()
        self.edu_combo.setEditable(True)
        self.edu_combo.setFixedHeight(36)
        self.edu_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #F8FAFC;
                color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 0 10px;
                font-size: 12px;
                font-weight: 600;
            }}
            QComboBox:focus {{
                background-color: #FFFFFF;
                border: 1.5px solid {COLOR_PRIMARY};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid {COLOR_BORDER};
            }}
            QComboBox QAbstractItemView {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER};
                selection-background-color: {COLOR_PRIMARY};
                selection-color: #FFFFFF;
                font-size: 12px;
            }}
        """)
        self._populate_education_presets(is_en=False, keep_current=False)
        self.edu_edit = self.edu_combo.lineEdit()
        grid1.addWidget(self.edu_combo, 4, 3)

        # Line 5: Badge ૬ + મોબાઇલ નંબર & ફોન નંબર
        self.badge_6 = f_badge("૬")
        self.lbl_contact = f_label("મોબાઇલ & ફોન નં. *")
        grid1.addWidget(f_badged_label(self.badge_6, self.lbl_contact, width=190), 5, 0)
        contact_row = QHBoxLayout()
        contact_row.setSpacing(8)
        self.flag_lbl = QLabel("🇮🇳 +91")
        self.flag_lbl.setFixedHeight(36)
        self.flag_lbl.setStyleSheet("background-color: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px; padding: 0 6px; font-size: 11px; font-weight: 700; color: #475569;")
        self.mobile_edit = f_input("૧૦ અંકનો મોબાઈલ નં. *")
        self.mobile_edit.setMaxLength(10)
        self.mobile_edit.setValidator(QRegularExpressionValidator(QRegularExpression(r"^\d{0,10}$")))
        self.phone_edit  = f_input("૧૦ અંકનો ફોન / લેન્ડલાઇન")
        self.phone_edit.setMaxLength(10)
        self.phone_edit.setValidator(QRegularExpressionValidator(QRegularExpression(r"^\d{0,10}$")))
        contact_row.addWidget(self.flag_lbl)
        contact_row.addWidget(self.mobile_edit)
        contact_row.addWidget(self.phone_edit)
        grid1.addLayout(contact_row, 5, 1, 1, 3)

        # Keyboard tab order for intuitive data entry
        self.setTabOrder(self.fullname_edit, self.address_edit)
        self.setTabOrder(self.address_edit, self.taluka_combo)
        self.setTabOrder(self.taluka_combo, self.state_edit)
        self.setTabOrder(self.state_edit, self.pincode_edit)
        self.setTabOrder(self.pincode_edit, self.village_address_edit)
        self.setTabOrder(self.village_address_edit, self.email_edit)
        self.setTabOrder(self.email_edit, self.edu_combo)
        self.setTabOrder(self.edu_combo, self.mobile_edit)
        self.setTabOrder(self.mobile_edit, self.phone_edit)

        sec1_layout.addLayout(grid1)
        form_vbox.addWidget(sec1_frame)

        # ── SECTION 2: વ્યવસાય / રોજગારની માહિતી (Business / Employment) ──
        sec2_frame = QFrame()
        sec2_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 10px;
            }
        """)
        sec2_layout = QVBoxLayout(sec2_frame)
        sec2_layout.setContentsMargins(18, 16, 18, 18)
        sec2_layout.setSpacing(14)

        sec2_hdr = QHBoxLayout()
        self.s2_title = QLabel("૨. વ્યવસાય / રોજગારની માહિતી")
        self.s2_title.setFixedHeight(30)
        self.s2_title.setStyleSheet("""
            background-color: #1B2F8A;
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 800;
            border-radius: 6px;
            padding: 4px 14px;
        """)
        sec2_hdr.addWidget(self.s2_title)
        sec2_hdr.addStretch()
        sec2_layout.addLayout(sec2_hdr)

        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(14)
        grid2.setVerticalSpacing(12)
        grid2.setColumnStretch(0, 0)
        grid2.setColumnStretch(1, 1)
        grid2.setColumnStretch(2, 0)
        grid2.setColumnStretch(3, 1)

        # Line 1: Badge ૭ + ધંધો / વ્યવસાય
        self.badge_7 = f_badge("૭")
        self.lbl_occ = f_label("ધંધો / વ્યવસાય")
        grid2.addWidget(f_badged_label(self.badge_7, self.lbl_occ, width=190), 0, 0)
        self.occ_edit = f_input("નોકરી, વેપાર, સ્વતંત્ર વ્યવસાય, વગેરે...")
        grid2.addWidget(self.occ_edit, 0, 1, 1, 3)

        # Line 2: Badge ૮ + ધંધા / વ્યવસાયનું સરનામું
        self.badge_8 = f_badge("૮")
        self.lbl_biz_addr = f_label("ધંધાનું સરનામું")
        grid2.addWidget(f_badged_label(self.badge_8, self.lbl_biz_addr, width=190), 1, 0)
        self.biz_address_edit = QPlainTextEdit()
        self.biz_address_edit.setPlaceholderText("દુકાન/ઓફિસ નં., કોમ્પ્લેક્ષ, શેરી, વિસ્તાર, શહેર...")
        self.biz_address_edit.setFixedHeight(54)
        self.biz_address_edit.setStyleSheet(self.address_edit.styleSheet())
        grid2.addWidget(self.biz_address_edit, 1, 1, 1, 3)

        # Line 3: Badge ૯ + બ્લડ ગ્રુપ
        self.badge_9 = f_badge("૯")
        self.lbl_bg = f_label("બ્લડ ગ્રુપ")
        grid2.addWidget(f_badged_label(self.badge_9, self.lbl_bg, width=190), 2, 0)
        self.bg_combo = QComboBox()
        self.bg_combo.addItems(BLOOD_GROUPS)
        self.bg_combo.setFixedHeight(36)
        self.bg_combo.setFixedWidth(280)
        self.bg_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #F8FAFC; color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER}; border-radius: 6px;
                padding: 0 8px; font-size: 12px; font-weight: 600;
            }}
        """)
        grid2.addWidget(self.bg_combo, 2, 1, 1, 3)

        # Retain internal fields for backwards compatibility with tests and database
        self.income_edit = f_input("")
        self.income_edit.hide()

        sec2_layout.addLayout(grid2)
        form_vbox.addWidget(sec2_frame)

        # ── SECTION 3: સમાજની માહિતી (Samaj Information) ────────────────
        sec3_frame = QFrame()
        sec3_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 10px;
            }
        """)
        sec3_layout = QVBoxLayout(sec3_frame)
        sec3_layout.setContentsMargins(18, 16, 18, 18)
        sec3_layout.setSpacing(14)

        sec3_hdr = QHBoxLayout()
        self.s3_title = QLabel("૩. સમાજની માહિતી")
        self.s3_title.setFixedHeight(30)
        self.s3_title.setStyleSheet("""
            background-color: #1B2F8A;
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 800;
            border-radius: 6px;
            padding: 4px 14px;
        """)
        sec3_hdr.addWidget(self.s3_title)
        sec3_hdr.addStretch()
        sec3_layout.addLayout(sec3_hdr)

        grid3 = QGridLayout()
        grid3.setHorizontalSpacing(14)
        grid3.setVerticalSpacing(12)
        grid3.setColumnStretch(0, 0)
        grid3.setColumnStretch(1, 1)
        grid3.setColumnStretch(2, 0)
        grid3.setColumnStretch(3, 1)

        # Line 1: Badge ૧૦ + સમાજ
        self.badge_10 = f_badge("૧૦")
        self.lbl_samaj = f_label("સમાજ")
        grid3.addWidget(f_badged_label(self.badge_10, self.lbl_samaj, width=190), 0, 0)
        self.samaj_edit = f_input("ગુજરાત બ્રહ્મ સમાજ")
        self.samaj_edit.setText("ગુજરાત બ્રહ્મ સમાજ")
        grid3.addWidget(self.samaj_edit, 0, 1, 1, 3)

        # Line 2: Badge ૧૧ + સભ્ય ફી & ફોર્મ ભરનારની સહી
        self.badge_11 = f_badge("૧૧")
        self.lbl_fee = f_label("સભ્ય ફી")
        grid3.addWidget(f_badged_label(self.badge_11, self.lbl_fee, width=190), 1, 0)
        fee_h = QHBoxLayout()
        fee_h.setSpacing(8)
        self.fee_edit = f_input("દા.ત. ₹ ૫૦૦")
        self.fee_edit.setText("₹ ૫૦૦")
        self.lbl_fee_sent = QLabel("મોકલેલ છે.")
        self.lbl_fee_sent.setStyleSheet("font-size: 12px; font-weight: 700; color: #1B2F8A; border: none;")
        fee_h.addWidget(self.fee_edit)
        fee_h.addWidget(self.lbl_fee_sent)
        grid3.addLayout(fee_h, 1, 1)

        self.lbl_sig = f_label("ફોર્મ ભરનારની સહી")
        self.lbl_sig.setFixedWidth(145)
        grid3.addWidget(self.lbl_sig, 1, 2)
        sig_row = QHBoxLayout()
        sig_row.setSpacing(8)

        self.sig_text_edit = f_input("સહી માટે નામ")
        sig_row.addWidget(self.sig_text_edit)

        self.btn_upload_sig = QPushButton("📁 અપલોડ")
        self.btn_upload_sig.setFixedHeight(36)
        self.btn_upload_sig.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_upload_sig.setStyleSheet("""
            QPushButton {
                background-color: #F5F3FF; color: #7C3AED;
                border: 1px solid #DDD6FE; border-radius: 6px;
                font-size: 11px; font-weight: 700; padding: 0 8px;
            }
            QPushButton:hover { background-color: #EDE9FE; }
        """)
        self.btn_upload_sig.clicked.connect(self._upload_signature)
        sig_row.addWidget(self.btn_upload_sig)

        self.sig_preview_frame = QFrame()
        self.sig_preview_frame.setFixedSize(110, 36)
        self.sig_preview_frame.setStyleSheet("background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 6px;")
        spf_layout = QVBoxLayout(self.sig_preview_frame)
        spf_layout.setContentsMargins(2, 2, 2, 2)
        self.sig_preview_label = QLabel("કોઈ છબી નથી")
        self.sig_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sig_preview_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10px; border: none;")
        spf_layout.addWidget(self.sig_preview_label)
        sig_row.addWidget(self.sig_preview_frame)

        self.btn_clear_sig = QPushButton("✖")
        self.btn_clear_sig.setFixedSize(28, 36)
        self.btn_clear_sig.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_clear_sig.setStyleSheet("""
            QPushButton {
                background-color: #FEF2F2; color: #DC2626;
                border: 1px solid #FECACA; border-radius: 6px;
                font-size: 12px; font-weight: 800;
            }
        """)
        self.btn_clear_sig.clicked.connect(self._clear_signature)
        self.btn_clear_sig.hide()
        sig_row.addWidget(self.btn_clear_sig)

        grid3.addLayout(sig_row, 1, 3)

        sec3_layout.addLayout(grid3)
        form_vbox.addWidget(sec3_frame)

        # ── SECTION 4: પરિવારની માહિતી (Family Information) ─────────────
        sec4_frame = QFrame()
        sec4_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 10px;
            }
        """)
        sec4_layout = QVBoxLayout(sec4_frame)
        sec4_layout.setContentsMargins(18, 16, 18, 18)
        sec4_layout.setSpacing(12)

        # Family Section Banner matching the paper form
        fam_banner_row = QHBoxLayout()
        self.s4_title = QLabel("૪. પરિવારની માહિતી")
        self.s4_title.setFixedHeight(30)
        self.s4_title.setStyleSheet("""
            background-color: #1B2F8A;
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 800;
            border-radius: 6px;
            padding: 4px 14px;
        """)

        self.s4_sub = QLabel("સત્તાવાર ફોર્મ મુજબ ૧૦ સભ્યોની વિગત")
        self.s4_sub.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {COLOR_TEXT_MUTED}; border: none;")

        fam_banner_row.addWidget(self.s4_title)
        fam_banner_row.addStretch()
        fam_banner_row.addWidget(self.s4_sub)
        sec4_layout.addLayout(fam_banner_row)

        # The 8-column FamilyTableWidget
        self.family_table = FamilyTableWidget()
        sec4_layout.addWidget(self.family_table)

        form_vbox.addWidget(sec4_frame)
        center_layout.addWidget(paper_card)

        # ── 4. Bottom Action Bar ─────────────────────────────────────
        bot_bar = QHBoxLayout()
        bot_bar.setSpacing(12)

        self.btn_bot_cancel  = QPushButton("✖ રદ કરો")
        self.btn_bot_preview = QPushButton("👁️  પ્રીવ્યૂ")
        self.btn_bot_print   = QPushButton("🖨️  પ્રિન્ટ")
        self.btn_bot_pdf     = QPushButton("📄  પીડીએફ")
        self.btn_bot_save    = QPushButton("💾  સભ્ય સાચવો")

        for btn in (self.btn_bot_cancel, self.btn_bot_preview, self.btn_bot_print, self.btn_bot_pdf, self.btn_bot_save):
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFixedHeight(42)

        self.btn_bot_cancel.setStyleSheet(self.btn_top_cancel.styleSheet())
        self.btn_bot_preview.setStyleSheet(self.btn_top_preview.styleSheet())
        self.btn_bot_print.setStyleSheet(self.btn_top_print.styleSheet())
        self.btn_bot_pdf.setStyleSheet(self.btn_top_pdf.styleSheet())
        self.btn_bot_save.setStyleSheet(self.btn_top_save.styleSheet())

        bot_bar.addStretch()
        bot_bar.addWidget(self.btn_bot_cancel)
        bot_bar.addWidget(self.btn_bot_preview)
        bot_bar.addWidget(self.btn_bot_print)
        bot_bar.addWidget(self.btn_bot_pdf)
        bot_bar.addWidget(self.btn_bot_save)
        center_layout.addLayout(bot_bar)

        # ── Connect Actions ──────────────────────────────────────────
        self.btn_top_save.clicked.connect(lambda: self._save(show_success_msg=True))
        self.btn_bot_save.clicked.connect(lambda: self._save(show_success_msg=True))

        self.btn_top_pdf.clicked.connect(self._generate_pdf_form)
        self.btn_bot_pdf.clicked.connect(self._generate_pdf_form)

        self.btn_top_print.clicked.connect(self._print_as_pdf)
        self.btn_bot_print.clicked.connect(self._print_as_pdf)

        self.btn_top_preview.clicked.connect(self._preview_form)
        self.btn_bot_preview.clicked.connect(self._preview_form)

        self.btn_top_cancel.clicked.connect(lambda: self._nav('dashboard'))
        self.btn_bot_cancel.clicked.connect(lambda: self._nav('dashboard'))

        # Auto sync full name to signature text
        self.fullname_edit.textChanged.connect(self._on_name_changed)

        # Initialize with next member code
        self._set_next_code_preview()

    def _set_next_code_preview(self):
        try:
            from database.models import Member
            with get_session() as session:
                setting = session.query(AppSetting).filter_by(setting_key='member_code_last').first()
                next_num = int(setting.setting_value or '0') + 1 if setting else 1
                while True:
                    candidate = f"GBS-{next_num:06d}"
                    exists = session.query(Member).filter_by(member_code=candidate).first()
                    if not exists:
                        break
                    next_num += 1
                self.form_no_edit.setText(candidate)
        except Exception:
            self.form_no_edit.setText("GBS-000001")

    def _on_name_changed(self, text: str):
        if not self._signature_image_path:
            cur_sig = self.sig_text_edit.text()
            if not cur_sig or cur_sig == text[:-1] or cur_sig == text:
                self.sig_text_edit.setText(text)

    def _upload_signature(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'સહીની છબી પસંદ કરો', '', 'Image Files (*.png *.jpg *.jpeg *.bmp)'
        )
        if not file_path:
            return

        ensure_dirs()
        sig_dir = os.path.join(DATA_DIR, 'signatures')
        os.makedirs(sig_dir, exist_ok=True)
        dest_filename = f"sig_{int(date.today().strftime('%Y%m%d'))}_{os.path.basename(file_path)}"
        dest_path = os.path.join(sig_dir, dest_filename)

        try:
            shutil.copy2(file_path, dest_path)
            self._signature_image_path = dest_path
            self._update_sig_preview()
        except Exception as exc:
            QMessageBox.warning(self, 'અપલોડ નિષ્ફળ', f'સહી કોપી કરવામાં ભૂલ:\n{exc}')

    def _clear_signature(self):
        self._signature_image_path = ''
        self.sig_preview_label.setText('કોઈ છબી નથી')
        self.sig_preview_label.setPixmap(QPixmap())
        self.btn_clear_sig.hide()

    def _update_sig_preview(self):
        if self._signature_image_path and os.path.exists(self._signature_image_path):
            pix = QPixmap(self._signature_image_path)
            if not pix.isNull():
                scaled = pix.scaled(106, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.sig_preview_label.setPixmap(scaled)
                self.btn_clear_sig.show()
                return
        self._clear_signature()

    def _populate_talukas(self, is_en: bool = False, keep_current: bool = True) -> None:
        curr = ""
        if keep_current and hasattr(self, 'taluka_combo'):
            curr = self.taluka_combo.currentText().strip()

        self.taluka_combo.blockSignals(True)
        self.taluka_combo.clear()
        self.taluka_combo.addItem("")
        for gu_name, en_name in SABARKANTHA_TALUKAS:
            disp = en_name if is_en else gu_name
            self.taluka_combo.addItem(disp, gu_name)

        ph = "Select Taluka..." if is_en else "તાલુકો પસંદ કરો..."
        if self.taluka_combo.lineEdit():
            self.taluka_combo.lineEdit().setPlaceholderText(ph)

        if keep_current and curr:
            idx = self.taluka_combo.findText(curr)
            if idx >= 0:
                self.taluka_combo.setCurrentIndex(idx)
            else:
                matched = False
                for gu_name, en_name in SABARKANTHA_TALUKAS:
                    if curr.lower() in (gu_name.lower(), en_name.lower(), 'ઈડર', 'ઇડર'):
                        disp = en_name if is_en else gu_name
                        c_idx = self.taluka_combo.findText(disp)
                        if c_idx >= 0:
                            self.taluka_combo.setCurrentIndex(c_idx)
                        else:
                            self.taluka_combo.setCurrentText(disp)
                        matched = True
                        break
                if not matched:
                    self.taluka_combo.setCurrentText(curr)
        self.taluka_combo.blockSignals(False)

    def _populate_education_presets(self, is_en: bool = False, keep_current: bool = True) -> None:
        curr = ""
        if keep_current and hasattr(self, 'edu_combo'):
            curr = self.edu_combo.currentText().strip()

        presets = EDUCATION_PRESETS_EN if is_en else EDUCATION_PRESETS_GU
        self.edu_combo.blockSignals(True)
        self.edu_combo.clear()
        for item in presets:
            self.edu_combo.addItem(item)

        ph = "Select or type Education..." if is_en else "શિક્ષણ પસંદ કરો અથવા લખો..."
        if self.edu_combo.lineEdit():
            self.edu_combo.lineEdit().setPlaceholderText(ph)

        # Smart Searchable Autocomplete (MatchContains for prefix/infix matching)
        completer = QCompleter(self.edu_combo.model(), self.edu_combo)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.edu_combo.setCompleter(completer)

        if keep_current and curr:
            idx = self.edu_combo.findText(curr)
            if idx >= 0:
                self.edu_combo.setCurrentIndex(idx)
            else:
                self.edu_combo.setCurrentText(curr)

        self.edu_combo.blockSignals(False)

    def load_for_edit(self, member) -> None:
        """Populate form fields with an existing member record."""
        is_en = (self._current_lang == 'en')
        t_prefix = "✏️  Edit Member Details" if is_en else "✏️  સભ્ય વિગતમાં સુધારો"
        self.title_label.setText(f"{t_prefix} — {member.full_name} ({member.member_code})")
        self._editing_id = member.id

        self.form_no_edit.setText(member.member_code or '')
        if member.created_at:
            try:
                c_part = str(member.created_at).split()[0]
                parts = c_part.split('-')
                if len(parts) == 3:
                    self.form_date_edit.setDate(QDate(int(parts[0]), int(parts[1]), int(parts[2])))
            except Exception:
                self.form_date_edit.setDate(QDate.currentDate())
        else:
            self.form_date_edit.setDate(QDate.currentDate())

        self.fullname_edit.setText(member.full_name or '')
        self.mobile_edit.setText(member.mobile or '')
        self.phone_edit.setText(member.phone_landline or '')
        self.email_edit.setText(member.email or '')
        self.address_edit.setPlainText(member.address or '')
        self.village_address_edit.setText(getattr(member, 'village_address', '') or '')
        
        # Taluka selection
        m_city = (member.city or '').strip()
        idx = self.taluka_combo.findText(m_city)
        if idx >= 0:
            self.taluka_combo.setCurrentIndex(idx)
        else:
            found = False
            for gu_name, en_name in SABARKANTHA_TALUKAS:
                if m_city.lower() in (gu_name.lower(), en_name.lower(), 'ઈડર', 'ઇડર'):
                    disp = en_name if is_en else gu_name
                    c_idx = self.taluka_combo.findText(disp)
                    if c_idx >= 0:
                        self.taluka_combo.setCurrentIndex(c_idx)
                    else:
                        self.taluka_combo.setCurrentText(disp)
                    found = True
                    break
            if not found:
                self.taluka_combo.setCurrentText(m_city)

        # District (Fixed Sabarkantha)
        dist_val = member.district or ('Sabarkantha' if is_en else 'સાબરકાંઠા')
        if is_en and dist_val in ('સાબરકાંઠા', 'Sabarkantha'):
            dist_val = 'Sabarkantha'
        elif not is_en and dist_val in ('સાબરકાંઠા', 'Sabarkantha'):
            dist_val = 'સાબરકાંઠા'
        self.district_edit.setText(dist_val)
        self.district_edit.setToolTip("District: Sabarkantha (Fixed)" if is_en else "જિલ્લો: સાબરકાંઠા (Fixed)")

        st_val = member.state or ('Gujarat' if is_en else 'ગુજરાત')
        if is_en and st_val in ('ગુજરાત', 'Gujarat'):
            st_val = 'Gujarat'
        elif not is_en and st_val in ('ગુજરાત', 'Gujarat'):
            st_val = 'ગુજરાત'
        self.state_edit.setText(st_val)

        self.pincode_edit.setText(member.pincode or '')
        self.occ_edit.setText(member.occupation or '')
        self.biz_address_edit.setPlainText(getattr(member, 'business_address', '') or '')
        self.income_edit.setText(getattr(member, 'income', '') or '')
        edu_val = member.education or ''
        if hasattr(self, 'edu_combo'):
            idx = self.edu_combo.findText(edu_val)
            if idx >= 0:
                self.edu_combo.setCurrentIndex(idx)
            else:
                self.edu_combo.setCurrentText(edu_val)
        self.edu_edit.setText(edu_val)

        idx = self.bg_combo.findText(member.blood_group or '')
        self.bg_combo.setCurrentIndex(max(idx, 0))

        smj_val = member.samaj or ('Gujarat Brahm Samaj' if is_en else 'ગુજરાત બ્રહ્મ સમાજ')
        if is_en and smj_val in ('ગુજરાત બ્રહ્મ સમાજ', 'Gujarat Brahm Samaj'):
            smj_val = 'Gujarat Brahm Samaj'
        elif not is_en and smj_val in ('ગુજરાત બ્રહ્મ સમાજ', 'Gujarat Brahm Samaj'):
            smj_val = 'ગુજરાત બ્રહ્મ સમાજ'
        self.samaj_edit.setText(smj_val)

        fee_val = member.membership_fee or ('₹ 500' if is_en else '₹ ૫૦૦')
        if is_en and fee_val in ('₹ ૫૦૦', '₹ 500'):
            fee_val = '₹ 500'
        elif not is_en and fee_val in ('₹ ૫૦૦', '₹ 500'):
            fee_val = '₹ ૫૦૦'
        self.fee_edit.setText(fee_val)

        self.sig_text_edit.setText(getattr(member, 'signature_text', '') or member.full_name or '')

        self._signature_image_path = getattr(member, 'signature_image', '') or ''
        self._update_sig_preview()

        fms = FamilyService().get_family_members(member.id)
        self.family_table.load_rows(fms)

    def reset(self) -> None:
        """Clear form for adding a new member."""
        is_en = (self._current_lang == 'en')
        self.title_label.setText("➕  Member Registration Form" if is_en else "➕  સભ્ય નોંધણી ફોર્મ")
        self._editing_id = None
        for widget in (
            self.fullname_edit, self.mobile_edit, self.phone_edit,
            self.email_edit, self.village_address_edit,
            self.pincode_edit, self.occ_edit, self.income_edit,
            self.edu_edit, self.sig_text_edit,
        ):
            widget.clear()

        self.taluka_combo.setCurrentIndex(0)
        if self.taluka_combo.lineEdit():
            self.taluka_combo.lineEdit().clear()
        if hasattr(self, 'edu_combo'):
            self.edu_combo.setCurrentIndex(0)
            if self.edu_combo.lineEdit():
                self.edu_combo.lineEdit().clear()
        self.district_edit.setText('Sabarkantha' if is_en else 'સાબરકાંઠા')
        self.district_edit.setToolTip("District: Sabarkantha (Fixed)" if is_en else "જિલ્લો: સાબરકાંઠા (Fixed)")
        self.address_edit.clear()
        self.biz_address_edit.clear()
        self.state_edit.setText('Gujarat' if is_en else 'ગુજરાત')
        self.samaj_edit.setText('Gujarat Brahm Samaj' if is_en else 'ગુજરાત બ્રહ્મ સમાજ')
        self.fee_edit.setText('₹ 500' if is_en else '₹ ૫૦૦')
        self.bg_combo.setCurrentIndex(0)
        self.form_date_edit.setDate(QDate.currentDate())
        self.family_table.table.setRowCount(0)
        self._clear_signature()
        self._set_next_code_preview()

    def _collect_data(self) -> dict:
        full_name = self.fullname_edit.text().strip()
        parts = full_name.split()
        surname = parts[0] if parts else ''

        form_code = self.form_no_edit.text().strip()
        form_date_str = self.form_date_edit.date().toString('yyyy-MM-dd')

        return {
            'member_code':      form_code,
            'full_name':        full_name,
            'surname':          surname,
            'father_name':      '',
            'mobile':           self.mobile_edit.text().strip(),
            'phone_landline':   self.phone_edit.text().strip(),
            'email':            self.email_edit.text().strip(),
            'address':          self.address_edit.toPlainText().strip(),
            'village_address':  self.village_address_edit.text().strip(),
            'city':             self.taluka_combo.currentText().strip() or self.city_edit.text().strip(),
            'district':         self.district_edit.text().strip() or 'સાબરકાંઠા',
            'state':            self.state_edit.text().strip() or 'ગુજરાત',
            'pincode':          self.pincode_edit.text().strip(),
            'occupation':       self.occ_edit.text().strip(),
            'business_address': self.biz_address_edit.toPlainText().strip(),
            'income':           self.income_edit.text().strip(),
            'education':        self.edu_edit.text().strip(),
            'blood_group':      self.bg_combo.currentText(),
            'samaj':            self.samaj_edit.text().strip() or 'ગુજરાત બ્રહ્મ સમાજ',
            'membership_fee':   self.fee_edit.text().strip() or '₹ ૫૦૦',
            'signature_text':   self.sig_text_edit.text().strip() or full_name,
            'signature_image':  self._signature_image_path,
            'birth_date':       '',
            'created_at':       f"{form_date_str} 00:00:00",
        }

    def _save(self, show_success_msg: bool = True) -> Any:
        data = self._collect_data()

        member_svc = MemberService()
        duplicate = member_svc.check_duplicate_warning(
            data['full_name'], data['mobile'], exclude_id=self._editing_id
        )
        if duplicate:
            reply = QMessageBox.warning(
                self, 'સંભવિત ડુપ્લિકેટ (Duplicate Warning)',
                f"આ નામ અને મોબાઇલ નંબર સાથે સભ્ય પહેલેથી નોંધાયેલ છે:\n\n"
                f"સભ્ય કોડ: {duplicate.member_code}\n"
                f"નામ: {duplicate.full_name}\n"
                f"મોબાઇલ: {duplicate.mobile}\n\n"
                f"શું તમે તેમ છતાં સેવ કરવા માંગો છો?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return None

        if self._editing_id is not None:
            member, errors = member_svc.update_member(self._editing_id, data)
        else:
            member, errors = member_svc.create_member(data)

        if errors:
            QMessageBox.warning(self, 'માન્યતા ભૂલ (Validation Error)', '\n'.join(errors))
            return None

        # Save family members
        family_svc = FamilyService()
        family_rows = self.family_table.get_rows()
        existing_fms = family_svc.get_family_members(member.id)
        for fm in existing_fms:
            family_svc.delete_family_member(fm.id)

        for row_data in family_rows:
            family_svc.add_family_member(member.id, row_data)

        if self._on_data_updated:
            self._on_data_updated()

        if show_success_msg:
            QMessageBox.information(
                self, 'સફળતા',
                f"✓ સભ્ય સફળતાપૂર્વક સાચવવામાં આવ્યો છે!\n\n"
                f"સભ્ય કોડ (ફોર્મ નં.): {member.member_code}\n"
                f"નામ: {member.full_name}\n"
                f"પરિવાર સભ્યો: {len(family_rows)}",
            )
            self._nav('profile', member_id=member.id)

        return member

    def _generate_pdf_form(self) -> None:
        member = self._save(show_success_msg=False)
        if not member:
            return

        try:
            family_svc = FamilyService()
            fms = family_svc.get_family_members(member.id)
            form_date_str = self.form_date_edit.date().toString('dd/MM/yyyy')
            form_data = build_form_data(member, fms, custom_date=form_date_str)

            default_name = get_pdf_filename(member.full_name, member.member_code)
            save_path, _ = QFileDialog.getSaveFileName(
                self, 'પીડીએફ સેવ કરો', os.path.join(EXPORT_DIR, default_name), 'PDF Files (*.pdf)'
            )
            if not save_path:
                return

            generate_form_pdf(form_data, save_path)

            reply = QMessageBox.information(
                self, 'પીડીએફ સફળ',
                f"✓ સભ્યપદ ફોર્મ પીડીએફ સફળતાપૂર્વક બનાવવામાં આવી છે!\n\nફાઇલ પથ:\n{save_path}",
                QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Ok,
            )
            if reply == QMessageBox.StandardButton.Open:
                try:
                    os.startfile(save_path)
                except Exception:
                    pass

            self._nav('profile', member_id=member.id)
        except Exception as exc:
            QMessageBox.critical(self, 'ભૂલ', f"પીડીએફ બનાવવામાં ભૂલ આવી:\n{exc}")

    def _print_as_pdf(self) -> None:
        member = self._save(show_success_msg=False)
        if not member:
            return

        try:
            family_svc = FamilyService()
            fms = family_svc.get_family_members(member.id)
            form_date_str = self.form_date_edit.date().toString('dd/MM/yyyy')
            form_data = build_form_data(member, fms, custom_date=form_date_str)

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            dlg = QPrintDialog(printer, self)
            if dlg.exec():
                painter = QPainter(printer)
                page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
                FormRenderer.draw_form(
                    painter,
                    form_data=form_data,
                    width=page_rect.width(),
                    height=page_rect.height(),
                    draw_background=True,
                    draw_labels_and_lines=True,
                    draw_values=True,
                )
                painter.end()
                QMessageBox.information(self, 'પ્રિન્ટ સફળ', "✓ ફોર્મ પ્રિન્ટર પર સફળતાપૂર્વક મોકલવામાં આવ્યું છે!")

            self._nav('profile', member_id=member.id)
        except Exception as exc:
            QMessageBox.critical(self, 'ભૂલ', f"પ્રિન્ટ કરવામાં ભૂલ આવી:\n{exc}")

    def _preview_form(self) -> None:
        member = self._save(show_success_msg=False)
        if not member:
            return
        self._nav('form_preview', member_id=member.id)

    def set_language(self, lang: str):
        """Update all form labels, placeholders, buttons, and family table to selected language."""
        from app.translations import t

        self._current_lang = lang
        is_en = (lang == 'en')

        # Top Action Bar Title & Subtitle
        if hasattr(self, 'title_label'):
            if self._editing_id:
                self.title_label.setText("✏️  Edit Member Details" if is_en else "✏️  સભ્ય વિગતમાં સુધારો")
            else:
                self.title_label.setText("➕  Member Registration Form" if is_en else "➕  સભ્ય નોંધણી ફોર્મ")
        if hasattr(self, 'subtitle_label'):
            self.subtitle_label.setText(
                "Shree Samast Gujarat Brahm Samaj S.K. — Official Membership Registration" if is_en
                else "શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સા.કાં. — સત્તાવાર સભ્યપદ નોંધણી"
            )

        # Hanging Banner & Letterhead
        if hasattr(self, 'banner_lbl'):
            self.banner_lbl.setText("MEMBERSHIP FORM" if is_en else "સભ્ય નોંધણી ફોર્મ")
        if hasattr(self, 'org_name_lbl'):
            self.org_name_lbl.setText("Shree Samast Gujarat Brahm Samaj S.K." if is_en else "શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સા.કાં.")
        if hasattr(self, 'org_addr_lbl'):
            self.org_addr_lbl.setText(
                "F.F.-114, 1st Floor, Shaiv Complex, Damodar Area, Opp. Satyam Hospital, Idar." if is_en
                else "એફ.એફ-૧૧૪, પહેલો માળ, શૈવ કૉમ્પ્લેક્સ, દામોદર એરિયા, સત્યમ હોસ્પિટલની સામે, ઇડર."
            )

        # Meta bar (Form No & Date)
        if hasattr(self, 'fn_lbl'):
            self.fn_lbl.setText("Form No. :" if is_en else "ફોર્મ ક્રમાંક :")
        if hasattr(self, 'dt_lbl'):
            self.dt_lbl.setText("Date :" if is_en else "તારીખ :")
        if hasattr(self, 'form_no_edit'):
            self.form_no_edit.setPlaceholderText("e.g. GBS-000001" if is_en else "દા.ત. GBS-000001")

        # Circular Badges 1-11
        num_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"] if is_en else ["૧", "૨", "૩", "૪", "૫", "૬", "૭", "૮", "૯", "૧૦", "૧૧"]
        for idx, b_name in enumerate(('badge_1', 'badge_2', 'badge_3', 'badge_4', 'badge_5', 'badge_6', 'badge_7', 'badge_8', 'badge_9', 'badge_10', 'badge_11')):
            if hasattr(self, b_name):
                getattr(self, b_name).setText(num_list[idx])

        # ── Section 1: સભ્યની વ્યક્તિગત માહિતી (Personal Information) ──
        if hasattr(self, 's1_title'):
            self.s1_title.setText("1. Member's Personal Information" if is_en else "૧. સભ્યની વ્યક્તિગત માહિતી")
        if hasattr(self, 's1_req'):
            self.s1_req.setText("* Mandatory Fields" if is_en else "* ફરજિયાત ક્ષેત્ર")

        if hasattr(self, 'lbl_fullname'):
            self.lbl_fullname.setText("Full Name (Surname first) *" if is_en else "પૂર્ણ નામ (અટક પહેલાં લખવી) *")
        if hasattr(self, 'fullname_edit'):
            self.fullname_edit.setPlaceholderText(
                "Surname first — e.g. Joshi Harshadbhai Ramaniklal *" if is_en
                else "અટક પહેલાં લખવી — દા.ત. જોષી હર્ષદભાઈ રમણિકલાલ *"
            )

        if hasattr(self, 'lbl_address'):
            self.lbl_address.setText("Residential Address *" if is_en else "રહેઠાણનું સરનામું *")
        if hasattr(self, 'address_edit'):
            self.address_edit.setPlaceholderText(
                "House No, Society, Street, Landmark... *" if is_en
                else "ઘર નં., ફ્લેટ/સોસાયટી, શેરી, વિસ્તાર... *"
            )

        if hasattr(self, 'lbl_city_dist'):
            self.lbl_city_dist.setText("Taluka & District" if is_en else "તાલુકો & જિલ્લો")
        if hasattr(self, 'taluka_combo'):
            self._populate_talukas(is_en=is_en, keep_current=True)
        if hasattr(self, 'district_edit'):
            self.district_edit.setText("Sabarkantha" if is_en else "સાબરકાંઠા")
            self.district_edit.setPlaceholderText("District" if is_en else "જિલ્લો")
            self.district_edit.setToolTip("District: Sabarkantha (Fixed)" if is_en else "જિલ્લો: સાબરકાંઠા (Fixed)")

        if hasattr(self, 'lbl_state_pin'):
            self.lbl_state_pin.setText("State & PIN Code *" if is_en else "રાજ્ય & પીન કોડ નં. *")
        if hasattr(self, 'state_edit'):
            self.state_edit.setPlaceholderText("State" if is_en else "રાજ્ય")
            if is_en and self.state_edit.text() == "ગુજરાત":
                self.state_edit.setText("Gujarat")
            elif not is_en and self.state_edit.text() == "Gujarat":
                self.state_edit.setText("ગુજરાત")

        if hasattr(self, 'pincode_edit'):
            self.pincode_edit.setPlaceholderText("PIN Code (6 digits) *" if is_en else "પીન કોડ (૬ અંક) *")

        if hasattr(self, 'lbl_village_address'):
            self.lbl_village_address.setText("Village Address" if is_en else "ગામનું સરનામું")
        if hasattr(self, 'village_address_edit'):
            self.village_address_edit.setPlaceholderText(
                "Village / Native Place Address" if is_en
                else "ગામ / મૂળ વતનનું સરનામું"
            )

        if hasattr(self, 'lbl_email'):
            self.lbl_email.setText("Email ID" if is_en else "ઈ-મેલ આઈડી")

        if hasattr(self, 'lbl_edu'):
            self.lbl_edu.setText("Education" if is_en else "શિક્ષણ")
        if hasattr(self, 'edu_combo'):
            self._populate_education_presets(is_en=is_en, keep_current=True)
        elif hasattr(self, 'edu_edit'):
            self.edu_edit.setPlaceholderText(
                "e.g. B.A., B.Com, M.Sc, B.E., etc." if is_en
                else "દા.ત. B.A., B.Com, M.Sc, B.E., વગેરે..."
            )

        if hasattr(self, 'lbl_contact'):
            self.lbl_contact.setText("Mobile & Phone *" if is_en else "મોબાઇલ & ફોન નં. *")
        if hasattr(self, 'mobile_edit'):
            self.mobile_edit.setPlaceholderText("10-digit Mobile Number *" if is_en else "૧૦ અંકનો મોબાઈલ નં. *")
        if hasattr(self, 'phone_edit'):
            self.phone_edit.setPlaceholderText("Phone / Landline" if is_en else "૧૦ અંકનો ફોન / લેન્ડલાઇન")

        # ── Section 2: વ્યવસાય / રોજગારની માહિતી (Business / Employment) ──
        if hasattr(self, 's2_title'):
            self.s2_title.setText("2. Business / Employment Information" if is_en else "૨. વ્યવસાય / રોજગારની માહિતી")

        if hasattr(self, 'lbl_occ'):
            self.lbl_occ.setText("Profession / Business" if is_en else "ધંધો / વ્યવસાય")
        if hasattr(self, 'occ_edit'):
            self.occ_edit.setPlaceholderText(
                "Job, Business, Independent Practice, etc..." if is_en
                else "નોકરી, વેપાર, સ્વતંત્ર વ્યવસાય, વગેરે..."
            )

        if hasattr(self, 'lbl_biz_addr'):
            self.lbl_biz_addr.setText("Business Address" if is_en else "ધંધાનું સરનામું")
        if hasattr(self, 'biz_address_edit'):
            self.biz_address_edit.setPlaceholderText(
                "Shop/Office No, Complex, Street, Area, City..." if is_en
                else "દુકાન/ઓફિસ નં., કોમ્પ્લેક્ષ, શેરી, વિસ્તાર, શહેર..."
            )

        if hasattr(self, 'lbl_bg'):
            self.lbl_bg.setText("Blood Group" if is_en else "બ્લડ ગ્રુપ")

        # ── Section 3: સમાજની માહિતી (Samaj Information) ────────────────
        if hasattr(self, 's3_title'):
            self.s3_title.setText("3. Samaj Information" if is_en else "૩. સમાજની માહિતી")

        if hasattr(self, 'lbl_samaj'):
            self.lbl_samaj.setText("Samaj" if is_en else "સમાજ")
        if hasattr(self, 'samaj_edit'):
            self.samaj_edit.setPlaceholderText("Gujarat Brahm Samaj" if is_en else "ગુજરાત બ્રહ્મ સમાજ")
            if is_en and self.samaj_edit.text() == "ગુજરાત બ્રહ્મ સમાજ":
                self.samaj_edit.setText("Gujarat Brahm Samaj")
            elif not is_en and self.samaj_edit.text() == "Gujarat Brahm Samaj":
                self.samaj_edit.setText("ગુજરાત બ્રહ્મ સમાજ")

        if hasattr(self, 'lbl_fee'):
            self.lbl_fee.setText("Member Fee" if is_en else "સભ્ય ફી")
        if hasattr(self, 'lbl_fee_sent'):
            self.lbl_fee_sent.setText("Paid" if is_en else "મોકલેલ છે.")
        if hasattr(self, 'fee_edit'):
            self.fee_edit.setPlaceholderText("e.g. ₹ 500" if is_en else "દા.ત. ₹ ૫૦૦")
            if is_en and self.fee_edit.text() == "₹ ૫૦૦":
                self.fee_edit.setText("₹ 500")
            elif not is_en and self.fee_edit.text() == "₹ 500":
                self.fee_edit.setText("₹ ૫૦૦")

        if hasattr(self, 'lbl_sig'):
            self.lbl_sig.setText("Applicant Signature" if is_en else "ફોર્મ ભરનારની સહી")
        if hasattr(self, 'sig_text_edit'):
            self.sig_text_edit.setPlaceholderText("Signatory Full Name" if is_en else "સહી માટે નામ")
        if hasattr(self, 'btn_upload_sig'):
            self.btn_upload_sig.setText("📁 Upload" if is_en else "📁 અપલોડ")
        if hasattr(self, 'sig_preview_label'):
            if self.sig_preview_label.text() in ("કોઈ છબી નથી", "No Image"):
                self.sig_preview_label.setText("No Image" if is_en else "કોઈ છબી નથી")

        # ── Section 4: પરિવારની માહિતી (Family Information) ─────────────
        if hasattr(self, 's4_title'):
            self.s4_title.setText("4. Family Information" if is_en else "૪. પરિવારની માહિતી")
        if hasattr(self, 's4_sub'):
            self.s4_sub.setText(
                "Up to 10 family members per official form" if is_en
                else "સત્તાવાર ફોર્મ મુજબ ૧૦ સભ્યોની વિગત"
            )

        # Propagate to Family Table
        if hasattr(self, 'family_table'):
            self.family_table.set_language(lang)

        # Top & Bottom Action Buttons
        for btn in (self.btn_top_cancel, self.btn_bot_cancel):
            if hasattr(self, btn.objectName()) or btn:
                btn.setText("✖ Cancel" if is_en else "✖ રદ કરો")
        for btn in (self.btn_top_preview, self.btn_bot_preview):
            if hasattr(self, btn.objectName()) or btn:
                btn.setText("👁️  Preview" if is_en else "👁️  પ્રીવ્યૂ")
        for btn in (self.btn_top_print, self.btn_bot_print):
            if hasattr(self, btn.objectName()) or btn:
                btn.setText("🖨️  Print" if is_en else "🖨️  પ્રિન્ટ")
        for btn in (self.btn_top_pdf, self.btn_bot_pdf):
            if hasattr(self, btn.objectName()) or btn:
                btn.setText("📄  Generate PDF" if is_en else "📄  પીડીએફ")
        for btn in (self.btn_top_save, self.btn_bot_save):
            if hasattr(self, btn.objectName()) or btn:
                btn.setText("💾  Save Member" if is_en else "💾  સભ્ય સાચવો")
