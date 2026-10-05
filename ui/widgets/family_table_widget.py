"""
Family member inline table widget.
8 editable columns matching the official form's 'પરિવારની માહિતી' section.
Full bilingual support: pure Gujarati in 'gu' mode, 100% English in 'en' mode (no Gujarati text).
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QComboBox, QSpinBox,
    QHeaderView, QAbstractItemView,
)

from app.config import (
    BLOOD_GROUPS, COLOR_PRIMARY,
    COLOR_PRIMARY_DARK, COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
)

RELATIONS_GU = [
    '', 'પત્ની', 'પુત્ર', 'પુત્રી', 'પતિ',
    'પિતા', 'માતા', 'ભાઈ', 'બહેન',
    'દાદા', 'દાદી', 'અન્ય',
]

RELATIONS_EN = [
    '', 'Wife', 'Son', 'Daughter', 'Husband',
    'Father', 'Mother', 'Brother', 'Sister',
    'Grand Father', 'Grand Mother', 'Other',
]

GU_TO_EN_REL: dict[str, str] = {
    '': '',
    'પત્ની': 'Wife',
    'પુત્ર': 'Son',
    'પુત્રી': 'Daughter',
    'પતિ': 'Husband',
    'પિતા': 'Father',
    'માતા': 'Mother',
    'ભાઈ': 'Brother',
    'બહેન': 'Sister',
    'દાદા': 'Grand Father',
    'દાદી': 'Grand Mother',
    'અન્ય': 'Other',
}

EN_TO_GU_REL: dict[str, str] = {v: k for k, v in GU_TO_EN_REL.items() if k}


class FamilyTableWidget(QWidget):
    """Editable table for adding/editing family members with full bilingual support."""

    COLUMNS_GU = [
        'ક્રમ',
        'નામ *',
        'સંબંધ',
        'ઉંમર',
        'અભ્યાસ',
        'બ્લડ ગ્રુપ',
        'વ્યવસાય',
        'સંપર્ક નંબર',
    ]

    COLUMNS_EN = [
        'Sr No.',
        'Name *',
        'Relationship',
        'Age',
        'Education',
        'Blood Group',
        'Occupation',
        'Contact Number',
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_lang = 'gu'
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Button row & counter
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_add = QPushButton('➕  પરિવાર સભ્ય ઉમેરો')
        self.btn_add.setFixedHeight(36)
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY}; color: #FFFFFF;
                border: none; border-radius: 8px;
                font-size: 12px; font-weight: 700; padding: 0 16px;
            }}
            QPushButton:hover {{ background-color: {COLOR_PRIMARY_DARK}; }}
            QPushButton:pressed {{ background-color: #0E1848; }}
        """)

        self.btn_remove = QPushButton('🗑️  પસંદ કરેલ હટાવો')
        self.btn_remove.setFixedHeight(36)
        self.btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_remove.setStyleSheet("""
            QPushButton {
                background-color: #FEF2F2; color: #DC2626;
                border: 1px solid #FECACA; border-radius: 8px;
                font-size: 12px; font-weight: 700; padding: 0 14px;
            }
            QPushButton:hover { background-color: #FEE2E2; border-color: #F87171; }
            QPushButton:pressed { background-color: #FECACA; }
        """)

        self.count_label = QLabel('કુલ નોંધાયેલ: ૦ / ૧૦')
        self.count_label.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {COLOR_TEXT_MUTED};")

        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_remove)
        btn_row.addStretch()
        btn_row.addWidget(self.count_label)

        # Table
        cols = self.COLUMNS_EN if self._current_lang == 'en' else self.COLUMNS_GU
        self.table = QTableWidget(0, len(cols))
        self.table.setHorizontalHeaderLabels(cols)

        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 75)   # No
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)         # Name
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Relation
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Age
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)         # Education
        hdr.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents) # Blood Group
        hdr.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)         # Occupation
        hdr.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)         # Contact Number

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {COLOR_BORDER};
                background-color: #FFFFFF;
                alternate-background-color: #F8FAFC;
                color: {COLOR_TEXT_MAIN};
                font-size: 12px;
                gridline-color: #E2E8F0;
                border-radius: 8px;
            }}
            QHeaderView::section {{
                background-color: #1B2F8A;
                color: #FFFFFF;
                padding: 6px 4px;
                font-size: 11px;
                font-weight: 700;
                border: 1px solid #142268;
            }}
            QTableWidget::item:selected {{
                background-color: #EFF6FF;
                color: #1B2F8A;
            }}
            QLineEdit {{
                background-color: #FFFFFF;
                color: {COLOR_TEXT_MAIN};
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {COLOR_PRIMARY};
            }}
            QComboBox {{
                background-color: #FFFFFF;
                color: {COLOR_TEXT_MAIN};
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding: 1px 4px;
                font-size: 12px;
            }}
            QSpinBox {{
                background-color: #FFFFFF;
                color: {COLOR_TEXT_MAIN};
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding: 1px 4px;
                font-size: 12px;
            }}
        """)
        self.table.setMinimumHeight(220)

        layout.addLayout(btn_row)
        layout.addWidget(self.table)

        self.btn_add.clicked.connect(self.add_empty_row)
        self.btn_remove.clicked.connect(self.remove_selected_row)

    # ------------------------------------------------------------------
    def set_language(self, lang: str = 'gu') -> None:
        """Update table headers, buttons, and row dropdowns for selected language."""
        self._current_lang = lang
        cols = self.COLUMNS_EN if lang == 'en' else self.COLUMNS_GU
        self.table.setHorizontalHeaderLabels(cols)

        if lang == 'en':
            self.btn_add.setText('➕  Add Family Member')
            self.btn_remove.setText('🗑️  Remove Selected')
        else:
            self.btn_add.setText('➕  પરિવાર સભ્ય ઉમેરો')
            self.btn_remove.setText('🗑️  પસંદ કરેલ હટાવો')

        self._update_serial_numbers()

        # Update relation dropdowns in all rows
        rel_items = RELATIONS_EN if lang == 'en' else RELATIONS_GU
        for r in range(self.table.rowCount()):
            combo = self.table.cellWidget(r, 2)
            if isinstance(combo, QComboBox):
                curr = combo.currentText().strip()
                if lang == 'en':
                    target = GU_TO_EN_REL.get(curr, curr)
                else:
                    target = EN_TO_GU_REL.get(curr, curr)

                combo.blockSignals(True)
                combo.clear()
                combo.addItems(rel_items)
                found = combo.findText(target)
                if found >= 0:
                    combo.setCurrentIndex(found)
                combo.blockSignals(False)

    def _update_serial_numbers(self) -> None:
        total = self.table.rowCount()
        for r in range(total):
            item = self.table.item(r, 0)
            if not item:
                item = QTableWidgetItem()
                self.table.setItem(r, 0, item)
            item.setText(f" {r + 1} ")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        if self._current_lang == 'en':
            self.count_label.setText(f'Total Registered: {total} / 10')
        else:
            self.count_label.setText(f'કુલ નોંધાયેલ: {total} / ૧૦')

    def add_empty_row(self, data: dict | None = None) -> int:
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Col 0: Sr. No.
        sr_item = QTableWidgetItem(f" {row + 1} ")
        sr_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        sr_item.setFlags(sr_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 0, sr_item)

        # Col 1: Name
        name_val = data.get('name', '') if data else ''
        self.table.setItem(row, 1, QTableWidgetItem(name_val))

        # Col 2: Relation
        rel_box = QComboBox()
        rel_items = RELATIONS_EN if self._current_lang == 'en' else RELATIONS_GU
        rel_box.addItems(rel_items)
        if data:
            raw_rel = data.get('relation', '').strip()
            # If in English mode but raw is Gujarati or vice versa, convert
            if self._current_lang == 'en':
                target_rel = GU_TO_EN_REL.get(raw_rel, raw_rel)
            else:
                target_rel = EN_TO_GU_REL.get(raw_rel, raw_rel)

            found_idx = rel_box.findText(target_rel)
            if found_idx < 0 and target_rel:
                for idx in range(rel_box.count()):
                    if target_rel.lower() in rel_box.itemText(idx).lower():
                        found_idx = idx
                        break
            if found_idx >= 0:
                rel_box.setCurrentIndex(found_idx)
        self.table.setCellWidget(row, 2, rel_box)

        # Col 3: Age
        age_box = QSpinBox()
        age_box.setRange(0, 120)
        age_box.setSpecialValueText('' if self._current_lang == 'en' else '')
        if data and data.get('age') is not None:
            try:
                age_box.setValue(int(data['age']))
            except (ValueError, TypeError):
                pass
        self.table.setCellWidget(row, 3, age_box)

        # Col 4: Education
        edu_val = data.get('education', '') if data else ''
        self.table.setItem(row, 4, QTableWidgetItem(edu_val))

        # Col 5: Blood Group
        bg_box = QComboBox()
        bg_box.addItems(BLOOD_GROUPS)
        if data:
            target_bg = data.get('blood_group', '').strip()
            found_bg = bg_box.findText(target_bg)
            if found_bg >= 0:
                bg_box.setCurrentIndex(found_bg)
        self.table.setCellWidget(row, 5, bg_box)

        # Col 6: Occupation
        occ_val = data.get('occupation', '') if data else ''
        self.table.setItem(row, 6, QTableWidgetItem(occ_val))

        # Col 7: Contact Number
        phone_val = data.get('contact_number', '') if data else ''
        self.table.setItem(row, 7, QTableWidgetItem(phone_val))

        self.table.setRowHeight(row, 32)
        self._update_serial_numbers()
        return row

    def remove_selected_row(self) -> None:
        rows = sorted(set(idx.row() for idx in self.table.selectedIndexes()), reverse=True)
        for row in rows:
            self.table.removeRow(row)
        self._update_serial_numbers()

    def get_rows(self) -> list[dict]:
        """Return list of dicts for each non-empty row."""
        rows = []
        for r in range(self.table.rowCount()):
            name_item = self.table.item(r, 1)
            name = name_item.text().strip() if name_item else ''
            if not name:
                continue

            rel_widget = self.table.cellWidget(r, 2)
            age_widget = self.table.cellWidget(r, 3)
            edu_item   = self.table.item(r, 4)
            bg_widget  = self.table.cellWidget(r, 5)
            occ_item   = self.table.item(r, 6)
            con_item   = self.table.item(r, 7)

            age_val = age_widget.value() if age_widget else 0
            rel_txt = rel_widget.currentText().strip() if rel_widget else ''
            # Normalize relation: if in English, can keep English or convert
            rows.append({
                'name':           name,
                'relation':       rel_txt,
                'age':            age_val if age_val > 0 else None,
                'education':      edu_item.text().strip() if edu_item else '',
                'blood_group':    bg_widget.currentText() if bg_widget else '',
                'occupation':     occ_item.text().strip() if occ_item else '',
                'contact_number': con_item.text().strip() if con_item else '',
            })
        return rows

    def load_rows(self, family_members: list) -> None:
        """Populate table from a list of FamilyMember ORM objects or dicts."""
        self.table.setRowCount(0)
        for fm in family_members:
            if hasattr(fm, 'name'):
                self.add_empty_row({
                    'name':           fm.name or '',
                    'relation':       fm.relation or '',
                    'age':            fm.age,
                    'education':      fm.education or '',
                    'blood_group':    fm.blood_group or '',
                    'occupation':     fm.occupation or '',
                    'contact_number': fm.contact_number or '',
                })
            elif isinstance(fm, dict):
                self.add_empty_row(fm)
        self._update_serial_numbers()
