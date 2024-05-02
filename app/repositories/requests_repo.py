from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.db.models import User, InviteUser, CompanyMember, Company
from app.enums.invite_status import InviteTypeEnum, InviteStatusEnum
from app.enums.roles_users import RoleEnum
from app.repositories.user_repo import UserRepository
from app.schemas.invites import InviteUserSchema, InviteCreateSchema
from app.services.handlers_errors import get_company_or_404
from app.services.requests_services import RequestService


class RequestsRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_all_user_requests(self, current_user: User):
        await RequestService.get_all_user_requests_service(session=self.session, current_user=current_user)


    async def get_requests_users_in_company(self, company_id: int, current_user: User):
        company = await get_company_or_404(session=self.session, id=company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        else:
            users = await RequestService.get_requests_users_in_company_service(session=self.session,
                                                                               company=company,
                                                                               company_id=company_id,
                                                                               current_user=current_user)
            return users


    async def create_request(self, invite: InviteCreateSchema, current_user: User):
        request_create = await RequestService.create_request_service(session=self.session,
                                                                     invite=invite,
                                                                     current_user=current_user)
        return request_create


    async def accept_request(self, invite_id: int, current_user: User):
        try:
            await RequestService.accept_request_service(session=self.session,
                                                        invite_id=invite_id,
                                                        current_user=current_user)
        except HTTPException:
            pass
        else:
            return {"message": "Request accepted successfully"}


    async def reject_request(self, invite_id: int, current_user: User):
        invite = await self.session.get(InviteUser, invite_id)
        if not invite:
            raise HTTPException(status_code=404, detail="Request not found")
        else:
            try:
                await RequestService.reject_invite_service(session=self.session,
                                                           invite=invite,
                                                           current_user=current_user)
            except HTTPException:
                pass
            else:
                return {"message": "Request rejected successfully"}


    async def delete_request(self, invite_id: int, current_user: User):
        invite = await self.session.get(InviteUser, invite_id)
        if invite.user_id == current_user.id:
            await self.session.delete(invite)
            await self.session.commit()
            return {"message": "Invite deleted successfully"}
        else:
            raise HTTPException(status_code=403, detail="Permission denied: You can only delete request that you sent")




