"""SQLAlchemy engine, session factory, and database initialisation."""

from contextlib import contextmanager
from datetime import datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

import app.config as config
from database.models import Base, AppSetting

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        config.ensure_dirs()
        _engine = create_engine(
            f'sqlite:///{config.DB_PATH}',
            connect_args={'check_same_thread': False},
            echo=False,
        )

        @event.listens_for(_engine, 'connect')
        def set_sqlite_pragma(dbapi_conn, _):
            cursor = dbapi_conn.cursor()
            cursor.execute('PRAGMA foreign_keys = ON')
            cursor.close()

    return _engine


def _get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
    return _SessionLocal


@contextmanager
def get_session():
    """Yield a SQLAlchemy session and auto-close it."""
    factory = _get_session_factory()
    session: Session = factory()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Create all tables and seed default app_settings rows."""
    engine = get_engine()
    Base.metadata.create_all(engine)

    # Migrate any missing columns in existing SQLite tables
    with get_session() as session:
        cursor = session.connection().connection.cursor()
        cursor.execute("PRAGMA table_info(members)")
        cols = [row[1] for row in cursor.fetchall()]
        if 'signature_text' not in cols:
            cursor.execute("ALTER TABLE members ADD COLUMN signature_text TEXT")
        if 'signature_image' not in cols:
            cursor.execute("ALTER TABLE members ADD COLUMN signature_image TEXT")
        if 'business_address' not in cols:
            cursor.execute("ALTER TABLE members ADD COLUMN business_address TEXT")
        if 'village_address' not in cols:
            cursor.execute("ALTER TABLE members ADD COLUMN village_address TEXT")
        if 'income' not in cols:
            cursor.execute("ALTER TABLE members ADD COLUMN income TEXT")
        cursor.close()

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        defaults = [
            ('schema_version',     '1.2'),
            ('member_code_prefix', 'GBS'),
            ('member_code_last',   '0'),
        ]
        for key, value in defaults:
            exists = session.query(AppSetting).filter_by(setting_key=key).first()
            if not exists:
                session.add(AppSetting(setting_key=key, setting_value=value, updated_at=now))
        session.commit()
