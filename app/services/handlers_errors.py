from fastapi import HTTPException
from sqlalchemy import select
from app.db.models import User


async def get_or_404(session, **kwargs):
    query = select(User).where(User.id == kwargs.get('id'))
    result = await session.execute(query)
    instance = result.scalars().first()
    if not instance:
        raise HTTPException(status_code=404, detail="User not found")
    return instance