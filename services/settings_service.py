"""
Settings service for Gujarat Brahm Samaj ERP.
Manages persistent application settings in the SQLite app_settings table.
"""

from __future__ import annotations

import os
import sqlite3
import platform
from datetime import datetime

from app.config import (
    APP_NAME, APP_VERSION, DB_PATH, EXPORT_DIR, BACKUP_DIR,
    MEMBER_CODE_PREFIX,
)
from database.connection import get_session, get_engine
from database.models import AppSetting, Member, FamilyMember

DEFAULT_SETTINGS = {
    'org_name_gu': 'ગુજરાત બ્રહ્મ સમાજ',
    'org_name_en': 'Gujarat Brahm Samaj',
    'erp_subtitle': 'BRAHM SAMAJ ERP',
    'member_code_prefix': MEMBER_CODE_PREFIX,
    'admin_name': 'સંચાલક (Admin)',
    'helpline_phone': '+91 98765 43210',
    'contact_email': 'contact@brahmsamaj.org',
    'office_address': 'અમદાવાદ, ગુજરાત',
    'default_language': 'gu',
    'date_format': 'DD/MM/YYYY',
    'rows_per_page': '50',
    'auto_backup_on_exit': 'True',
    'default_export_dir': EXPORT_DIR,
    'signatory_title': 'પ્રમુખ / મંત્રી શ્રી',
}


class SettingsService:
    def __init__(self):
        self._ensure_defaults()

    def _ensure_defaults(self) -> None:
        """Seed any missing default settings into app_settings table."""
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with get_session() as session:
                for key, val in DEFAULT_SETTINGS.items():
                    exists = session.query(AppSetting).filter_by(setting_key=key).first()
                    if not exists:
                        session.add(AppSetting(setting_key=key, setting_value=val, updated_at=now))
                session.commit()
        except Exception:
            pass

    def get(self, key: str, default: str | None = None) -> str:
        """Get single setting value by key."""
        try:
            with get_session() as session:
                row = session.query(AppSetting).filter_by(setting_key=key).first()
                if row and row.setting_value is not None:
                    return str(row.setting_value)
        except Exception:
            pass
        return default if default is not None else DEFAULT_SETTINGS.get(key, '')

    def get_all(self) -> dict[str, str]:
        """Return dict of all current settings merged with defaults."""
        result = dict(DEFAULT_SETTINGS)
        try:
            with get_session() as session:
                rows = session.query(AppSetting).all()
                for r in rows:
                    if r.setting_key and r.setting_value is not None:
                        result[str(r.setting_key)] = str(r.setting_value)
        except Exception:
            pass
        return result

    def set(self, key: str, value: str) -> None:
        """Set a single setting key and value."""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with get_session() as session:
            row = session.query(AppSetting).filter_by(setting_key=key).first()
            if row:
                row.setting_value = value
                row.updated_at = now
            else:
                session.add(AppSetting(setting_key=key, setting_value=value, updated_at=now))
            session.commit()

    def set_many(self, settings_dict: dict[str, str]) -> None:
        """Set multiple settings in a single transaction."""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with get_session() as session:
            for key, val in settings_dict.items():
                row = session.query(AppSetting).filter_by(setting_key=key).first()
                if row:
                    row.setting_value = val
                    row.updated_at = now
                else:
                    session.add(AppSetting(setting_key=key, setting_value=val, updated_at=now))
            session.commit()

    def optimize_database(self) -> tuple[bool, str]:
        """Run SQLite VACUUM and ANALYZE for peak performance."""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("VACUUM")
            conn.execute("ANALYZE")
            conn.close()
            return True, "ડેટાબેઝ સફળતાપૂર્વક ઓપ્ટિમાઇઝ અને ક્લીનઅપ થયો છે."
        except Exception as exc:
            return False, f"ઓપ્ટિમાઇઝેશનમાં ભૂલ: {exc}"

    def get_system_info(self) -> dict:
        """Retrieve system runtime, db size, and stats."""
        db_size_kb = 0
        if os.path.exists(DB_PATH):
            db_size_kb = round(os.path.getsize(DB_PATH) / 1024, 2)

        member_count = 0
        family_count = 0
        try:
            with get_session() as session:
                member_count = session.query(Member).count()
                family_count = session.query(FamilyMember).count()
        except Exception:
            pass

        return {
            'app_name': APP_NAME,
            'app_version': APP_VERSION,
            'db_path': DB_PATH,
            'db_size_kb': db_size_kb,
            'member_count': member_count,
            'family_count': family_count,
            'python_version': platform.python_version(),
            'sqlite_version': sqlite3.sqlite_version,
            'os_name': platform.system(),
        }
