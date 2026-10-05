# UI/UX Design & Architecture Specification

## Gujarat Brahm Samaj Desktop Management System

**Document Version:** 1.3  
**Release Target:** Production v1.0  
**Target Users:** Samaj administrators, community trustees, data entry operators, and senior citizens  
**Platform:** Windows 10 / 11 (64-bit Desktop Application)  
**Design System:** Modern Professional Light Theme with Deep Slate Navigation & Cultural Blue Accents  

---

## 1. Design Purpose & Philosophy

The user interface of the Gujarat Brahm Samaj Desktop Management System balances two essential objectives:
1. **Modern Professional Aesthetics**: Delivers a crisp, desktop application feel utilizing clean card elevations, harmonious HSL palettes, and refined typography.
2. **Senior & Non-Technical Accessibility**: Prioritizes effortless readability, high contrast, self-explanatory iconography, and one-click actions tailored for community elders and operators without IT background.

### Core UX Principles
- **Clarity Over Complexity**: Critical actions (`Add Member`, `Print Form`, `Backup`) are always top-level and never hidden in cascading menus.
- **Bilingual Fluidity**: Instant runtime toggle between Gujarati (ગુજરાતી) and English with zero application restarts.
- **Safe & Predictable Interactions**: Double confirmation for destructive operations (delete/restore) and pre-action backup guarantees.
- **Physical-to-Digital Parity**: The digital data-entry form and generated printout directly mirror the community's official paper document.

---

## 2. Design Tokens & Visual Hierarchy

The application employs a curated design token system defined centrally in `app/config.py`:

### 2.1 Color Palette
| Token | Hex Value | Usage & Visual Role |
|---|---|---|
| `BG_DARK_SIDEBAR` | `#0F172A` | Deep slate navigation sidebar background |
| `BG_SIDEBAR_ACTIVE` | `#1E293B` | Selected navigation item background |
| `SIDEBAR_ACTIVE_ACCENT`| `#2563EB` | Active indicator left-border (3px solid) |
| `BG_LIGHT` | `#F8FAFC` | Primary application canvas / workspace background |
| `BG_CARD` | `#FFFFFF` | Elevated card container background |
| `BORDER_LIGHT` | `#E2E8F0` | Subtle hairline borders on cards, inputs, and tables |
| `TEXT_PRIMARY` | `#0F172A` | High-contrast heading and primary text |
| `TEXT_SECONDARY` | `#64748B` | Subtitles, field descriptions, and metadata |
| `TEXT_MUTED` | `#94A3B8` | Watermarks, placeholders, and inactive labels |
| `ACCENT_CULTURAL_BLUE` | `#1B2F8A` | Traditional official Samaj blue (form borders, logos, banners) |
| `ACCENT_BRAND_BLUE` | `#2563EB` | Primary CTA buttons, focus outlines, selection highlights |
| `STATUS_SUCCESS` | `#16A34A` | Success messages, backup confirmations, active badges |
| `STATUS_DANGER` | `#DC2626` | Delete actions, destructive alerts, error notices |
| `STATUS_WARNING` | `#D97706` | Pre-import conflict notices, unsaved changes warnings |

### 2.2 Typography System
The application utilizes bundled high-definition Unicode fonts to ensure uniform cross-platform Gujarati rendering:
- **Primary Gujarati Font**: `Noto Sans Gujarati` (`assets/fonts/NotoSansGujarati-Regular.ttf` & `Bold.ttf`).
- **Primary Latin/System Font**: `Segoe UI`, `SF Pro Display`, `sans-serif`.
- **Typographic Scale**:
  - **Hero Welcome Title**: 24pt Bold (`#0F172A`)
  - **Screen Titles**: 18pt–20pt Semi-Bold (`#0F172A`)
  - **Card Headers & Section Titles**: 13pt–15pt Semi-Bold (`#1E293B`)
  - **Body & Form Field Labels**: 10.5pt–11pt Medium (`#334155`)
  - **Table Cells & Input Text**: 10pt–10.5pt Regular (`#0F172A`)
  - **Microcopy & Captions**: 9pt Regular (`#64748B`)

---

## 3. Global Application Architecture & Layout

The main window (`ui/main_window.py`) utilizes a fixed dual-pane layout:

