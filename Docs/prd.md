# Product Requirements Document (PRD)

## Gujarat Brahm Samaj Desktop Management System

**Document Version:** 1.3  
**Release Target:** Production v1.0  
**Platform:** Windows 10 / 11 (64-bit Desktop Application)  
**Primary Mode:** 100% Offline (Local SQLite Storage)  
**Target Users:** Gujarat Brahm Samaj administrators, trustees, and authorized data entry operators  

---

## 1. Product Overview

The **Gujarat Brahm Samaj Desktop Management System** is a standalone, offline Windows desktop application engineered specifically for the Gujarat Brahm Samaj community (Sabarkantha / Idar jurisdiction).

The application provides a comprehensive digital ledger and official document generation suite:
- **Member & Family Registry**: Maintains full family profiles with primary member demographics and a 10-row family member table mirroring the official physical paper form.
- **Bilingual Operation**: Full Gujarati and English language support with instant runtime language switching.
- **Smart & Phonetic Search**: Instant lookup across Gujarati and English script with an automated phonetic transliteration engine (e.g., searching "joshi" or "trivedi" matches "જોશી" and "ત્રિવેદી").
- **Authentic Official Form Generation**: Direct vector recreation of the official paper application form via a custom `QPainter` drawing engine, complete with religious emblems (Gayatri Mata, Bhagwan Parshuram), the official Idar office header, and 10 family member rows with Gujarati numerals (૧ થી ૧૦).
- **Form Preview, Print & PDF Export**: Real-time raster preview in the UI, direct Windows printer dispatch, and high-definition 300 DPI PDF generation via `QPdfWriter` and ReportLab.
- **Smart Data Import & Export**: Full Excel (.xlsx) and CSV import/export engine featuring deduplication strategies (overwrite by mobile, code, or both) and automated pre-import safety backups.
- **Database Backup & Integrity Diagnostics**: One-click timestamped backups, instant restore with integrity verification, and vacuum optimization.
- **Single-File Windows Installer**: Production-ready Inno Setup installer delivering desktop shortcuts, uninstaller, and self-contained runtime dependencies.

---

## 2. Problem Statement

Historically, Gujarat Brahm Samaj membership records were maintained through physical paper forms or fragmented spreadsheets:
1. **Inefficient Member Retrieval**: Locating a specific member among thousands took hours.
2. **Language Barrier in Data Entry**: Operators often type in English phonetic script while records and official certificates require formal Gujarati Unicode script.
3. **Repeated Manual Paper Form Filling**: Administrative certificates, matrimony verifications, and directory publications required manually handwriting the official paper form repeatedly.
4. **Data Fragmentation and Risk of Loss**: Excel sheets lacked relational integrity between primary members and family dependents, with no automated backup or deduplication guardrails.

The system replaces manual paper workflows with a unified, high-performance offline solution that generates an authentic, print-ready replica of the official paper form on demand.

---

## 3. Product Goals & Success Criteria

### Primary Goals
1. **100% Offline Operation**: Zero reliance on cloud servers, external APIs, or active internet connectivity.
2. **Authentic Form Replication**: Render and print digital application forms that are indistinguishable from the official printed paper forms of the Samaj.
3. **Zero Data Loss**: Robust SQLite transactional safety with automated pre-import and pre-restore backups.
4. **Low Hardware Footprint**: Fluent responsiveness on budget PCs with dual-core CPUs and 2 GB RAM.
5. **Intuitive Bilingual UX**: Clean, modern interface accessible to non-technical Gujarati operators.

### Success Criteria
- Member search returns results in under 50 milliseconds across 10,000+ records.
- Official form rendering and PDF generation completes in under 1 second.
- Full backup creation and verification takes under 2 seconds.

---

## 4. Target User Personas

### 1. Chief Administrator / Trustee
- **Responsibilities**: Oversees community records, performs mass data imports/exports, manages database backups, audits system integrity, and configures organization metadata.
- **Key Features**: System Settings, Backup & Restore Manager, Import Wizard with duplicate resolution, Database Vacuum & Integrity Checks.

### 2. Office Data Entry Operator
- **Responsibilities**: Registers new families, updates phone numbers or addresses, searches records for community members visiting the office, and prints official application forms.
- **Key Features**: Dashboard KPI cards, Member Registration Form (Sections 1–4), Member Directory table, Form Preview & Print dialog.

---

## 5. Core Feature Specifications

