"""SQLAlchemy ORM models — v1.2 schema."""

from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Member(Base):
    __tablename__ = 'members'

    id              = Column(Integer, primary_key=True, autoincrement=True)
    member_code     = Column(Text, unique=True, nullable=False)

    # Name fields — surname first per official form field ૧
    full_name       = Column(Text, nullable=False)
    surname         = Column(Text)
    father_name     = Column(Text)

    # Contact
    mobile          = Column(Text)          # મોબાઈલ નં.
    phone_landline  = Column(Text)          # ફોન નં.
    email           = Column(Text)          # ઈ-મેઈલ

    # Address
    address         = Column(Text)          # (૨) પત્ર વ્યવહારનું સરનામું
    village_address = Column(Text)          # (૩) ગામનું સરનામું
    city            = Column(Text)
    district        = Column(Text)
    state           = Column(Text)
    pincode         = Column(Text)

    # Professional / Employment (Section 2)
    occupation       = Column(Text)          # (૪) ધંધો / વ્યવસાય
    business_address = Column(Text)          # (૫) ધંધા / વ્યવસાયનું સરનામું
    income           = Column(Text)          # (૬) આવક
    education        = Column(Text)          # અભ્યાસ
    blood_group      = Column(Text)          # બ્લડ ગ્રુપ

    # Community
    samaj           = Column(Text)          # ૭ — સમાજ
    membership_fee  = Column(Text)          # સભ્ય ફી

    # Signature (text or uploaded image path)
    signature_text  = Column(Text)
    signature_image = Column(Text)

    # DOB — age computed at display time, never stored
    birth_date      = Column(Text)          # YYYY-MM-DD

    created_at      = Column(Text, nullable=False)
    updated_at      = Column(Text, nullable=False)

    # Relationship
    family_members  = relationship(
        'FamilyMember',
        back_populates='member',
        cascade='all, delete-orphan',
        lazy='select',
    )

    def __repr__(self) -> str:
        return f'<Member {self.member_code} {self.full_name}>'


class FamilyMember(Base):
    __tablename__ = 'family_members'

    id              = Column(Integer, primary_key=True, autoincrement=True)
    member_id       = Column(Integer, ForeignKey('members.id', ondelete='CASCADE'), nullable=False)

    name            = Column(Text, nullable=False)      # નામ
    relation        = Column(Text)                      # સબંધ
    age             = Column(Integer)                   # ઉમર (entered directly)
    education       = Column(Text)                      # અભ્યાસ
    blood_group     = Column(Text)                      # બ્લડ ગ્રુ
    occupation      = Column(Text)                      # વ્યવસાય
    contact_number  = Column(Text)                      # કોન્ટેક નંબર

    created_at      = Column(Text, nullable=False)
    updated_at      = Column(Text, nullable=False)

    # Relationship
    member          = relationship('Member', back_populates='family_members')

    def __repr__(self) -> str:
        return f'<FamilyMember {self.name} ({self.relation})>'


class AppSetting(Base):
    __tablename__ = 'app_settings'

    id              = Column(Integer, primary_key=True, autoincrement=True)
    setting_key     = Column(Text, unique=True, nullable=False)
    setting_value   = Column(Text)
    updated_at      = Column(Text, nullable=False)

    def __repr__(self) -> str:
        return f'<AppSetting {self.setting_key}={self.setting_value}>'
