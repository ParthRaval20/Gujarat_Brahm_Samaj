# Database Schema Document

# Gujarat Brahm Samaj Desktop Management System

**Document Version:** 1.2
**Database Type:** SQLite
**Database File:** `brahm_samaj.db`
**Application Type:** Offline Desktop Application
**Related Documents:** PRD.md, TRD.md, UIUX.md, appflow.md

---

# Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | Initial draft | Base schema created |
| 1.1 | Revision | Hardware requirements added |
| 1.2 | 2026-09-08 | Official form fields mapped from physical form image. Added `phone_landline`, `samaj`, `membership_fee` to members. Added `blood_group` to family_members. Removed stored `age` from members (now computed from `birth_date`). Confirmed surname-first name entry order. |
| 1.3 | 2026-10-05 | **Synchronized schema with live production models and migrations. Added `village_address` (ગામનું સરનામું), `business_address` (ધંધા/વ્યવસાયનું સરનામું), `income` (આવક), `signature_text` (સહી માટે નામ), and `signature_image` (સહીની છબી પાથ). Documented automatic PRAGMA table migration in `init_db()`.** |

---

# 1. Purpose

This document defines the database schema for the Gujarat Brahm Samaj Desktop Management System.

The schema is finalized based on the official **શ્રી સમરત ગુજરાત બ્રહ્મ સમાજ સા.કાં.** physical registration form (સભ્ય નોંધણી ફોર્મ).

Every field visible on the official form has been mapped to a database column. No form field is left unmapped.

The database stores:

- Member information (all fields from the official form).
- Family information (all columns from the પરિવારની માહિતી table).
- Application settings.

The application works completely offline using a local SQLite database.

---

# 2. Official Form Field Mapping

This section records the mapping between every field on the official Gujarati form and its corresponding database column.

## 2.1 Form Header Fields

| Form Field (Gujarati) | Meaning | Source |
|---|---|---|
| ફોર્મ નં. | Form / Member number | Generated from `member_code` |
| તારીખ | Date | Generated at print time (current date) |

---

## 2.2 Personal Information Fields

| # | Form Field (Gujarati) | Meaning | DB Column |
|---|---|---|---|
| ૧ | પૂરુ નામ (અટક પહેલા લખવી) | Full name — surname written first | `surname` + `full_name` |
| ૨ | પત્ર વ્યવહારનું સરનામું (પીન કોડ નં. સહિત) | Postal residential address including PIN code | `address` + `pincode` |
| — | ગામનું સરનામું | Native village address | `village_address` |
| ૩ | ઈ-મેઈલ | Email address | `email` |
| — | મોબાઈલ નં. | Mobile number | `mobile` |
| — | ફોન નં. | Landline / phone number | `phone_landline` |
| ૪ | ધંધો / વ્યવસાય | Business / Occupation | `occupation` |
| ૫ | ધંધા / વ્યવસાયનું સરનામું | Business address | `business_address` |
| ૬ | આવક | Monthly or annual income | `income` |
| ૭ | અભ્યાસ | Education | `education` |
| ૮ | બ્લડ ગ્રુપ | Blood group | `blood_group` |
| ૯ | સમાજ | Community or society name | `samaj` |
| ૧૦ | સભ્ય ફી | Membership fee amount paid | `membership_fee` |
| ૧૧ | ફોર્મ ભરનારની સહી | Signature of form filler (typed text / uploaded image) | `signature_text` + `signature_image` |

**Important note on field ૧:**
The official form explicitly states **"અટક પહેલા લખવી"** — the surname must be written first.
The UI input reflects this order: **Surname → First/Given Name → Father/Husband Name**.
The `full_name` column stores the complete formatted name. The `surname` column stores the surname separately for search indexing.

---

## 2.3 Family Information Table (પરિવારની માહિતી)

| Column Header (Gujarati) | Meaning | DB Column |
|---|---|---|
| ક્રમ | Serial number | Auto-generated at display/print time |
| નામ | Name of family member | `name` |
| સબંધ | Relation to primary member | `relation` |
| ઉમર | Age | `age` |
| અભ્યાસ | Education | `education` |
| બ્લડ ગ્રુ | Blood group | `blood_group` |
| વ્યવસાય | Occupation | `occupation` |
| કોન્ટેક નંબર | Contact number | `contact_number` |

