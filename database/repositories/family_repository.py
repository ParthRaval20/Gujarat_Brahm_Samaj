"""Family member repository."""

from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session

from database.models import FamilyMember


class FamilyRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def get_by_member_id(self, member_id: int) -> list[FamilyMember]:
        return (
            self._s.query(FamilyMember)
            .filter(FamilyMember.member_id == member_id)
            .order_by(FamilyMember.id)
            .all()
        )

    def get_by_id(self, fm_id: int) -> Optional[FamilyMember]:
        return self._s.query(FamilyMember).filter(FamilyMember.id == fm_id).first()

    def count_all(self) -> int:
        return self._s.query(FamilyMember).count()

    def create(self, fm: FamilyMember) -> FamilyMember:
        self._s.add(fm)
        self._s.flush()
        return fm

    def update(self, fm: FamilyMember) -> FamilyMember:
        self._s.flush()
        return fm

    def delete(self, fm: FamilyMember) -> None:
        self._s.delete(fm)
        self._s.flush()

    def delete_all_for_member(self, member_id: int) -> None:
        self._s.query(FamilyMember).filter(FamilyMember.member_id == member_id).delete()
        self._s.flush()
