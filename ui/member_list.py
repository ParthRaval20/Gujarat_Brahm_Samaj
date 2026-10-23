"""
Modern Member List Page — Matching Stitch Design Revamp.
Features:
- Header bar with All Members directory branding and Quick Add action
- Search input with City dropdown filter
- Modern styled Table with dark slate header (#0F172A), status pills, and action buttons
- Pagination bar with smooth page navigation
"""

from __future__ import annotations

import os

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCursor, QFont, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox, QComboBox, QFrame, QFileDialog,
)

from app.config import (
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_BG, COLOR_CARD_BG,
    COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    COLOR_ACCENT_BLUE, COLOR_ACCENT_EMERALD, COLOR_ACCENT_PURPLE,
    COLOR_ACCENT_ROSE, EXPORT_DIR,
)
from services.member_service import MemberService
from services.search_service import SearchService
from services.import_export_service import ImportExportService
from ui.import_data_dialog import ImportDataDialog

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
}


class MemberListPage(QWidget):
    PAGE_SIZE = 50

    def __init__(self, nav_callback, on_data_updated=None, parent=None):
        super().__init__(parent)
        self._nav = nav_callback
        self._on_data_updated = on_data_updated
        self._member_svc = MemberService()
        self._search_svc = SearchService()
        self._offset = 0
        self._current_lang = 'gu'
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._do_search)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 24)
        layout.setSpacing(16)

        # ── 1. Top Header ────────────────────────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(12)

        icon_box = QLabel("👥")
        icon_box.setFixedSize(40, 40)
        icon_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_box.setStyleSheet(f"""
            background-color: #EFF6FF;
            color: {COLOR_ACCENT_BLUE};
            border-radius: 10px;
            font-size: 18px;
        """)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)
        self.title_lbl = QLabel("બધા સભ્યોની ડિરેક્ટરી (All Members Directory)")
        self.title_lbl.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {COLOR_TEXT_MAIN};")

        self.subtitle = QLabel("સમાજના તમામ નોંધાયેલા સભ્યોની યાદી, વિસ્તૃત શોધ અને સંચાલન")
        self.subtitle.setStyleSheet(f"font-size: 11px; font-weight: 500; color: {COLOR_TEXT_MUTED};")

        title_vbox.addWidget(self.title_lbl)
        title_vbox.addWidget(self.subtitle)

        hdr.addWidget(icon_box)
        hdr.addLayout(title_vbox)
        hdr.addStretch()

        self.delete_all_btn = QPushButton("🗑️  બધા સભ્યો રદ કરો")
        self.delete_all_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.delete_all_btn.setFixedHeight(38)
        self.delete_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #FEF2F2; color: #DC2626;
                border: 1px solid #FECACA; border-radius: 8px;
                font-size: 12px; font-weight: 700; padding: 0 14px;
            }
            QPushButton:hover {
                background-color: #FEE2E2;
                border-color: #F87171;
                color: #B91C1C;
            }
        """)
        self.delete_all_btn.clicked.connect(self._delete_all_members)
        hdr.addWidget(self.delete_all_btn)

        self.import_btn = QPushButton("📥  ડેટા આયાત (Import)")
        self.import_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.import_btn.setFixedHeight(38)
        self.import_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF; color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER}; border-radius: 8px;
                font-size: 12px; font-weight: 700; padding: 0 14px;
            }}
            QPushButton:hover {{
                background-color: #EFF6FF;
                border-color: {COLOR_ACCENT_BLUE};
                color: {COLOR_ACCENT_BLUE};
            }}
        """)
        self.import_btn.clicked.connect(self._open_import_dialog)
        hdr.addWidget(self.import_btn)

        self.export_btn = QPushButton("📤  એક્સપોર્ટ (Export)")
        self.export_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.export_btn.setFixedHeight(38)
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF; color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER}; border-radius: 8px;
                font-size: 12px; font-weight: 700; padding: 0 14px;
            }}
            QPushButton:hover {{ background-color: #F8FAFC; }}
        """)
        self.export_btn.clicked.connect(self._export_members)
        hdr.addWidget(self.export_btn)

        self.add_btn = QPushButton("➕  નવો સભ્ય ઉમેરો")
        self.add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_btn.setFixedHeight(38)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT_BLUE}; color: white;
                border: none; border-radius: 8px;
                font-size: 12px; font-weight: 700; padding: 0 18px;
            }}
            QPushButton:hover {{ background-color: {COLOR_PRIMARY_DARK}; }}
        """)
        self.add_btn.clicked.connect(lambda: self._nav('add'))
        hdr.addWidget(self.add_btn)
        layout.addLayout(hdr)

        # ── 2. Filter & Search Bar ───────────────────────────────────
        filter_card = QFrame()
        filter_card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER};
                border-radius: 10px;
                padding: 4px;
            }}
        """)
        fc_layout = QHBoxLayout(filter_card)
        fc_layout.setContentsMargins(10, 6, 10, 6)
        fc_layout.setSpacing(10)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍  નામ, મોબાઈલ, સભ્ય કોડ, શહેર અથવા વ્યવસાય દ્વારા શોધો...")
        self.search_edit.setFixedHeight(36)
        self.search_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: #F8FAFC;
                color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER}; border-radius: 8px;
                padding: 0 12px; font-size: 12px;
            }}
            QLineEdit:focus {{
                border-color: {COLOR_ACCENT_BLUE};
                background-color: #FFFFFF;
            }}
        """)
        self.search_edit.textChanged.connect(lambda: self._search_timer.start(250))
        fc_layout.addWidget(self.search_edit, stretch=1)

        self.city_filter = QComboBox()
        self.city_filter.setFixedHeight(36)
        self.city_filter.setMinimumWidth(180)
        self.city_filter.setStyleSheet(f"""
            QComboBox {{
                background-color: #F8FAFC;
                color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER}; border-radius: 8px;
                padding: 0 12px; font-size: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #FFFFFF;
                color: {COLOR_TEXT_MAIN};
                selection-background-color: #EFF6FF;
                selection-color: {COLOR_ACCENT_BLUE};
            }}
        """)
        self.city_filter.currentIndexChanged.connect(self._do_search)
        fc_layout.addWidget(self.city_filter)

        self.btn_reset = QPushButton("ફિલ્ટર્સ રીસેટ")
        self.btn_reset.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_reset.setFixedHeight(36)
        self.btn_reset.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER}; border-radius: 8px;
                padding: 0 14px; font-size: 12px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #F1F5F9; }}
        """)
        self.btn_reset.clicked.connect(self._reset_filters)
        fc_layout.addWidget(self.btn_reset)

        layout.addWidget(filter_card)

        # ── 3. Table ─────────────────────────────────────────────────
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            'સભ્ય કોડ (Code)',
            'સભ્યનું પૂરું નામ (Full Name)',
            "પિતા / વાલીનું નામ (Father's Name)",
            'મોબાઇલ નંબર (Mobile)',
            'શહેર (City)',
            'સ્થિતિ (Status)',
            'કાર્ય (Actions)',
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: #FFFFFF;
                alternate-background-color: #F8FAFC;
                color: {COLOR_TEXT_MAIN};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
                gridline-color: transparent;
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 8px;
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
        layout.addWidget(self.table, stretch=1)

        # ── 4. Pagination Bar ────────────────────────────────────────
        pag = QHBoxLayout()
        pag.setSpacing(10)

        self.prev_btn = QPushButton("◀ અગાઉનું")
        self.prev_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.prev_btn.clicked.connect(self._prev_page)

        self.next_btn = QPushButton("આગળ ▶")
        self.next_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.next_btn.clicked.connect(self._next_page)

        self.page_label = QLabel("")
        self.page_label.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLOR_TEXT_MAIN}; padding: 0 10px;")

        for btn in (self.prev_btn, self.next_btn):
            btn.setFixedHeight(34)
            btn.setStyleSheet(f"""
                QPushButton {{
                    border: 1px solid {COLOR_BORDER}; border-radius: 8px;
                    font-size: 12px; font-weight: 600; color: {COLOR_TEXT_MAIN};
                    padding: 0 16px; background-color: #FFFFFF;
                }}
                QPushButton:hover {{ background-color: #F1F5F9; }}
                QPushButton:disabled {{ color: #CBD5E1; border-color: #E2E8F0; background-color: #F8FAFC; }}
            """)

        pag.addWidget(self.prev_btn)
        pag.addWidget(self.page_label)
        pag.addWidget(self.next_btn)
        pag.addStretch()
        layout.addLayout(pag)

    def _refresh_city_filter(self):
        cities = self._member_svc.get_distinct_cities()
        is_en = (self._current_lang == 'en')
        curr_data = self.city_filter.currentData()
        self.city_filter.blockSignals(True)
        self.city_filter.clear()
        self.city_filter.addItem("All Cities" if is_en else "તમામ શહેર", "")
        for c in cities:
            disp = CITY_TRANSLATIONS.get(c, c) if is_en else c
            self.city_filter.addItem(disp, c)
        if curr_data:
            idx = self.city_filter.findData(curr_data)
            if idx >= 0:
                self.city_filter.setCurrentIndex(idx)
        self.city_filter.blockSignals(False)

    def _reset_filters(self):
        self.search_edit.clear()
        self.city_filter.setCurrentIndex(0)
        self._offset = 0
        self.load_members()

    def load_members(self):
        """Load the current page of members with filters."""
        self._refresh_city_filter()
        query = self.search_edit.text().strip()
        selected_city = self.city_filter.currentData()
        if selected_city is None:
            txt = self.city_filter.currentText()
            selected_city = "" if txt in ("તમામ શહેર", "All Cities", "તમામ શહેર (All Cities)") else txt

        if query:
            results = self._search_svc.search(query)
            if selected_city:
                results = [m for m in results if (m.city or "").strip() == selected_city]
            self._populate(results)
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            total = len(results)
            if self._current_lang == 'en':
                self.page_label.setText(f"{total} Results")
            else:
                self.page_label.setText(f"{total} પરિણામો")
        else:
            if selected_city:
                # filter all members matching selected city
                all_m = self._member_svc.get_all(0, 50000)
                filtered = [m for m in all_m if (m.city or "").strip() == selected_city]
                total = len(filtered)
                paged = filtered[self._offset : self._offset + self.PAGE_SIZE]
                self._populate(paged)
            else:
                total = self._member_svc.count()
                paged = self._member_svc.get_all(self._offset, self.PAGE_SIZE)
                self._populate(paged)

            page = (self._offset // self.PAGE_SIZE) + 1
            pages = max(1, (total + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
            if self._current_lang == 'en':
                self.page_label.setText(f"Page {page} of {pages}  (Total: {total} members)")
            else:
                self.page_label.setText(f"પાનું {page} / {pages}  (કુલ {total} સભ્યો)")
            self.prev_btn.setEnabled(self._offset > 0)
            self.next_btn.setEnabled(self._offset + self.PAGE_SIZE < total)

    def _populate(self, members: list):
        # Cleanly unparent existing action cell widgets
        for r in range(self.table.rowCount()):
            w = self.table.cellWidget(r, 6)
            if w:
                w.setParent(None)
        self.table.setRowCount(0)

        if not members:
            self.table.setRowCount(1)
            msg = "No members found." if self._current_lang == 'en' else "કોઈ સભ્યો મળ્યા નથી."
            no_data = QTableWidgetItem(msg)
            no_data.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data.setForeground(Qt.GlobalColor.gray)
            self.table.setItem(0, 0, no_data)
            self.table.setSpan(0, 0, 1, 7)
            return

        for row, member in enumerate(members):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 44)

            # 0. Code (Blue mono font)
            item_code = QTableWidgetItem(member.member_code)
            item_code.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            item_code.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
            item_code.setForeground(QColor("#2563EB"))
            self.table.setItem(row, 0, item_code)

            # 1. Full name
            name_text = member.full_name or ""
            if member.surname and member.surname not in name_text:
                name_text = f"{member.full_name} ({member.surname})"
            item_name = QTableWidgetItem(name_text)
            item_name.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            item_name.setForeground(QColor("#0F172A"))
            self.table.setItem(row, 1, item_name)

            # 2. Father
            item_father = QTableWidgetItem(member.father_name or "—")
            item_father.setFont(QFont("Segoe UI", 10))
            item_father.setForeground(QColor("#334155"))
            self.table.setItem(row, 2, item_father)

            # 3. Mobile
            item_mob = QTableWidgetItem(member.mobile or "—")
            item_mob.setFont(QFont("Consolas", 10))
            item_mob.setForeground(QColor("#334155"))
            self.table.setItem(row, 3, item_mob)

            # 4. City (Clean aligned native cell)
            disp_city = CITY_TRANSLATIONS.get(member.city, member.city) if self._current_lang == 'en' else member.city
            item_city = QTableWidgetItem(disp_city or "—")
            item_city.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            item_city.setFont(QFont("Segoe UI", 10))
            item_city.setForeground(QColor("#334155"))
            self.table.setItem(row, 4, item_city)

            # 5. Status (Active / સક્રિય)
            status_text = "●  Active" if self._current_lang == 'en' else "●  સક્રિય"
            item_status = QTableWidgetItem(status_text)
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_status.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            item_status.setForeground(QColor("#059669"))
            self.table.setItem(row, 5, item_status)

            # 6. Action buttons (View, Edit, Print, Delete)
            act_widget = QWidget()
            act_layout = QHBoxLayout(act_widget)
            act_layout.setContentsMargins(4, 2, 4, 2)
            act_layout.setSpacing(5)

            btn_view = QPushButton("👁")
            btn_view.setToolTip("View Member" if self._current_lang == 'en' else "સભ્ય જુઓ")
            btn_view.setFixedSize(28, 28)
            btn_view.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_view.setStyleSheet("""
                QPushButton {
                    background-color: #EFF6FF; color: #2563EB;
                    border: 1px solid #BFDBFE; border-radius: 6px; font-size: 12px;
                }
                QPushButton:hover { background-color: #DBEAFE; }
                QToolTip {
                    background-color: #0F172A; color: #FFFFFF;
                    border: 1px solid #334155; border-radius: 6px;
                    padding: 5px 9px; font-size: 11px; font-weight: 500;
                }
            """)
            mid = member.id
            btn_view.clicked.connect(lambda _, m=mid: self._nav('profile', member_id=m))

            btn_edit = QPushButton("✏️")
            btn_edit.setToolTip("Edit Member" if self._current_lang == 'en' else "સુધારો કરો")
            btn_edit.setFixedSize(28, 28)
            btn_edit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #ECFDF5; color: #059669;
                    border: 1px solid #A7F3D0; border-radius: 6px; font-size: 12px;
                }
                QPushButton:hover { background-color: #D1FAE5; }
                QToolTip {
                    background-color: #0F172A; color: #FFFFFF;
                    border: 1px solid #334155; border-radius: 6px;
                    padding: 5px 9px; font-size: 11px; font-weight: 500;
                }
            """)
            btn_edit.clicked.connect(lambda _, m=mid: self._nav('edit', member_id=m))

            btn_print = QPushButton("🖨️")
            btn_print.setToolTip("Print / Form PDF" if self._current_lang == 'en' else "ફોર્મ / પ્રિન્ટ")
            btn_print.setFixedSize(28, 28)
            btn_print.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_print.setStyleSheet("""
                QPushButton {
                    background-color: #F5F3FF; color: #7C3AED;
                    border: 1px solid #DDD6FE; border-radius: 6px; font-size: 12px;
                }
                QPushButton:hover { background-color: #EDE9FE; }
                QToolTip {
                    background-color: #0F172A; color: #FFFFFF;
                    border: 1px solid #334155; border-radius: 6px;
                    padding: 5px 9px; font-size: 11px; font-weight: 500;
                }
            """)
            btn_print.clicked.connect(lambda _, m=mid: self._nav('form_preview', member_id=mid))

            btn_del = QPushButton("🗑️")
            btn_del.setToolTip("Delete Member" if self._current_lang == 'en' else "સભ્ય રદ કરો")
            btn_del.setFixedSize(28, 28)
            btn_del.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: #FEF2F2; color: #DC2626;
                    border: 1px solid #FECACA; border-radius: 6px; font-size: 12px;
                }
                QPushButton:hover { background-color: #FEE2E2; }
                QToolTip {
                    background-color: #0F172A; color: #FFFFFF;
                    border: 1px solid #334155; border-radius: 6px;
                    padding: 5px 9px; font-size: 11px; font-weight: 500;
                }
            """)
            btn_del.clicked.connect(lambda _, m=mid: self._delete_member(m))

            act_layout.addWidget(btn_view)
            act_layout.addWidget(btn_edit)
            act_layout.addWidget(btn_print)
            act_layout.addWidget(btn_del)
            act_layout.addStretch()

            self.table.setCellWidget(row, 6, act_widget)

    def _do_search(self):
        self._offset = 0
        self.load_members()

    def _prev_page(self):
        self._offset = max(0, self._offset - self.PAGE_SIZE)
        self.load_members()

    def _next_page(self):
        self._offset += self.PAGE_SIZE
        self.load_members()

    def _delete_member(self, member_id: int):
        reply = QMessageBox.question(
            self, 'સભ્ય રદ પુષ્ટિ (Confirm Delete)',
            'શું તમે ખરેખર આ સભ્યને કાઢી નાખવા માંગો છો?\n'
            'આ ક્રિયાથી તમામ સંકળાયેલ કુટુંબ રેકોર્ડ્સ પણ રદ થશે.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            MemberService().delete_member(member_id)
            self.load_members()
            if self._on_data_updated:
                self._on_data_updated()

    def _delete_all_members(self):
        """Prompt user with confirmation and delete all members & family members from the database."""
        is_en = (self._current_lang == 'en')
        count = self._member_svc.count()
        if count == 0:
            title = "No Members" if is_en else "કોઈ સભ્યો નથી"
            msg = (
                "There are no members in the database to delete."
                if is_en else
                "ડેટાબેઝમાં કાઢી નાખવા માટે કોઈ સભ્યો નથી."
            )
            QMessageBox.information(self, title, msg)
            return

        title = "Confirm Delete All Members" if is_en else "તમામ સભ્યો રદ કરવાની પુષ્ટિ (Confirm Delete All)"
        msg = (
            f"Are you ABSOLUTELY sure you want to delete ALL {count} members and their family records from the database?\n\n"
            "⚠️ WARNING: This action cannot be undone! All member profiles, family data, and records will be permanently erased."
            if is_en else
            f"શું તમે ખરેખર ડેટાબેઝમાંથી તમામ {count} સભ્યો અને તેમના કુંટુંબની વિગતો કાયમ માટે રદ કરવા માંગો છો?\n\n"
            "⚠️ ચેતવણી: આ ક્રિયા પાછી વાળી શકાશે નહીં! તમામ સભ્યોનો ડેટા કાયમ માટે ભૂંસાઈ જશે."
        )

        reply = QMessageBox.warning(
            self,
            title,
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            deleted_count = self._member_svc.delete_all_members()
            self._offset = 0
            self.load_members()
            if self._on_data_updated:
                self._on_data_updated()

            succ_title = "All Members Deleted" if is_en else "તમામ સભ્યો રદ કર્યા"
            succ_msg = (
                f"Successfully deleted {deleted_count} members and their associated records."
                if is_en else
                f"સફળતાપૂર્વક {deleted_count} સભ્યો અને તેમનો તમામ ડેટા રદ કરવામાં આવ્યો છે."
            )
            QMessageBox.information(self, succ_title, succ_msg)


    def _open_import_dialog(self):
        """Open the data import dialog and refresh members on completion."""
        dlg = ImportDataDialog(self)
        dlg.import_finished.connect(self._on_import_finished)
        dlg.exec()

    def _on_import_finished(self, result):
        """Refresh data after successful import."""
        self.load_members()
        self._refresh_city_filter()
        if self._on_data_updated:
            self._on_data_updated()

    def _export_members(self):
        """Export all registered members to an Excel or CSV file."""
        from datetime import datetime
        ts = datetime.now().strftime("%Y_%m_%d_%H%M")
        default_path = os.path.join(EXPORT_DIR, f"members_export_{ts}.xlsx")

        path, sel_filter = QFileDialog.getSaveFileName(
            self,
            "સભ્યોનો ડેટા એક્સપોર્ટ કરો",
            default_path,
            "Excel Files (*.xlsx);;CSV Files (*.csv)",
        )
        if not path:
            return

        fmt = "csv" if path.lower().endswith(".csv") else "xlsx"
        try:
            total, out_file = ImportExportService.export_members_to_file(path, fmt)
            QMessageBox.information(
                self,
                "એક્સપોર્ટ સફળ",
                f"કુલ {total} સભ્યોનો ડેટા સફળતાપૂર્વક એક્સપોર્ટ થયેલ છે:\n\n{out_file}",
            )
        except Exception as e:
            QMessageBox.critical(self, "ક્ષતિ", f"એક્સપોર્ટ કરવામાં ક્ષતિ આવી:\n{str(e)}")

    def set_language(self, lang: str):
        """Update member list text dynamically when language changes."""
        from app.translations import t
        self._current_lang = lang

        if hasattr(self, 'title_lbl'):
            self.title_lbl.setText(t('list_title', lang))
        if hasattr(self, 'subtitle'):
            self.subtitle.setText(t('list_sub', lang))
        if hasattr(self, 'add_btn'):
            self.add_btn.setText(t('list_btn_add', lang))
        if hasattr(self, 'delete_all_btn'):
            self.delete_all_btn.setText(t('list_btn_delete_all', lang))
        if hasattr(self, 'import_btn'):
            self.import_btn.setText(t('list_btn_import', lang))
        if hasattr(self, 'export_btn'):
            self.export_btn.setText(t('list_btn_export', lang))
        if hasattr(self, 'btn_reset'):
            self.btn_reset.setText(t('list_btn_reset', lang))
        if hasattr(self, 'prev_btn'):
            self.prev_btn.setText(t('list_prev', lang))
        if hasattr(self, 'next_btn'):
            self.next_btn.setText(t('list_next', lang))
        if hasattr(self, 'search_edit'):
            self.search_edit.setPlaceholderText(t('list_search_placeholder', lang))

        if hasattr(self, 'city_filter'):
            self._refresh_city_filter()

        if hasattr(self, 'table'):
            if lang == 'en':
                self.table.setHorizontalHeaderLabels([
                    "Member Code", "Full Name", "Father / Guardian",
                    "Mobile Number", "City / Village", "Status", "Actions"
                ])
            else:
                self.table.setHorizontalHeaderLabels([
                    "સભ્ય કોડ", "સભ્યનું પૂરું નામ", "પિતા / વાલીનું નામ",
                    "મોબાઇલ નંબર", "શહેર / ગામ", "સ્થિતિ", "કાર્ય"
                ])
            # Re-render current page with new language
            self._do_search()