---

# 3. Database Design Principles

1. Every member must have a unique identifier.
2. One member can have multiple family members.
3. Gujarati Unicode text must be stored correctly.
4. Frequently searched fields must be indexed.
5. Data must avoid unnecessary duplication.
6. Records must support creation and update timestamps.
7. Relationships must use foreign keys.
8. The schema must be expandable in future versions.
9. The database must remain easy to back up and restore.
10. User-entered data must not be lost accidentally.
11. Age must never be stored as a static column on the `members` table — it must be computed from `birth_date` at display time to avoid stale data.

---

# 4. Database Overview

Version 1 contains the following tables:

```text
+----------------------+
|       members        |
+----------+-----------+
           |
           | 1
           |
           | N
           v
+----------------------+
|    family_members    |
+----------------------+

+----------------------+
|     app_settings     |
+----------------------+
```

---

# 5. Entity Relationship Diagram

```text
┌──────────────────────────────────┐
│             MEMBERS              │
├──────────────────────────────────┤
│ id (PK)                          │
│ member_code (UNIQUE)             │
│ full_name                        │
│ surname                          │
│ father_name                      │
│ mobile                           │
│ phone_landline                   │  ← ફોન નં. from official form
│ email                            │
│ address                          │  ← પત્રવ્યવહાર સરનામું
│ village_address                  │  ← ગામનું સરનામું
│ city                             │
│ district                         │
│ state                            │
│ pincode                          │
│ occupation                       │  ← ધંધો / વ્યવસાય
│ business_address                 │  ← ધંધાનું સરનામું
│ income                           │  ← આવક
│ education                        │  ← અભ્યાસ
│ blood_group                      │  ← બ્લડ ગ્રુપ
│ samaj                            │  ← સમાજ
│ membership_fee                   │  ← સભ્ય ફી
│ signature_text                   │  ← સહી માટે નામ
│ signature_image                  │  ← સહીની છબી પાથ
│ birth_date                       │  ← YYYY-MM-DD (age computed)
│ created_at                       │
│ updated_at                       │
└──────────────────┬───────────────┘
                   │
                   │ One Member
                   │
                   │ Many Family Members
                   │
                   ▼
┌──────────────────────────────────┐
│          FAMILY_MEMBERS          │
├──────────────────────────────────┤
│ id (PK)                          │
│ member_id (FK)                   │
│ name                             │
│ relation                         │
│ age                              │
│ education                        │
│ blood_group                      │  ← Added from official form table
│ occupation                       │
│ contact_number                   │
│ created_at                       │
│ updated_at                       │
└──────────────────────────────────┘
```

---

# 6. Table: members

The `members` table stores the primary information for each Gujarat Brahm Samaj member.

## 6.1 Members Table Fields

| Column | Type | Required | Description |
|---|---|---|---|
| id | INTEGER | Yes | Primary key, auto-incremented |
| member_code | TEXT | Yes | Unique member code (e.g. GBS-000001) |
| full_name | TEXT | Yes | Complete formatted name (surname first) |
| surname | TEXT | No | Surname / family name for search |
| father_name | TEXT | No | Father's or guardian's name |
| mobile | TEXT | No | Primary mobile number (10 digits) — મોબાઈલ નં. |
| phone_landline | TEXT | No | Landline or phone number — ફોન નં. |
| email | TEXT | No | Email address — ઈ-મેઈલ |
| address | TEXT | Yes | Complete residential postal address — પત્રવ્યવહાર સરનામું |
| village_address | TEXT | No | Native village address — ગામ / મૂળ વતનનું સરનામું |
| city | TEXT | No | Taluka or city name |
| district | TEXT | No | District (defaults to Sabarkantha / સાબરકાંઠા) |
| state | TEXT | No | State (defaults to Gujarat / ગુજરાત) |
| pincode | TEXT | No | 6-digit postal PIN code |
| occupation | TEXT | No | Business or occupation — ધંધો / વ્યવસાય |
| business_address | TEXT | No | Business / office address — ધંધાનું સરનામું |
| income | TEXT | No | Income details — આવક (e.g. ₹ ૫,૦૦,૦૦૦ વાર્ષિક) |
| education | TEXT | No | Educational qualification — અભ્યાસ |
| blood_group | TEXT | No | Blood group — બ્લડ ગ્રુપ |
| samaj | TEXT | No | Community name — સમાજ (default: શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ) |
| membership_fee | TEXT | No | Membership fee paid — સભ્ય ફી (e.g. ₹ ૫૦૦, આજીવન) |
| signature_text | TEXT | No | Form filler typed signature name |
| signature_image | TEXT | No | Absolute or relative path to uploaded signature image |
| birth_date | TEXT | No | Date of birth in YYYY-MM-DD format (age dynamically computed) |
| created_at | TEXT | Yes | Record creation timestamp |
| updated_at | TEXT | Yes | Last update timestamp |

