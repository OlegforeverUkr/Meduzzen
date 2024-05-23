from datetime import datetime

from pydantic import BaseModel


class MessageSchema(BaseModel):
    id: int
    message: str

    class Config:
        from_attributes = True


class MessageReadSchema(BaseModel):
    id: int
    message: str
    status: str
    updated_at: datetime

    class Config:
        from_attributes = True