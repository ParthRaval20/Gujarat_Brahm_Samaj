"""Application entry point."""

from __future__ import annotations

import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import ensure_dirs, LOG_PATH, APP_NAME, APP_VERSION, APP_ICON_PATH


def _setup_logging() -> None:
    ensure_dirs()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(LOG_PATH, encoding='utf-8'),
            logging.StreamHandler(sys.stdout),
        ],
    )


def main() -> None:
    # Set Windows AppUserModelID so the taskbar icon displays correctly
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('GujaratBrahmSamaj.Portal.App.1.0')
        except Exception:
            pass

    _setup_logging()
    log = logging.getLogger(__name__)
    log.info(f'Starting {APP_NAME} v{APP_VERSION}')

    # Initialize database before creating QApplication
    try:
        from database.connection import init_db
        init_db()
        log.info('Database initialized successfully.')
    except Exception as exc:
        log.critical(f'Database initialization failed: {exc}', exc_info=True)
        # Continue — will show error in UI

    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QFont, QPalette, QColor, QIcon

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    if os.path.exists(APP_ICON_PATH):
        app.setWindowIcon(QIcon(APP_ICON_PATH))

    # Use Fusion style for consistent cross-platform rendering
    app.setStyle('Fusion')

    # Force an explicit light theme palette matching Stitch Design
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor('#F8FAFC'))
    palette.setColor(QPalette.ColorRole.WindowText, QColor('#0F172A'))
    palette.setColor(QPalette.ColorRole.Base, QColor('#FFFFFF'))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor('#F1F5F9'))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor('#0F172A'))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor('#FFFFFF'))
    palette.setColor(QPalette.ColorRole.Text, QColor('#0F172A'))
    palette.setColor(QPalette.ColorRole.Button, QColor('#FFFFFF'))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor('#0F172A'))
    palette.setColor(QPalette.ColorRole.BrightText, QColor('#EF4444'))
    palette.setColor(QPalette.ColorRole.Link, QColor('#2563EB'))
    palette.setColor(QPalette.ColorRole.Highlight, QColor('#2563EB'))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor('#FFFFFF'))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor('#94A3B8'))
    app.setPalette(palette)

    # Register custom Gujarati fonts
    from PySide6.QtGui import QFontDatabase
    from app.config import GUJARATI_FONT_REGULAR, GUJARATI_FONT_BOLD
    if os.path.exists(GUJARATI_FONT_REGULAR):
        QFontDatabase.addApplicationFont(GUJARATI_FONT_REGULAR)
    if os.path.exists(GUJARATI_FONT_BOLD):
        QFontDatabase.addApplicationFont(GUJARATI_FONT_BOLD)

    # Global font — modern typography with Gujarati support
    font = QFont('Noto Sans Gujarati', 10)
    if 'Noto Sans Gujarati' not in QFontDatabase.families():
        font = QFont('Segoe UI', 10)
    app.setFont(font)

    # Global stylesheet ensuring proper defaults without cascading dark text to dark backgrounds
    app.setStyleSheet("""
        QMainWindow, QDialog {
            background-color: #F8FAFC;
            font-family: 'Segoe UI', 'Noto Sans Gujarati', 'Arial Unicode MS', sans-serif;
            color: #0F172A;
        }
        QLabel {
            border: none;
            background: transparent;
        }
        #appSidebar {
            background-color: #0F172A;
            border-right: 1px solid #1E293B;
        }
        #appSidebar QLabel {
            color: #E2E8F0;
            background: transparent;
            border: none;
        }
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #FFFFFF;
            color: #0F172A;
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            selection-background-color: #2563EB;
            selection-color: #FFFFFF;
        }
        QDateEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #FFFFFF;
            color: #0F172A;
            selection-background-color: #2563EB;
            selection-color: #FFFFFF;
        }
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QDateEdit:focus, QSpinBox:focus, QComboBox:focus {
            border-color: #2563EB;
        }
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled, QComboBox:disabled, QDateEdit:disabled {
            background-color: #F1F5F9;
            color: #94A3B8;
        }
        QComboBox QAbstractItemView {
            background-color: #FFFFFF;
            color: #0F172A;
            selection-background-color: #EFF6FF;
            selection-color: #2563EB;
        }
        QTableWidget, QTableView {
            background-color: #FFFFFF;
            color: #0F172A;
            alternate-background-color: #F8FAFC;
            gridline-color: transparent;
            selection-background-color: #EFF6FF;
            selection-color: #2563EB;
        }
        QTableWidget::item, QTableView::item {
            color: #0F172A;
        }
        QTableWidget::item:selected, QTableView::item:selected {
            background-color: #EFF6FF;
            color: #2563EB;
        }
        QHeaderView::section {
            background-color: #0F172A;
            color: #FFFFFF;
            font-weight: bold;
        }
        QCalendarWidget QWidget {
            background-color: #FFFFFF;
            color: #0F172A;
        }
        QCalendarWidget QAbstractItemView {
            background-color: #FFFFFF;
            color: #0F172A;
            selection-background-color: #2563EB;
            selection-color: #FFFFFF;
        }
        QCalendarWidget QToolButton {
            color: #0F172A;
            background-color: transparent;
            font-weight: bold;
        }
        QToolTip {
            background: #0F172A;
            color: white;
            border: none;
            padding: 4px 8px;
            font-size: 11px;
            border-radius: 4px;
        }
        QScrollBar:vertical {
            background: #F1F5F9;
            width: 8px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical {
            background: #CBD5E1;
            border-radius: 4px;
            min-height: 24px;
        }
        QScrollBar::handle:vertical:hover {
            background: #94A3B8;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
        }
    """)

    from ui.main_window import MainWindow
    window = MainWindow()
    window.showMaximized()

    log.info('Application window opened.')
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