**Note:** `age` is NOT stored as a column. It is computed at display time using:
```python
age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
```

---

## 6.2 SQL Definition

```sql
CREATE TABLE members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    member_code TEXT NOT NULL UNIQUE,

    full_name TEXT NOT NULL,
    surname TEXT,
    father_name TEXT,

    mobile TEXT,
    phone_landline TEXT,
    email TEXT,

    address TEXT,
    village_address TEXT,
    city TEXT,
    district TEXT,
    state TEXT,
    pincode TEXT,

    occupation TEXT,
    business_address TEXT,
    income TEXT,
    education TEXT,
    blood_group TEXT,

    samaj TEXT,
    membership_fee TEXT,

    signature_text TEXT,
    signature_image TEXT,

    birth_date TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

---

# 7. Table: family_members

The `family_members` table stores family members connected to a primary member.

One primary member can have zero, one, or many family members.

These columns directly map to the **પરિવારની માહિતી** table on the official form.

## 7.1 Family Members Table Fields

| Column | Type | Required | Description |
|---|---|---|---|
| id | INTEGER | Yes | Primary key |
| member_id | INTEGER | Yes | Foreign key to members.id |
| name | TEXT | Yes | Family member name — નામ |
| relation | TEXT | No | Relationship to primary member — સબંધ |
| age | INTEGER | No | Age — ઉમર |
| education | TEXT | No | Education — અભ્યાસ |
| blood_group | TEXT | No | Blood group — બ્લડ ગ્રુ |
| occupation | TEXT | No | Occupation — વ્યવસાય |
| contact_number | TEXT | No | Contact number — કોન્ટેક નંબર |
| created_at | TEXT | Yes | Creation timestamp |
| updated_at | TEXT | Yes | Update timestamp |

**Note:** `age` is stored directly in the family_members table because family member records
do not always have a birth_date. The data entry operator enters age directly from the form.

---

## 7.2 SQL Definition

```sql
CREATE TABLE family_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    member_id INTEGER NOT NULL,

    name TEXT NOT NULL,
    relation TEXT,

    age INTEGER,

    education TEXT,
    blood_group TEXT,
    occupation TEXT,
    contact_number TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (member_id)
        REFERENCES members(id)
        ON DELETE CASCADE
);
```

---

# 8. Table: app_settings

The `app_settings` table stores application-level configuration.

This prevents configuration values from being hard-coded inside the application.

## 8.1 Fields

| Column | Type | Required | Description |
|---|---|---|---|
| id | INTEGER | Yes | Primary key |
| setting_key | TEXT | Yes | Unique setting name |
| setting_value | TEXT | No | Setting value |
| updated_at | TEXT | Yes | Last update time |

## 8.2 SQL Definition

```sql
CREATE TABLE app_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT,

    updated_at TEXT NOT NULL
);
```

---

# 9. Relationship Rules

## Member → Family Members

```text
One Member
    |
    | 1 : N
    |
Many Family Members
```

Example:

```text
Member:
Parth Raval (GBS-000001)

