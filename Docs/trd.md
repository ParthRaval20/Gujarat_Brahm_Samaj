# Technical Requirements Document (TRD)

# Gujarat Brahm Samaj Desktop Management System

**Document Version:** 1.2
**Related Documents:** PRD.md, databaseschema.md, UIUX.md, appflow.md
**Application Type:** Offline Windows Desktop Application
**Primary Technology:** Python + PySide6 + SQLite + ReportLab
**Status:** Ready for Development

---

# Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | Initial draft | Base TRD created |
| 1.1 | Revision | Low-end hardware requirements added |
| 1.2 | 2026-09-08 | PDF library decision finalized. Form data mapper updated to include all official form fields: `phone_landline`, `samaj`, `membership_fee`. Family member mapper updated to include `blood_group`. Surname-first name order documented. `age` removed as stored field from members — computed from `birth_date`. |
| 1.3 | 2026-10-05 | **Comprehensive production architecture update. Added FormRenderer engine (vector/raster QPainter physical form replica with 10 family rows and Gujarati row numerals ૧-૧૦). Added ImportExportService with OpenPyXL for Excel/CSV bulk import/export. Added bilingual localization system (`app/translations.py`). Added phonetic transliteration search (`utils/gujarati_search.py`). Added Inno Setup 6 Windows installer pipeline (`installer.iss`, `Build_Installer.bat`). Updated project directory tree to match production codebase.** |

---

# 1. Purpose

This Technical Requirements Document (TRD) defines the technical architecture, technologies, database structure, modules, implementation approach, and technical requirements for the **Gujarat Brahm Samaj Desktop Management System**.

The system allows authorized users to:

- Manage Gujarat Brahm Samaj member information.
- Manage family details.
- Perform smart search across all member records.
- Automatically fill and print the official **સભ્ય નોંધણી ફોર્મ**.
- Export the form as a PDF.
- Back up and restore the local database.

All features must work completely offline.

---

# 2. Technical Goals

The application must:

- Run as a Windows desktop application.
- Work without an internet connection.
- Store all data in a local SQLite database.
- Support Gujarati Unicode text in the UI, database, and PDF output.
- Support CRUD operations for member information.
- Support multiple family members per member record.
- Provide fast smart search.
- Automatically populate all fields of the official Gujarati form.
- Support form preview, PDF export, and printing.
- Provide database backup and restore.
- Run reliably on computers with as little as 2 GB RAM.
- Be maintainable and scalable for future features.

---

# 3. Technology Stack

## 3.1 Programming Language

**Python 3.12+**

Selected because it provides:

- Fast development.
- Strong SQLite and SQLAlchemy support.
- Excellent desktop GUI support via PySide6.
- Native Unicode support for Gujarati text.
- Easy packaging for Windows via PyInstaller.

---

## 3.2 Desktop GUI Framework

**PySide6 (Qt for Python)**

PySide6 handles:

- Main application window.
- Forms and input widgets.
- Member list tables.
- Search interface.
- Member profile screens.
- Form preview.
- Print dialog integration.

PySide6 is selected over Tkinter for:

- Professional appearance.
- Better table widget support.
- Better font and Unicode rendering.
- Qt's native printing infrastructure.

---

## 3.3 Database

**SQLite**

Database file:

```text
data/brahm_samaj.db
```

SQLite is appropriate for Version 1 because:

- No server installation is required.
- Works completely offline.
- Backup is a simple file copy.
- Reliable for thousands of records.
- Easy to distribute with the application.
- Very low memory footprint (critical for 2 GB RAM machines).

---

## 3.4 Database Access Layer

**SQLAlchemy (ORM)**

SQLAlchemy provides:

- Declarative ORM models.
- Database abstraction (easier future migration to PostgreSQL).
- Clean and maintainable query code.
- Connection management.

Alternative: raw `sqlite3` module may be used for simple queries where SQLAlchemy adds unnecessary complexity.

---

## 3.5 PDF & Official Form Generation Engine

The application implements a dual-engine architecture for authentic form generation:

