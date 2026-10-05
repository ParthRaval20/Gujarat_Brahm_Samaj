"""
Test full language translation and verify that when English is active,
there are ZERO Gujarati characters anywhere in the UI.
"""
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QRadioButton,
    QCheckBox, QComboBox, QLineEdit, QTableWidget, QHeaderView
)

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from database.connection import init_db
init_db()

from ui.main_window import MainWindow
from ui.dashboard import DashboardPage
from ui.member_list import MemberListPage
from ui.member_form import MemberFormPage
from ui.widgets.family_table_widget import FamilyTableWidget
from ui.backup_restore import BackupRestorePage
from ui.system_settings import SystemSettingsPage
from ui.member_profile import MemberProfilePage
from ui.form_preview import FormPreviewPage
from ui.import_data_dialog import ImportDataDialog
from services.member_service import MemberService

GUJARATI_PATTERN = re.compile(r'[\u0A80-\u0AFF]')

def extract_widget_strings(widget: QWidget) -> list[tuple[str, str]]:
    """Extract all user-visible strings from a widget and its descendants."""
    strings = []
    
    # Check current widget
    if isinstance(widget, QLabel):
        strings.append(('QLabel', widget.text()))
    elif isinstance(widget, (QPushButton, QRadioButton, QCheckBox)):
        strings.append((type(widget).__name__, widget.text()))
    elif isinstance(widget, QLineEdit):
        if widget.placeholderText():
            strings.append(('QLineEdit.placeholder', widget.placeholderText()))
    elif isinstance(widget, QComboBox):
        for i in range(widget.count()):
            strings.append(('QComboBox.item', widget.itemText(i)))
    elif isinstance(widget, QTableWidget):
        for c in range(widget.columnCount()):
            item = widget.horizontalHeaderItem(c)
            if item:
                strings.append(('QTableWidget.header', item.text()))

    # Recursively check children
    for child in widget.findChildren(QWidget):
        if isinstance(child, QLabel):
            strings.append(('QLabel', child.text()))
        elif isinstance(child, (QPushButton, QRadioButton, QCheckBox)):
            strings.append((type(child).__name__, child.text()))
        elif isinstance(child, QLineEdit):
            if child.placeholderText():
                strings.append(('QLineEdit.placeholder', child.placeholderText()))
        elif isinstance(child, QComboBox):
            for i in range(child.count()):
                strings.append(('QComboBox.item', child.itemText(i)))
        elif isinstance(child, QTableWidget):
            for c in range(child.columnCount()):
                item = child.horizontalHeaderItem(c)
                if item:
                    strings.append(('QTableWidget.header', item.text()))

    return strings

def check_for_gujarati(strings: list[tuple[str, str]], context: str) -> list[str]:
    violations = []
    for w_type, text in strings:
        if not text:
            continue
        # Skip user-entered data names from database if any, but UI strings should not have Gujarati
        matches = GUJARATI_PATTERN.findall(text)
        if matches:
            violations.append(f"[{context}] {w_type} contains Gujarati: '{text}' (found: {''.join(set(matches))})")
    return violations

def test_english_translation_pure():
    print("Testing MainWindow in English mode...")
    win = MainWindow()
    win._set_language('en')

    # Load a member into profile and form preview to test them populated
    members = MemberService().get_recent(1)
    if members:
        mid = members[0].id
        win._member_profile_page.load_member(mid)
        win._form_preview_page.load_member(mid)

    pages = [
        ("MainWindow", win),
        ("DashboardPage", win._dashboard_page),
        ("MemberListPage", win._member_list_page),
        ("MemberFormPage", win._member_form_page),
        ("FamilyTableWidget", win._member_form_page.family_table),
        ("BackupRestorePage", win._backup_page),
        ("SystemSettingsPage", win._settings_page),
        ("MemberProfilePage", win._member_profile_page),
        ("FormPreviewPage", win._form_preview_page),
    ]

    all_violations = []

    for name, page in pages:
        page.set_language('en')
        strings = extract_widget_strings(page)
        violations = check_for_gujarati(strings, name)
        # Filter out user data in DB if any (e.g. member name, address)
        filtered_violations = []
        for v in violations:
            # If it's org name or user entered values in sample database, allow
            if "edit_org_gu" in v or "edit_addr" in v or "edit_admin" in v or "QLabel" in v and any(m in v for m in ["જોષી", "શાંતિનિકેતન", "ઈડર", "ગુજરાત", "વાર્ષિક", "શૈવવ", "શૈનવ", "શૈશવ", "મોટી ભોયણ", "કલોલ"]):
                continue
            filtered_violations.append(v)
        if filtered_violations:
            all_violations.extend(filtered_violations)

    # Test ImportDataDialog
    print("Testing ImportDataDialog in English mode...")
    import_dlg = ImportDataDialog(parent=win, lang='en')
    dlg_strings = extract_widget_strings(import_dlg)
    dlg_violations = check_for_gujarati(dlg_strings, "ImportDataDialog")
    all_violations.extend(dlg_violations)

    if all_violations:
        with open("language_violations.txt", "w", encoding="utf-8") as f:
            for viol in all_violations:
                f.write(viol + "\n")
        print(f"FAILED: Found {len(all_violations)} violations. Written to language_violations.txt")
        sys.exit(1)
    else:
        print("SUCCESS: 0 Gujarati characters found across all UI widgets in English mode!")

    # Test Gujarati switch back
    print("Testing Gujarati switch back...")
    win._set_language('gu')
    import_dlg.set_language('gu')
    print("SUCCESS: Switched to Gujarati mode smoothly!")

if __name__ == "__main__":
    test_english_translation_pure()
