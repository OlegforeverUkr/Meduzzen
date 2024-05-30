from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Notification
from app.enums.notification_status import NotificationStatusEnum


class NotificationRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def save_message_to_db(self, user_id: int, message: str):
        notification = Notification(user_id=user_id, message=message)
        self.session.add(notification)
        await self.session.commit()


    async def mark_message_as_read(self, message_id: int, user_id: int):
        query = await self.session.execute(select(Notification)
                                            .where(and_(Notification.id == message_id, Notification.user_id == user_id)))
        notification = query.scalar_one_or_none()

        if notification:
            notification.status = NotificationStatusEnum.READ
            await self.session.commit()
            await self.session.refresh(notification)
            return notification
        else:
            raise HTTPException(status_code=404, detail="Message not found")