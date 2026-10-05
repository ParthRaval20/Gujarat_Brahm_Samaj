"""Test MemberListPage Delete All button and workflow."""

import os
import sys
import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import init_db
from services.member_service import MemberService
from services.family_service import FamilyService
from ui.member_list import MemberListPage
from app.translations import t


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    import app.config as cfg
    db = str(tmp_path / "test.db")
    monkeypatch.setattr(cfg, "DB_PATH", db)
    monkeypatch.setattr(cfg, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(cfg, "BACKUP_DIR", str(tmp_path / "backups"))
    monkeypatch.setattr(cfg, "EXPORT_DIR", str(tmp_path / "exports"))
    monkeypatch.setattr(cfg, "LOG_DIR", str(tmp_path / "logs"))
    import database.connection as conn
    conn._engine = None
    conn._SessionLocal = None
    init_db()
    yield
    conn._engine = None
    conn._SessionLocal = None


def test_member_list_delete_all_workflow(qapp, monkeypatch):
    svc = MemberService()
    fsvc = FamilyService()

    # Seed members
    m1, _ = svc.create_member({
        'full_name': 'Raval Parth',
        'surname': 'Raval',
        'father_name': 'Mahesh Raval',
        'mobile': '9876543210',
        'city': 'Rajkot',
        'district': 'Rajkot',
        'state': 'Gujarat',
        'pincode': '360001',
    })
    fsvc.add_family_member(m1.id, {
        'name': 'Mahesh', 'relation': 'Father', 'age': 50,
        'contact_number': '9876543211',
    })

    updated_called = []
    def on_updated():
        updated_called.append(True)

    nav_called = []
    def nav(action, **kwargs):
        nav_called.append((action, kwargs))

    page = MemberListPage(nav_callback=nav, on_data_updated=on_updated)
    page.load_members()
    assert page.table.rowCount() == 1
    assert hasattr(page, 'delete_all_btn')
    assert "બધા સભ્યો રદ કરો" in page.delete_all_btn.text()

    # Test language switch
    page.set_language('en')
    assert "Delete All" in page.delete_all_btn.text()
    page.set_language('gu')
    assert "બધા સભ્યો રદ કરો" in page.delete_all_btn.text()

    # Test cancel deletion
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: QMessageBox.StandardButton.No)
    page.delete_all_btn.click()
    assert svc.count() == 1
    assert page.table.rowCount() == 1

    # Test confirm deletion
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: QMessageBox.StandardButton.Yes)
    info_shown = []
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: info_shown.append(a))
    page.delete_all_btn.click()

    assert svc.count() == 0
    assert fsvc.count_all() == 0
    assert len(updated_called) > 0
    assert len(info_shown) > 0

    # Test clicking when empty
    info_empty = []
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: info_empty.append(a))
    page.delete_all_btn.click()
    assert len(info_empty) > 0
