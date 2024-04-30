from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connect_db import get_session
from app.db.models import User
from app.repositories.invite_repo import InviteRepository
from app.schemas.invites import InviteUserSchema, InviteCreateSchema
from app.schemas.users import UserSchema
from app.services.get_user_from_token import get_current_user_from_token

invite_routers = APIRouter()


@invite_routers.post("/invites/", response_model=InviteUserSchema)
async def create_invite(invite: InviteCreateSchema,
                  session: AsyncSession = Depends(get_session),
                  current_user: User = Depends(get_current_user_from_token)):
    new_invite = await InviteRepository(session).create_invite(invite, current_user)
    return new_invite


@invite_routers.get("/invites/", response_model=List[InviteUserSchema])
async def get_user_invites(session: AsyncSession = Depends(get_session),
                           current_user: User = Depends(get_current_user_from_token)):
    user_requests = await InviteRepository(session).get_user_all_invites(current_user=current_user)
    return user_requests


@invite_routers.get("/incoming_invites/", response_model=List[InviteUserSchema])
async def get_user_incoming_invites(session: AsyncSession = Depends(get_session),
                                    current_user: User = Depends(get_current_user_from_token)):
    incoming_invites = await InviteRepository(session).get_user_incoming_invites(current_user=current_user)
    return incoming_invites


@invite_routers.get("/incoming_invites/{company_id}/", response_model=List[UserSchema])
async def get_invited_users_for_company(company_id: int,
                                        session: AsyncSession = Depends(get_session),
                                        current_user: User = Depends(get_current_user_from_token)):
    invited_users = await InviteRepository(session).get_invited_users_for_company(company_id=company_id,
                                                                                  current_user=current_user)
    return invited_users


@invite_routers.post("/invites/accept/{invite_id}/")
async def accept_invite_endpoint(invite_id: int,
                                 session: AsyncSession = Depends(get_session),
                                 current_user: User = Depends(get_current_user_from_token)):
    await InviteRepository(session).accept_invite(invite_id=invite_id, current_user=current_user)
    return {"message": "Invite accepted successfully"}



@invite_routers.delete("/invites/reject/{invite_id}/")
async def reject_invite(invite_id: int,
                        session: AsyncSession = Depends(get_session),
                        current_user: User = Depends(get_current_user_from_token)):
    await InviteRepository(session).reject_invite(invite_id=invite_id, current_user=current_user)
    return {"message": "Invite rejected successfully"}


@invite_routers.delete("/invites/{invite_id}/")
async def delete_invite(invite_id: int,
                        session: AsyncSession = Depends(get_session),
                        current_user: User = Depends(get_current_user_from_token)):
    await InviteRepository(session).delete_invite(invite_id=invite_id, current_user=current_user)
    return {"message": "Invite deleted successfully"}