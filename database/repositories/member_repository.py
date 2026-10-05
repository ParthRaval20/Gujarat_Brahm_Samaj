"""Member repository — raw database queries for members table."""

from __future__ import annotations

from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database.models import Member, FamilyMember
from utils.gujarati_search import expand_search_terms


class MemberRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------
    def get_by_id(self, member_id: int) -> Optional[Member]:
        return self._s.query(Member).filter(Member.id == member_id).first()

    def get_by_code(self, member_code: str) -> Optional[Member]:
        return self._s.query(Member).filter(Member.member_code == member_code).first()

    def get_by_code_flexible(self, code_str: str) -> Optional[Member]:
        if not code_str:
            return None
        clean = str(code_str).strip()
        m = self._s.query(Member).filter(Member.member_code.ilike(clean)).first()
        if m:
            return m
        digits = "".join(ch for ch in clean if ch.isdigit())
        if digits:
            num = int(digits)
            candidate = f"GBS-{num:06d}"
            m = self._s.query(Member).filter(Member.member_code.ilike(candidate)).first()
            if m:
                return m
            m = self._s.query(Member).filter(Member.member_code == digits).first()
            if m:
                return m
        return None

    def get_by_mobile(self, mobile: str) -> Optional[Member]:
        if not mobile:
            return None
        clean_mob = "".join(ch for ch in str(mobile) if ch.isdigit())
        if len(clean_mob) >= 10:
            last10 = clean_mob[-10:]
            return self._s.query(Member).filter(
                or_(
                    Member.mobile == last10,
                    Member.mobile == f"+91{last10}",
                    Member.mobile == f"0{last10}",
                    Member.mobile.like(f"%{last10}")
                )
            ).first()
        return self._s.query(Member).filter(Member.mobile == str(mobile).strip()).first()

    def find_for_replace(
        self,
        member_code: Optional[str] = None,
        mobile: Optional[str] = None,
        strategy: str = "both",
    ) -> Optional[Member]:
        """
        Locate existing member for upsert/replace based on strategy:
        - 'both': Check form number / code first, then mobile number.
        - 'code': Check form number / code only.
        - 'mobile': Check mobile number only.
        """
        if strategy in ("code", "both") and member_code:
            found = self.get_by_code_flexible(member_code)
            if found:
                return found

        if strategy in ("mobile", "both") and mobile:
            found = self.get_by_mobile(mobile)
            if found:
                return found

        return None

    def get_all(self, offset: int = 0, limit: int = 100) -> list[Member]:
        return (
            self._s.query(Member)
            .order_by(Member.full_name)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_all(self) -> int:
        return self._s.query(Member).count()

    def search(self, query: str, limit: int = 200) -> list[Member]:
        raw_query = query.strip()
        if not raw_query:
            return []

        search_terms = expand_search_terms(raw_query)
        if not search_terms:
            search_terms = [raw_query]

        member_conds = []
        family_conds = []

        for term in search_terms:
            pat = f'%{term}%'
            member_conds.extend([
                Member.full_name.ilike(pat),
                Member.surname.ilike(pat),
                Member.father_name.ilike(pat),
                Member.mobile.ilike(pat),
                Member.phone_landline.ilike(pat),
                Member.address.ilike(pat),
                Member.city.ilike(pat),
                Member.district.ilike(pat),
                Member.occupation.ilike(pat),
                Member.education.ilike(pat),
                Member.samaj.ilike(pat),
                Member.member_code.ilike(pat),
            ])
            family_conds.extend([
                FamilyMember.name.ilike(pat),
                FamilyMember.contact_number.ilike(pat),
                FamilyMember.occupation.ilike(pat),
                FamilyMember.education.ilike(pat),
            ])

        # Subquery to match members who have matching family members
        family_match_subq = (
            self._s.query(FamilyMember.member_id)
            .filter(or_(*family_conds))
            .scalar_subquery()
        )

        all_conditions = or_(*member_conds, Member.id.in_(family_match_subq))

        return (
            self._s.query(Member)
            .filter(all_conditions)
            .order_by(Member.full_name)
            .limit(limit)
            .all()
        )

    def find_duplicate(self, full_name: str, mobile: str) -> Optional[Member]:
        """Return an existing member with same name+mobile (for duplicate warning)."""
        q = self._s.query(Member).filter(Member.full_name.ilike(full_name))
        if mobile:
            q = q.filter(Member.mobile == mobile)
        return q.first()

    def get_today(self) -> list[Member]:
        from datetime import date
        today_prefix = f'{date.today().isoformat()}%'
        return (
            self._s.query(Member)
            .filter(Member.created_at.like(today_prefix))
            .all()
        )

    def count_today(self) -> int:
        from datetime import date
        today_prefix = f'{date.today().isoformat()}%'
        return (
            self._s.query(Member)
            .filter(Member.created_at.like(today_prefix))
            .count()
        )

    def get_recent(self, limit: int = 10) -> list[Member]:
        return (
            self._s.query(Member)
            .order_by(Member.id.desc())
            .limit(limit)
            .all()
        )

    def get_distinct_cities(self) -> list[str]:
        results = (
            self._s.query(Member.city)
            .filter(Member.city.isnot(None), Member.city != '')
            .distinct()
            .order_by(Member.city)
            .all()
        )
        return [r[0] for r in results if r[0]]

    # ------------------------------------------------------------------
    # WRITE
    # ------------------------------------------------------------------
    def create(self, member: Member) -> Member:
        self._s.add(member)
        self._s.flush()   # populate id without full commit
        return member

    def update(self, member: Member) -> Member:
        self._s.flush()
        return member

    def delete(self, member: Member) -> None:
        self._s.delete(member)
        self._s.flush()

    def delete_all(self) -> int:
        """Delete all family members and members from the database."""
        self._s.query(FamilyMember).delete()
        count = self._s.query(Member).delete()
        self._s.flush()
        return count

