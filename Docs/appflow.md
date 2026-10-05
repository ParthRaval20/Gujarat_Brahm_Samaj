# Application Flow Document (App Flow)

## Gujarat Brahm Samaj Desktop Management System

**Document Version:** 1.3  
**Release Target:** Production v1.0  
**Application Type:** Standalone Offline Windows Desktop Application  
**Primary Users:** Samaj Administrators, Community Trustees, and Data Entry Operators  
**Related Documents:** PRD.md, TRD.md, UIUX.md, DatabaseSchema.md  

---

## 1. Core Architectural Flow Philosophy

The Gujarat Brahm Samaj Desktop Management System is engineered for smooth, uninterrupted operator workflow. Navigation adheres to three guiding principles:
1. **Zero-Dead-End Guarantee**: Every view contains clear, visible breadcrumbs or back actions (`← Back to Directory` / `← Back to Dashboard`).
2. **Instant Situational Feedback**: All data operations (saves, updates, imports, backups, deletions) provide explicit visual confirmation dialogs.
3. **Safety First**: Non-reversible actions (deleting records, restoring backups, importing spreadsheets) are guarded by multi-step confirmations and automated pre-operation backups.

---

## 2. High-Level System Navigation Map

```text
                                 +-----------------------+
                                 |  APPLICATION STARTUP  |
                                 +-----------+-----------+
                                             |
                                             v
                                 +-----------------------+
                                 |   EXECUTIVE DASHBOARD | <-----------------------------------+
                                 +-----------+-----------+                                     |
                                             |                                                 |
         +-------------------+---------------+-------------------+------------------+          |
         |                   |                                   |                  |          |
         v                   v                                   v                  v          |
+-----------------+ +-----------------+                 +-----------------+ +----------------+ |
| + ADD NEW       | | MEMBER          |                 | SMART DATA      | | BACKUP &       | |
| MEMBER          | | DIRECTORY       |                 | IMPORT WIZARD   | | RESTORE        | |
+--------+--------+ +--------+--------+                 +--------+--------+ +--------+-------+ |
         |                   |                                   |                  |          |
         |                   v                                   v                  v          |
         |          +-----------------+                 +-----------------+ +----------------+ |
         |          | PHONETIC SEARCH |                 | EXCEL/CSV FILE  | | ONE-CLICK      | |
         |          | & LIVE FILTERS  |                 | & CONFLICT MODE | | DB BACKUP      | |
         |          +--------+--------+                 +--------+--------+ +--------+-------+ |
         |                   |                                   |                  |          |
         v                   v                                   v                  v          |
+-----------------+ +-----------------+                 +-----------------+ +----------------+ |
| 4-SECTION FORM  | | MEMBER PROFILE  |                 | AUTO BACKUP &   | | RESTORE & DB   | |
| & 10 FAMILY ROWS| | SUMMARY         |                 | TRANSACTION RUN | | VACUUM CLEAN   | |
+--------+--------+ +--------+--------+                 +-----------------+ +----------------+ |
         |                   |                                                                 |
         |                   +------------------+                                              |
         |                                      |                                              |
         v                                      v                                              |
+-----------------+                   +--------------------+                                   |
| SAVE RECORD     | ----------------> | FORM PREVIEW ENGINE| ----------------------------------+
+-----------------+                   +---------+----------+
                                                |
                                      +---------+----------+
                                      |                    |
                                      v                    v
                              +---------------+    +---------------+
                              | NATIVE WIN32  |    | 300 DPI A4    |
                              | PRINT DISPATCH|    | VECTOR PDF    |
                              +---------------+    +---------------+
```

---

## 3. Application Startup & Initialization Flow

```text
[ Windows Shortcut / GujaratBrahmSamaj.exe ]
                  │
                  ▼
        main.py Entry Point
                  │
                  ▼
         QApplication Init
                  │
                  ▼
    Initialize Storage Directories
 (data/, backups/, exports/, logs/)
                  │
                  ▼
       database/connection.py
   - Connect to data/brahm_samaj.db
   - PRAGMA foreign_keys = ON;
   - PRAGMA journal_mode = WAL;
   - Run check_and_migrate_db()
                  │
                  ▼
       Load User Preferences
(Language: Gujarati / English; Org Info)
                  │
                  ▼
       Launch MainWindow UI
(Set Fusion Style, Apply Palette & Fonts)
                  │
                  ▼
         Open Dashboard View
```

---

## 4. End-to-End User Workflows

### 4.1 Member Registration Flow (`ui/member_form.py`)

This workflow captures full household records mirroring the physical paper document:

