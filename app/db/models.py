from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.utils.visability import VisibilityEnum
from app.db.base_model import Base
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from app.utils.roles_users import RoleEnum


class User(Base):
    __tablename__ = 'users'

    username = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=True)

    companies = relationship("CompanyMember", back_populates="user", cascade="all, delete")


class Company(Base):
    __tablename__ = "companies"

    company_name = Column(String(128), unique=True, index=True, nullable=False)
    description = Column(String(128), nullable=False)
    visibility = Column(PgEnum(VisibilityEnum, name="visibility", create_type=True), nullable=False, default=VisibilityEnum.PUBLIC)

    members = relationship("CompanyMember", back_populates="company", cascade="all, delete")


class CompanyMember(Base):
    __tablename__ = "company_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    role = Column(PgEnum(RoleEnum, name="role", create_type=True), nullable=False, default=RoleEnum.OWNER)

    user = relationship("User", back_populates="companies")
    company = relationship("Company", back_populates="members")