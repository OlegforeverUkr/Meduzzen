from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, InviteUser
from app.schemas.invites import InviteCreateSchema
from app.services.handlers_errors import get_company_or_404
from app.enums.invite_status import InviteStatusEnum, InviteTypeEnum
from app.services.invites_services import InvitesServices


class InviteRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create_invite(self, invite:InviteCreateSchema, current_user: User):
        company = await get_company_or_404(session=self.session, company_name=invite.company_name)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        results = await InvitesServices.create_invite_service(session=self.session,
                                                        current_user=current_user,
                                                        company=company,
                                                        username=invite.username)
        return results


    async def get_user_incoming_invites(self, current_user: User):
        results = await InvitesServices.get_all_incoming_invites_service(session=self.session,
                                                                         current_user=current_user)
        return results


    async def accept_invite(self, invite_id: int, current_user: User):
        invite = await self.session.get(InviteUser, invite_id)
        if invite:
            await InvitesServices.accept_invite_service(session=self.session,
                                                    invite=invite,
                                                    current_user=current_user)
        else:
            raise HTTPException(status_code=404, detail="Invite not found")


    async def reject_invite(self, invite_id: int, current_user: User):
        invite = await self.session.get(InviteUser, invite_id)
        if not invite:
            raise HTTPException(status_code=404, detail="Invite not found")

        if invite.user_id == current_user.id and invite.type_invite == InviteTypeEnum.INVITE:
            invite.status = InviteStatusEnum.DECLINED
            await self.session.commit()
            return {"message": "Invite declined successfully"}
        else:
            raise HTTPException(status_code=403,
                                detail="Permission denied: You can only reject invites that were sent to you")


    async def delete_invite_or_request(self, invite_id: int, current_user: User):
        invite = await self.session.get(InviteUser, invite_id)
        if invite:
            await InvitesServices.delete_invite_or_request_service(session=self.session,
                                                        invite=invite,
                                                        current_user=current_user)
        else:
            raise HTTPException(status_code=404, detail="Invite not found")