1. **`FormRenderer` (`services/form_renderer.py`)**:
   - Custom high-resolution vector and raster rendering engine built directly on `QPainter`.
   - Replicates the exact physical dimensions, blue borders (`#1B2F8A`), Gujarati header with organization address (*શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સા.કાં., શૈવ કૉમ્પ્લેક્સ, દામોદર એરિયા, સત્યમ હોસ્પિટલની સામે, ઇડર*), community emblem, and 4 official numbered sections.
   - 10-row, 8-column family table with row numbers printed in official Gujarati numerals: ૧, ૨, ૩, ૪, ૫, ૬, ૭, ૮, ૯, ૧૦.
   - Used directly by `FormPreviewPage` for instant live preview and by `QPdfWriter` for print-grade 300 DPI PDF generation.

2. **ReportLab & QPdfWriter (`services/pdf_service.py`)**:
   - Generates high-definition A4 PDF documents directly in `exports/` without requiring external print drivers or internet access.
   - Uses embedded `Noto Sans Gujarati` TrueType fonts for flawless Gujarati text shaping.

### Font Decision

The application bundles Google's **Noto Sans Gujarati** font:
- `assets/fonts/NotoSansGujarati-Regular.ttf`
- `assets/fonts/NotoSansGujarati-Bold.ttf`

Loaded at application launch into `QFontDatabase` and registered with PDF writers.

---

## 3.6 Data Import & Export Engine

**`services/import_export_service.py` (via `openpyxl` & `csv`)**:
- Supports importing member and family datasets from Excel (.xlsx) and CSV files.
- Smart conflict resolution & deduplication strategies:
  - `both`: Match existing records by both Mobile Number and Member Code.
  - `mobile`: Match and update existing records by Mobile Number.
  - `code`: Match and update existing records by Member Code (`GBS-XXXXXX`).
  - `insert_only`: Skip matching existing records and only insert new members.
- Automatic pre-import safety backup: Creates an automatic database backup before running any bulk operations.
- Sample template generator for downloadable Excel and CSV import templates.

---

## 3.7 Bilingual Localization & Phonetic Search

- **`app/translations.py`**: Complete in-memory dictionary for Gujarati (`gu`) and English (`en`) providing instant live switching of all UI titles, headers, labels, placeholders, and dialogs.
- **`utils/gujarati_search.py`**: Phonetic transliteration dictionary mapping English spellings to Gujarati Unicode equivalents (e.g., `joshi` → `જોષી`/`જોશી`, `trivedi` → `ત્રિવેદી`, `sabarkantha` → `સાબરકાંઠા`) enabling seamless cross-lingual search.

---

## 3.8 Packaging and Distribution

- **PyInstaller**: Onedir compilation using `GujaratBrahmSamaj.spec` with all native Qt DLLs, assets, fonts, and SQLAlchemy extensions bundled.
- **Inno Setup 6**: Professional Windows Setup wizard (`installer.iss`) compiling `GujaratBrahmSamaj_Setup_v1.0.exe` with desktop icon, Start Menu shortcuts, and uninstaller.
- **`Build_Installer.bat`**: One-click build script automating icon generation, PyInstaller bundling, and Inno Setup compilation.

---

# 4. High-Level Architecture

```text
+--------------------------------------------------+
|                 Presentation Layer               |
|                                                  |
|  PySide6 Screens / Widgets / Dialogs             |
|  (main_window, dashboard, member_form,           |
|   member_list, member_profile, form_preview,     |
|   backup_restore)                                |
+--------------------------+-----------------------+
                           |
                           v
+--------------------------------------------------+
|                 Application Layer                |
|                                                  |
|  member_service.py    — CRUD for members         |
|  family_service.py    — CRUD for family          |
|  search_service.py    — Smart search logic       |
|  form_service.py      — Form field mapping       |
|  pdf_service.py       — ReportLab PDF generation |
|  backup_service.py    — Backup and restore       |
+--------------------------+-----------------------+
                           |
                           v
+--------------------------------------------------+
|                    Data Layer                    |
|                                                  |
|  SQLAlchemy ORM Models                           |
|  SQLite Database (brahm_samaj.db)                |
+--------------------------------------------------+
```

The UI layer must never contain SQL queries or business logic.
The service layer must never directly manipulate UI widgets.

---

# 5. Project Directory Structure

