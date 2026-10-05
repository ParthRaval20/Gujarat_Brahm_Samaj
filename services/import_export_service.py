"""
Import and Export Service for Gujarat Brahm Samaj ERP.

Supports:
- Importing members from Excel (.xlsx) and CSV (.csv) files.
- Smart deduplication & replacement (upsert):
  * Match & Replace by Mobile Number
  * Match & Replace by Form Number / Member Code
  * Match & Replace by Form Number OR Mobile (Flexible/Both)
  * Insert Only (Skip existing duplicates)
- Safety: Automatic pre-import database backup.
- Flexible header detection supporting both Gujarati and English column headers.
- Exporting members to Excel and CSV.
- Generating sample import templates.
"""

from __future__ import annotations

import csv
import io
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Any

from database.connection import get_session
from database.models import Member, AppSetting
from database.repositories.member_repository import MemberRepository
from services.backup_service import create_backup


# Ordered column aliases for precise header matching (specific keys first)
COLUMN_ALIASES: list[tuple[str, list[str]]] = [
    ('birth_date', ['birth_date', 'birthdate', 'dob', 'date_of_birth', 'જન્મ તારીખ', 'જન્મતારીખ']),
    ('membership_fee', ['membership_fee', 'fee', 'fees', 'સભ્ય ફી', 'ફી']),
    ('blood_group', ['blood_group', 'blood', 'bg', 'બ્લડ ગ્રુપ', 'રક્ત જૂથ', 'બ્લડગ્રુપ', 'બ્લડ ગ્રૂપ']),
    ('income', ['income', 'annual_income', 'salary', 'આવક', 'વાર્ષિક આવક']),
    ('education', ['education', 'qualification', 'degree', 'અભ્યાસ', 'લાયકાત', 'શિક્ષણ']),
    ('business_address', ['business_address', 'office_address', 'work_address', 'ધંધાનું સરનામું', 'ધંધા / વ્યવસાયનું સરનામું', 'ઓફિસ સરનામું']),
    ('occupation', ['occupation', 'business', 'job', 'profession', 'વ્યવસાય', 'ધંધો', 'નોકરી']),
    ('pincode', ['pincode', 'pin', 'zip', 'zipcode', 'પિનકોડ', 'પીનકોડ', 'પિન કોડ']),
    ('phone_landline', ['phone_landline', 'landline', 'telephone', 'ફોન નં', 'ટેલિફોન', 'લેન્ડલાઈન', 'ફોન નંબર']),
    ('mobile', ['mobile', 'mobile_no', 'phone', 'cell', 'contact', 'મોબાઈલ નંબર', 'મોબાઈલ નં', 'મોબાઈલ', 'મોબાઇલ નં', 'મોબાઇલ']),
    ('email', ['email', 'e-mail', 'mail', 'ઈમેઈલ', 'ઈ-મેઈલ', 'ઈમેલ', 'ઇમેઇલ']),
    ('address', ['address', 'residence', 'સરનામું', 'રહેઠાણનું સરનામું', 'સરનામુ']),
    ('village_address', ['village_address', 'native_village', 'native_place', 'village_addr', 'ગામનું સરનામું', 'મૂળ વતનનું સરનામું', 'ગામ સરનામું', 'મૂળ વતન']),
    ('city', ['city', 'town', 'village', 'native', 'taluka', 'taluk', 'શહેર', 'ગામ', 'તાલુકો']),
    ('district', ['district', 'dist', 'જિલ્લો', 'જીલ્લો']),
    ('state', ['state', 'રાજ્ય']),
    ('samaj', ['samaj', 'community', 'સમાજ', 'ગોળ']),
    ('surname', ['surname', 'last_name', 'lastname', 'અટક', 'શાખ']),
    ('father_name', ['father_name', 'father', 'husband_name', 'husband', 'પિતાનું નામ', 'પતિનું નામ', 'પિતા']),
    ('member_code', ['member_code', 'form_no', 'form_number', 'code', 'સભ્ય કોડ', 'સભ્યકોડ', 'ફોર્મ નંબર', 'ફોર્મ નં', 'સભ્ય નંબર', 'ફોર્મ']),
    ('full_name', ['full_name', 'fullname', 'member_name', 'applicant_name', 'સભ્યનું નામ', 'પૂર્ણ નામ', 'સભ્ય નામ', 'નામ']),
]


