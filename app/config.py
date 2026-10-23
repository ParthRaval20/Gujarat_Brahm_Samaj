"""Application configuration — centralized paths and constants."""

import os
import sys

def _get_base_dir() -> str:
    """Return the project root directory."""
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR: str = _get_base_dir()


def _can_write(path: str) -> bool:
    try:
        os.makedirs(path, exist_ok=True)
        test_file = os.path.join(path, '.perm_test')
        with open(test_file, 'w') as f:
            f.write('1')
        os.remove(test_file)
        return True
    except Exception:
        return False


def _get_storage_dir() -> str:
    """Determine writable root for database, backups, logs, and exports."""
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        pf = os.environ.get('ProgramFiles', 'C:\\Program Files').lower()
        pf_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)').lower()
        exe_lower = exe_dir.lower()
        in_pf = exe_lower.startswith(pf) or exe_lower.startswith(pf_x86)
        if in_pf or not _can_write(os.path.join(exe_dir, 'data')):
            local_appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
            return os.path.join(local_appdata, 'GujaratBrahmSamaj')
        return exe_dir
    return BASE_DIR


STORAGE_DIR: str = _get_storage_dir()

# ---------- Data directories ----------
DATA_DIR: str = os.path.join(STORAGE_DIR, 'data')
BACKUP_DIR: str = os.path.join(STORAGE_DIR, 'backups')
EXPORT_DIR: str = os.path.join(STORAGE_DIR, 'exports')
LOG_DIR: str = os.path.join(STORAGE_DIR, 'logs')

def _get_assets_dir() -> str:
    """Locate assets folder across dev, onedir (_internal), and onefile modes."""
    if hasattr(sys, '_MEIPASS'):
        p = os.path.join(sys._MEIPASS, 'assets')
        if os.path.exists(p):
            return p
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        p = os.path.join(exe_dir, '_internal', 'assets')
        if os.path.exists(p):
            return p
        p = os.path.join(exe_dir, 'assets')
        if os.path.exists(p):
            return p
    return os.path.join(BASE_DIR, 'assets')


# ---------- Asset paths ----------
ASSETS_DIR: str = _get_assets_dir()
FONT_DIR: str = os.path.join(ASSETS_DIR, 'fonts')
IMAGE_DIR: str = os.path.join(ASSETS_DIR, 'images')
ICON_DIR: str = os.path.join(ASSETS_DIR, 'icons')

# ---------- File paths ----------
DB_PATH: str = os.path.join(DATA_DIR, 'brahm_samaj.db')
LOG_PATH: str = os.path.join(LOG_DIR, 'application.log')

GUJARATI_FONT_REGULAR: str = os.path.join(FONT_DIR, 'NotoSansGujarati-Regular.ttf')
GUJARATI_FONT_BOLD: str = os.path.join(FONT_DIR, 'NotoSansGujarati-Bold.ttf')
LOGO_PATH: str = os.path.join(IMAGE_DIR, 'logo.png')
APP_ICON_PATH: str = os.path.join(ICON_DIR, 'app_icon.ico')
CHEVRON_DOWN_PATH: str = os.path.join(ICON_DIR, 'chevron_down.svg')
CHEVRON_DOWN_BLUE_PATH: str = os.path.join(ICON_DIR, 'chevron_down_blue.svg')

# ---------- App metadata ----------
APP_NAME: str = 'Gujarat Brahm Samaj Management System'
APP_VERSION: str = '1.1'
WINDOW_TITLE: str = 'શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ — સભ્ય વ્યવસ્થાપન પોર્ટલ'

# ---------- Developer / Company metadata ----------
GAYATRI_LOGO_PATH: str = os.path.join(IMAGE_DIR, 'gayatri_logo.png')
DEVELOPER_NAME: str = 'Gayatri Technology'
DEVELOPER_NAME_GU: str = 'ગાયત્રી ટેકનોલોજી'
DEVELOPER_WEBSITE: str = 'https://gayatritechnology.in'
DEVELOPER_EMAIL: str = 'info@gayatritechnology.in'

