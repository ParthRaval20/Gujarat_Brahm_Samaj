"""Backup and restore service."""

from __future__ import annotations

import os
import shutil
from datetime import datetime

from app.config import DB_PATH, BACKUP_DIR, ensure_dirs

_SQLITE_MAGIC = b'SQLite format 3\x00'


def _is_valid_sqlite(path: str) -> bool:
    """Return True if the file starts with the SQLite magic bytes."""
    try:
        with open(path, 'rb') as f:
            return f.read(16) == _SQLITE_MAGIC
    except OSError:
        return False


def create_backup(custom_dir: str | None = None) -> str:
    """
    Copy the current database to the backup directory.
    Returns the full path of the created backup file.
    Raises RuntimeError on failure.
    """
    ensure_dirs()
    dest_dir = custom_dir or BACKUP_DIR
    os.makedirs(dest_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y_%m_%d_%H%M')
    filename  = f'brahm_samaj_backup_{timestamp}.db'
    dest_path = os.path.join(dest_dir, filename)

    if not os.path.exists(DB_PATH):
        raise RuntimeError('No database found to back up.')

    shutil.copy2(DB_PATH, dest_path)

    if not os.path.exists(dest_path) or os.path.getsize(dest_path) == 0:
        raise RuntimeError('Backup file was not created correctly.')

    return dest_path


def restore_backup(backup_path: str) -> None:
    """
    Validate and restore a backup database file.
    Automatically creates a safety backup of the current database first.
    Raises RuntimeError on invalid file or failure.
    """
    if not os.path.exists(backup_path):
        raise RuntimeError(f'Backup file not found: {backup_path}')

    if not _is_valid_sqlite(backup_path):
        raise RuntimeError('Selected file is not a valid SQLite database.')

    ensure_dirs()

    # Safety backup of current DB before replacing
    if os.path.exists(DB_PATH):
        try:
            create_backup()
        except Exception:
            pass   # proceed even if safety backup fails

    shutil.copy2(backup_path, DB_PATH)


def list_backups() -> list[dict]:
    """Return list of dicts with 'filename', 'path', 'size_mb', 'modified' for each backup."""
    ensure_dirs()
    result = []
    if not os.path.isdir(BACKUP_DIR):
        return result

    for fname in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if not (fname.endswith('.db') or fname.endswith('.enc')):
            continue
        full = os.path.join(BACKUP_DIR, fname)
        try:
            stat = os.stat(full)
            result.append({
                'filename': fname,
                'path':     full,
                'size_mb':  round(stat.st_size / (1024 * 1024), 2),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M'),
            })
        except OSError:
            continue
    return result


def check_database_integrity() -> tuple[bool, str]:
    """Execute SQLite PRAGMA integrity_check on the database. Return (is_healthy, message)."""
    import sqlite3
    if not os.path.exists(DB_PATH):
        return False, 'ડેટાબેઝ ફાઇલ ઉપલબ્ધ નથી (Database file missing)'
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('PRAGMA integrity_check;')
        row = cursor.fetchone()
        conn.close()
        if row and row[0] == 'ok':
            return True, '100% સ્વસ્થ (Healthy) — 0 Corrupted records'
        return False, f'ચેતવણી: {row[0] if row else "Unknown"}'
    except Exception as exc:
        return False, f'Error: {str(exc)}'


def get_backup_stats() -> dict:
    """Return summary statistics of backups for status cards."""
    backups = list_backups()
    total_count = len(backups)
    total_size_mb = round(sum(b['size_mb'] for b in backups), 2)
    last_backup_str = backups[0]['modified'] if backups else 'કોઈ બેકઅપ નથી (None)'
    is_healthy, health_msg = check_database_integrity()
    return {
        'total_count': total_count,
        'total_size_mb': total_size_mb,
        'last_backup': last_backup_str,
        'is_healthy': is_healthy,
        'health_message': health_msg,
    }