SAMPLE_HEADERS = [
    ("સભ્ય કોડ (Form No)", "member_code"),
    ("પૂર્ણ નામ (Full Name) *", "full_name"),
    ("અટક (Surname)", "surname"),
    ("પિતા/પતિનું નામ (Father Name)", "father_name"),
    ("મોબાઈલ નંબર (Mobile No)", "mobile"),
    ("ફોન નં. (Landline)", "phone_landline"),
    ("ઈ-મેઈલ (Email)", "email"),
    ("રહેઠાણનું સરનામું (Address)", "address"),
    ("ગામનું સરનામું (Village Address)", "village_address"),
    ("શહેર (City)", "city"),
    ("જિલ્લો (District)", "district"),
    ("રાજ્ય (State)", "state"),
    ("પિનકોડ (Pincode)", "pincode"),
    ("ધંધો / વ્યવસાય (Occupation)", "occupation"),
    ("ધંધાનું સરનામું (Business Address)", "business_address"),
    ("આવક (Income)", "income"),
    ("અભ્યાસ (Education)", "education"),
    ("બ્લડ ગ્રુપ (Blood Group)", "blood_group"),
    ("સમાજ (Samaj)", "samaj"),
    ("સભ્ય ફી (Fee)", "membership_fee"),
    ("જન્મ તારીખ (Birth Date)", "birth_date"),
]


@dataclass
class ImportRowError:
    row_num: int
    name: str
    mobile: str
    error: str


@dataclass
class ImportResult:
    total_rows: int = 0
    inserted_count: int = 0
    updated_count: int = 0
    skipped_count: int = 0
    backup_path: Optional[str] = None
    errors: list[ImportRowError] = field(default_factory=list)
    success: bool = True
    message: str = ""