# ---------- Member code ----------
MEMBER_CODE_PREFIX: str = 'GBS'

# ---------- Validation constants ----------
BLOOD_GROUPS: list[str] = ['', 'A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']

RELATION_TYPES: list[str] = [
    '', 'પત્ની (Wife)', 'પુત્ર (Son)', 'પુત્રી (Daughter)', 'પુત્રવધૂ (Daughter-in-law)', 'પતિ (Husband)',
    'પિતા (Father)', 'માતા (Mother)', 'ભાઈ (Brother)', 'બહેન (Sister)',
    'દાદા (Grand Father)', 'દાદી (Grand Mother)', 'અન્ય (Other)',
]

EDUCATION_PRESETS_GU: list[str] = [
    '',
    'ધોરણ ૧૦ (SSC)',
    'ધોરણ ૧૨ (HSC - સામાન્ય પ્રવાહ)',
    'ધોરણ ૧૨ (HSC - વિજ્ઞાન પ્રવાહ)',
    'પ્રાથમિક શાળા (Primary School)',
    'શાસ્ત્રી (Shastri)',
    'આચાર્ય (Acharya)',
    'ડિપ્લોમા (Diploma Engineering)',
    'D.Pharm (Diploma in Pharmacy)',
    'P.T.C. / D.El.Ed.',
    'B.A. (Bachelor of Arts)',
    'B.Com (Bachelor of Commerce)',
    'B.Sc. (Bachelor of Science)',
    'B.E. / B.Tech (Engineering)',
    'B.C.A. (Computer Applications)',
    'B.B.A. (Business Administration)',
    'B.Ed (Bachelor of Education)',
    'B.Arch (Architecture)',
    'B.D.S. (Dental Surgery)',
    'B.A.M.S. (Ayurvedacharya)',
    'B.H.M.S. (Homeopathy)',
    'B.Sc. Nursing',
    'M.A. (Master of Arts)',
    'M.Com (Master of Commerce)',
    'M.Sc. (Master of Science)',
    'M.E. / M.Tech (Engineering)',
    'M.B.A. (Business Administration)',
    'M.C.A. (Computer Applications)',
    'M.Ed (Master of Education)',
    'M.Pharm (Master of Pharmacy)',
    'M.B.B.S. (Medical)',
    'M.D. / M.S. (Medical Specialist)',
    'LL.B. (Bachelor of Law)',
    'LL.M. (Master of Law)',
    'Chartered Accountant (CA)',
    'Company Secretary (CS)',
    'ICWA / CMA',
    'Ph.D. (Doctor of Philosophy)',
    'M.Phil',
    'અન્ય (Other)',
]

EDUCATION_PRESETS_EN: list[str] = [
    '',
    '10th (SSC)',
    '12th (HSC - General / Commerce / Arts)',
    '12th (HSC - Science)',
    'Primary School',
    'Shastri (Sanskrit)',
    'Acharya (Sanskrit / Vedanta)',
    'Diploma Engineering',
    'D.Pharm (Diploma in Pharmacy)',
    'P.T.C. / D.El.Ed.',
    'B.A. (Bachelor of Arts)',
    'B.Com (Bachelor of Commerce)',
    'B.Sc. (Bachelor of Science)',
    'B.E. / B.Tech (Engineering)',
    'B.C.A. (Computer Applications)',
    'B.B.A. (Business Administration)',
    'B.Ed (Bachelor of Education)',
    'B.Arch (Architecture)',
    'B.D.S. (Dental Surgery)',
    'B.A.M.S. (Ayurveda)',
    'B.H.M.S. (Homeopathy)',
    'B.Sc. Nursing',
    'M.A. (Master of Arts)',
    'M.Com (Master of Commerce)',
    'M.Sc. (Master of Science)',
    'M.E. / M.Tech (Engineering)',
    'M.B.A. (Business Administration)',
    'M.C.A. (Computer Applications)',
    'M.Ed (Master of Education)',
    'M.Pharm (Master of Pharmacy)',
    'M.B.B.S. (Medical)',
    'M.D. / M.S. (Medical Specialist)',
    'LL.B. (Bachelor of Law)',
    'LL.M. (Master of Law)',
    'Chartered Accountant (CA)',
    'Company Secretary (CS)',
    'ICWA / CMA',
    'Ph.D. (Doctor of Philosophy)',
    'M.Phil',
    'Other',
]

