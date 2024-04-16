from sqlalchemy import Column, String, Boolean
from app.db.base_model import Base


class User(Base):
    __tablename__ = 'users'

    username = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
