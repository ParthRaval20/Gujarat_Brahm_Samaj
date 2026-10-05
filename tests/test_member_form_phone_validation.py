"""Test phone and mobile input field restrictions in MemberFormPage."""

import os
import sys
import pytest
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import init_db
from ui.member_form import MemberFormPage


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


def test_mobile_and_phone_field_10_digits_only(qapp):
    nav_called = []
    def nav(action, **kwargs):
        nav_called.append((action, kwargs))

    form = MemberFormPage(nav_callback=nav)

    # 1. Test max length
    assert form.mobile_edit.maxLength() == 10
    assert form.phone_edit.maxLength() == 10
    assert form.pincode_edit.maxLength() == 6

    # 2. Test validators exist
    val_mob = form.mobile_edit.validator()
    val_phone = form.phone_edit.validator()
    assert val_mob is not None
    assert val_phone is not None

    # 3. Test entering valid 10 digits
    form.mobile_edit.setText("9876543210")
    assert form.mobile_edit.text() == "9876543210"

    form.phone_edit.setText("0282212345")
    assert form.phone_edit.text() == "0282212345"

    # 4. Test validator rejects letters and symbols
    # QRegularExpressionValidator.validate returns (State, text, pos)
    state_mob, _, _ = val_mob.validate("98765abc", 0)
    assert state_mob != val_mob.State.Acceptable

    state_phone, _, _ = val_phone.validate("028-12345", 0)
    assert state_phone != val_phone.State.Acceptable

    state_valid_mob, _, _ = val_mob.validate("9876543210", 0)
    assert state_valid_mob == val_mob.State.Acceptable

    state_valid_phone, _, _ = val_phone.validate("0282212345", 0)
    assert state_valid_phone == val_phone.State.Acceptable