### 5.1 Executive Dashboard
- **Metric Cards (KPIs)**:
  - **Total Members**: Count of primary registered heads of households.
  - **Total Family Members**: Total registered dependents across all families.
  - **Total Population**: Sum of primary members and dependents.
  - **Recent Registrations**: Number of registrations in the last 30 days.
- **Quick Action Launchpad**:
  - `+ Add New Member` (Navigates directly to Section 1 of registration).
  - `Members Directory` (Opens full searchable table).
  - `Import Data` (Opens Excel/CSV smart import wizard).
  - `Database Backup` (Direct one-click backup shortcut).
- **Recent Registrations Table**: Displays the 5 most recent members with one-click shortcuts to View Profile, Edit, or Print Form.

### 5.2 Member Registration & Editing (4-Section Form)
The member form faithfully maps to the official community registration document:
- **Section 1: Basic Information (સામાન્ય વિગત)**
  - Auto-generated sequential Member Code (`GBS-XXXXXX`).
  - (૧) **Full Name (નામ - અટક પ્રથમ)**: Required surname-first convention.
  - **Surname (અટક)** & **Father/Husband Name (પિતા/પતિનું નામ)**: Auto-parsed or manually refined.
  - (૨) **Postal Address (પત્ર વ્યવહારનું સરનામું)**: Current residential address.
  - (૩) **Native Village Address (ગામનું સરનામું)**: Ancestral native village in Gujarat.
  - City / Taluka, District, State, Pincode.
  - Primary Mobile (10-digit validated), Alternate Landline, Email Address.
  - Date of Birth with live automated age computation.
- **Section 2: Professional & Community Details (વ્યવસાય અને સમાજ વિગત)**
  - (૪) **Occupation / Business (ધંધો / વ્યવસાય)**.
  - (૫) **Business / Workplace Address (ધંધા / વ્યવસાયનું સરનામું)**.
  - (૬) **Annual Income (આવક)**.
  - Educational Qualification, Blood Group.
  - (૭) **Sub-Samaj / Branch (સમાજ)** and Membership Fee status.
- **Section 3: Family Members Grid (કુટુંબના સભ્યોની વિગત)**
  - 10-row structured table mirroring the physical form's table.
  - Row numbering in Gujarati numerals (૧ થી ૧૦).
  - Fields per dependent: Full Name, Relationship (સબંધ), Age (ઉમર), Education (અભ્યાસ), Blood Group (બ્લડ ગ્રુપ), Occupation (વ્યવસાય), Contact Number (મોબાઈલ).
  - Add/Remove row controls with automatic sequence recalculation.
- **Section 4: Declaration & Signature (સહી અને બાંહેધરી)**
  - Official text declaration pledging allegiance to Samaj bylaws.
  - Digital signature support: Typed applicant name or scanned signature image upload.

### 5.3 Member Directory & Smart Search
- **High-Performance Table**:
  - Columns: Member Code, Full Name, Father's Name, Native Village, City, Mobile, Samaj, Total Family Members, Actions.
  - Instant live filtering as the operator types.
- **Phonetic Bilingual Search**:
  - Translates Roman English input to Gujarati phonetic syllables.
  - Searches simultaneously across `full_name`, `surname`, `father_name`, `mobile`, `village_address`, `city`, and `occupation`.
- **Bulk & Individual Actions**:
  - View Profile, Edit Record, Generate Official Form, Delete Record (with double confirmation).
  - Export filtered search results directly to Excel (.xlsx) or CSV.

### 5.4 Authentic Official Form Generation (QPainter Engine)
The system renders an authentic vector/raster digital twin of the physical paper form:
- **Exact Layout Replica**:
  - Traditional double blue borders (`#1B2F8A`).
  - Religious invocations: *॥ શ્રી ગણેશાય નમઃ ॥*, *॥ શ્રી ગાયત્રી માતાયૈ નમઃ ॥*, *॥ શ્રી પરશુરામાય નમઃ ॥*.
  - Circular vector emblem badges on top-left and top-right corners.
  - Official header: **શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સા.કાં.** with registered office details: *શૈવ કૉમ્પ્લેક્સ, દામોદર એરિયા, સત્યમ હોસ્પિટલની સામે, ઇડર*.
  - Section banners with shaded headers and numbered Gujarati items.
  - 10-row family grid with Gujarati column headers and Gujarati serial numbers.
  - Standard passport photo box (૩ x ૨.૫ સેમી) in the top-right corner.
  - Bottom signature boxes for Member Signature and Authorized Samaj Secretary.