# ---------- UI Dimensions ----------
SIDEBAR_WIDTH: int = 270
HEADER_HEIGHT: int = 64
MIN_WINDOW_WIDTH: int = 1200
MIN_WINDOW_HEIGHT: int = 760

# ---------- Stitch Design System Colour Palette ----------
# Primary & Sidebar Colors (Slate Navy)
COLOR_SIDEBAR_BG: str = '#0F172A'
COLOR_SIDEBAR_HEADER: str = '#070D18'
COLOR_SIDEBAR_FOOTER: str = '#0B1120'
COLOR_SIDEBAR_HOVER: str = '#1E293B'
COLOR_SIDEBAR_ACTIVE: str = '#2563EB'
COLOR_SIDEBAR_BORDER: str = '#1E293B'
COLOR_NAV_TEXT: str = '#94A3B8'
COLOR_NAV_TEXT_ACTIVE: str = '#FFFFFF'

# Accent Colors
COLOR_PRIMARY: str = '#2563EB'          # Brand Blue
COLOR_PRIMARY_DARK: str = '#1D4ED8'
COLOR_PRIMARY_LIGHT: str = '#3B82F6'

COLOR_ACCENT_BLUE: str = '#2563EB'
COLOR_ACCENT_EMERALD: str = '#10B981'
COLOR_ACCENT_PURPLE: str = '#8B5CF6'
COLOR_ACCENT_AMBER: str = '#F59E0B'
COLOR_ACCENT_GOLD: str = '#D97706'
COLOR_ACCENT_ROSE: str = '#F43F5E'

# Background & Surface Colors
COLOR_BG: str = '#F8FAFC'
COLOR_CARD_BG: str = '#FFFFFF'
COLOR_BORDER: str = '#E2E8F0'
COLOR_BORDER_LIGHT: str = '#F1F5F9'
COLOR_WHITE: str = '#FFFFFF'

# Text Colors
COLOR_TEXT_MAIN: str = '#0F172A'
COLOR_TEXT: str = '#1E293B'
COLOR_TEXT_MUTED: str = '#64748B'
COLOR_TEXT_LIGHT: str = '#94A3B8'

# Status Colors
COLOR_SUCCESS: str = '#10B981'
COLOR_SUCCESS_BG: str = '#ECFDF5'
COLOR_DANGER: str = '#EF4444'
COLOR_DANGER_BG: str = '#FEF2F2'
COLOR_WARNING: str = '#F59E0B'
COLOR_WARNING_BG: str = '#FFFBEB'
COLOR_INFO_BG: str = '#EFF6FF'

# Font sizes (px)
FONT_SIZE_TITLE: int = 22
FONT_SIZE_SECTION: int = 16
FONT_SIZE_NORMAL: int = 13
FONT_SIZE_LABEL: int = 12
FONT_SIZE_BUTTON: int = 13


def ensure_dirs() -> None:
    """Create all required directories if they do not exist."""
    for path in (DATA_DIR, BACKUP_DIR, EXPORT_DIR, LOG_DIR, FONT_DIR, IMAGE_DIR, ICON_DIR):
        os.makedirs(path, exist_ok=True)

    # When running packaged app with separate storage dir, copy seed DB if DB_PATH doesn't exist
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        seed_db = os.path.join(exe_dir, 'data', 'brahm_samaj.db')
        if os.path.exists(seed_db) and not os.path.exists(DB_PATH):
            try:
                import shutil
                shutil.copy2(seed_db, DB_PATH)
            except Exception:
                pass
