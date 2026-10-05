"""Tests for member service."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from database.connection import init_db
from services.member_service import MemberService
from services.family_service import FamilyService


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    """Use a temporary DB for each test."""
    import app.config as cfg
    db = str(tmp_path / 'test.db')
    monkeypatch.setattr(cfg, 'DB_PATH', db)
    monkeypatch.setattr(cfg, 'DATA_DIR', str(tmp_path))
    monkeypatch.setattr(cfg, 'BACKUP_DIR', str(tmp_path / 'backups'))
    monkeypatch.setattr(cfg, 'EXPORT_DIR', str(tmp_path / 'exports'))
    monkeypatch.setattr(cfg, 'LOG_DIR',    str(tmp_path / 'logs'))
    import database.connection as conn
    conn._engine = None
    conn._SessionLocal = None
    init_db()
    yield
    conn._engine = None
    conn._SessionLocal = None


def _sample_data(**overrides):
    data = {
        'full_name':      'Raval Parth',
        'surname':        'Raval',
        'father_name':    'Mahesh Raval',
        'mobile':         '9876543210',
        'phone_landline': '02822-123456',
        'email':          'parth@example.com',
        'address':        'A-101 Gandhi Nagar',
        'city':           'Rajkot',
        'district':       'Rajkot',
        'state':          'Gujarat',
        'pincode':        '360001',
        'education':      'B.Tech',
        'occupation':     'Software Developer',
        'blood_group':    'B+',
        'samaj':          'Raval',
        'membership_fee': '500',
        'birth_date':     '2003-11-20',
    }
    data.update(overrides)
    return data


class TestMemberService:
    def test_create_member_success(self):
        svc = MemberService()
        member, errors = svc.create_member(_sample_data())
        assert not errors
        assert member is not None
        assert member.member_code.startswith('GBS-')
        assert member.full_name == 'Raval Parth'

    def test_member_code_sequential(self):
        svc = MemberService()
        m1, _ = svc.create_member(_sample_data(mobile='9000000001'))
        m2, _ = svc.create_member(_sample_data(full_name='Test Two', mobile='9000000002'))
        n1 = int(m1.member_code.split('-')[1])
        n2 = int(m2.member_code.split('-')[1])
        assert n2 == n1 + 1

    def test_create_member_missing_name(self):
        _, errors = MemberService().create_member(_sample_data(full_name=''))
        assert errors

    def test_create_member_invalid_mobile(self):
        _, errors = MemberService().create_member(_sample_data(mobile='123'))
        assert errors

    def test_create_member_invalid_pincode(self):
        _, errors = MemberService().create_member(_sample_data(pincode='12345'))
        assert errors

    def test_update_member(self):
        svc = MemberService()
        member, _ = svc.create_member(_sample_data())
        updated, errors = svc.update_member(member.id, _sample_data(full_name='Raval Updated'))
        assert not errors
        assert updated.full_name == 'Raval Updated'

    def test_delete_member(self):
        svc = MemberService()
        member, _ = svc.create_member(_sample_data())
        result = svc.delete_member(member.id)
        assert result
        assert svc.get_member(member.id) is None

    def test_delete_cascades_family(self):
        svc = MemberService()
        fsvc = FamilyService()
        member, _ = svc.create_member(_sample_data())
        fsvc.add_family_member(member.id, {
            'name': 'Mahesh', 'relation': 'Father', 'age': 50,
            'education': 'B.Com', 'blood_group': 'A+',
            'occupation': 'Business', 'contact_number': '9000000001',
        })
        svc.delete_member(member.id)
        fms = fsvc.get_family_members(member.id)
        assert len(fms) == 0

    def test_samaj_phone_landline_membership_fee_stored(self):
        svc = MemberService()
        member, _ = svc.create_member(_sample_data())
        fetched = svc.get_member(member.id)
        assert fetched.samaj == 'Raval'
        assert fetched.phone_landline == '02822-123456'
        assert fetched.membership_fee == '500'

    def test_delete_all_members(self):
        svc = MemberService()
        fsvc = FamilyService()
        m1, _ = svc.create_member(_sample_data(full_name='Member One', mobile='9111111111'))
        m2, _ = svc.create_member(_sample_data(full_name='Member Two', mobile='9222222222'))
        fsvc.add_family_member(m1.id, {
            'name': 'Mahesh', 'relation': 'Father', 'age': 50,
            'education': 'B.Com', 'blood_group': 'A+',
            'occupation': 'Business', 'contact_number': '9000000001',
        })
        fsvc.add_family_member(m2.id, {
            'name': 'Geeta', 'relation': 'Mother', 'age': 48,
            'education': 'B.A', 'blood_group': 'B+',
            'occupation': 'Homemaker', 'contact_number': '9000000002',
        })
        assert svc.count() == 2
        assert fsvc.count_all() == 2

        deleted = svc.delete_all_members()
        assert deleted == 2
        assert svc.count() == 0
        assert fsvc.count_all() == 0
        assert svc.get_all() == []

        # Ensure next member created starts at GBS-000001
        m3, _ = svc.create_member(_sample_data(full_name='Member Three', mobile='9333333333'))
        assert m3.member_code == 'GBS-000001'

