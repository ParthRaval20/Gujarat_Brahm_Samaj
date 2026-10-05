"""
Test dynamic language switching on Member Profile, Form Preview, and Member List.
Ensures buttons update cleanly without ghost/overlapping widgets or broken layouts.
"""
import sys
import os

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QPushButton, QLabel
from database.connection import init_db
from ui.main_window import MainWindow
from services.member_service import MemberService

def test_member_profile_and_buttons_toggle():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    init_db()
    win = MainWindow()

    # Get a member
    members = MemberService().get_recent(1)
    assert len(members) > 0, "Need at least 1 member to test"
    mid = members[0].id

    # 1. Navigate to profile in Gujarati
    win._set_language('gu')
    win._nav_to('profile', member_id=mid)

    profile_page = win._member_profile_page
    buttons_gu = profile_page.findChildren(QPushButton)
    btn_texts_gu = [b.text() for b in buttons_gu]
    print("Gujarati buttons:", btn_texts_gu)

    assert any("પાછા જાઓ" in t for t in btn_texts_gu), f"Back button missing Gujarati: {btn_texts_gu}"
    assert any("વિગત સુધારો" in t for t in btn_texts_gu), f"Edit button missing Gujarati: {btn_texts_gu}"
    assert any("પીડીએફ" in t or "PDF" in t for t in btn_texts_gu), f"PDF button missing: {btn_texts_gu}"
    assert any("કાઢી નાખો" in t for t in btn_texts_gu), f"Delete button missing Gujarati: {btn_texts_gu}"

    gu_btn_count = len(buttons_gu)

    # 2. Switch to English
    win._set_language('en')
    buttons_en = profile_page.findChildren(QPushButton)
    btn_texts_en = [b.text() for b in buttons_en]
    print("English buttons:", btn_texts_en)

    # CRITICAL: Verify old Gujarati buttons are completely gone (not piled up)
    assert len(buttons_en) == gu_btn_count, f"Ghost buttons accumulated! Was {gu_btn_count}, now {len(buttons_en)}"
    assert any("Back" in t for t in btn_texts_en), f"Back button missing English: {btn_texts_en}"
    assert any("Edit Details" in t for t in btn_texts_en), f"Edit button missing English: {btn_texts_en}"
    assert any("Generate Form / PDF" in t for t in btn_texts_en), f"PDF button missing English: {btn_texts_en}"
    assert any("Delete Member" in t for t in btn_texts_en), f"Delete button missing English: {btn_texts_en}"
    assert not any("પાછા જાઓ" in t for t in btn_texts_en), "Old Gujarati button still present in English mode!"

    # 3. Switch back to Gujarati
    win._set_language('gu')
    buttons_gu2 = profile_page.findChildren(QPushButton)
    btn_texts_gu2 = [b.text() for b in buttons_gu2]
    print("Gujarati buttons after switch back:", btn_texts_gu2)
    assert len(buttons_gu2) == gu_btn_count, f"Ghost buttons accumulated on 2nd switch: {len(buttons_gu2)}"
    assert not any("Edit Details" in t for t in btn_texts_gu2), "Old English button still present in Gujarati mode!"

    # 4. Check Form Preview page buttons
    win._nav_to('form_preview', member_id=mid)
    win._set_language('en')
    preview_page = win._form_preview_page
    prev_btns_en = [b.text() for b in preview_page.findChildren(QPushButton)]
    print("Form preview English buttons:", prev_btns_en)
    assert any("Back to Profile" in t for t in prev_btns_en)
    assert any("Print Form" in t for t in prev_btns_en)
    assert any("Save PDF" in t for t in prev_btns_en)

    win._set_language('gu')
    prev_btns_gu = [b.text() for b in preview_page.findChildren(QPushButton)]
    print("Form preview Gujarati buttons:", prev_btns_gu)
    assert any("પ્રોફાઇલ પર પાછા જાઓ" in t for t in prev_btns_gu)
    assert any("ફોર્મ પ્રિન્ટ કરો" in t for t in prev_btns_gu)

    # 5. Check Sidebar Nav labels fit in English
    win._set_language('en')
    assert win._nav_text_labels['list'].text() == 'All Members'
    win._set_language('gu')
    assert win._nav_text_labels['list'].text() == 'બધા સભ્યો'

    print("ALL BUTTON & LANGUAGE SWITCH TESTS PASSED PERFECTLY!")

if __name__ == '__main__':
    test_member_profile_and_buttons_toggle()
