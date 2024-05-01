from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.db.models import User, InviteUser, CompanyMember
from app.enums.invite_status import InviteTypeEnum, InviteStatusEnum
from app.enums.roles_users import RoleEnum
from app.repositories.user_repo import UserRepository
from app.schemas.invites import InviteUserSchema, InviteCreateSchema
from app.services.handlers_errors import get_company_or_404


class RequestsRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_all_user_requests(self, current_user: User):
        user_requests = await self.session.execute(
            select(InviteUser)
            .where((InviteUser.user_id == current_user.id) & (InviteUser.type_invite == InviteTypeEnum.REQUEST))
            .options(joinedload(InviteUser.user), joinedload(InviteUser.company))
        )
        return [InviteUserSchema(id=invite[0].id,
                                 user=invite[0].inviter.username,
                                 company=invite[0].company.company_name,
                                 status=invite[0].status.value
                                 ) for invite in user_requests.fetchall()]


    async def get_requests_users_in_company(self, company_id: int, current_user: User):
        company = await get_company_or_404(session=self.session, id=company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        user = await self.session.execute(select(CompanyMember)
                                          .where((CompanyMember.user_id == current_user.id) & (CompanyMember.company_id == company.id)))
        user = user.scalar_one_or_none()

        if not user or user.role != RoleEnum.OWNER:
            raise HTTPException(status_code=403, detail="You are not allowed to show users to this company")

        members = await self.session.execute(
            select(CompanyMember)
            .filter(CompanyMember.company_id == company_id)
            .filter(CompanyMember.role == RoleEnum.MEMBER)
            .options(selectinload(CompanyMember.user))
        )
        members = members.fetchall()
        member_users = [member.user for member in members]

        return member_users


    async def create_request(self, invite: InviteCreateSchema, current_user: User):
        company = await get_company_or_404(session=self.session, company_name=invite.company_name)
        invited_user = await UserRepository(self.session).get_user_by_username(username=current_user.username)
        create_request = InviteUser(user_id=invited_user.id,
                                    company_id=company.id,
                                    status=InviteStatusEnum.REQUEST,
                                    type_invite=InviteTypeEnum.REQUEST)
        self.session.add(create_request)
        await self.session.commit()

        return InviteUserSchema(id=create_request.id,
                                user=invited_user.username,
                                company=company.company_name,
                                status=create_request.status)


    async def accept_request(self, invite_id: int, current_user: User):
        invite = await self.session.get(InviteUser, invite_id)
        if not invite or invite.type_invite != InviteTypeEnum.REQUEST:
            raise HTTPException(status_code=404, detail="Request not found")

        current_user_info = await self.session.execute(
            select(CompanyMember)
            .where((CompanyMember.user_id == current_user.id) & (CompanyMember.company_id == invite.company_id))
        )
        current_user_info = current_user_info.scalar_one_or_none()

        if not current_user_info or current_user_info.role != RoleEnum.OWNER:
            raise HTTPException(status_code=403, detail="Permission denied: You can only accept requests to join your company")

        invite.status = InviteStatusEnum.ACCEPTED
        await self.session.commit()


    async def reject_request(self, invite_id: int, current_user: User):
        invite = await self.session.get(InviteUser, invite_id)
        if not invite:
            raise HTTPException(status_code=404, detail="Request not found")

        current_user_info = await self.session.execute(
            select(CompanyMember)
            .where((CompanyMember.user_id == current_user.id) & (CompanyMember.company_id == invite.company_id))
            .first()
        )
        current_user_info = current_user_info.scalar_one_or_none()

        if not current_user_info or current_user_info.role != RoleEnum.OWNER:
            raise HTTPException(status_code=403, detail="Permission denied: You can only reject requests to join your company")

        invite.status = InviteStatusEnum.DECLINED
        await self.session.commit()