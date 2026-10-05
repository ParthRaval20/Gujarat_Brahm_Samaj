"""Smoke test script — runs without Qt."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 1. DB init
from database.connection import init_db
init_db()
print('DB init: OK')

# 2. Member service
from services.member_service import MemberService
svc = MemberService()
member, errors = svc.create_member({
    'full_name': 'Raval Parth',
    'surname': 'Raval',
    'father_name': 'Mahesh',
    'mobile': '9876543210',
    'phone_landline': '02822-123456',
    'email': 'parth@example.com',
    'address': 'A-101 Gandhi Nagar',
    'city': 'Rajkot',
    'district': 'Rajkot',
    'state': 'Gujarat',
    'pincode': '360001',
    'education': 'B.Tech',
    'occupation': 'Software Developer',
    'blood_group': 'B+',
    'samaj': 'Raval',
    'membership_fee': '500',
    'birth_date': '2003-11-20',
})
assert not errors, f'Member create errors: {errors}'
print(f'Member created: {member.member_code} - {member.full_name}')

# 3. Family service
from services.family_service import FamilyService
fsvc = FamilyService()
fm, ferr = fsvc.add_family_member(member.id, {
    'name': 'Mahesh Raval',
    'relation': 'Father',
    'age': 52,
    'education': 'B.Com',
    'blood_group': 'A+',
    'occupation': 'Business',
    'contact_number': '9876500001',
})
assert not ferr, f'Family create errors: {ferr}'
print(f'Family member created: {fm.name}')

# 4. Form service
from services.form_service import build_form_data
fms = fsvc.get_family_members(member.id)
form_data = build_form_data(member, fms)
fam_count = len(form_data['family_members'])
print(f'Form data keys: {list(form_data.keys())}')
print(f'Family rows in form: {fam_count}')

# 5. PDF generation
from services.pdf_service import generate_form_pdf
os.makedirs('exports', exist_ok=True)
pdf_path = generate_form_pdf(form_data, 'exports/test_output.pdf')
size = os.path.getsize(pdf_path)
print(f'PDF generated: {pdf_path}  ({size} bytes)')
assert size > 5000, 'PDF too small — something went wrong'

# 6. Search
from services.search_service import SearchService
results = SearchService().search('Raval')
print(f'Search results: {len(results)} member(s)')
assert len(results) >= 1

# 7. Backup
from services.backup_service import create_backup
os.makedirs('backups', exist_ok=True)
bk_path = create_backup()
print(f'Backup: {bk_path}')

print()
print('=== All smoke tests PASSED ===')