```text
GujaratBrahmSamaj/
│
├── main.py                        ← Application entry point
│
├── app/
│   ├── __init__.py
│   ├── config.py                  ← Centralized paths, theme tokens, constants
│   └── translations.py            ← Complete bilingual Gujarati/English dictionary
│
├── database/
│   ├── __init__.py
│   ├── connection.py              ← SQLAlchemy engine, sessionmaker, schema migrations
│   └── models.py                  ← ORM models (Member, FamilyMember, AppSetting)
│
├── services/
│   ├── __init__.py
│   ├── backup_service.py          ← SQLite backup, restore & integrity check
│   ├── family_service.py          ← Family members CRUD
│   ├── form_renderer.py          ← Authentic official Gujarati form drawing engine (QPainter)
│   ├── form_service.py            ← Maps DB records to form data dictionary
│   ├── import_export_service.py  ← Excel/CSV import & export with smart deduplication
│   ├── member_service.py          ← Member CRUD & validation
│   ├── pdf_service.py             ← High-definition 300 DPI QPdfWriter/ReportLab generator
│   ├── search_service.py          ← Multi-field member search
│   └── settings_service.py        ← Application preferences & org metadata
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py             ← MainWindow with dark sidebar, status & lang toggle
│   ├── dashboard.py               ← Modern KPI dashboard, launchpads & recent table
│   ├── member_form.py             ← 4-section authentic registration form with 10 family rows
│   ├── member_list.py             ← Member directory table with search, filters & export
│   ├── member_profile.py          ← Detailed member profile & quick actions
│   ├── form_preview.py            ← Real-time authentic vector/raster form preview
│   ├── backup_restore.py          ← Backup archive management & DB health
│   ├── system_settings.py         ← App settings, org details & database statistics
│   ├── import_data_dialog.py      ← Import wizard with conflict resolution strategies
│   └── widgets/
│       ├── __init__.py
│       └── family_table_widget.py ← Dynamic family member grid editor
│
├── utils/
│   ├── __init__.py
│   ├── date_utils.py              ← Age calculation & date formatting
│   ├── file_utils.py              ← Filename sanitization
│   ├── gujarati_search.py         ← Phonetic transliteration & multi-script matching
│   ├── gujarati_utils.py          ← Unicode text helpers
│   └── validators.py              ← Input validation rules
│
├── assets/
│   ├── fonts/
│   │   ├── NotoSansGujarati-Regular.ttf
│   │   └── NotoSansGujarati-Bold.ttf
│   ├── icons/
│   │   └── app_icon.ico
│   └── images/
│       ├── logo.png
│       ├── gayatri_logo.png
│       ├── parshuram_logo.png
│       └── official_form.jpg
│
├── data/
│   └── brahm_samaj.db
├── backups/
├── exports/
├── logs/
│   └── application.log
│
├── scripts/
│   └── seed_100_members.py
├── tests/
│   ├── test_avatar_initials.py
│   ├── test_button_language_switch.py
│   ├── test_import_export_service.py
│   ├── test_language_switch_verification.py
│   ├── test_member_form_flow.py
│   ├── test_member_form_layout.py
│   ├── test_member_form_phone_validation.py
│   ├── test_member_list_delete_all.py
│   ├── test_member_service.py
│   └── test_updated_form_visual.py
│
├── smoke_test.py                  ← Headless end-to-end integration test
├── dev_reload.py                  ← Auto-reloading developer daemon
├── Build_Installer.bat            ← Automated PyInstaller + Inno Setup compiler script
├── installer.iss                  ← Inno Setup 6 packaging configuration
├── GujaratBrahmSamaj.spec         ← PyInstaller onedir build spec
├── Run App.bat                    ← Launcher batch script
├── Run Dev (Auto-Reload).bat      ← Development auto-reload launcher
└── requirements.txt               ← Python dependencies
```

---

# 6. Database Design

The complete database schema is defined in `databaseschema.md` (v1.3).

This section summarizes the technical implementation details.

## 6.1 SQLAlchemy Models

### Member Model