```text
+----------------------------------------------------------------------------------------------------+
|  [Logo] Gujarat Brahm Samaj                                                    [🌐 ગુજરાતી] [Status]|
+-----------------------+----------------------------------------------------------------------------+
|                       |                                                                            |
|  📊 Dashboard         |                                                                            |
|                       |                                                                            |
|  ➕ Add Member        |                         Active Workspace Area                              |
|                       |                        (QStackedWidget Pages)                              |
|  👥 Member Directory  |                                                                            |
|                       |   - Dashboard (KPIs, launchpads, recent table)                             |
|  📄 Form Preview      |   - Member Form (4-section registration wizard)                            |
|                       |   - Member List (Searchable directory with filters)                        |
|  📥 Import Data       |   - Member Profile (Details, family summary, shortcuts)                   |
|                       |   - Form Preview & Print Engine                                            |
|  💾 Backup & Restore  |   - Smart Import & Conflict Resolver                                       |
|                       |   - Backup Manager & Diagnostics                                           |
|  ⚙ Settings          |   - System Preferences & Samaj Metadata                                    |
|                       |                                                                            |
+-----------------------+----------------------------------------------------------------------------+
|  v1.0.0 Production   |  Database: Connected (data/brahm_samaj.db)                   Auto-Save OK  |
+-----------------------+----------------------------------------------------------------------------+
```

### 3.1 Sidebar Navigation
- **Width**: Fixed 250px for stable visual weight.
- **Top Brand Block**:
  - Gold & blue community insignia (`assets/images/logo.png`).
  - Organization title: **ગુજરાત બ્રહ્મ સમાજ** with subtitle: **સાબરકાંઠા - ઇડર શાખા**.
- **Interactive Navigation Links**:
  - High vertical hit target (44px height) with 12px horizontal padding.
  - Hover transition with subtle background lightens (`rgba(255, 255, 255, 0.06)`).
  - Selected state: Deep blue background (`#1E293B`) with a 3.5px solid blue border on the left edge (`#2563EB`).
- **Footer Section**:
  - Current system version badge and active database status.

### 3.2 Top Header & Control Bar
- **Bilingual Toggle Button**: Prominently situated at the top-right (`🌐 ગુજરાતી` / `🌐 English`). Clicking immediately refreshes all static labels, table headers, validation tooltips, and dialogs.
- **Current Page Breadcrumb**: Shows current location (e.g., `મુખ્ય પૃષ્ઠ / સભ્ય નોંધણી ફોર્મ`).

---

## 4. Screen-by-Screen UI Specifications

### 4.1 Dashboard (`ui/dashboard.py`)
The central command center greets the operator and provides instant situational awareness:

```text
+----------------------------------------------------------------------------------------------------+
| [Hero Banner] શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ - સાબરકાંઠા (ઇડર)                                          |
| "॥ ૐ ભૂર્ભુવઃ સ્વઃ તત્સવિતુર્વરેણ્યં ભર્ગો દેવસ્ય ધીમહિ ધિયો યો નઃ પ્રચોદયાત્ ॥"                       |
+----------------------------------------------------------------------------------------------------+
|  [ 👤 Total Members ]    [ 👨‍👩‍👧‍👦 Family Members ]    [ 👥 Total Population ]    [ 📅 Recent 30 Days ]   |
|         1,250                     4,680                    5,930                     48            |
+----------------------------------------------------------------------------------------------------+
|  QUICK LAUNCHPAD                                                                                   |
|  [ + Add New Member ]     [ 🔍 Search Directory ]    [ 📥 Import Excel ]      [ 💾 Backup Database ]|
+----------------------------------------------------------------------------------------------------+
|  RECENT REGISTRATIONS                                                           [ View All Members ]|
|  Code       Name                  Village         City          Mobile       Actions               |
|  GBS-001250 Joshi Rameshchandra   Chandrani       Idar          98250XXXXX   [View] [Edit] [Print] |
|  GBS-001249 Trivedi Harshadrai    Khedbrahma      Himatnagar    94260XXXXX   [View] [Edit] [Print] |
|  GBS-001248 Dave Bharatkumar      Bhiloda         Idar          99090XXXXX   [View] [Edit] [Print] |
+----------------------------------------------------------------------------------------------------+
```

- **Hero Cultural Banner**: Deep navy gradient with gold religious invocation, instilling institutional pride.
- **Metric Cards (KPIs)**: Clean white cards with light borders (`#E2E8F0`), colored accent icon badges, bold 24pt counters, and descriptive sub-labels.
- **Action Launchpad**: 4 large cards with hover elevation enabling single-click navigation to primary workflows.
- **Recent Registrations**: Displays the 5 latest members with direct action buttons (`View`, `Edit`, `Print Form`).

