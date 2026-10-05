"""Member service — business logic for member CRUD."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from database.connection import get_session
from database.models import Member, AppSetting
from database.repositories.member_repository import MemberRepository
from utils.validators import (
    validate_full_name, validate_mobile, validate_phone_landline,
    validate_pincode, validate_blood_group, validate_birth_date,
)


class MemberService:
    """Handles member CRUD and member-code generation."""

    @staticmethod
    def _now() -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def _detach(session: Session, obj):
        """Expunge object so it can be used after session closes."""
        session.expunge(obj)
        return obj

    # ------------------------------------------------------------------
    # Code generation
    # ------------------------------------------------------------------
    @staticmethod
    def generate_member_code() -> str:
        """Generate next sequential GBS-XXXXXX code safely without collisions."""
        with get_session() as session:
            setting = session.query(AppSetting).filter_by(setting_key='member_code_last').first()
            if setting is None:
                setting = AppSetting(
                    setting_key='member_code_last',
                    setting_value='0',
                    updated_at=MemberService._now(),
                )
                session.add(setting)
                session.flush()
            next_num = int(setting.setting_value or '0') + 1

            while True:
                candidate = f'GBS-{next_num:06d}'
                exists = session.query(Member).filter_by(member_code=candidate).first()
                if not exists:
                    break
                next_num += 1

            setting.setting_value = str(next_num)
            setting.updated_at = MemberService._now()
            session.commit()
            return f'GBS-{next_num:06d}'

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    @staticmethod
    def validate(data: dict) -> list[str]:
        errors = []
        for fn in (
            lambda: validate_full_name(data.get('full_name', '')),
            lambda: validate_mobile(data.get('mobile', '')),
            lambda: validate_phone_landline(data.get('phone_landline', '')),
            lambda: validate_pincode(data.get('pincode', '')),
            lambda: validate_blood_group(data.get('blood_group', '')),
            lambda: validate_birth_date(data.get('birth_date', '')),
        ):
            err = fn()
            if err:
                errors.append(err)
        return errors

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def create_member(self, data: dict) -> tuple[Optional[Member], list[str]]:
        errors = self.validate(data)
        if errors:
            return None, errors

        candidate_code = data.get('member_code', '').strip()
        if candidate_code:
            with get_session() as session:
                exists = session.query(Member).filter_by(member_code=candidate_code).first()
                if exists:
                    member_code = self.generate_member_code()
                else:
                    member_code = candidate_code
        else:
            member_code = self.generate_member_code()
        now = self._now()
        created_at = data.get('created_at') or now

        member = Member(
            member_code    = member_code,
            full_name      = data.get('full_name', '').strip(),
            surname        = data.get('surname', '').strip(),
            father_name    = data.get('father_name', '').strip(),
            mobile         = data.get('mobile', '').strip(),
            phone_landline = data.get('phone_landline', '').strip(),
            email          = data.get('email', '').strip(),
            address        = data.get('address', '').strip(),
            village_address = data.get('village_address', '').strip(),
            city           = data.get('city', '').strip(),
            district       = data.get('district', '').strip(),
            state          = data.get('state', 'Gujarat').strip(),
            pincode        = data.get('pincode', '').strip(),
            occupation       = data.get('occupation', '').strip(),
            business_address = data.get('business_address', '').strip(),
            income           = data.get('income', '').strip(),
            education        = data.get('education', '').strip(),
            blood_group      = data.get('blood_group', '').strip(),
            samaj            = data.get('samaj', '').strip(),
            membership_fee   = data.get('membership_fee', '').strip(),
            signature_text   = data.get('signature_text', '').strip(),
            signature_image  = data.get('signature_image', '').strip(),
            birth_date       = data.get('birth_date', '').strip(),
            created_at       = now,
            updated_at       = now,
        )

        with get_session() as session:
            session.add(member)
            session.commit()
            session.refresh(member)
            self._detach(session, member)
            return member, []

    def update_member(self, member_id: int, data: dict) -> tuple[Optional[Member], list[str]]:
        errors = self.validate(data)
        if errors:
            return None, errors

        with get_session() as session:
            repo = MemberRepository(session)
            member = repo.get_by_id(member_id)
            if not member:
                return None, ['Member not found.']

            member.full_name        = data.get('full_name', member.full_name).strip()
            member.surname          = data.get('surname', member.surname or '').strip()
            member.father_name      = data.get('father_name', member.father_name or '').strip()
            member.mobile           = data.get('mobile', member.mobile or '').strip()
            member.phone_landline   = data.get('phone_landline', member.phone_landline or '').strip()
            member.email            = data.get('email', member.email or '').strip()
            member.address          = data.get('address', member.address or '').strip()
            if 'village_address' in data:
                member.village_address = data.get('village_address', getattr(member, 'village_address', '') or '').strip()
            member.city             = data.get('city', member.city or '').strip()
            member.district         = data.get('district', member.district or '').strip()
            member.state            = data.get('state', member.state or 'Gujarat').strip()
            member.pincode          = data.get('pincode', member.pincode or '').strip()
            member.occupation       = data.get('occupation', member.occupation or '').strip()
            if 'business_address' in data:
                member.business_address = data.get('business_address', member.business_address or '').strip()
            if 'income' in data:
                member.income = data.get('income', member.income or '').strip()
            member.education        = data.get('education', member.education or '').strip()
            member.blood_group      = data.get('blood_group', member.blood_group or '').strip()
            member.samaj            = data.get('samaj', member.samaj or '').strip()
            member.membership_fee   = data.get('membership_fee', member.membership_fee or '').strip()
            if 'signature_text' in data:
                member.signature_text = data.get('signature_text', '').strip()
            if 'signature_image' in data:
                member.signature_image = data.get('signature_image', '').strip()
            member.birth_date     = data.get('birth_date', member.birth_date or '').strip()
            member.updated_at     = self._now()

            session.commit()
            session.refresh(member)
            self._detach(session, member)
            return member, []

    def delete_member(self, member_id: int) -> bool:
        with get_session() as session:
            repo = MemberRepository(session)
            member = repo.get_by_id(member_id)
            if not member:
                return False
            repo.delete(member)
            session.commit()
            return True

    def delete_all_members(self) -> int:
        """Delete all members and associated family members, and reset member code counter."""
        with get_session() as session:
            repo = MemberRepository(session)
            count = repo.delete_all()
            setting = session.query(AppSetting).filter_by(setting_key='member_code_last').first()
            if setting:
                setting.setting_value = '0'
                setting.updated_at = self._now()
            session.commit()
            return count


    def get_member(self, member_id: int) -> Optional[Member]:
        with get_session() as session:
            member = MemberRepository(session).get_by_id(member_id)
            if member:
                self._detach(session, member)
            return member

    def get_all(self, offset: int = 0, limit: int = 100) -> list[Member]:
        with get_session() as session:
            members = MemberRepository(session).get_all(offset, limit)
            for m in members:
                session.expunge(m)
            return members

    def count(self) -> int:
        with get_session() as session:
            return MemberRepository(session).count_all()

    def count_today(self) -> int:
        with get_session() as session:
            return MemberRepository(session).count_today()

    def get_recent(self, limit: int = 10) -> list[Member]:
        with get_session() as session:
            members = MemberRepository(session).get_recent(limit)
            for m in members:
                session.expunge(m)
            return members

    def get_distinct_cities(self) -> list[str]:
        with get_session() as session:
            return MemberRepository(session).get_distinct_cities()

    def check_duplicate_warning(self, full_name: str, mobile: str, exclude_id: int | None = None) -> Optional[Member]:
        with get_session() as session:
            found = MemberRepository(session).find_duplicate(full_name, mobile)
            if found and found.id != exclude_id:
                self._detach(session, found)
                return found
            return None