class ImportExportService:
    """Service to handle importing and exporting member data with duplicate replacement logic."""

    @staticmethod
    def _now() -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def normalize_cell(cls, val: Any) -> str:
        """Safely convert cell value to trimmed string."""
        if val is None:
            return ""
        if isinstance(val, (datetime, date)):
            return val.strftime('%Y-%m-%d')
        # If float ending in .0 (e.g. integer read from Excel)
        if isinstance(val, float) and val.is_integer():
            return str(int(val)).strip()
        s = str(val).strip()
        if s.endswith('.0') and s[:-2].isdigit():
            return s[:-2]
        return s

    @classmethod
    def canonical_member_code(cls, code_str: str) -> str:
        """Format form number / member code canonically (e.g. 777 -> GBS-000777)."""
        if not code_str:
            return ""
        clean = code_str.strip().upper()
        if clean.startswith("GBS-") and len(clean) == 10 and clean[4:].isdigit():
            return clean
        digits = "".join(ch for ch in clean if ch.isdigit())
        if digits:
            return f"GBS-{int(digits):06d}"
        return clean

    @classmethod
    def clean_mobile(cls, val: Any) -> str:
        """Extract clean 10-digit mobile number if possible."""
        raw = cls.normalize_cell(val)
        digits = "".join(ch for ch in raw if ch.isdigit())
        if len(digits) >= 10:
            return digits[-10:]
        return digits

    @classmethod
    def normalize_date(cls, val: Any) -> str:
        """Attempt to convert diverse date formats to YYYY-MM-DD."""
        if not val:
            return ""
        if isinstance(val, (datetime, date)):
            return val.strftime('%Y-%m-%d')
        s = str(val).strip()
        # Already YYYY-MM-DD
        if re.match(r'^\d{4}-\d{2}-\d{2}$', s):
            return s
        # DD/MM/YYYY or DD-MM-YYYY
        m = re.match(r'^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})$', s)
        if m:
            d, mth, y = m.groups()
            return f"{int(y):04d}-{int(mth):02d}-{int(d):02d}"
        # YYYY/MM/DD
        m2 = re.match(r'^(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})$', s)
        if m2:
            y, mth, d = m2.groups()
            return f"{int(y):04d}-{int(mth):02d}-{int(d):02d}"
        return s

    @classmethod
    def map_header(cls, header: str) -> Optional[str]:
        """Map raw column header to standard field name using exact and token matching."""
        if not header:
            return None
        raw_clean = header.strip().lower()
        tokens = [t.lower().strip() for t in re.split(r'[\s_/\-().*+,]+', header) if t.strip()]

        # Pass 1: exact match with an alias
        for key, aliases in COLUMN_ALIASES:
            for a in aliases:
                if raw_clean == a.lower():
                    return key

        # Pass 2: check if any token exactly matches an alias
        for key, aliases in COLUMN_ALIASES:
            for a in aliases:
                if a.lower() in tokens:
                    return key

        # Pass 3: substring phrase match for multi-word aliases
        for key, aliases in COLUMN_ALIASES:
            for a in aliases:
                if ' ' in a and a.lower() in raw_clean:
                    return key

        return None

    @classmethod
    def read_file(cls, file_path: str) -> tuple[list[dict[str, str]], list[str], list[str]]:
        """
        Read Excel or CSV file and return (rows_as_dicts, standard_keys_found, raw_headers).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext in ('.xlsx', '.xls'):
            return cls._read_excel(file_path)
        elif ext == '.csv':
            return cls._read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Please choose an Excel (.xlsx) or CSV (.csv) file.")

    @classmethod
    def _read_excel(cls, file_path: str) -> tuple[list[dict[str, str]], list[str], list[str]]:
        try:
            import openpyxl
        except ImportError:
            raise RuntimeError("openpyxl library is required to read Excel files. Please install openpyxl.")

        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            return [], [], []

        raw_headers = [cls.normalize_cell(h) for h in rows[0]]
        mapped_keys = [cls.map_header(h) if h else None for h in raw_headers]

        data_rows: list[dict[str, str]] = []
        for row in rows[1:]:
            if not any(row):
                continue
            row_dict: dict[str, str] = {}
            for col_idx, cell_val in enumerate(row):
                if col_idx < len(mapped_keys):
                    k = mapped_keys[col_idx]
                    if k:
                        row_dict[k] = cls.normalize_cell(cell_val)
            # Only include if at least name or mobile or code is present
            if any(row_dict.values()):
                data_rows.append(row_dict)

        found_keys = [k for k in mapped_keys if k is not None]
        return data_rows, found_keys, raw_headers

    @classmethod
    def _read_csv(cls, file_path: str) -> tuple[list[dict[str, str]], list[str], list[str]]:
        # Try multiple encodings for Gujarati / Unicode text safety
        encodings = ['utf-8-sig', 'utf-8', 'cp1252', 'iso-8859-1']
        content = None
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, OSError):
                continue

        if content is None:
            raise RuntimeError("Could not decode CSV file. Please make sure it is UTF-8 encoded.")

        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        if not rows:
            return [], [], []

        raw_headers = [cls.normalize_cell(h) for h in rows[0]]
        mapped_keys = [cls.map_header(h) if h else None for h in raw_headers]

        data_rows: list[dict[str, str]] = []
        for row in rows[1:]:
            if not any(row):
                continue
            row_dict: dict[str, str] = {}
            for col_idx, cell_val in enumerate(row):
                if col_idx < len(mapped_keys):
                    k = mapped_keys[col_idx]
                    if k:
                        row_dict[k] = cls.normalize_cell(cell_val)
            if any(row_dict.values()):
                data_rows.append(row_dict)

        found_keys = [k for k in mapped_keys if k is not None]
        return data_rows, found_keys, raw_headers

    @classmethod
    def generate_sample_template(cls, output_path: str, format_type: str = 'xlsx') -> str:
        """
        Generate a sample file template with standard Gujarati / English headers
        and 2 sample rows so users can easily prepare their data.
        """
        sample_rows = [
            {
                'member_code': 'GBS-000001',
                'full_name': 'જોષી હર્ષદભાઈ રમણિકલાલ',
                'surname': 'જોષી',
                'father_name': 'રમણિકલાલ',
                'mobile': '9898012345',
                'phone_landline': '02778250123',
                'email': 'harshad.joshi@example.com',
                'address': '૧૪, શાંતિનિકેતન સોસાયટી, સત્યમ હોસ્પિટલ પાછળ',
                'village_address': 'મોટી ભોયણ, તા. કલોલ',
                'city': 'ઈડર',
                'district': 'સાબરકાંઠા',
                'state': 'ગુજરાત',
                'pincode': '383430',
                'occupation': 'વેપાર અને સીએ કન્સલ્ટન્ટ',
                'education': 'M.Com, FCA',
                'blood_group': 'B+',
                'samaj': 'ગુજરાત બ્રહ્મ સમાજ',
                'membership_fee': '₹ ૫૦૦',
                'birth_date': '1985-06-15',
            },
            {
                'member_code': 'GBS-000002',
                'full_name': 'રાવલ પાર્થકુમાર દિનેશભાઈ',
                'surname': 'રાવલ',
                'father_name': 'દિનેશભાઈ',
                'mobile': '9876543210',
                'phone_landline': '',
                'email': 'parth.raval@example.com',
                'address': '૨૫, શિવ શક્તિ બંગલોઝ, શ્યામલ ક્રોસ રોડ',
                'village_address': 'ગોજારીયા, તા. મહેસાણા',
                'city': 'અમદાવાદ',
                'district': 'અમદાવાદ',
                'state': 'ગુજરાત',
                'pincode': '380015',
                'occupation': 'સોફ્ટવેર એન્જિનિયર',
                'education': 'B.Tech IT',
                'blood_group': 'O+',
                'samaj': 'ગુજરાત બ્રહ્મ સમાજ',
                'membership_fee': '₹ ૫૦૦',
                'birth_date': '1995-11-20',
            }
        ]

        headers_display = [h[0] for h in SAMPLE_HEADERS]
        header_keys = [h[1] for h in SAMPLE_HEADERS]

        if format_type.lower() == 'csv':
            if not output_path.lower().endswith('.csv'):
                output_path += '.csv'
            with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers_display)
                for row in sample_rows:
                    writer.writerow([row.get(k, '') for k in header_keys])
            return output_path
        else:
            # Excel XLSX
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

            if not output_path.lower().endswith('.xlsx'):
                output_path += '.xlsx'

            wb = openpyxl.Workbook()
            ws = wb.active
            if ws is None:
                ws = wb.create_sheet(title="Members Import")
            else:
                ws.title = "Members Import"

            # Header styling
            header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
            header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            thin_border = Border(
                left=Side(style='thin', color='CBD5E1'),
                right=Side(style='thin', color='CBD5E1'),
                top=Side(style='thin', color='CBD5E1'),
                bottom=Side(style='thin', color='CBD5E1'),
            )

            ws.append(headers_display)
            for row in ws.iter_rows(min_row=1, max_row=1, max_col=len(headers_display)):
                for cell in row:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

            ws.row_dimensions[1].height = 28

            # Sample rows
            for row in sample_rows:
                ws.append([row.get(k, '') for k in header_keys])

            for row in ws.iter_rows(min_row=2, max_row=1 + len(sample_rows), max_col=len(header_keys)):
                for cell in row:
                    cell.border = thin_border
                    cell.alignment = Alignment(vertical="center")

            # Adjust column widths
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                ws.column_dimensions[col_letter].width = max(max_len + 5, 14)

            wb.save(output_path)
            return output_path

    @classmethod
    def export_members_to_file(cls, output_path: str, format_type: str = 'xlsx') -> tuple[int, str]:
        """
        Export all database members to Excel or CSV file.
        """
        with get_session() as session:
            members = session.query(Member).order_by(Member.id).all()
            total = len(members)

            headers_display = [h[0] for h in SAMPLE_HEADERS]
            header_keys = [h[1] for h in SAMPLE_HEADERS]

            if format_type.lower() == 'csv':
                if not output_path.lower().endswith('.csv'):
                    output_path += '.csv'
                with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers_display)
                    for m in members:
                        row_vals = [getattr(m, k, '') or '' for k in header_keys]
                        writer.writerow(row_vals)
                return total, output_path
            else:
                import openpyxl
                from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

                if not output_path.lower().endswith('.xlsx'):
                    output_path += '.xlsx'

                wb = openpyxl.Workbook()
                ws = wb.active
                if ws is None:
                    ws = wb.create_sheet(title="Brahm Samaj Members")
                else:
                    ws.title = "Brahm Samaj Members"

                header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
                header_font = Font(name="Calibri", size=11, bold=True, color="F8FAFC")
                thin_border = Border(
                    left=Side(style='thin', color='E2E8F0'),
                    right=Side(style='thin', color='E2E8F0'),
                    top=Side(style='thin', color='E2E8F0'),
                    bottom=Side(style='thin', color='E2E8F0'),
                )

                ws.append(headers_display)
                for row in ws.iter_rows(min_row=1, max_row=1, max_col=len(headers_display)):
                    for cell in row:
                        cell.fill = header_fill
                        cell.font = header_font
                        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

                ws.row_dimensions[1].height = 28

                for m in members:
                    row_vals = [getattr(m, k, '') or '' for k in header_keys]
                    ws.append(row_vals)

                for row in ws.iter_rows(min_row=2, max_row=1 + total, max_col=len(header_keys)):
                    for cell in row:
                        cell.border = thin_border
                        cell.alignment = Alignment(vertical="center")

                for col in ws.columns:
                    max_len = max(len(str(cell.value or '')) for cell in col)
                    col_letter = col[0].column_letter
                    ws.column_dimensions[col_letter].width = max(max_len + 4, 13)

                wb.save(output_path)
                return total, output_path

    @classmethod
    def import_members(
        cls,
        file_path: str,
        match_strategy: str = "both",
        keep_existing_on_blank: bool = True,
        create_safety_backup: bool = True,
    ) -> ImportResult:
        """
        Import members from file with smart deduplication and replacement.

        :param file_path: Path to .xlsx or .csv file.
        :param match_strategy:
            - 'both': Check Form Number/Code first, then Mobile Number. If either matches, replace.
            - 'mobile': Check Mobile Number only. If matches, replace.
            - 'code': Check Form Number/Code only. If matches, replace.
            - 'insert_only': If duplicate found by code or mobile, skip it.
        :param keep_existing_on_blank: If True, do not overwrite existing DB fields when imported cell is blank.
        :param create_safety_backup: Automatically take a full database backup before running import.
        """
        result = ImportResult()

        # Step 1: Read rows from file
        try:
            rows, found_keys, _ = cls.read_file(file_path)
        except Exception as e:
            result.success = False
            result.message = f"Error reading file: {str(e)}"
            return result

        result.total_rows = len(rows)
        if result.total_rows == 0:
            result.success = True
            result.message = "No member records found in the selected file."
            return result

        # Step 2: Safety backup
        if create_safety_backup:
            try:
                b_path = create_backup()
                result.backup_path = b_path
            except Exception as e:
                # Do not stop, but note
                result.backup_path = None

        # Step 3: Process rows inside DB session
        now_str = cls._now()

        with get_session() as session:
            repo = MemberRepository(session)

            for idx, r in enumerate(rows, start=2):  # Row 1 is header
                raw_name = r.get('full_name', '').strip()
                raw_mobile = cls.clean_mobile(r.get('mobile', ''))
                raw_code = r.get('member_code', '').strip()

                # Basic validation: Name is mandatory
                if not raw_name:
                    result.errors.append(ImportRowError(
                        row_num=idx,
                        name=raw_name or "(Blank)",
                        mobile=raw_mobile,
                        error="નામ આપેલ નથી (Full Name is required)"
                    ))
                    result.skipped_count += 1
                    continue

                # Find existing member for matching/replacement
                existing: Optional[Member] = None
                if match_strategy in ("both", "code", "mobile"):
                    existing = repo.find_for_replace(
                        member_code=raw_code,
                        mobile=raw_mobile,
                        strategy=match_strategy,
                    )
                elif match_strategy == "insert_only":
                    # Check if already exists by code or mobile
                    existing = repo.find_for_replace(
                        member_code=raw_code,
                        mobile=raw_mobile,
                        strategy="both",
                    )
                    if existing:
                        result.skipped_count += 1
                        continue

                # Prepare sanitized fields
                norm_dob = cls.normalize_date(r.get('birth_date', ''))
                pincode = "".join(ch for ch in r.get('pincode', '') if ch.isdigit())[:6]

                fields_to_apply = {
                    'full_name': raw_name,
                    'surname': r.get('surname', '').strip(),
                    'father_name': r.get('father_name', '').strip(),
                    'mobile': raw_mobile,
                    'phone_landline': r.get('phone_landline', '').strip(),
                    'email': r.get('email', '').strip(),
                    'address': r.get('address', '').strip(),
                    'village_address': r.get('village_address', '').strip(),
                    'city': r.get('city', '').strip(),
                    'district': r.get('district', '').strip(),
                    'state': r.get('state', 'ગુજરાત').strip() or 'ગુજરાત',
                    'pincode': pincode,
                    'occupation': r.get('occupation', '').strip(),
                    'business_address': r.get('business_address', '').strip(),
                    'income': r.get('income', '').strip(),
                    'education': r.get('education', '').strip(),
                    'blood_group': r.get('blood_group', '').strip(),
                    'samaj': r.get('samaj', 'ગુજરાત બ્રહ્મ સમાજ').strip() or 'ગુજરાત બ્રહ્મ સમાજ',
                    'membership_fee': r.get('membership_fee', '').strip(),
                    'birth_date': norm_dob,
                }

                if existing:
                    # REPLACE / UPDATE EXISTING RECORD
                    try:
                        for k, v in fields_to_apply.items():
                            if keep_existing_on_blank:
                                if v:
                                    setattr(existing, k, v)
                            else:
                                setattr(existing, k, v)

                        # If user provided a new code and it's not taken by another, optionally update
                        canon_raw = cls.canonical_member_code(raw_code)
                        if canon_raw and canon_raw != existing.member_code:
                            code_check = repo.get_by_code(canon_raw)
                            if not code_check or code_check.id == existing.id:
                                existing.member_code = canon_raw

                        existing.updated_at = now_str
                        result.updated_count += 1
                    except Exception as exc:
                        result.errors.append(ImportRowError(
                            row_num=idx,
                            name=raw_name,
                            mobile=raw_mobile,
                            error=f"Update failed: {str(exc)}"
                        ))
                        result.skipped_count += 1

                else:
                    # INSERT NEW RECORD
                    try:
                        # Determine unique member code
                        final_code = ""
                        if raw_code:
                            cand_code = cls.canonical_member_code(raw_code)
                            code_check = repo.get_by_code(cand_code)
                            if not code_check:
                                final_code = cand_code

                        if not final_code:
                            # Generate sequential code
                            setting = session.query(AppSetting).filter_by(setting_key='member_code_last').first()
                            if setting is None:
                                setting = AppSetting(
                                    setting_key='member_code_last',
                                    setting_value='0',
                                    updated_at=now_str,
                                )
                                session.add(setting)
                                session.flush()
                            next_num = int(setting.setting_value or '0') + 1
                            while True:
                                candidate = f'GBS-{next_num:06d}'
                                if not session.query(Member).filter_by(member_code=candidate).first():
                                    break
                                next_num += 1
                            setting.setting_value = str(next_num)
                            setting.updated_at = now_str
                            final_code = f'GBS-{next_num:06d}'

                        new_member = Member(
                            member_code    = final_code,
                            full_name      = fields_to_apply['full_name'],
                            surname        = fields_to_apply['surname'],
                            father_name    = fields_to_apply['father_name'],
                            mobile         = fields_to_apply['mobile'],
                            phone_landline = fields_to_apply['phone_landline'],
                            email          = fields_to_apply['email'],
                            address        = fields_to_apply['address'],
                            village_address = fields_to_apply['village_address'],
                            city           = fields_to_apply['city'],
                            district       = fields_to_apply['district'],
                            state          = fields_to_apply['state'],
                            pincode        = fields_to_apply['pincode'],
                            occupation     = fields_to_apply['occupation'],
                            business_address = fields_to_apply['business_address'],
                            income         = fields_to_apply['income'],
                            education      = fields_to_apply['education'],
                            blood_group    = fields_to_apply['blood_group'],
                            samaj          = fields_to_apply['samaj'],
                            membership_fee = fields_to_apply['membership_fee'],
                            birth_date     = fields_to_apply['birth_date'],
                            created_at     = now_str,
                            updated_at     = now_str,
                        )
                        session.add(new_member)
                        session.flush()
                        result.inserted_count += 1
                    except Exception as exc:
                        result.errors.append(ImportRowError(
                            row_num=idx,
                            name=raw_name,
                            mobile=raw_mobile,
                            error=f"Insert failed: {str(exc)}"
                        ))
                        result.skipped_count += 1

            session.commit()

        result.success = True
        result.message = (
            f"ડેટા આયાત સફળતાપૂર્વક પૂર્ણ થયેલ છે: "
            f"કુલ {result.total_rows} રેકોર્ડ્સમાંથી {result.inserted_count} નવા ઉમેરાયા, "
            f"{result.updated_count} જૂના રેકોર્ડ્સ બદલાયા (Replaced), "
            f"{result.skipped_count} છોડી દીધા."
        )
        return result