```python
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Member(Base):
    __tablename__ = 'members'

    id              = Column(Integer, primary_key=True, autoincrement=True)
    member_code     = Column(Text, unique=True, nullable=False)

    # Name fields — surname first per official form field ૧
    full_name       = Column(Text, nullable=False)
    surname         = Column(Text)
    father_name     = Column(Text)

    # Contact
    mobile          = Column(Text)          # મોબાઈલ નં.
    phone_landline  = Column(Text)          # ફોન નં.
    email           = Column(Text)          # ઈ-મેઈલ

    # Address
    address         = Column(Text)          # (૨) પત્ર વ્યવહારનું સરનામું
    village_address = Column(Text)          # (૩) ગામનું સરનામું
    city            = Column(Text)
    district        = Column(Text)
    state           = Column(Text)
    pincode         = Column(Text)

    # Professional / Employment (Section 2)
    occupation       = Column(Text)          # (૪) ધંધો / વ્યવસાય
    business_address = Column(Text)          # (૫) ધંધા / વ્યવસાયનું સરનામું
    income           = Column(Text)          # (૬) આવક
    education        = Column(Text)          # અભ્યાસ
    blood_group      = Column(Text)          # બ્લડ ગ્રુપ

    # Community
    samaj           = Column(Text)          # ૭ — સમાજ
    membership_fee  = Column(Text)          # સભ્ય ફી

    # Signature (text or uploaded image path)
    signature_text  = Column(Text)
    signature_image = Column(Text)

    # DOB — age computed at display time, never stored
    birth_date      = Column(Text)          # YYYY-MM-DD

    created_at      = Column(Text, nullable=False)
    updated_at      = Column(Text, nullable=False)

    # Relationship
    family_members  = relationship(
        'FamilyMember',
        back_populates='member',
        cascade='all, delete-orphan',
        lazy='select',
    )
```

**Note:** There is no `age` column on the `Member` model. Age is always computed using:

```python
# date_utils.py
from datetime import date

def calculate_age(birth_date_str: str) -> int | None:
    if not birth_date_str:
        return None
    birth = date.fromisoformat(birth_date_str)
    today = date.today()
    age = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    return age
```

---

### Family Member Model

```python
class FamilyMember(Base):
    __tablename__ = 'family_members'

    id              = Column(Integer, primary_key=True, autoincrement=True)
    member_id       = Column(Integer, ForeignKey('members.id', ondelete='CASCADE'), nullable=False)

    name            = Column(Text, nullable=False)      # નામ
    relation        = Column(Text)                      # સબંધ
    age             = Column(Integer)                   # ઉમર (entered directly)
    education       = Column(Text)                      # અભ્યાસ
    blood_group     = Column(Text)                      # બ્લડ ગ્રુ
    occupation      = Column(Text)                      # વ્યવસાય
    contact_number  = Column(Text)                      # કોન્ટેક નંબર

    created_at      = Column(Text, nullable=False)
    updated_at      = Column(Text, nullable=False)

    # Relationship
    member          = relationship('Member', back_populates='family_members')
```

---

### App Setting Model

```python
class AppSetting(Base):
    __tablename__ = 'app_settings'

    id              = Column(Integer, primary_key=True, autoincrement=True)
    setting_key     = Column(Text, unique=True, nullable=False)
    setting_value   = Column(Text)
    updated_at      = Column(Text, nullable=False)
```

---

## 6.2 Recommended Indexes

```sql
CREATE INDEX IF NOT EXISTS idx_members_full_name     ON members(full_name);
CREATE INDEX IF NOT EXISTS idx_members_surname        ON members(surname);
CREATE INDEX IF NOT EXISTS idx_members_father_name    ON members(father_name);
CREATE INDEX IF NOT EXISTS idx_members_mobile         ON members(mobile);
CREATE INDEX IF NOT EXISTS idx_members_city           ON members(city);
CREATE INDEX IF NOT EXISTS idx_members_occupation     ON members(occupation);
CREATE INDEX IF NOT EXISTS idx_members_samaj          ON members(samaj);
CREATE INDEX IF NOT EXISTS idx_family_members_id      ON family_members(member_id);
CREATE INDEX IF NOT EXISTS idx_family_members_name    ON family_members(name);
```

---

# 7. Member Code Generation

Each member receives a unique, sequential member code.

Format:

```text
GBS-000001
GBS-000002
GBS-000003
```

The last used number is stored in `app_settings`:

```text
setting_key:   member_code_last
setting_value: 25
```

Generation logic:

```python
def generate_member_code(session) -> str:
    setting = session.query(AppSetting).filter_by(setting_key='member_code_last').first()
    next_number = int(setting.setting_value) + 1
    setting.setting_value = str(next_number)
    return f"GBS-{next_number:06d}"
```

This prints as **GBS-000025** on the **ફોર્મ નં.** field of the official form.

---

# 8. Smart Search Technical Design

One search box searches across multiple fields simultaneously.

## 8.1 Search Fields

```text
full_name
surname
father_name
mobile
phone_landline
city
district
occupation
samaj
member_code
```