Family Members:
- Mahesh Raval | Father | Age 52 | Business | A+
- Meena Raval  | Mother | Age 48 | Homemaker | B+
- Rahul Raval  | Brother | Age 24 | Student | O+
```

All three family member records contain `member_id = 1`.

---

# 10. Primary Keys

Each table uses:

```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
```

The `id` is used internally. Users see the human-readable `member_code`.

Example:

```text
Database ID:  25
Member Code:  GBS-000025
```

---

# 11. Member Code Design

Every primary member must have a unique member code.

Recommended format:

```text
GBS-000001
GBS-000002
GBS-000003
```

Future format options:

```text
GBS-RJK-000001     (with city code)
GBS-2026-000001    (with year)
```

The member code is what gets printed in the **ફોર્મ નં.** field on the official form.

---

# 12. Search Indexes

Indexes must be created for all frequently searched fields.

```sql
CREATE INDEX idx_members_full_name
ON members(full_name);

CREATE INDEX idx_members_surname
ON members(surname);

CREATE INDEX idx_members_father_name
ON members(father_name);

CREATE INDEX idx_members_mobile
ON members(mobile);

CREATE INDEX idx_members_city
ON members(city);

CREATE INDEX idx_members_occupation
ON members(occupation);

CREATE INDEX idx_members_samaj
ON members(samaj);

CREATE INDEX idx_family_members_member_id
ON family_members(member_id);

CREATE INDEX idx_family_members_name
ON family_members(name);
```

---

# 13. Smart Search Fields

The smart search queries these fields in the `members` table:

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

Future versions may also search `family_members.name` and `family_members.contact_number`.

---

# 14. Search Query Example

Example parameterized search:

```sql
SELECT *
FROM members
WHERE
    LOWER(full_name)    LIKE LOWER(?)
    OR LOWER(surname)   LIKE LOWER(?)
    OR LOWER(father_name) LIKE LOWER(?)
    OR mobile           LIKE ?
    OR LOWER(city)      LIKE LOWER(?)
    OR LOWER(samaj)     LIKE LOWER(?)
ORDER BY full_name
LIMIT 50;
```

All queries must use parameterized placeholders (`?`) to prevent SQL injection.

---

# 15. Gujarati Unicode Support

SQLite stores text as Unicode natively.

The application must ensure:

- Python strings are handled as UTF-8.
- Gujarati names are never converted or corrupted.
- PDF generation uses an embedded Gujarati Unicode font.
- Search works for both Gujarati and English text input.

Example values that must be stored correctly:

```text
પાર્થ રાવલ
મહેશ રાવલ
રાજકોટ
```

---

# 16. Date and Age Strategy

## Primary Member — birth_date

- Store as `TEXT` in `YYYY-MM-DD` format.
- Display in UI as `DD/MM/YYYY` (Gujarati-style format).
- **Compute age at display time** — do not store age as a column.

```python
from datetime import date

def calculate_age(birth_date_str):
    birth = date.fromisoformat(birth_date_str)
    today = date.today()
    age = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    return age
```

## Family Members — age

- Store `age` directly as entered by the operator.
- Family members on the official form use a simple age number, not birth date.
- This is acceptable for the family table only.

---

# 17. Timestamp Storage Strategy

Recommended format:

```text
YYYY-MM-DD HH:MM:SS
```

Example:

```text
2026-09-08 13:46:00
```

Both `created_at` and `updated_at` are populated by the application layer, not a database trigger.

---

# 18. Data Validation Rules

## members Table

| Field | Rule |
|---|---|
| full_name | Required. Minimum 2 characters. |
| member_code | Required. Unique. Auto-generated. |
| mobile | Optional. If provided, numeric only. |
| phone_landline | Optional. If provided, numeric only. |
| pincode | Optional. If provided, 6 digits. |
| blood_group | Optional. If provided, from allowed list: A+, A-, B+, B-, O+, O-, AB+, AB-. |
| membership_fee | Optional. Stored as TEXT to allow values like "500", "Free", etc. |
| birth_date | Optional. If provided, must be a valid date in YYYY-MM-DD format. |

## family_members Table

| Field | Rule |
|---|---|
| name | Required. |
| age | Optional. If provided, must be a non-negative integer. |
| blood_group | Optional. If provided, from the allowed blood group list. |

---

# 19. Duplicate Detection

The database enforces uniqueness only on `member_code`.

The application should warn (not block) when a possibly duplicate member is detected:

```text
A similar member may already exist:

