from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.utils.visability import VisibilityEnum
from app.db.base_model import Base
from sqlalchemy.dialects.postgresql import ENUM as PgEnum


class User(Base):
    __tablename__ = 'users'

    username = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=True)

    owner_companies = relationship("Company", back_populates="owner")


class Company(Base):
    __tablename__ = "companies"

    company_name = Column(String(128), unique=True, index=True, nullable=False)
    description = Column(String(128), nullable=False)
    visibility = Column(PgEnum(VisibilityEnum, name="visibility", create_type=True), nullable=False, default=VisibilityEnum.PUBLIC)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="owner_companies")