---

### 4.2 Member Registration & Edit Form (`ui/member_form.py`)
Designed as a structured, 4-section card layout that strictly adheres to the official paper form fields:

- **Section 1: Basic Information (સામાન્ય વિગત)**
  - Auto-generated Member Code badge (`GBS-XXXXXX`).
  - (૧) **Full Name (નામ - અટક પ્રથમ)**: Large prominent text field.
  - **Surname (અટક)** & **Father/Husband Name (પિતા/પતિનું નામ)** in side-by-side columns.
  - (૨) **Postal Address (પત્ર વ્યવહારનું સરનામું)** & (૩) **Native Village Address (ગામનું સરનામું)**.
  - City / Taluka, District, State, Pincode.
  - Primary Mobile (10 digits with live validation badge), Landline, Email Address.
  - Date of Birth with automated live age calculation label.
- **Section 2: Professional & Community Details (વ્યવસાય અને સમાજ વિગત)**
  - (૪) **Occupation / Business (ધંધો / વ્યવસાય)** & (૫) **Workplace Address (ધંધાનું સરનામું)**.
  - (૬) **Annual Income (આવક)**.
  - Education Qualification & Blood Group dropdown.
  - (૭) **Sub-Samaj / Branch (સમાજ)** and Membership Fee status.
- **Section 3: Family Members Grid (કુટુંબના સભ્યોની વિગત)**
  - 10-row structured table with Gujarati numerals (`૧, ૨, ૩ ... ૧૦`).
  - Columns: No., Name (નામ), Relation (સબંધ), Age (ઉમર), Education (અભ્યાસ), Blood Group (બ્લડ ગ્રુપ), Occupation (વ્યવસાય), Contact Number (મોબાઈલ નં.).
  - `+ Add Family Member` button and row delete controls (`✕`).
- **Section 4: Declaration & Signature (સહી અને બાંહેધરી)**
  - Official text declaration.
  - Choice of digital signature: Typed applicant signature or scanned image upload with live thumbnail.
- **Action Footer**:
  - `[ Cancel / Back ]` (Neutral secondary)
  - `[ 💾 Save Member Record ]` (Prominent Primary Blue `#2563EB`)
  - `[ 🖨 Save & Print Official Form ]` (Success Green `#16A34A`)

---

### 4.3 Member Directory & Smart Search (`ui/member_list.py`)
Engineered for rapid lookup across thousands of community records:

- **Search Toolbar**:
  - Prominent search input with built-in clear button and search icon.
  - **Phonetic Bilingual Search**: Type in English phonetic characters (e.g. `dave`, `trivedi`, `idar`) or Gujarati Unicode (`દવે`, `ત્રિવેદી`, `ઇડર`).
  - Village, City, and Samaj filter dropdowns.
  - Records count indicator (e.g., `Showing 1,250 of 1,250 members`).
- **Data Table**:
  - Alternating light row backgrounds for effortless tracking across wide screens.
  - Hover row highlight.
  - Direct Action Buttons per row: `View` (Eye icon), `Edit` (Pencil icon), `Print Form` (Printer icon), `Delete` (Trash icon).
- **Batch Export**:
  - `[ 📥 Export to Excel (.xlsx) ]` and `[ 📄 Export to CSV ]` buttons export the active filtered list instantly.

---

### 4.4 Form Preview & Print Engine (`ui/form_preview.py`)
Provides an authentic digital preview of the printed form:

