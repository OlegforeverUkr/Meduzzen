from datetime import datetime

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship

from app.enums.invite_status import InviteStatusEnum, InviteTypeEnum
from app.enums.visability import VisibilityEnum
from app.db.base_model import Base
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from app.enums.roles_users import RoleEnum



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
    quizzes = relationship("Quiz", back_populates="company")


class CompanyMember(Base):
    __tablename__ = "company_members"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    role = Column(PgEnum(RoleEnum, name="role", create_type=True), nullable=False, default=RoleEnum.OWNER)

    user = relationship("User", back_populates="companies")
    company = relationship("Company", back_populates="members")


class InviteUser(Base):
    __tablename__ = "invites"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    status = Column(PgEnum(InviteStatusEnum), nullable=False, default=InviteStatusEnum.REQUEST)
    type_invite = Column(PgEnum(InviteTypeEnum), nullable=False)

    user = relationship("User", foreign_keys=[user_id])
    company = relationship("Company")



class Quiz(Base):
    __tablename__ = "quizzes"

    title = Column(String, nullable=False)
    description = Column(String)
    frequency_days = Column(Integer, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))

    company = relationship("Company", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete", lazy="selectin")


class Question(Base):
    __tablename__ = "questions"

    text = Column(String, nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"))

    quiz = relationship("Quiz", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete", lazy="selectin")


class Option(Base):
    __tablename__ = "options"

    text = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))

    question = relationship("Question", back_populates="options")


class QuizResult(Base):
    __tablename__ = "quiz_results"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)
    total_correct_answers = Column(Integer, nullable=False, default=0)
    total_questions_answered = Column(Integer, nullable=False, default=0)
    solved_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User")
    quiz = relationship("Quiz")
    company = relationship("Company")