Name: Parth Raval
Mobile: 9876543210

[ View Existing Member ]

[ Add Anyway ]
```

Suggested duplicate detection fields:

```text
full_name + mobile
full_name + father_name
```

---

# 20. Referential Integrity

Foreign keys must be enabled at the start of every database session:

```sql
PRAGMA foreign_keys = ON;
```

This ensures:

- Family members cannot reference a non-existent member.
- When a primary member is deleted, all their family records are deleted automatically (`ON DELETE CASCADE`).

---

# 21. Transaction Strategy

Multi-step writes must use transactions.

Example — saving a new member with family:

```text
BEGIN TRANSACTION
    Insert into members
    Insert into family_members (row 1)
    Insert into family_members (row 2)
COMMIT

If any step fails → ROLLBACK
```

This prevents partial or incomplete records from being saved.

---

# 22. Backup Strategy

The entire SQLite database is a single file:

```text
brahm_samaj.db
```

Backup filename format:

```text
brahm_samaj_backup_YYYY_MM_DD_HH_MM.db
```

Example:

```text
brahm_samaj_backup_2026_09_08_1346.db
```

The application must verify the backup file exists and has a non-zero size before reporting success.

---

# 23. Restore Strategy

```text
Select Backup File
      |
      v
Validate: Is it a valid SQLite file?
      |
      v
Create Automatic Safety Backup of Current DB
      |
      v
Replace Current Database
      |
      v
Reload Application
```

The current database must never be silently overwritten.

---

# 24. Database Migration Strategy

If future versions add new fields:

```text
Version 1.x → ALTER TABLE to add new columns
Version 2.x → Alembic migrations if schema changes are significant
```

A `schema_version` setting in `app_settings` is recommended:

```sql
INSERT INTO app_settings (setting_key, setting_value, updated_at)
VALUES ('schema_version', '1.2', '2026-09-08 00:00:00');
```

---

# 25. Future Tables (Not in Version 1)

## users

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

## activity_logs

```sql
CREATE TABLE activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL
);
```

## member_documents

```sql
CREATE TABLE member_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    document_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
);
```

---

# 26. Complete SQL Initialization Script

```sql
PRAGMA foreign_keys = ON;

-- Members table
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    member_code TEXT NOT NULL UNIQUE,

    full_name TEXT NOT NULL,
    surname TEXT,
    father_name TEXT,

    mobile TEXT,
    phone_landline TEXT,

    address TEXT,
    city TEXT,
    district TEXT,
    state TEXT,
    pincode TEXT,

    email TEXT,

    occupation TEXT,
    education TEXT,
    blood_group TEXT,

    samaj TEXT,
    membership_fee TEXT,

    birth_date TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Family members table
CREATE TABLE IF NOT EXISTS family_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    member_id INTEGER NOT NULL,

    name TEXT NOT NULL,
    relation TEXT,

    age INTEGER,

    education TEXT,
    blood_group TEXT,
    occupation TEXT,
    contact_number TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (member_id)
        REFERENCES members(id)
        ON DELETE CASCADE
);

-- App settings table
CREATE TABLE IF NOT EXISTS app_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT,
    updated_at TEXT NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_members_full_name     ON members(full_name);
CREATE INDEX IF NOT EXISTS idx_members_surname        ON members(surname);
CREATE INDEX IF NOT EXISTS idx_members_father_name    ON members(father_name);
CREATE INDEX IF NOT EXISTS idx_members_mobile         ON members(mobile);
CREATE INDEX IF NOT EXISTS idx_members_city           ON members(city);
CREATE INDEX IF NOT EXISTS idx_members_occupation     ON members(occupation);
CREATE INDEX IF NOT EXISTS idx_members_samaj          ON members(samaj);
CREATE INDEX IF NOT EXISTS idx_family_members_id      ON family_members(member_id);
CREATE INDEX IF NOT EXISTS idx_family_members_name    ON family_members(name);

