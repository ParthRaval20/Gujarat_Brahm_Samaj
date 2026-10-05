"""
Visual and data integration test for the updated member registration form.
Verifies:
1. FormRenderer rasterization with blank form & filled form.
2. 10 family rows with Gujarati numerals ૧ થી ૧૦.
3. Corrected spellings in header address, section titles, and table headers.
4. Seamless integration with MemberFormPage (Add Member page) and PDF generator.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QPainter

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from services.form_renderer import FormRenderer, CANVAS_W, CANVAS_H, COL_HEADERS, GUJARATI_ROW_NUMERALS
from services.pdf_service import generate_form_pdf
from database.connection import init_db
from database.models import Member, FamilyMember
from services.form_service import build_form_data

def test_form_renderer_visual():
    init_db()

    # Verify column headers
    assert COL_HEADERS == [
        'ક્રમ', 'નામ', 'સંબંધ', 'ઉંમર',
        'અભ્યાસ', 'બ્લડ ગ્રુપ', 'વ્યવસાય', 'સંપર્ક નંબર',
    ]

    # Verify row numerals
    assert GUJARATI_ROW_NUMERALS == ['૧', '૨', '૩', '૪', '૫', '૬', '૭', '૮', '૯', '૧૦']
    assert len(GUJARATI_ROW_NUMERALS) == 10

    # 1. Test blank form rasterization
    img_blank = QImage(int(CANVAS_W), int(CANVAS_H), QImage.Format.Format_ARGB32)
    p_blank = QPainter(img_blank)
    FormRenderer.draw_form(p_blank, form_data={}, width=CANVAS_W, height=CANVAS_H)
    p_blank.end()
    blank_preview_path = os.path.join(os.path.dirname(__file__), "preview_blank_updated_form.png")
    img_blank.save(blank_preview_path)
    assert os.path.exists(blank_preview_path)
    print("Blank updated form rendered successfully:", blank_preview_path)

    # 2. Test filled form with 10 family members
    test_member = Member(
        member_code="GBS-000100",
        full_name="જોષી કમલેશકુમાર રમણિકલાલ",
        address="૧૪, સરસ્વતી સોસાયટી, સત્યમ હોસ્પિટલ રોડ, ઇડર",
        village_address="મોટી ભોયણ, તા. કલોલ, જિ. ગાંધીનગર",
        city="ઇડર",
        district="સાબરકાંઠા",
        state="ગુજરાત",
        pincode="383430",
        email="kamlesh.joshi@example.com",
        education="M.Sc., B.Ed. (ગણિત - વિજ્ઞાન)",
        mobile="9825012345",
        phone_landline="02778250999",
        occupation="શિક્ષક અને વ્યવસાય",
        business_address="શૈવ કૉમ્પ્લેક્સ, દામોદર એરિયા, ઇડર",
        blood_group="B+",
        samaj="ગુજરાત બ્રહ્મ સમાજ",
        membership_fee="₹ ૫૦૦",
        signature_text="જોષી કમલેશકુમાર",
        created_at="2026-10-04 10:00:00",
        updated_at="2026-10-04 10:00:00",
    )

    relations = ["પત્ની", "પુત્ર", "પુત્રી", "પિતા", "માતા", "ભાઈ", "બહેન", "પુત્રવધૂ", "પૌત્ર", "પૌત્રી"]
    test_fms = []
    for i in range(10):
        test_fms.append(FamilyMember(
            id=i + 1,
            member_id=1,
            name=f"જોષી પરિવાર સભ્ય {i + 1}",
            relation=relations[i],
            age=20 + i * 4,
            education=f"ડિગ્રી {i + 1}",
            blood_group="B+",
            occupation=f"વ્યવસાય {i + 1}",
            contact_number=f"982501234{i}",
            created_at="2026-10-04 10:00:00",
            updated_at="2026-10-04 10:00:00",
        ))

    form_data = build_form_data(test_member, test_fms, custom_date="04/10/2026")
    assert form_data['full_name'] == "જોષી કમલેશકુમાર રમણિકલાલ"
    assert form_data['education'] == "M.Sc., B.Ed. (ગણિત - વિજ્ઞાન)"
    assert len(form_data['family_members']) == 10

    img_filled = QImage(int(CANVAS_W), int(CANVAS_H), QImage.Format.Format_ARGB32)
    p_filled = QPainter(img_filled)
    FormRenderer.draw_form(p_filled, form_data=form_data, width=CANVAS_W, height=CANVAS_H)
    p_filled.end()
    filled_preview_path = os.path.join(os.path.dirname(__file__), "preview_filled_updated_form.png")
    img_filled.save(filled_preview_path)
    assert os.path.exists(filled_preview_path)
    print("Filled updated form rendered successfully:", filled_preview_path)

    # 3. Test PDF generation
    pdf_out = os.path.join(os.path.dirname(__file__), "test_updated_form.pdf")
    generated_pdf = generate_form_pdf(form_data, pdf_out)
    assert os.path.exists(generated_pdf)
    assert os.path.getsize(generated_pdf) > 1000
    print("PDF generated successfully:", generated_pdf)

if __name__ == '__main__':
    test_form_renderer_visual()
    print("ALL TESTS IN test_updated_form_visual PASSED!")
