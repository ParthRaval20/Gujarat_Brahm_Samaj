import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from ui.member_form import MemberFormPage

def test_member_form_layout():
    app = QApplication.instance() or QApplication(sys.argv)
    form = MemberFormPage(nav_callback=lambda *args: None)
    form.resize(1200, 900)
    form.show()

    # Test Gujarati
    form.set_language('gu')
    assert form.lbl_address.text() == "રહેઠાણનું સરનામું *"
    assert form.district_edit.text() == "સાબરકાંઠા"
    assert form.lbl_city_dist.text() == "તાલુકો & જિલ્લો"
    assert form.lbl_occ.text() == "ધંધો / વ્યવસાય"
    assert form.lbl_biz_addr.text() == "ધંધાનું સરનામું"
    assert form.lbl_samaj.text() == "સમાજ"
    assert form.lbl_contact.text() == "મોબાઇલ & ફોન નં. *"
    assert form.taluka_combo.lineEdit().placeholderText() == "તાલુકો પસંદ કરો..."

    # Test English
    form.set_language('en')
    assert form.lbl_address.text() == "Residential Address *"
    assert form.district_edit.text() == "Sabarkantha"
    assert form.district_edit.toolTip() == "District: Sabarkantha (Fixed)"
    assert form.state_edit.text() == "Gujarat"
    assert form.lbl_city_dist.text() == "Taluka & District"
    assert form.lbl_occ.text() == "Profession / Business"
    assert form.lbl_biz_addr.text() == "Business Address"
    assert form.lbl_samaj.text() == "Samaj"
    assert form.lbl_contact.text() == "Mobile & Phone *"
    assert form.taluka_combo.lineEdit().placeholderText() == "Select Taluka..."
    assert form.edu_combo.lineEdit().placeholderText() == "Select or type Education..."

    # Check button texts
    assert form.btn_top_cancel.text() == "✖ Cancel"
    assert form.btn_top_preview.text() == "👁️  Preview"
    assert form.btn_top_print.text() == "🖨️  Print"
    assert form.btn_top_pdf.text() == "📄  Generate PDF"
    assert form.btn_top_save.text() == "💾  Save Member"

    # Check widths and layout stretches
    assert form.bg_combo.width() == 280
    assert form.lbl_city_dist.width() == 190
    assert form.lbl_state_pin.width() == 145

    # Switch back to Gujarati smoothly
    form.set_language('gu')
    assert form.lbl_address.text() == "રહેઠાણનું સરનામું *"
    assert form.district_edit.text() == "સાબરકાંઠા"
    assert form.state_edit.text() == "ગુજરાત"

    print("ALL MEMBER FORM LAYOUT & LANGUAGE SWITCH ASSERTIONS PASSED!")

if __name__ == "__main__":
    test_member_form_layout()