```text
1. Operator clicks "+ Add New Member" from Dashboard or Sidebar.
2. System allocates next sequential Member Code (e.g. GBS-001251).
3. Section 1: Basic Details (સામાન્ય વિગત)
   ├── Enters Full Name (Surname first, e.g. "જોશી રમેશચંદ્ર મોહનલાલ")
   ├── System auto-splits / operator verifies Surname & Father's Name
   ├── Enters Postal Address & Native Village Address
   ├── Enters City, District, State, Pincode
   ├── Enters 10-digit Mobile Number (Live regex validation)
   └── Enters Date of Birth (System automatically calculates & displays age)
4. Section 2: Professional & Community Details (વ્યવસાય અને સમાજ વિગત)
   ├── Enters Occupation & Workplace Address
   ├── Enters Annual Income
   └── Selects Education, Blood Group, and Samaj branch
5. Section 3: 10-Row Family Grid (કુટુંબના સભ્યોની વિગત)
   ├── Operator enters dependents in rows 1 to 10 (Numbered ૧ થી ૧૦)
   ├── For each dependent: Name, Relation, Age, Education, Blood Group, Occupation, Contact
   └── Operator can Add Row or Delete Row
6. Section 4: Declaration & Signature (સહી અને બાંહેધરી)
   ├── Types applicant signature name OR uploads scanned signature file
7. Operator clicks "[ 💾 Save Member Record ]" or "[ 🖨 Save & Print Official Form ]"
   ├── Validation Check: Verifies Full Name and 10-digit Mobile
   │     ├── If Invalid: Highlights field with red alert tooltip
   │     └── If Valid: Begins atomic database transaction
   ├── Saves primary Member record to 'members' table
   ├── Saves family dependents to 'family_members' table with foreign key linkage
   └── Displays success notification and navigates to Profile or Form Preview
```

---

### 4.2 Member Directory & Phonetic Search Flow (`ui/member_list.py`)

Enables instantaneous discovery across thousands of community members:

```text
1. Operator navigates to "Member Directory" (સભ્ય યાદી).
2. All members load in a high-speed paginated table.
3. Operator enters search term in search box:
   ├── English Phonetic Input: "trivedi idar"
   │     └── Phonetic Engine (utils/gujarati_search.py) transliterates to "ત્રિવેદી ઇડર"
   └── Gujarati Direct Input: "જોશી"
4. Search query executes multi-column match across:
   ├── full_name, surname, father_name
   ├── mobile, village_address, city, occupation
5. Table updates in real-time (< 30ms latency).
6. Operator applies optional dropdown filters:
   ├── Filter by Native Village (ગામ)
   ├── Filter by City / Taluka (શહેર)
   └── Filter by Samaj Branch (શાખા)
7. Per-Row Action Launchers:
   ├── [👁 View]: Opens Member Profile screen
   ├── [✏ Edit]: Opens Member Form pre-populated for editing
   ├── [🖨 Form]: Directly opens Authentic Form Preview & Print
   └── [🗑 Delete]: Triggers confirmation dialog with cascading deletion
8. Batch Export Actions:
   ├── Operator clicks "[ 📥 Export to Excel ]" -> writes active filtered list to .xlsx
   └── Operator clicks "[ 📄 Export to CSV ]"   -> writes active filtered list to .csv
```

---

### 4.3 Authentic Form Generation & Print Pipeline (`services/form_renderer.py` & `ui/form_preview.py`)

Generates a 100% digital vector twin of the official paper application form:

```text
1. Operator initiates form generation from Member Profile, Directory, or Form Save.
2. FormService extracts member demographics and family members list.
3. FormRenderer (services/form_renderer.py) initializes QPainter on high-DPI surface:
   ├── Draws double royal blue outer border (#1B2F8A)
   ├── Draws top religious invocations:
   │   "॥ શ્રી ગણેશાય નમઃ ॥"  "॥ શ્રી ગાયત્રી માતાયૈ નમઃ ॥"  "॥ શ્રી પરશુરામાય નમઃ ॥"
   ├── Renders vector emblem medallions for Gayatri Mata & Bhagwan Parshuram
   ├── Renders official Samaj header & Idar office address:
   │   "શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સા.કાં. (ઇડર)"
   ├── Draws Member Code badge and Passport Photo Box (૩ x ૨.૫ સેમી)
   ├── Fills numbered Gujarati fields:
   │   (૧) સભ્યનું પૂરું નામ (અટક પ્રથમ)
   │   (૨) પત્ર વ્યવહારનું સરનામું, (૩) ગામનું સરનામું, ફોન / મોબાઈલ નં.
   │   (૪) ધંધો / વ્યવસાય, (૫) ધંધાનું સરનામું, (૬) આવક, (૭) સમાજ
   ├── Draws 10-row family table with official column headers and Gujarati numerals (૧ થી ૧૦)
   └── Draws applicant signature block and authorized Samaj secretary verification box
4. FormPreview dialog displays interactive preview:
   ├── Zoom Controls: Fit Width, 100% Native, Zoom In (+), Zoom Out (-)
5. Output Options:
   ├── [ 🖨 Print ]:
   │     └── Invokes QPrintDialog -> Windows Spooler -> Dispatches to physical A4 printer
   └── [ 📄 Save as PDF ]:
         └── Invokes QPdfWriter / ReportLab -> Prompts destination -> Generates 300 DPI vector PDF
```