## 8.2 Search Algorithm

```text
1. Trim whitespace from query.
2. Build LIKE pattern: '%query%'
3. Execute parameterized multi-field query.
4. Return results sorted by full_name.
5. Limit to 50 results per search.
```

Parameterized SQL concept:

```sql
SELECT id, member_code, full_name, father_name, mobile, city
FROM members
WHERE
    LOWER(full_name)     LIKE LOWER(?)
    OR LOWER(surname)    LIKE LOWER(?)
    OR LOWER(father_name) LIKE LOWER(?)
    OR mobile            LIKE ?
    OR LOWER(city)       LIKE LOWER(?)
    OR LOWER(samaj)      LIKE LOWER(?)
ORDER BY full_name
LIMIT 50;
```

Never use `SELECT *` for list queries — select only the columns needed for display.

## 8.3 Gujarati Search

SQLite's `LIKE` operator works with Unicode text. The application should:

- Accept both Gujarati and English input in the search box.
- Not attempt transliteration in Version 1.
- Store all Gujarati text as-is in UTF-8.

---

# 9. Gujarati Form Generation Architecture

This is the most important technical component of the application.

## 9.1 Official Form Field Mapping

The `form_service.py` module maps database fields to official form positions.

Complete mapping based on physical form:

```python
def build_form_data(member: Member, family_members: list[FamilyMember]) -> dict:
    return {
        # Header
        "form_number":      member.member_code,        # ફોર્મ નં.
        "form_date":        date.today().strftime("%d/%m/%Y"),  # તારીખ

        # Personal fields
        "full_name":        member.full_name,           # ૧ — surname first
        "address":          member.address,             # ૨ — સરનામું
        "pincode":          member.pincode,             # ૨ — PIN code
        "email":            member.email,               # ૩ — ઈ-મેઈલ
        "mobile":           member.mobile,              # — મોબાઈલ નં.
        "phone_landline":   member.phone_landline,      # — ફોન નં.
        "occupation":       member.occupation,          # ૪ — ધંધો / વ્યવસાય
        "education":        member.education,           # ૫ — અભ્યાસ
        "blood_group":      member.blood_group,         # ક — બ્લડ ગ્રુપ
        "samaj":            member.samaj,               # ૭ — સમાજ
        "membership_fee":   member.membership_fee,      # — સભ્ય ફી

        # Family members table (પરિવારની માહિતી)
        "family_members": [
            {
                "serial":         idx + 1,
                "name":           fm.name,
                "relation":       fm.relation,
                "age":            fm.age,
                "education":      fm.education,
                "blood_group":    fm.blood_group,
                "occupation":     fm.occupation,
                "contact_number": fm.contact_number,
            }
            for idx, fm in enumerate(family_members)
        ]
    }
```

## 9.2 Form Generation Flow

```text
User Selects Member
        |
        v
member_service fetches Member record
        |
        v
family_service fetches all FamilyMember records
        |
        v
form_service.build_form_data() creates form dict
        |
        v
pdf_service.generate_form_pdf(form_data) creates PDF
        |
        v
Form Preview opens
        |
        +-----> Print
        |
        +-----> Save PDF
```

---

# 10. PDF Service — ReportLab Implementation

## 10.1 Form Layout

The PDF must recreate the official form with:

- Blue double-line outer border.
- Gujarati heading: **સભ્ય નોંધણી ફોર્મ** in blue banner.
- Organization name: **શ્રી સમરત ગુજરાત બ્રહ્મ સમાજ સા.કાં.**
- Organization logo (Shiva image) in top left.
- Address line below organization name.
- Numbered fields ૧ through ૭.
- Blue banner: **પરિવારની માહિતી**
- Family table with 8 columns: ક્રમ, નામ, સબંધ, ઉમર, અભ્યાસ, બ્લડ ગ્રુ, વ્યવસાય, કોન્ટેક નંબર.
- Membership fee and signature line at the bottom of the personal section.
- A4 paper size (210mm × 297mm).

## 10.2 PDF Output Requirements

- Paper size: A4.
- Font: Noto Sans Gujarati (embedded — not system-dependent).
- All Gujarati text must render correctly.
- Blue color: use the same shade as the official form (`#1B2F8A` or calibrate from form).
- Family table: minimum 8 rows. Additional rows added automatically if family_members count exceeds 8.
- Empty rows remain as blank cells.
- PDF must be print-ready at 300 DPI minimum quality.