- **Preview & Output Pipeline**:
  - Interactive preview dialog with dynamic zoom (Fit Width, 100%, Zoom In/Out).
  - Direct 1-click print to any installed Windows printer or virtual PDF printer.
  - High-resolution 300 DPI PDF export (`QPdfWriter` + ReportLab fallback).

### 5.5 Smart Import & Export Engine
- **Supported Formats**: Excel (`.xlsx`) via OpenPyXL and Delimited Text (`.csv`).
- **Conflict Resolution Strategies**:
  - **Update Existing (Mobile & Code)**: Overwrites existing record if either matches.
  - **Match on Mobile Number Only**: Useful for bulk directory updates.
  - **Match on Member Code Only**: Strict ID overwrite.
  - **Insert Only (Skip Existing)**: Safe import preventing accidental overwrite.
- **Safety Rails**:
  - Automatically creates a timestamped database backup before executing any import.
  - Displays pre-import validation summary (Total Rows, Valid Records, Warnings, Conflicts).
  - Atomic transaction: rolls back completely if an unrecoverable database fault occurs.

### 5.6 Backup, Restore & System Maintenance
- **Automated & Manual Backups**:
  - Generates standalone SQLite copies in `backups/brahm_samaj_backup_YYYYMMDD_HHMMSS.db`.
  - Displays backup history with file size, creation timestamp, and integrity status.
- **Restore Engine**:
  - Validates SQLite header and runs `PRAGMA integrity_check` before applying restore.
  - Prompts for explicit operator confirmation.
- **Maintenance Tools**:
  - One-click Database Vacuum (`VACUUM`) to reclaim disk space and defragment indexes.
  - Schema migration runner (`check_and_migrate_db`) to ensure existing databases receive new columns seamlessly.

---

## 6. Technical Specifications Summary

| Layer | Technology |
|---|---|
| **Programming Language** | Python 3.12+ (Compatible with Python 3.14) |
| **GUI Framework** | PySide6 6.11.2 (Qt for Python, Fusion style with modern light palette) |
| **Database & ORM** | SQLite 3 with SQLAlchemy 2.0.46 |
| **Spreadsheet Engine** | OpenPyXL 3.1.5 & Python native `csv` |
| **Image & Graphics Engine** | Pillow (PIL) 12.3.0 & Qt `QPainter` vector pipeline |
| **PDF Generation** | PySide6 `QPdfWriter` (Primary) & ReportLab 5.0.1 (Fallback) |
| **Typography** | Noto Sans Gujarati (Regular & Bold), Segoe UI (System) |
| **Packaging & Installer** | PyInstaller 6.19.0 (onedir) + Inno Setup 6 (Single-file Setup Wizard) |

---

## 7. Non-Functional Requirements

### 7.1 Hardware Compatibility (Low-End PC Target)
- **Minimum RAM**: 2 GB RAM (Application baseline memory footprint: ~85 MB).
- **Processor**: Intel Celeron / Core 2 Duo or AMD equivalent (64-bit architecture).
- **Disk Footprint**: ~150 MB for installed runtime + local database.
- **Display Resolution**: Optimized for 1366x768 (standard laptop screens) up to 4K displays with DPI awareness.

### 7.2 Reliability & Fault Tolerance
- **Transactional Atomicity**: All multi-step write operations (member + 10 family rows) execute within atomic SQLAlchemy sessions.
- **Database Self-Healing**: On startup, database connections run migration checks and ensure foreign keys (`PRAGMA foreign_keys = ON;`) are enforced.
- **Crash Logging**: Unhandled exceptions are logged to `logs/application.log` with traceback details.

---

## 8. Release Roadmap & Future Scope

### Current Release: Version 1.0 (Completed)
- [x] Full offline Member & 10-Row Family Management.
- [x] Authentic Gujarati Form Drawing Engine (`FormRenderer`).
- [x] 300 DPI PDF generation and native Windows printing.
- [x] Excel/CSV Import/Export with conflict deduplication.
- [x] Bilingual English/Gujarati interface switch.
- [x] Inno Setup Windows installer (`GujaratBrahmSamaj_Setup_v1.0.exe`).

### Version 2.0 (Planned Post-Release Enhancements)
- **Digital Photo Capture**: Direct USB webcam integration to snap and crop member passport photos inside the app.
- **Digital Member ID Card Generator**: Printable PVC ID cards with QR codes linking to member verification records.
- **LAN Multi-User Sync**: Local SQLite replication across multiple PCs in the Samaj office over Wi-Fi/Ethernet without cloud dependency.
- **Matrimony Directory Filter**: Specialized community search module filtering unmarried members with horoscope and educational criteria.
