"""Member profile page — read-only view with action buttons."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
)

from app.config import (
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_BORDER, COLOR_TEXT_MAIN,
)
from services.member_service import MemberService
from services.family_service import FamilyService
from utils.date_utils import calculate_age, format_date_display

COMMON_GUJ_TO_ENG = {
    'સાબરકાંઠા': 'Sabarkantha',
    'અમદાવાદ': 'Ahmedabad',
    'આણંદ': 'Anand',
    'ઈડર': 'Idar',
    'ગાંધીનગર': 'Gandhinagar',
    'ગુજરાત': 'Gujarat',
    'ગુજરાત બ્રહ્મ સમાજ': 'Gujarat Brahm Samaj',
    'વેપાર અને સીએ કન્સલ્ટન્ટ': 'Business & CA Consultant',
    '₹ ૫૦૦ (મળેલ છે)': '₹ 500 (Received)',
    '₹ ૫૦૦': '₹ 500',
    'પિતા': 'Father',
    'માતા': 'Mother',
    'પુત્ર': 'Son',
    'પુત્રી': 'Daughter',
    'પુત્રવધૂ': 'Daughter-in-law',
    'પત્ની': 'Wife',
    'પતિ': 'Husband',
    'ભાઈ': 'Brother',
    'બહેન': 'Sister',
    'દાદા': 'Grandfather',
    'દાદી': 'Grandmother',
}


class MemberProfilePage(QWidget):
    def __init__(self, nav_callback, on_data_updated=None, parent=None):
        super().__init__(parent)
        self._nav = nav_callback
        self._on_data_updated = on_data_updated
        self._member_id: int | None = None
        self._current_lang: str = 'gu'
        self._setup_ui()

    def set_language(self, lang: str) -> None:
        self._current_lang = lang
        if self._member_id is not None:
            self.load_member(self._member_id)

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(self.scroll)

        self._container = None
        self.main_layout = None

    def load_member(self, member_id: int) -> None:
        self._member_id = member_id
        is_en = (self._current_lang == 'en')

        # 1. Cleanly detach, unparent, and delete old container and all of its child widgets & sub-layouts
        old_container = self.scroll.takeWidget()
        if old_container is not None:
            old_container.setParent(None)
            old_container.deleteLater()

        # 2. Create fresh container
        container = QWidget()
        self._container = container
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(28, 20, 28, 24)
        self.main_layout.setSpacing(16)
        self.scroll.setWidget(container)

        member = MemberService().get_member(member_id)
        if not member:
            err_msg = 'Member not found.' if is_en else 'સભ્ય મળ્યા નથી.'
            err = QLabel(err_msg)
            err.setStyleSheet("font-size: 14px; color: #DC2626; padding: 20px;")
            self.main_layout.addWidget(err)
            return

        family_members = FamilyService().get_family_members(member_id)

        # ── Header bar ─────────────────────────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(12)
        back_text = '← Back' if is_en else '← પાછા જાઓ'
        back_btn = QPushButton(back_text)
        back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_btn.setFixedHeight(36)
        back_btn.setStyleSheet(f"""
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
        back_btn.clicked.connect(lambda: self._nav('list'))

        title = QLabel(f'👤  {member.full_name}')
        title.setStyleSheet(f'font-size: 20px; font-weight: 800; color: {COLOR_PRIMARY};')

        code_prefix = 'Member Code: ' if is_en else 'સભ્ય કોડ: '
        code_lbl = QLabel(f'{code_prefix}{member.member_code}')
        code_lbl.setStyleSheet('font-size: 12px; font-weight: 700; color: #475569; background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px; padding: 4px 10px;')

        hdr.addWidget(back_btn)
        hdr.addWidget(title)
        hdr.addWidget(code_lbl)
        hdr.addStretch()
        self.main_layout.addLayout(hdr)

        # ── Action buttons ──────────────────────────────────────────
        act_row = QHBoxLayout()
        act_row.setSpacing(10)

        btn_edit = QPushButton('✏️  Edit Details' if is_en else '✏️  વિગત સુધારો')
        btn_edit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_edit.setFixedHeight(38)
        btn_edit.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 700;
                padding: 0 18px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_DARK};
            }}
            QPushButton:pressed {{
                background-color: #0E1848;
            }}
        """)
        btn_edit.clicked.connect(lambda: self._nav('edit', member_id=member_id))
        act_row.addWidget(btn_edit)

        btn_pdf = QPushButton('📄  Generate Form / PDF' if is_en else '📄  ફોર્મ PDF બનાવો')
        btn_pdf.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_pdf.setFixedHeight(38)
        btn_pdf.setStyleSheet("""
            QPushButton {
                background-color: #8E44AD;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 700;
                padding: 0 18px;
            }
            QPushButton:hover {
                background-color: #7D3C98;
            }
            QPushButton:pressed {
                background-color: #6C3483;
            }
        """)
        btn_pdf.clicked.connect(lambda: self._generate_pdf(member_id))
        act_row.addWidget(btn_pdf)

        btn_del = QPushButton('🗑️  Delete Member' if is_en else '🗑️  સભ્ય કાઢી નાખો')
        btn_del.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_del.setFixedHeight(38)
        btn_del.setStyleSheet("""
            QPushButton {
                background-color: #DC2626;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 700;
                padding: 0 18px;
            }
            QPushButton:hover {
                background-color: #B91C1C;
            }
            QPushButton:pressed {
                background-color: #991B1B;
            }
        """)
        btn_del.clicked.connect(lambda: self._delete(member_id))
        act_row.addWidget(btn_del)

        act_row.addStretch()
        self.main_layout.addLayout(act_row)

        # ── Info card ───────────────────────────────────────────────
        info_frame = QFrame()
        info_frame.setStyleSheet('background: white; border: 1px solid #E2E8F0; border-radius: 10px;')
        info_layout = QGridLayout(info_frame)
        info_layout.setContentsMargins(24, 20, 24, 20)
        info_layout.setHorizontalSpacing(16)
        info_layout.setVerticalSpacing(12)

        bdate = str(member.birth_date or '')
        age = calculate_age(bdate)
        age_str = f'  (Age: {age})' if (age and is_en) else (f'  (ઉંમર: {age})' if age else '')
        dob_display = format_date_display(bdate) + age_str

        if is_en:
            fields = [
                ('Full Name',           member.full_name or '—'),
                ('Surname',             member.surname or '—'),
                ("Father's Name",       member.father_name or '—'),
                ('Mobile',              member.mobile or '—'),
                ('Phone / Landline',    member.phone_landline or '—'),
                ('Email',               member.email or '—'),
                ('Date of Birth',       dob_display or '—'),
                ('Residential Address', member.address or '—'),
                ('Village Address',     getattr(member, 'village_address', '') or '—'),
                ('Taluka / City',       member.city or '—'),
                ('District',            member.district or '—'),
                ('State',               member.state or '—'),
                ('PIN Code',            member.pincode or '—'),
                ('Occupation',          member.occupation or '—'),
                ('Business Address',    getattr(member, 'business_address', '') or '—'),
                ('Income',              getattr(member, 'income', '') or '—'),
                ('Blood Group',         member.blood_group or '—'),
                ('Education',           member.education or '—'),
                ('Samaj',               member.samaj or '—'),
                ('Membership Fee',      member.membership_fee or '—'),
            ]
        else:
            fields = [
                ('પૂરું નામ',             member.full_name or '—'),
                ('અટક',                 member.surname or '—'),
                ('પિતાનું નામ',           member.father_name or '—'),
                ('મોબાઈલ',              member.mobile or '—'),
                ('ફોન / લેન્ડલાઇન',       member.phone_landline or '—'),
                ('ઇમેઇલ',               member.email or '—'),
                ('જન્મ તારીખ',           dob_display or '—'),
                ('રહેઠાણનું સરનામું',      member.address or '—'),
                ('ગામનું સરનામું',        getattr(member, 'village_address', '') or '—'),
                ('તાલુકો / શહેર',        member.city or '—'),
                ('જિલ્લો',               member.district or '—'),
                ('રાજ્ય',                member.state or '—'),
                ('પીન કોડ',             member.pincode or '—'),
                ('ધંધો / વ્યવસાય',        member.occupation or '—'),
                ('ધંધાનું સરનામું',        getattr(member, 'business_address', '') or '—'),
                ('આવક',                 getattr(member, 'income', '') or '—'),
                ('બ્લડ ગ્રુપ',            member.blood_group or '—'),
                ('અભ્યાસ',              member.education or '—'),
                ('સમાજ',                member.samaj or '—'),
                ('સભ્ય ફી',              member.membership_fee or '—'),
            ]

        for i, (label, value) in enumerate(fields):
            row, col = divmod(i, 2)
            base_col = col * 2
            lbl = QLabel(label + ':')
            lbl.setStyleSheet('font-size: 12px; color: #64748B; font-weight: 700; border: none; background: transparent;')
            lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
            str_val = str(value)
            if is_en and str_val in COMMON_GUJ_TO_ENG:
                str_val = COMMON_GUJ_TO_ENG[str_val]
            val = QLabel(str_val)
            val.setStyleSheet('font-size: 13px; color: #0F172A; font-weight: 500; border: none; background: transparent;')
            val.setWordWrap(True)
            info_layout.addWidget(lbl, row, base_col)
            info_layout.addWidget(val, row, base_col + 1)

        self.main_layout.addWidget(info_frame)

        # ── Family members ──────────────────────────────────────────
        if family_members:
            fam_title = '👨‍👩‍👧  Family Members' if is_en else '👨‍👩‍👧  પરિવાર સભ્યો'
            fam_label = QLabel(fam_title)
            fam_label.setStyleSheet(f'font-size: 16px; font-weight: 800; color: {COLOR_PRIMARY}; margin-top: 6px;')
            self.main_layout.addWidget(fam_label)

            fam_table = QTableWidget(len(family_members), 8)
            if is_en:
                headers = ['#', 'Name', 'Relation', 'Age', 'Education', 'Blood Grp', 'Occupation', 'Contact No.']
            else:
                headers = ['ક્રમ', 'નામ', 'સંબંધ', 'ઉંમર', 'અભ્યાસ', 'બ્લડ ગૃપ', 'વ્યવસાય', 'સંપર્ક નંબર']
            fam_table.setHorizontalHeaderLabels(headers)
            fam_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            fam_table.verticalHeader().setVisible(False)
            fam_table.setEditTriggers(fam_table.EditTrigger.NoEditTriggers)
            fam_table.setStyleSheet(f"""
                QTableWidget {{
                    border: 1px solid #E2E8F0;
                    border-radius: 8px;
                    background: white;
                    color: #0F172A;
                    font-size: 12px;
                    gridline-color: #F1F5F9;
                }}
                QTableWidget::item {{
                    color: #0F172A;
                    padding: 4px;
                }}
                QHeaderView::section {{
                    background: {COLOR_PRIMARY}; color: white;
                    padding: 8px 6px; border: none;
                    border-right: 1px solid #142268;
                    font-weight: 700;
                    font-size: 11px;
                }}
                QTableWidget::item:selected {{
                    background: #EFF6FF;
                    color: {COLOR_PRIMARY};
                }}
            """)
            for i, fm in enumerate(family_members):
                rel = str(fm.relation or '')
                if is_en and rel in COMMON_GUJ_TO_ENG:
                    rel = COMMON_GUJ_TO_ENG[rel]
                occ = str(fm.occupation or '')
                if is_en and occ in COMMON_GUJ_TO_ENG:
                    occ = COMMON_GUJ_TO_ENG[occ]
                for j, item_val in enumerate([
                    str(i + 1), str(fm.name), rel,
                    str(fm.age) if fm.age else '',
                    str(fm.education or ''), str(fm.blood_group or ''), occ,
                    str(fm.contact_number or ''),
                ]):
                    fam_table.setItem(i, j, QTableWidgetItem(item_val))
            self.main_layout.addWidget(fam_table)

        self.main_layout.addStretch()

    def _generate_pdf(self, member_id: int) -> None:
        self._nav('form_preview', member_id=member_id)

    def _delete(self, member_id: int) -> None:
        is_en = (self._current_lang == 'en')
        member = MemberService().get_member(member_id)
        name = member.full_name if member else ('this member' if is_en else 'આ સભ્ય')
        
        q_title = 'Confirm Delete' if is_en else 'ખાતરી કરો'
        q_msg = (
            f'Delete member "{name}"?\n\nThis will also remove all family records.'
            if is_en else
            f'શું તમે ખરેખર "{name}" ની નોંધણી કાઢી નાખવા માંગો છો?\n\nઆ સાથે તમામ પરિવાર સભ્યોની વિગત પણ રદ થશે.'
        )
        reply = QMessageBox.question(
            self, q_title, q_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            MemberService().delete_member(member_id)
            if self._on_data_updated:
                self._on_data_updated()
            info_title = 'Deleted' if is_en else 'કાઢી નાખેલ'
            info_msg = 'Member deleted successfully.' if is_en else 'સભ્ય સફળતાપૂર્વક કાઢી નાખવામાં આવ્યા છે.'
            QMessageBox.information(self, info_title, info_msg)
            self._nav('list')