-- Default settings
INSERT OR IGNORE INTO app_settings (setting_key, setting_value, updated_at)
VALUES
    ('schema_version', '1.2', datetime('now')),
    ('member_code_prefix', 'GBS', datetime('now')),
    ('member_code_last', '0', datetime('now'));
```

---

# 27. Example Data

## Member Record

```text
id:               1
member_code:      GBS-000001
full_name:        રાવલ પાર્થ મહેશભાઈ       (surname first, per form field ૧)
surname:          રાવલ
father_name:      મહેશભાઈ
mobile:           9876543210
phone_landline:   02822-123456
email:            parth@example.com
address:          A-101, ગાંધી નગર, રાજકોટ
village_address:  ઈડર, જિ. સાબરકાંઠા
city:             રાજકોટ
district:         સાબરકાંઠા
state:            ગુજરાત
pincode:          360001
occupation:       સોફ્ટવેર ડેવલપર
business_address: ઇન્ફોસિટી, બ્લોક-સી, ગાંધીનગર
income:           ₹ ૧,૨૦,૦૦૦ / માસિક
education:        B.Tech Computer
blood_group:      B+
samaj:            શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ
membership_fee:   ₹ ૫૦૦ (મળેલ છે)
signature_text:   રાવલ પાર્થ
birth_date:       2003-11-20
```

## Family Member Records

```text
id: 1 | member_id: 1 | name: મહેશ રાવલ   | relation: Father | age: 52 | education: B.Com | blood_group: A+ | occupation: Business   | contact_number: 9876500001
id: 2 | member_id: 1 | name: મીના રાવલ   | relation: Mother | age: 48 | education: HSC   | blood_group: B+ | occupation: Homemaker  | contact_number: 9876500002
```

---

# 28. Schema Naming Conventions

## Tables

Lowercase, plural, snake_case:

```text
members
family_members
app_settings
```

## Columns

Lowercase, snake_case:

```text
full_name
father_name
phone_landline
birth_date
blood_group
created_at
```

## Foreign Keys

```text
member_id
user_id
```

---

# 29. Low-End Hardware Performance Rules

The database is designed for machines with as little as 2 GB RAM.

- Never load all member records into Python memory.
- Use `LIMIT` and `OFFSET` for paginated member list queries.
- Use indexes for all search fields.
- Select only required columns (`SELECT id, full_name, mobile, city` not `SELECT *`) for list views.
- Use `SELECT *` only when opening a full member profile.
- Use transactions for grouped write operations.
- Generate PDFs only on demand — never pre-generate.
- Release form preview resources after printing or closing.

---

# 30. Database Acceptance Criteria

The schema is considered ready when:

1. The SQLite database is created automatically on first launch.
2. Member records can be created with all form fields.
3. Member codes are unique and auto-generated.
4. Gujarati Unicode text is stored and retrieved correctly.
5. Multiple family members can be linked to one member.
6. Foreign key relationships and `ON DELETE CASCADE` work correctly.
7. Search indexes are present and functional.
8. Smart search performs efficiently across all indexed fields.
9. The `samaj`, `phone_landline`, and `membership_fee` fields are present and writable.
10. The `blood_group` column exists in both `members` and `family_members`.
11. Age on the member record is computed from `birth_date`, not stored.
12. Backup copies the database file safely.
13. Restore validates the backup file before replacing the current database.
14. The database functions completely offline.
15. The initialization script runs without errors on a fresh machine.

---

# Conclusion

The Version 1.2 database schema is fully aligned with the official **સભ્ય નોંધણી ફોર્મ** of **શ્રી સમરત ગુજરાત બ્રહ્મ સમાજ સા.કાં.**

Every visible field on the official form has a corresponding database column.

The core data flow is:

```text
Enter Member Details (surname first)
        ↓
Enter Family Members (name, relation, age, education, blood group, occupation, contact)
        ↓
Search by Name / Mobile / Samaj / City
        ↓
Retrieve Complete Record
        ↓
Auto-fill Official Gujarati Form
        ↓
Preview → Print or Save PDF
```

The schema is intentionally simple and offline-first, while remaining expandable for future features.
