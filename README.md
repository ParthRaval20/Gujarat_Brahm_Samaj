# Gujarat Brahm Samaj Desktop Management System
### શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ મેનેજમેન્ટ સિસ્ટમ (સાબરકાંઠા - ઇડર શાખા)

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011%20(64--bit)-0078D6?style=flat&logo=windows)](https://microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.14-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Framework](https://img.shields.io/badge/Framework-PySide6%206.11-41CD52?style=flat&logo=qt)](https://qt.io)
[![Database](https://img.shields.io/badge/Database-SQLite%203%20(WAL)-003B57?style=flat&logo=sqlite)](https://sqlite.org)
[![Mode](https://img.shields.io/badge/Mode-100%25%20Offline-success)](file:///d:/Gujarat%20Brahm%20Samaj)
[![Installer](https://img.shields.io/badge/Release-v1.0%20Setup%20Installer-orange)](file:///d:/Gujarat%20Brahm%20Samaj/dist_installer)

A modern, high-performance, offline Windows desktop management system designed specifically for **Shree Samast Gujarat Brahm Samaj** (Sabarkantha / Idar branch). 

The system provides community member registration, 10-row family management, smart bilingual phonetic search, an authentic digital replica of the official printed Gujarati paper application form (`QPainter` vector engine), high-definition 300 DPI PDF export, native Windows printing, Excel/CSV bulk import/export with deduplication, and automated database backups.

---

## 🌟 Key Features

### 📊 Modern Executive Dashboard
- Real-time metric cards (KPIs): Total Members, Total Family Members, Total Population, and Registrations in the last 30 days.
- Quick-action launchpads: `+ Add Member`, `Search Directory`, `Import Data`, and `Backup Database`.
- 5 most recent registrations table with one-click actions: View Profile, Edit, and Print Official Form.
- Cultural hero header with Gayatri Mantra invocation.

### 📝 4-Section Member Registration Form
Strictly mirrors the official printed paper form:
1. **Section 1: Basic Information (સામાન્ય વિગત)**: Auto-generated sequential Member Code (`GBS-XXXXXX`), (૧) Full Name (Surname first), Surname, Father/Husband Name, (૨) Postal Address, (૩) Native Village Address, City/Taluka, District, State, Pincode, 10-digit Mobile Number (with regex validation), Landline, Email, and Date of Birth with live automated age calculation.
2. **Section 2: Professional & Community Details (વ્યવસાય અને સમાજ વિગત)**: (૪) Occupation/Business, (૫) Workplace Address, (૬) Annual Income, Education, Blood Group, (૭) Sub-Samaj/Branch, and Membership Fee.
3. **Section 3: Family Members Grid (કુટુંબના સભ્યોની વિગત)**: 10 structured rows with Gujarati numerals (`૧ થી ૧૦`), capturing Name, Relation, Age, Education, Blood Group, Occupation, and Contact Number.
4. **Section 4: Declaration & Signature (સહી અને બાંહેધરી)**: Text pledge with choice of typed digital signature or scanned signature image upload.

### 🔍 Smart Phonetic Bilingual Search
- Rapid lookup across 10,000+ records in under 30 milliseconds.
- **Phonetic Transliteration**: Type names in English (e.g. `joshi`, `trivedi`, `sabarkantha`) to match records written in Gujarati Unicode (`જોશી`, `ત્રિવેદી`, `સાબરકાંઠા`).
- Multi-field live query across name, surname, father's name, phone, native village, city, and occupation.
- Instant filters for Native Village, City/Taluka, and Samaj branch.

### 📄 Authentic Gujarati Form Vector Drawing Engine (`QPainter`)
- Generates an authentic digital twin of the physical paper form via `services/form_renderer.py`.
- Features traditional double royal blue borders (`#1B2F8A`), religious invocations (*॥ શ્રી ગણેશાય નમઃ ॥*, *॥ શ્રી ગાયત્રી માતાયૈ નમઃ ॥*, *॥ શ્રી પરશુરામાય નમઃ ॥*), circular vector medallions for Gayatri Mata & Bhagwan Parshuram, and official Idar office header credentials:
  > **શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સા.કાં.**  
  > *શૈવ કૉમ્પ્લેક્સ, દામોદર એરિયા, સત્યમ હોસ્પિટલની સામે, ઇડર*
- 10-row family table with official column headers and Gujarati serial numbers.
- 3 x 2.5 cm passport photo box and applicant/secretary signature boxes.

### 🖨 Native Printing & 300 DPI Vector PDF Export
- Real-time interactive raster/vector form preview with dynamic zoom (Fit Width, 100%, Zoom In/Out).
- One-click direct printing to any installed Windows printer via `QPrinter`.
- High-definition 300 DPI vector PDF export via `QPdfWriter` with ReportLab fallback.

### 📥 Smart Excel & CSV Import/Export Engine
- Supports both Excel (`.xlsx` via OpenPyXL) and delimited text (`.csv`).
- **4 Conflict Resolution Strategies**:
  1. `both`: Update existing record if either mobile number or member code matches.
  2. `mobile`: Match and update existing records by mobile number only.
  3. `code`: Match and update existing records by member code only.
  4. `insert_only`: Safe import skipping duplicates and inserting only new members.
- **Safety Rails**: Automatically takes a timestamped safety backup of the database before executing any import.

### 💾 Database Backup, Restore & VACUUM Maintenance
- One-click timestamped backups saved to `backups/brahm_samaj_backup_YYYYMMDD_HHMMSS.db`.
- Database restore engine with SQLite header validation and `PRAGMA integrity_check` verification.
- One-click `Optimize & Compact Database` (`VACUUM`) to reclaim disk space and defragment indexes.
- Dynamic schema migration (`check_and_migrate_db`) ensuring updates never wipe existing databases.

### 🌐 Instant Runtime Bilingual Toggle
- Switch between **ગુજરાતી** and **English** with a single click in the top toolbar.
- Updates all UI labels, form fields, table headers, and dialogs instantly without restarting.

### 📦 Windows Installer & Standalone Packaging
- Automated build pipeline producing a single-file Windows installer (`GujaratBrahmSamaj_Setup_v1.0.exe`).
- Installs desktop shortcut, Start Menu folder, and clean uninstaller that preserves user data.

---

## 🛠 Technology Stack

| Component | Technology | Version |
|---|---|---|
| **Language** | Python | 3.12+ (Tested on Python 3.14) |
| **GUI Framework** | PySide6 (Qt for Python) | 6.11.2 |
| **Database & ORM** | SQLite 3 (WAL Mode) + SQLAlchemy | 2.0.46 |
| **Form Rendering** | Qt QPainter Vector Engine | Bundled in PySide6 |
| **PDF Generation** | PySide6 QPdfWriter + ReportLab | ReportLab 5.0.1 |
| **Spreadsheets** | OpenPyXL + Python native csv | 3.1.5 |
| **Image Processing** | Pillow (PIL) | 12.3.0 |
| **Typography** | Noto Sans Gujarati (Bundled) | Regular & Bold |
| **Packaging** | PyInstaller + Inno Setup | PyInstaller 6.19.0 / Inno Setup 6 |

---

## 📁 Project Directory Structure

```text
GujaratBrahmSamaj/
│
├── main.py                        ← Main application entry point
├── dev_reload.py                  ← Development daemon with auto-reload
├── smoke_test.py                  ← Headless end-to-end integration test
├── Build_Installer.bat            ← Automated PyInstaller + Inno Setup build script
├── Run App.bat                    ← 1-Click application launcher
├── Run Dev (Auto-Reload).bat      ← 1-Click developer auto-reload launcher
├── GujaratBrahmSamaj.spec         ← PyInstaller onedir build specification
├── installer.iss                  ← Inno Setup 6 packaging configuration script
├── requirements.txt               ← Python package dependencies
│
├── app/                           ← Core application configuration
│   ├── config.py                  ← Paths, theme tokens, typography, constants
│   └── translations.py            ← Complete bilingual Gujarati/English dictionaries
│
├── database/                      ← Database layer
│   ├── connection.py              ← SQLAlchemy engine, sessionmaker, schema migrations
│   └── models.py                  ← ORM models (Member, FamilyMember, AppSetting)
│
├── services/                      ← Business logic layer
│   ├── member_service.py          ← Member CRUD & validation
│   ├── family_service.py          ← Family member CRUD
│   ├── search_service.py          ← Multi-field member search
│   ├── form_renderer.py          ← Authentic official Gujarati form QPainter engine
│   ├── form_service.py            ← Maps DB records to form data dictionary
│   ├── pdf_service.py             ← 300 DPI A4 PDF generator (QPdfWriter/ReportLab)
│   ├── import_export_service.py  ← Excel/CSV smart import & export with deduplication
│   ├── backup_service.py          ← SQLite backup, restore & integrity check
│   └── settings_service.py        ← Application preferences & org metadata
│
├── ui/                            ← User interface layer (PySide6)
│   ├── main_window.py             ← MainWindow with dark sidebar, top bar & lang toggle
│   ├── dashboard.py               ← Modern KPI dashboard, launchpads & recent table
│   ├── member_form.py             ← 4-section authentic registration form with 10 family rows
│   ├── member_list.py             ← Member directory table with search, filters & export
│   ├── member_profile.py          ← Detailed member profile & quick action launchers
│   ├── form_preview.py            ← Real-time authentic vector/raster form preview
│   ├── backup_restore.py          ← Backup archive management & DB maintenance
│   ├── import_data_dialog.py      ← Import wizard with conflict resolution strategies
│   ├── system_settings.py         ← App preferences, org details & DB diagnostics
│   └── widgets/
│       └── family_table_widget.py ← Dynamic 10-row family member grid editor
│
├── utils/                         ← Helper utilities
│   ├── gujarati_search.py         ← Phonetic transliteration & multi-script matching
│   ├── date_utils.py              ← Age calculation & date formatting
│   ├── file_utils.py              ← Filename sanitization & path helpers
│   └── validators.py              ← Input validation rules
│
├── assets/                        ← Bundled application assets
│   ├── fonts/                     ← Noto Sans Gujarati (Regular & Bold)
│   ├── icons/                     ← Application icon & SVG chevron dropdown indicators
│   └── images/                    ← Official logos & emblems (Gayatri, Parshuram, official_form)
│
├── data/                          ← Local database directory (brahm_samaj.db)
├── backups/                       ← Automated & manual database backup snapshots
├── exports/                       ← Exported PDF forms and Excel/CSV files
├── logs/                          ← Runtime execution logs (application.log)
├── tests/                         ← Automated pytest test suites (6 consolidated suites)
└── Docs/                          ← Project documentation suite (v1.3)
    ├── prd.md                     ← Product Requirements Document
    ├── trd.md                     ← Technical Requirements Document
    ├── uiux.md                    ← UI/UX Design & Architecture Specification
    ├── databaseschema.md          ← Database Schema Specification & DDL
    ├── appflow.md                 ← Application Flow & Navigation Document
    └── implementation plan.md     ← Implementation Plan & Status Scorecard
```

---

## 🚀 Getting Started

### Prerequisites
- **Operating System**: Windows 10 or Windows 11 (64-bit).
- **Python**: Version 3.12 or higher (Python 3.14 fully supported).

### Installation & Setup

1. **Clone or Download the Repository**:
   ```powershell
   git clone https://github.com/ParthRaval20/Gujarat_Brahm_Samaj.git
   cd "Gujarat Brahm Samaj"
   ```

2. **Create and Activate a Virtual Environment**:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

---

## 💻 Running the Application

### Option 1: Standard Launcher (Double-Click)
Simply double-click **`Run App.bat`** in the project root directory.

### Option 2: Command Line
```powershell
python main.py
```

### Option 3: Developer Mode with Auto-Reload
For active development with instant reloading when files change:
- Double-click **`Run Dev (Auto-Reload).bat`**, OR run:
  ```powershell
  python dev_reload.py
  ```

---

## 🧪 Testing & Quality Assurance

The project comes with a comprehensive suite of 10 automated test suites.

### Run All Tests via PyTest
```powershell
pytest
```

### Run Fast Headless Smoke Test
Verifies database initialization, member/family creation, form data mapping, PDF export, search, and backup in under 2 seconds:
```powershell
python smoke_test.py
```

---

## 📦 Building the Windows Installer

The application includes an automated one-click packaging pipeline:

1. Ensure **Inno Setup 6** is installed on your system.
2. Run the build batch file:
   ```powershell
   .\Build_Installer.bat
   ```
3. The build process will:
   - Compile the Python code and bundled assets into a standalone directory (`dist/GujaratBrahmSamaj/`) using PyInstaller.
   - Run Inno Setup Compiler (`iscc`) to package everything into a single setup executable:
     ```text
     dist_installer/GujaratBrahmSamaj_Setup_v1.0.exe
     ```

---

## 📚 Documentation Reference

Complete technical and functional specifications are maintained in the [Docs/](file:///d:/Gujarat%20Brahm%20Samaj/Docs) folder:

| Document | Description |
|---|---|
| [prd.md](file:///d:/Gujarat%20Brahm%20Samaj/Docs/prd.md) | **Product Requirements Document (v1.3)**: Core features, user personas, success criteria, offline and low-end hardware target specifications. |
| [trd.md](file:///d:/Gujarat%20Brahm%20Samaj/Docs/trd.md) | **Technical Requirements Document (v1.3)**: System architecture, ORM models, QPainter vector rendering pipeline, import/export mechanics, and build tools. |
| [uiux.md](file:///d:/Gujarat%20Brahm%20Samaj/Docs/uiux.md) | **UI/UX Design Specification (v1.3)**: Color tokens (`#0F172A`, `#1B2F8A`, `#2563EB`), typography scale, screen layouts, accessibility standards, and senior citizen usability guidelines. |
| [databaseschema.md](file:///d:/Gujarat%20Brahm%20Samaj/Docs/databaseschema.md) | **Database Schema (v1.3)**: Mermaid ER diagram, full data dictionaries, indexing strategy, SQLite DDL, and sample records. |
| [appflow.md](file:///d:/Gujarat%20Brahm%20Samaj/Docs/appflow.md) | **Application Flow Document (v1.3)**: Step-by-step navigation diagrams, form generation flows, spreadsheet import wizard flows, and error recovery handling. |
| [implementation plan.md](file:///d:/Gujarat%20Brahm%20Samaj/Docs/implementation%20plan.md) | **Implementation Plan & Status (v1.3)**: Phase-by-phase completion scorecard, test verification summary, and v2.0 roadmap. |

---

## 🔒 Data Safety & Privacy
- **100% Offline**: All records are stored strictly on the local machine in `data/brahm_samaj.db`. No data is ever transmitted over the network or stored in external cloud services.
- **Safety Backups**: The system takes automatic safety backups prior to executing any spreadsheet import or database restore operation.

---

## 👥 Organization & Credits

Dedicated to **Shree Samast Gujarat Brahm Samaj (Sabarkantha / Idar branch)**.  
Registered Office: *શૈવ કૉમ્પ્લેક્સ, દામોદર એરિયા, સત્યમ હોસ્પિટલની સામે, ઇડર*.
