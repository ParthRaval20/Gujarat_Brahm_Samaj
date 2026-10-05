"""Smart search service."""

from __future__ import annotations

from database.connection import get_session
from database.models import Member
from database.repositories.member_repository import MemberRepository


class SearchService:
    def search(self, query: str) -> list[Member]:
        query = query.strip()
        if not query:
            return []
        with get_session() as session:
            members = MemberRepository(session).search(query)
            for m in members:
                session.expunge(m)
            return members

    def get_today_members(self) -> list[Member]:
        with get_session() as session:
            members = MemberRepository(session).get_today()
            for m in members:
                session.expunge(m)
            return members
