from datetime import datetime

from pydantic import BaseModel


class NotificationSchema(BaseModel):
    id: int
    message: str

    class Config:
        from_attributes = True


class NotificationReadSchema(BaseModel):
    id: int
    message: str
    status: str
    updated_at: datetime

    class Config:
        from_attributes = True