```text
+----------------------------------------------------------------------------------------------------+
|  Form Preview - GBS-000102: Trivedi Harshadrai                                                     |
+----------------------------------------------------------------------------------------------------+
|  [ 🔍 Fit Width ]  [ 100% ]  [ 🔍+ Zoom In ]  [ 🔍- Zoom Out ]       [ 🖨 Print ]  [ 📄 Save PDF ]|
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|    +------------------------------------------------------------------------------------------+    |
|    |  ॥ શ્રી ગણેશાય નમઃ ॥           ॥ શ્રી ગાયત્રી માતાયૈ નમઃ ॥         ॥ શ્રી પરશુરામાય નમઃ ॥   |    |
|    |  [Gayatri Emblem]           શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સા.કાં.         [Parshuram Emblem]   |    |
|    |                           શૈવ કૉમ્પ્લેક્સ, દામોદર એરિયા, ઇડર                               |    |
|    |  --------------------------------------------------------------------------------------  |    |
|    |  સભ્ય નોંધણી ક્રમાંક: GBS-000102                                      [ ફોટો ચોંટાડવો ]   |    |
|    |  (૧) સભ્યનું પૂરું નામ: ત્રિવેદી હર્ષદરાય મોહનલાલ                                         |    |
|    |  (૨) પત્ર વ્યવહારનું સરનામું: ૧૨, શાંતિનિકેતન સોસાયટી, ઇડર                                |    |
|    |  (૩) મૂળ ગામનું સરનામું: ખેડબ્રહ્મા, જિ. સાબરકાંઠા                      મોબાઈલ: 94260XXXXX  |    |
|    |  --------------------------------------------------------------------------------------  |    |
|    |  કુટુંબના સભ્યોની વિગત (૧ થી ૧૦):                                                        |    |
|    |  ૧. ત્રિવેદી મીનાબેન હર્ષદરાય          પત્ની      ૪૮     બી.એ.       B+     ગૃહિણી        |    |
|    |  ૨. ત્રિવેદી પાર્થ હર્ષદરાય            પુત્ર      ૨૪     બી.ઈ.       B+     એન્જિનિયર    |    |
|    |  --------------------------------------------------------------------------------------  |    |
|    |  અરજદારની સહી: [હર્ષદરાય ત્રિવેદી]                    હોદ્દેદારની સહી: __________________   |    |
|    +------------------------------------------------------------------------------------------+    |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

- **Interactive Canvas**: High-DPI rasterized preview rendered by `FormRenderer`.
- **Zoom Toolbar**: Fit Width, 100% Scale, Zoom In, Zoom Out.
- **Print Dispatch**: Single-click opens native Windows Print Dialog with orientation and paper selection pre-configured for A4.
- **PDF Export**: Prompts for file destination and outputs crisp 300 DPI vector PDF.

---

### 4.5 Smart Import Wizard (`ui/import_data_dialog.py`)
Allows safe bulk population from existing spreadsheets:
- **File Chooser**: Drag-and-drop or browse for `.xlsx` or `.csv`.
- **Conflict Strategy Selector**:
  - `Update Existing (Match Mobile or Code)`
  - `Update Existing (Match Mobile Only)`
  - `Update Existing (Match Code Only)`
  - `Insert Only (Skip duplicates)`
- **Safety Indicator**: Informs operator: *"An automatic backup will be created before importing."*
- **Live Progress & Summary**: Displays total rows processed, newly inserted records, updated records, and skipped conflicts.

---

### 4.6 Backup, Restore & Maintenance (`ui/backup_restore.py`)
- **One-Click Backup**: Creates a timestamped `.db` file in `backups/`.
- **Backup History Table**: Lists available archives with timestamp, size in MB, and one-click Restore or Delete.
- **Restore Guardrail**: Red warning modal with required confirmation checkbox to prevent accidental data overwrites.
- **Database Maintenance**: One-click `Optimize & Compact Database` (VACUUM) with storage space reclaimed report.

---

## 5. Senior-Friendly Accessibility Checklist

| Requirement | Implementation Detail in Project |
|---|---|
| **High Visual Contrast** | Text passes WCAG AA contrast against card and body backgrounds (`#0F172A` on `#FFFFFF` = 15.8:1 ratio). |
| **Touch/Click Target Size**| All interactive buttons have a minimum height of 38px–44px. |
| **Clear Labeling** | Every icon is paired with a clear textual label in Gujarati or English. |
| **No Silent Operations** | Every save, edit, delete, export, or backup generates a clear notification banner or dialog. |
| **Undo / Safety Net** | Destructive actions require explicit dialog confirmation; imports automatically create safety backups first. |
| **Keyboard Accessibility**| Full Tab navigation between fields; `Enter` triggers primary form submission; `Esc` dismisses dialogs. |

---

## 6. UI Performance Standards on 2 GB RAM PCs

1. **Lightweight Native Widgets**: Built entirely on Qt6 native widgets without webview or Electron overhead.
2. **Minimal Memory Footprint**: Idle memory consumption remains stable between 75 MB – 95 MB.
3. **On-Demand Rendering**: Official form preview images and PDF pages are generated in memory only when viewed or printed, immediately freeing buffers post-print.
4. **Instant Startup**: Launches in under 1.5 seconds on solid-state drives and under 3.5 seconds on traditional mechanical hard drives.