---

### 4.4 Smart Spreadsheet Import Flow (`services/import_export_service.py` & `ui/import_data_dialog.py`)

Handles safe bulk ingestion from community spreadsheets:

```text
1. Operator clicks "Import Data" from Dashboard or Sidebar.
2. Operator selects .xlsx or .csv source file.
3. Operator selects Conflict Resolution Strategy:
   ├── Mode A: Update Existing (Match on Mobile OR Member Code)
   ├── Mode B: Match on Mobile Number Only
   ├── Mode C: Match on Member Code Only
   └── Mode D: Insert Only (Skip all conflicting records)
4. System executes Pre-Import Validation:
   ├── Scans column headers (maps English & Gujarati headers)
   ├── Verifies row count and flags invalid phone numbers or missing names
   └── Displays pre-flight summary dialog to operator
5. Operator clicks "[ Confirm & Run Import ]":
   ├── Safety Step: System automatically creates a timestamped database backup in backups/
   ├── Database executes batch transaction
   ├── Updates existing members / inserts new members & family rows
   └── On error: rolls back transaction completely and restores from pre-import backup
6. Import completion modal presents detailed summary:
   └── "Import Complete: 250 Total Rows | 210 Inserted | 35 Updated | 5 Skipped"
```

---

### 4.5 Database Backup, Restore & Maintenance Flow (`ui/backup_restore.py`)

Guarantees data permanence and zero data loss on offline machines:

```text
[ Backup Workflow ]
1. Operator navigates to "Backup & Restore" screen.
2. Clicks "[ 💾 Create Backup Now ]".
3. System copies active data/brahm_samaj.db into backups/brahm_samaj_backup_YYYYMMDD_HHMMSS.db.
4. BackupService runs PRAGMA integrity_check on the generated archive.
5. Backup history table refreshes with new entry, file size, and "Verified" status.

[ Restore Workflow ]
1. Operator selects a backup from history or clicks "[ Choose External Backup File ]".
2. System inspects the candidate file:
   ├── Validates SQLite header magic bytes
   └── Runs integrity check
3. Red Danger Modal appears:
   "Warning: Restoring will overwrite the current database. Proceed?"
4. Operator confirms restore.
5. System takes an emergency safety backup of current database first.
6. Target backup replaces active database.
7. System reloads database connection and refreshes UI.

[ Maintenance Workflow ]
1. Operator clicks "[ 🧹 Optimize & Compact Database ]".
2. System executes SQL "VACUUM;" command.
3. Defragments tables, rebuilds indexes, and reclaims deleted disk space.
4. Displays confirmation showing bytes saved.
```

---

### 4.6 Runtime Language Switching Flow

Provides instant localization without interrupting work:

```text
1. Operator clicks top-right language button: "[ 🌐 ગુજરાતી ]" or "[ 🌐 English ]".
2. translations.py loads requested language dictionary.
3. MainWindow dispatches languageChanged signal across all active widgets:
   ├── Sidebar navigation labels refresh
   ├── Screen titles and breadcrumbs refresh
   ├── Form section titles and input labels refresh
   ├── Table column headers and filter menus refresh
   └── Status bar updates
4. Persistent preference is saved to app_settings table in database.
```

---

## 5. Error Recovery & Edge Case Handling Flows

| Scenario | System Flow & Operator Experience |
|---|---|
| **Database File Locked or Inaccessible** | Displays descriptive error modal suggesting user close conflicting software; offers to retry or load latest backup. |
| **Duplicate Mobile Number on New Registration** | Warning dialog appears informing operator that a member with this mobile already exists; provides shortcut to view existing member profile. |
| **Missing Fonts on Target Windows Machine** | System automatically falls back to bundled `assets/fonts/NotoSansGujarati-Regular.ttf` loaded via `QFontDatabase`. |
| **Power Failure During Data Import** | Atomic transaction guarantees SQLite WAL rollback; automated pre-import backup ensures zero data loss. |
| **Printer Offline or Paper Jam** | Win32 spooler error is trapped; user is notified and given 1-click option to save as PDF instead. |