## 10.3 Output Filename

```python
def get_pdf_filename(member: Member) -> str:
    safe_name = member.full_name.replace(' ', '_').replace('/', '_')
    return f"{safe_name}_{member.member_code}.pdf"
```

Example:

```text
રાવલ_પાર્થ_GBS-000001.pdf
```

Output directory:

```text
exports/
```

## 10.4 ReportLab Dependencies

```text
reportlab>=4.0.0
```

No additional PDF library is required. Qt printing (`QPrinter`) is used only for sending the generated PDF to the system print dialog, not for generating it.

---

# 11. Print Flow

```text
PDF generated by ReportLab
        |
        v
Save to temp file in exports/
        |
        v
Open with QPrinter or os.startfile() (Windows)
        |
        v
System Print Dialog appears
        |
        v
User selects printer and prints
```

Alternatively, the PDF can be opened using:

```python
import os
os.startfile(pdf_path)  # Windows — opens with default PDF viewer/printer
```

This keeps the printing implementation simple and reliable across all Windows versions.

---

# 12. UI Architecture

## 12.1 Main Window Structure

```python
QMainWindow
    └── QWidget (central)
         ├── QFrame (left navigation panel)
         │    ├── Dashboard button
         │    ├── Add Member button
         │    ├── All Members button
         │    ├── Search button
         │    ├── Generate Form button
         │    └── Backup button
         └── QStackedWidget (content area)
              ├── Page 0: Dashboard
              ├── Page 1: Add / Edit Member Form
              ├── Page 2: Member List
              ├── Page 3: Member Profile
              ├── Page 4: Form Preview
              └── Page 5: Backup / Restore
```

## 12.2 Member Form Widgets

| Field | Widget | Notes |
|---|---|---|
| Surname | QLineEdit | Entered first, per form field ૧ |
| Full Name | QLineEdit | Surname + given name combined |
| Father's Name | QLineEdit | |
| Mobile | QLineEdit | Numeric validation |
| Phone (Landline) | QLineEdit | ફોન નં. — new field |
| Address | QPlainTextEdit | Multi-line |
| City | QLineEdit | |
| District | QLineEdit | |
| State | QLineEdit | Default: "ગુજરાત" |
| PIN Code | QLineEdit | 6-digit validation |
| Email | QLineEdit | |
| Occupation | QLineEdit | |
| Education | QLineEdit | |
| Blood Group | QComboBox | A+, A-, B+, B-, O+, O-, AB+, AB- |
| Samaj | QLineEdit | ૭ — new field |
| Membership Fee | QLineEdit | ફ |
| Date of Birth | QDateEdit | Age displayed automatically on selection |

## 12.3 Family Member Table Widget

The family table must have exactly these 7 input columns (matching the official form):

| # | Column | Widget per Cell |
|---|---|---|
| 1 | નામ (Name) | QLineEdit |
| 2 | સબંધ (Relation) | QComboBox or QLineEdit |
| 3 | ઉમર (Age) | QSpinBox |
| 4 | અભ્યાસ (Education) | QLineEdit |
| 5 | બ્લડ ગ્રુ (Blood Group) | QComboBox |
| 6 | વ્યવસાય (Occupation) | QLineEdit |
| 7 | કોન્ટેક નંબર (Contact) | QLineEdit |

The serial number (ક્રમ) is auto-generated at display and print time.

Controls:

```text
[ + Add Row ]    [ Remove Selected Row ]
```

---

# 13. Validation Rules

## Member Form

| Field | Validation |
|---|---|
| full_name | Required. Minimum 2 characters. |
| mobile | Optional. If provided, digits only, 10 characters. |
| phone_landline | Optional. If provided, digits and hyphens allowed. |
| pincode | Optional. If provided, exactly 6 digits. |
| blood_group | Optional. If provided, must be from allowed list. |
| birth_date | Optional. If provided, must be a valid past date. |
| membership_fee | Optional. Free text — allows "500", "Free", "Paid". |

## Family Member Row

| Field | Validation |
|---|---|
| name | Required if row is not empty. |
| age | Optional. If provided, integer between 0 and 120. |
| blood_group | Optional. If provided, must be from allowed list. |

---

# 14. Error Handling

## User Errors

Display clear, simple Gujarati or English messages:

