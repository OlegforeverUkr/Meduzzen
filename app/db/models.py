from sqlalchemy import Column, String, Boolean
from app.db.base_model import Base


class User(Base):
    __tablename__ = 'users'

    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
