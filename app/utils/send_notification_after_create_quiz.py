from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Notification, CompanyMember, Quiz
from app.enums.roles_users import RoleEnum


async def send_notifications(session: AsyncSession, quiz: Quiz):
    query = (
        select(CompanyMember)
        .where(and_(CompanyMember.company_id == quiz.company_id, CompanyMember.role == RoleEnum.MEMBER)))
    result = await session.execute(query)
    company_members = result.scalars().all()

    for member in company_members:
        notification = Notification(
            user_id=member.user_id,
            message=f"New quiz '{quiz.title}' has been created in your company. Take the quiz!"
        )
        session.add(notification)

    await session.commit()