```text
"Full name is required."
"Please enter a valid mobile number."
"Date of birth cannot be in the future."
```

## Database Errors

```text
1. Log the error to logs/application.log
2. Show user-friendly message
3. Offer retry or cancel option
4. Never expose technical stack traces to the user
```

## Startup Errors

```text
Database not found    → Create new database automatically
Database corrupted    → Show recovery guidance, offer restore from backup
```

---

# 15. Backup System

## Backup Process

```python
def create_backup(db_path: str, backup_dir: str) -> str:
    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M")
    backup_filename = f"brahm_samaj_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    shutil.copy2(db_path, backup_path)
    # Verify
    assert os.path.exists(backup_path)
    assert os.path.getsize(backup_path) > 0
    return backup_path
```

## Restore Process

```text
1. User selects .db backup file
2. Validate: open file, check SQLite magic bytes
3. Show warning: "Current data will be replaced. Are you sure?"
4. Auto-backup current database first
5. Replace brahm_samaj.db with selected file
6. Reload database connection
```

---

# 16. Application Configuration

Centralized in `app/config.py`:

```python
import os

BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
DATA_DIR       = os.path.join(BASE_DIR, '..', 'data')
BACKUP_DIR     = os.path.join(BASE_DIR, '..', 'backups')
EXPORT_DIR     = os.path.join(BASE_DIR, '..', 'exports')
LOG_DIR        = os.path.join(BASE_DIR, '..', 'logs')
FONT_DIR       = os.path.join(BASE_DIR, '..', 'assets', 'fonts')

DB_PATH        = os.path.join(DATA_DIR, 'brahm_samaj.db')
LOG_PATH       = os.path.join(LOG_DIR, 'application.log')

APP_NAME       = "Gujarat Brahm Samaj Management System"
APP_VERSION    = "1.0.0"

GUJARATI_FONT_REGULAR = os.path.join(FONT_DIR, 'NotoSansGujarati-Regular.ttf')
GUJARATI_FONT_BOLD    = os.path.join(FONT_DIR, 'NotoSansGujarati-Bold.ttf')

BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']

MEMBER_CODE_PREFIX = 'GBS'
```

---

# 17. File Storage Locations

```text
Application Installation Directory
├── GujaratBrahmSamaj.exe
├── assets/
│   ├── fonts/
│   │   ├── NotoSansGujarati-Regular.ttf
│   │   └── NotoSansGujarati-Bold.ttf
│   └── images/
│       └── logo.png
│
User Data Directory (writable)
├── data/
│   └── brahm_samaj.db
├── backups/
├── exports/
└── logs/
    └── application.log
```

The writable data directory must be outside the protected Windows installation folder.

Recommended location on Windows:

```text
C:\Users\<Username>\AppData\Local\GujaratBrahmSamaj\
```

---

# 18. Development Standards

## Code Style

- PEP 8.
- Type hints on all public functions and methods.
- Docstrings on all service classes and public methods.
- Meaningful variable names in English.
- Gujarati string literals written directly as Unicode.

## Architecture Rules

| Layer | Responsibility | Must NOT |
|---|---|---|
| UI | Collect input, display data, call services | Contain SQL or business logic |
| Service | Business logic, validation, orchestration | Directly import PySide6 widgets |
| Repository | Database queries only | Contain business logic |

---

# 19. Testing Requirements

## Unit Tests

- Member creation with all fields including `samaj`, `phone_landline`, `membership_fee`.
- Member update.
- Member deletion with cascade to family members.
- Search across all indexed fields.
- Family member CRUD.
- Member code generation.
- Field validation.
- Age calculation from `birth_date`.

## Database Tests

- Foreign key enforcement.
- `ON DELETE CASCADE` behavior.
- Duplicate `member_code` rejection.
- Transaction rollback on failure.
- Backup file validation.
- Restore replacing existing database.

## PDF Tests

- Gujarati text renders correctly using Noto Sans Gujarati.
- Long names do not overflow fields.
- Long addresses wrap correctly.
- Family tables with 0, 1, 5, and 10+ members.
- All 8 family table columns render correctly (including `blood_group`).
- `phone_landline`, `samaj`, `membership_fee` fields appear correctly.
- Output is A4 size.
- Print margins are correct.

## UI Tests

- Add member form — all fields present including new fields.
- Family member table — 7 columns present and editable.
- Blood group dropdowns populated.
- Age displayed (computed from birth_date, not from stored column).
- Search finds members by samaj field.
- Form preview opens after selecting a member.

