"""Form service — maps DB records to the official form field dict."""

from __future__ import annotations

from datetime import date
from typing import Any

from database.models import Member, FamilyMember
from utils.date_utils import calculate_age, format_date_display


def build_form_data(
    member: Member,
    family_members: list[FamilyMember],
    custom_date: str | None = None,
) -> dict[str, Any]:
    """
    Return a dictionary containing every field visible on the official
    'સભ્ય નોંધણી ફોર્મ' of 'શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ સા.કાં.'
    """
    age = calculate_age(member.birth_date)
    age_str = str(age) if age is not None else ''

    # Build address with pincode — deduplicate if city/district already in address
    if member.address:
        addr = str(member.address).strip()
        supplements = []
        if member.city and member.city.strip().lower() not in addr.lower():
            supplements.append(member.city.strip())
        if member.district and member.district.strip().lower() not in addr.lower():
            if not member.city or member.district.strip().lower() != member.city.strip().lower():
                supplements.append(member.district.strip())
        if supplements:
            addr += ', ' + ', '.join(supplements)
        if member.pincode and member.pincode.strip() not in addr:
            addr += f' - {member.pincode.strip()}'
        address_full = addr
    else:
        address_parts = [p for p in [member.city, member.district, member.state] if p]
        address_full = ', '.join(address_parts)
        if member.pincode:
            address_full = f'{address_full} - {member.pincode}' if address_full else member.pincode

    # Determine form date
    if custom_date:
        form_date_str = custom_date
    elif getattr(member, 'created_at', None):
        try:
            c_part = str(member.created_at).split()[0]
            if '-' in c_part:
                from datetime import datetime
                dt = datetime.strptime(c_part, '%Y-%m-%d')
                form_date_str = dt.strftime('%d/%m/%Y')
            else:
                form_date_str = c_part
        except Exception:
            form_date_str = date.today().strftime('%d/%m/%Y')
    else:
        form_date_str = date.today().strftime('%d/%m/%Y')

    family_rows = [
        {
            'serial':         idx + 1,
            'name':           fm.name or '',
            'relation':       fm.relation or '',
            'age':            str(fm.age) if fm.age is not None else '',
            'education':      fm.education or '',
            'blood_group':    fm.blood_group or '',
            'occupation':     fm.occupation or '',
            'contact_number': fm.contact_number or '',
        }
        for idx, fm in enumerate(family_members)
    ]

    return {
        # Header
        'form_number':    member.member_code or '',
        'form_date':      form_date_str,

        # Personal & Professional fields (matching the official form)
        'full_name':        member.full_name or '',              # Section 1 (૧)
        'address':          address_full,                        # Section 1 (૨)
        'village_address':  getattr(member, 'village_address', '') or '',  # Section 1 (૩)
        'email':            member.email or '',                  # Section 1 (૪)
        'mobile':           member.mobile or '',                 # Section 1 (૫) મોબાઈલ નં.
        'phone_landline':   member.phone_landline or '',         # Section 1 (૫) ફોન નં.
        'occupation':       member.occupation or '',             # Section 2 (૬)
        'business_address': getattr(member, 'business_address', '') or '',  # Section 2 (૭)
        'income':           getattr(member, 'income', '') or '',
        'blood_group':      member.blood_group or '',            # Section 2 (૮) બ્લડ ગ્રુપ
        'education':        member.education or '',              # અભ્યાસ
        'samaj':            member.samaj or '',                  # Section 3 સમાજ
        'membership_fee':   member.membership_fee or '',         # Section 3 સભ્ય ફી
        'signature_text': getattr(member, 'signature_text', '') or member.full_name or '',
        'signature_image': getattr(member, 'signature_image', '') or '',
        'signature':      getattr(member, 'signature_text', '') or member.full_name or '',
        'birth_date':     format_date_display(member.birth_date),
        'age':            age_str,

        # Family members table
        'family_members': family_rows,
    }
