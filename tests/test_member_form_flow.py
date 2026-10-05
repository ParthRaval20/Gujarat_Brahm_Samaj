"""
Test member form GUI flow, field mappings, and PDF export completeness.
"""
import sys
import os

from PySide6.QtWidgets import QApplication, QMessageBox

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set UTF-8 encoding on standard streams if needed
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# Mock message boxes for unattended testing
QMessageBox.warning = lambda *args, **kwargs: QMessageBox.StandardButton.Yes
QMessageBox.information = lambda *args, **kwargs: QMessageBox.StandardButton.Ok
QMessageBox.critical = lambda *args, **kwargs: QMessageBox.StandardButton.Ok

from database.connection import init_db
from ui.member_form import MemberFormPage
from services.member_service import MemberService
from services.family_service import FamilyService
from services.form_service import build_form_data
from services.pdf_service import generate_form_pdf

def test_member_form_flow():
    init_db()

    nav_target = []
    def mock_nav(target, **kwargs):
        nav_target.append((target, kwargs))

    form = MemberFormPage(nav_callback=mock_nav)
    print("MemberFormPage instantiated successfully.")

    # 1. Fill all fields exactly as a real user would
    import time
    uniq_mobile = f"98{int(time.time()) % 100000000:08d}"
    form.fullname_edit.setText("જોષી હર્ષદભાઈ રમણિકલાલ")
    form.address_edit.setPlainText("૧૪, શાંતિનિકેતન સોસાયટી, સત્યમ હોસ્પિટલ પાછળ")
    form.village_address_edit.setText("મોટી ભોયણ, તા. કલોલ")
    form.city_edit.setText("ઈડર")
    form.district_edit.setText("સાબરકાંઠા")
    form.state_edit.setText("ગુજરાત")
    form.pincode_edit.setText("383430")
    form.email_edit.setText("harshad.joshi@example.com")
    form.mobile_edit.setText(uniq_mobile)
    form.phone_edit.setText("02778250123")
    form.occ_edit.setText("વેપાર અને સીએ કન્સલ્ટન્ટ")
    form.biz_address_edit.setPlainText("શૈશવ કૉમ્પ્લેક્ષ, દામોદર એરીયા, ઈડર")
    form.income_edit.setText("")
    form.edu_edit.setText("M.Com, FCA")
    idx = form.bg_combo.findText("B+")
    form.bg_combo.setCurrentIndex(idx)
    form.samaj_edit.setText("ગુજરાત બ્રહ્મ સમાજ")
    form.fee_edit.setText("₹ ૫૦૦ (મળેલ છે)")

    # 2. Add family members to the 8-column family table
    form.family_table.add_empty_row({
        'name': 'જોષી ગીતાબેન હર્ષદભાઈ',
        'relation': 'પત્ની (Wife)',
        'age': 46,
        'education': 'B.A.',
        'blood_group': 'B+',
        'occupation': 'ગૃહિણી',
        'contact_number': '9898123457',
    })

    form.family_table.add_empty_row({
        'name': 'જોષી દર્શન હર્ષદભાઈ',
        'relation': 'પુત્ર (Son)',
        'age': 21,
        'education': 'B.Tech IT',
        'blood_group': 'O+',
        'occupation': 'અભ્યાસ',
        'contact_number': '9898123458',
    })

    print(f"Family table rows: {form.family_table.table.rowCount()}")
    assert form.family_table.table.rowCount() == 2

    # Verify serial numbers auto-updated in col 0
    print(f"Col 0 Row 0: {form.family_table.table.item(0, 0).text().strip()}")
    print(f"Col 0 Row 1: {form.family_table.table.item(1, 0).text().strip()}")
    assert form.family_table.table.item(0, 0).text().strip() == '1'
    assert form.family_table.table.item(1, 0).text().strip() == '2'

    # 3. Test saving the member
    member = form._save(show_success_msg=False)
    assert member is not None
    print(f"Saved member code: {member.member_code}")
    assert member.village_address == "મોટી ભોયણ, તા. કલોલ"
    assert member.business_address == "શૈશવ કૉમ્પ્લેક્ષ, દામોદર એરીયા, ઈડર"

    # 4. Verify family members saved to DB
    fms = FamilyService().get_family_members(member.id)
    assert len(fms) == 2
    print(f"Retrieved family members count from DB: {len(fms)}")

    # 5. Build form data & verify all keys are filled
    form_data = build_form_data(member, fms, custom_date=form.form_date_edit.date().toString('dd/MM/yyyy'))
    assert form_data['full_name'] == "જોષી હર્ષદભાઈ રમણિકલાલ"
    assert "ઈડર" in form_data['address']
    assert "383430" in form_data['address']
    assert form_data['village_address'] == "મોટી ભોયણ, તા. કલોલ"
    assert form_data['mobile'] == uniq_mobile
    assert form_data['email'] == "harshad.joshi@example.com"
    assert form_data['occupation'] == "વેપાર અને સીએ કન્સલ્ટન્ટ"
    assert form_data['business_address'] == "શૈશવ કૉમ્પ્લેક્ષ, દામોદર એરીયા, ઈડર"
    assert form_data['blood_group'] == "B+"
    assert form_data['samaj'] == "ગુજરાત બ્રહ્મ સમાજ"
    assert form_data['membership_fee'] == "₹ ૫૦૦ (મળેલ છે)"
    assert len(form_data['family_members']) == 2
    assert form_data['family_members'][0]['name'] == 'જોષી ગીતાબેન હર્ષદભાઈ'
    assert form_data['family_members'][1]['name'] == 'જોષી દર્શન હર્ષદભાઈ'
    print("All form_data fields verified successfully!")

    # 6. Test generating PDF with all filled data
    test_pdf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'exports', 'test_filled_form.pdf')
    generate_form_pdf(form_data, test_pdf)
    assert os.path.exists(test_pdf)
    print(f"Verified generated PDF at: {test_pdf} (size: {os.path.getsize(test_pdf)} bytes)")

    # 7. Test load_for_edit
    form.load_for_edit(member)
    assert form.fullname_edit.text() == "જોષી હર્ષદભાઈ રમણિકલાલ"
    assert form.village_address_edit.text() == "મોટી ભોયણ, તા. કલોલ"
    assert form.biz_address_edit.toPlainText() == "શૈશવ કૉમ્પ્લેક્ષ, દામોદર એરીયા, ઈડર"
    assert form.family_table.table.rowCount() == 2
    print("load_for_edit verified successfully.")

    # 8. Test reset
    form.reset()
    assert form.fullname_edit.text() == ""
    assert form.village_address_edit.text() == ""
    assert form.biz_address_edit.toPlainText() == ""
    assert form.income_edit.text() == ""
    assert form.family_table.table.rowCount() == 0
    print("reset verified successfully.")

    print("=== ALL GUI AND FLOW TESTS PASSED SUCCESSFULLY ===")

if __name__ == '__main__':
    test_member_form_flow()