---

# 20. Performance Requirements

Minimum target: 2 GB RAM, dual-core CPU, Windows.

- Application startup: under 5 seconds on minimum hardware.
- Member search: results appear within 1-2 seconds for up to 10,000 records.
- Member profile open: under 2 seconds.
- PDF generation: under 10 seconds.
- Member list: loads visible rows only — never loads all records into memory.
- Idle memory usage: should remain low between actions.

---

# 21. Development Milestones

## Milestone 0: Requirement Confirmation ✅

- Official form photographed and all fields mapped.
- Database schema finalized (v1.2).
- TRD finalized (v1.2).
- PDF library selected: ReportLab.
- Font selected: Noto Sans Gujarati.

## Milestone 1: Project Setup

- Python virtual environment.
- PySide6 installed and tested.
- SQLAlchemy installed.
- ReportLab installed.
- Noto Sans Gujarati font tested for Gujarati rendering.
- Project directory structure created.
- Git initialized.

## Milestone 2: Database and Models

- SQLAlchemy models for `Member`, `FamilyMember`, `AppSetting`.
- Database initialization script runs.
- All v1.2 schema fields present.
- Foreign keys and cascade tested.
- Member code generation working.

## Milestone 3: Member CRUD

- Add Member form with all fields.
- Edit Member.
- Delete Member with confirmation.
- View Member profile.
- Family member table in form (7 editable columns).

## Milestone 4: Member List and Search

- Member list with pagination/efficient scroll.
- Search bar searching across all indexed fields including `samaj`.
- No-results handling.

## Milestone 5: Gujarati Form PDF

- ReportLab generates PDF matching official form layout.
- All personal fields placed correctly.
- Family table with all 8 columns.
- `phone_landline`, `samaj`, `membership_fee` fields rendered.
- Form number from `member_code` appears in ફોર્મ નં. field.
- Gujarati text renders correctly.

## Milestone 6: Preview and Print

- Form preview screen.
- Print via system dialog.
- Save PDF to exports directory.

## Milestone 7: Backup and Packaging

- Backup working.
- Restore working.
- All error handling complete.
- PyInstaller Windows executable built.
- Tested on 2 GB RAM machine or equivalent.

---

# 22. Dependencies — requirements.txt

```text
PySide6>=6.6.0
SQLAlchemy>=2.0.0
reportlab>=4.0.0
pytest>=7.0.0
```

Optional for future:

```text
alembic
pyinstaller
```

---

# 23. Technical Acceptance Criteria

The application is release-ready when all of the following pass:

1. Application launches on supported Windows systems without errors.
2. SQLite database initializes automatically with the v1.2 schema.
3. A member can be added with all fields including `phone_landline`, `samaj`, `membership_fee`.
4. A member can be edited.
5. A member can be deleted with cascade to family records.
6. Multiple family members can be added with all 7 editable columns including `blood_group`.
7. Smart search finds members by name, mobile, samaj, and city.
8. Gujarati text is stored and displayed correctly in the UI.
9. Selecting a member auto-fills all fields of the official form.
10. `phone_landline`, `samaj`, and `membership_fee` appear in the generated form.
11. Family table `blood_group` column renders in the PDF.
12. Form can be previewed.
13. Form exports to PDF with correct Gujarati rendering.
14. PDF is A4 size and print-ready.
15. Form can be printed via system print dialog.
16. Database backup creates a valid `.db` file.
17. Database restore replaces data after confirmation.
18. Application works without internet connection.
19. Application runs acceptably on a 2 GB RAM machine.
20. Application can be packaged as a Windows executable.

---

# Conclusion

This TRD v1.2 provides a complete, finalized technical foundation for building the Gujarat Brahm Samaj Desktop Management System.

Key decisions made in this version:

- **ReportLab** is the confirmed PDF library — chosen for reliable Gujarati Unicode font embedding and precise layout control.
- **Noto Sans Gujarati** is the confirmed font — free, distributable, and full Unicode coverage.
- **All official form fields are now mapped** — `phone_landline`, `samaj`, `membership_fee` added to members; `blood_group` added to family_members.
- **Age is computed, not stored** — computed from `birth_date` on the member record at display time.
- **Surname-first entry order** is confirmed and documented for the member name input.

The application is ready to enter Milestone 1 development.
