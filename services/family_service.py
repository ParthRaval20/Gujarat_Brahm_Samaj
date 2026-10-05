"""Family member service."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from database.connection import get_session
from database.models import FamilyMember
from database.repositories.family_repository import FamilyRepository
from utils.validators import validate_family_member_age, validate_blood_group


class FamilyService:
    @staticmethod
    def _now() -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def get_family_members(self, member_id: int) -> list[FamilyMember]:
        with get_session() as session:
            fms = FamilyRepository(session).get_by_member_id(member_id)
            for fm in fms:
                session.expunge(fm)
            return fms

    def count_all(self) -> int:
        with get_session() as session:
            return FamilyRepository(session).count_all()

    def add_family_member(self, member_id: int, data: dict) -> tuple[Optional[FamilyMember], list[str]]:
        errors = self._validate(data)
        if errors:
            return None, errors

        now = self._now()
        age_val = data.get('age')
        fm = FamilyMember(
            member_id      = member_id,
            name           = data.get('name', '').strip(),
            relation       = data.get('relation', '').strip(),
            age            = int(age_val) if age_val not in ('', None) else None,
            education      = data.get('education', '').strip(),
            blood_group    = data.get('blood_group', '').strip(),
            occupation     = data.get('occupation', '').strip(),
            contact_number = data.get('contact_number', '').strip(),
            created_at     = now,
            updated_at     = now,
        )

        with get_session() as session:
            session.add(fm)
            session.commit()
            session.refresh(fm)
            session.expunge(fm)
            return fm, []

    def update_family_member(self, fm_id: int, data: dict) -> tuple[Optional[FamilyMember], list[str]]:
        errors = self._validate(data)
        if errors:
            return None, errors

        with get_session() as session:
            repo = FamilyRepository(session)
            fm = repo.get_by_id(fm_id)
            if not fm:
                return None, ['Family member not found.']

            age_val = data.get('age')
            fm.name           = data.get('name', fm.name).strip()
            fm.relation       = data.get('relation', fm.relation or '').strip()
            fm.age            = int(age_val) if age_val not in ('', None) else None
            fm.education      = data.get('education', fm.education or '').strip()
            fm.blood_group    = data.get('blood_group', fm.blood_group or '').strip()
            fm.occupation     = data.get('occupation', fm.occupation or '').strip()
            fm.contact_number = data.get('contact_number', fm.contact_number or '').strip()
            fm.updated_at     = self._now()

            session.commit()
            session.refresh(fm)
            session.expunge(fm)
            return fm, []

    def delete_family_member(self, fm_id: int) -> bool:
        with get_session() as session:
            repo = FamilyRepository(session)
            fm = repo.get_by_id(fm_id)
            if not fm:
                return False
            repo.delete(fm)
            session.commit()
            return True

    @staticmethod
    def _validate(data: dict) -> list[str]:
        errors = []
        name = data.get('name', '').strip()
        if not name:
            errors.append('Family member name is required.')
        err = validate_family_member_age(data.get('age'))
        if err:
            errors.append(err)
        err = validate_blood_group(data.get('blood_group', ''))
        if err:
            errors.append(err)
        return errors

    def save_all_for_member(self, member_id: int, rows: list[dict]) -> list[str]:
        """Replace all family members with the given rows (used when saving member form)."""
        with get_session() as session:
            repo = FamilyRepository(session)
            repo.delete_all_for_member(member_id)
            now = self._now()
            for row in rows:
                name = row.get('name', '').strip()
                if not name:
                    continue
                age_val = row.get('age')
                fm = FamilyMember(
                    member_id      = member_id,
                    name           = name,
                    relation       = row.get('relation', '').strip(),
                    age            = int(age_val) if age_val not in ('', None) else None,
                    education      = row.get('education', '').strip(),
                    blood_group    = row.get('blood_group', '').strip(),
                    occupation     = row.get('occupation', '').strip(),
                    contact_number = row.get('contact_number', '').strip(),
                    created_at     = now,
                    updated_at     = now,
                )
                session.add(fm)
            session.commit()
        return []
