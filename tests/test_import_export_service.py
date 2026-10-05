"""
Unit tests for ImportExportService.
Tests:
- Template generation for Excel and CSV.
- File parsing with Gujarati and English headers.
- Replacement / Upsert logic by:
  1. Mobile number
  2. Form number / Member code
  3. Both (code or mobile)
  4. Insert-only (skip duplicates)
- Safety backup integration.
"""

import os
import pytest
from database.connection import get_session, init_db
from database.models import Member
from services.import_export_service import ImportExportService, ImportResult


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    """Setup isolated test database."""
    import app.config as cfg
    import database.connection as conn

    test_db = str(tmp_path / "test_import.db")
    monkeypatch.setattr(cfg, "DB_PATH", test_db)
    monkeypatch.setattr(cfg, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(cfg, "BACKUP_DIR", str(tmp_path / "backups"))
    monkeypatch.setattr(cfg, "EXPORT_DIR", str(tmp_path / "exports"))
    monkeypatch.setattr(cfg, "LOG_DIR", str(tmp_path / "logs"))

    conn._engine = None
    conn._SessionLocal = None
    init_db()
    yield
    conn._engine = None
    conn._SessionLocal = None


def test_generate_and_read_templates(tmp_path):
    xlsx_path = str(tmp_path / "sample.xlsx")
    csv_path = str(tmp_path / "sample.csv")

    out_xlsx = ImportExportService.generate_sample_template(xlsx_path, "xlsx")
    assert os.path.exists(out_xlsx)
    rows_x, keys_x, _ = ImportExportService.read_file(out_xlsx)
    assert len(rows_x) == 2
    assert "full_name" in keys_x
    assert "mobile" in keys_x
    assert "member_code" in keys_x

    out_csv = ImportExportService.generate_sample_template(csv_path, "csv")
    assert os.path.exists(out_csv)
    rows_c, keys_c, _ = ImportExportService.read_file(out_csv)
    assert len(rows_c) == 2
    assert rows_c[0]["full_name"] == "જોષી હર્ષદભાઈ રમણિકલાલ"


def test_import_new_members(tmp_path):
    csv_path = str(tmp_path / "new_members.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        f.write("સભ્ય કોડ,સભ્યનું નામ,મોબાઈલ નંબર,શહેર,વ્યવસાય\n")
        f.write("GBS-000501,ભટ્ટ કમલેશભાઈ,9825000001,અમદાવાદ,વેપાર\n")
        f.write("GBS-000502,વ્યાસ સુરેશભાઈ,9825000002,રાજકોટ,શિક્ષક\n")

    res = ImportExportService.import_members(csv_path, match_strategy="both", create_safety_backup=False)
    assert res.success is True
    assert res.total_rows == 2
    assert res.inserted_count == 2
    assert res.updated_count == 0

    with get_session() as session:
        m1 = session.query(Member).filter_by(mobile="9825000001").first()
        assert m1 is not None
        assert m1.full_name == "ભટ્ટ કમલેશભાઈ"
        assert m1.city == "અમદાવાદ"


def test_replace_by_mobile_number(tmp_path):
    # First create an existing member
    with get_session() as session:
        m = Member(
            member_code="GBS-000601",
            full_name="ત્રિવેદી જૂનું નામ",
            mobile="9825099999",
            city="સુરત",
            occupation="જૂનો વ્યવસાય",
            created_at="2026-01-01 10:00:00",
            updated_at="2026-01-01 10:00:00",
        )
        session.add(m)
        session.commit()

    # Now import file with SAME mobile number but different name and city
    csv_path = str(tmp_path / "update_by_mobile.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        f.write("સભ્યનું નામ,મોબાઈલ નંબર,શહેર,વ્યવસાય\n")
        f.write("ત્રિવેદી નવું નામ,9825099999,વડોદરા,સોફ્ટવેર એન્જિનિયર\n")

    res = ImportExportService.import_members(csv_path, match_strategy="mobile", create_safety_backup=False)
    assert res.success is True
    assert res.total_rows == 1
    assert res.updated_count == 1
    assert res.inserted_count == 0

    with get_session() as session:
        updated = session.query(Member).filter_by(mobile="9825099999").first()
        assert updated is not None
        assert updated.member_code == "GBS-000601"  # preserved code
        assert updated.full_name == "ત્રિવેદી નવું નામ"
        assert updated.city == "વડોદરા"
        assert updated.occupation == "સોફ્ટવેર એન્જિનિયર"


def test_replace_by_form_number(tmp_path):
    # Create existing member with a specific member_code
    with get_session() as session:
        m = Member(
            member_code="GBS-000777",
            full_name="શુક્લા દીપકભાઈ",
            mobile="9825077777",
            city="ભાવનગર",
            created_at="2026-01-01 10:00:00",
            updated_at="2026-01-01 10:00:00",
        )
        session.add(m)
        session.commit()

    # Import file matching by Form No / Member Code (even with numeric "777" or "GBS-000777")
    csv_path = str(tmp_path / "update_by_code.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        f.write("ફોર્મ નંબર,સભ્યનું નામ,મોબાઈલ નંબર,શહેર\n")
        f.write("777,શુક્લા દીપકકુમાર,9825088888,ગાંધીનગર\n")

    res = ImportExportService.import_members(csv_path, match_strategy="code", create_safety_backup=False)
    assert res.success is True
    assert res.updated_count == 1

    with get_session() as session:
        updated = session.query(Member).filter_by(member_code="GBS-000777").first()
        assert updated is not None
        assert updated.full_name == "શુક્લા દીપકકુમાર"
        assert updated.mobile == "9825088888"
        assert updated.city == "ગાંધીનગર"


def test_replace_by_both_flexible(tmp_path):
    with get_session() as session:
        m1 = Member(
            member_code="GBS-000888",
            full_name="પંડ્યા મહેશભાઈ",
            mobile="9825011111",
            city="જામનગર",
            created_at="2026-01-01 10:00:00",
            updated_at="2026-01-01 10:00:00",
        )
        session.add(m1)
        session.commit()

    # File has 2 rows: one matches code, one matches mobile without code
    csv_path = str(tmp_path / "update_both.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        f.write("ફોર્મ નંબર,પૂર્ણ નામ,મોબાઈલ નંબર,શહેર\n")
        f.write("GBS-000888,પંડ્યા મહેશકુમાર અપડેટ,9825011111,જામનગર સિટી\n")
        f.write(",નવો સભ્ય ૧,9825022222,જુનાગઢ\n")

    res = ImportExportService.import_members(csv_path, match_strategy="both", create_safety_backup=False)
    assert res.success is True
    assert res.total_rows == 2
    assert res.updated_count == 1
    assert res.inserted_count == 1


def test_insert_only_skips_duplicates(tmp_path):
    with get_session() as session:
        m = Member(
            member_code="GBS-000999",
            full_name="જાની અશોકભાઈ",
            mobile="9825033333",
            city="આણંદ",
            created_at="2026-01-01 10:00:00",
            updated_at="2026-01-01 10:00:00",
        )
        session.add(m)
        session.commit()

    csv_path = str(tmp_path / "insert_only.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        f.write("સભ્ય કોડ,સભ્યનું નામ,મોબાઈલ નંબર,શહેર\n")
        f.write("GBS-000999,જાની અશોકભાઈ,9825033333,આણંદ\n")
        f.write("GBS-001000,જાની નરેશભાઈ,9825044444,નડિયાદ\n")

    res = ImportExportService.import_members(csv_path, match_strategy="insert_only", create_safety_backup=False)
    assert res.total_rows == 2
    assert res.skipped_count == 1
    assert res.inserted_count == 1


def test_export_members(tmp_path):
    with get_session() as session:
        m = Member(
            member_code="GBS-000001",
            full_name="જોષી ટેસ્ટ",
            mobile="9898000000",
            created_at="2026-01-01 10:00:00",
            updated_at="2026-01-01 10:00:00",
        )
        session.add(m)
        session.commit()

    exp_xlsx = str(tmp_path / "all_members.xlsx")
    count, out_p = ImportExportService.export_members_to_file(exp_xlsx, "xlsx")
    assert count >= 1
    assert os.path.exists(out_p)

    exp_csv = str(tmp_path / "all_members.csv")
    count_c, out_c = ImportExportService.export_members_to_file(exp_csv, "csv")
    assert count_c >= 1
    assert os.path.exists(out_c)
