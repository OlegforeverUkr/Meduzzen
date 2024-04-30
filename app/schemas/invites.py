from pydantic import BaseModel
from app.utils.invite_status import InviteStatusEnum


class InviteUserSchema(BaseModel):
    id: int
    user: str
    company: str
    status: InviteStatusEnum


class InviteCreateSchema(BaseModel):
    username: str
    company_name: str
    status: InviteStatusEnum = InviteStatusEnum.REQUEST