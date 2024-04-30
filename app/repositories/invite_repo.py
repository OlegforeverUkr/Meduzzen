from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.db.models import User, InviteUser, CompanyMember, Company
from app.repositories.user_repo import UserRepository
from app.schemas.invites import InviteCreateSchema, InviteUserSchema
from app.services.handlers_errors import get_company_or_404
from app.utils.invite_status import InviteStatusEnum
from app.utils.roles_users import RoleEnum


class InviteRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create_invite(self, invite:InviteCreateSchema, current_user: User):
        company = await get_company_or_404(session=self.session, company_name=invite.company_name)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        user_created = await self.session.execute(select(CompanyMember)
                                               .where(CompanyMember.user_id == current_user.id)
                                               .where(CompanyMember.company_id == company.id))
        user_created = user_created.scalar_one_or_none()

        if user_created.role != RoleEnum.OWNER:
            raise HTTPException(status_code=403, detail="You are not allowed to invite users to this company")

        invited_user = await UserRepository(self.session).get_user_by_username(username=invite.username)

        created_invite = InviteUser(invite_from=current_user.id,
                                    invite_to=invited_user.id,
                                    company_id=company.id,
                                    status=InviteStatusEnum.REQUEST)
        self.session.add(created_invite)
        await self.session.commit()

        return InviteUserSchema(id=created_invite.id,
                                user=invited_user.username,
                                company=company.company_name,
                                status=created_invite.status)


    async def get_user_all_invites(self, current_user: User):
        user_requests = await self.session.execute(
            select(InviteUser)
            .where(InviteUser.invite_from == current_user.id)
            .options(joinedload(InviteUser.inviter), joinedload(InviteUser.company))
        )
        return [InviteUserSchema(
            id=invite[0].id,
            user=invite[0].inviter.username,
            company=invite[0].company.company_name,
            status=invite[0].status.value
        ) for invite in user_requests.fetchall()]


    async def get_user_incoming_invites(self, current_user: User):
        incoming_invites = await self.session.execute(
            select(InviteUser)
            .where(InviteUser.invite_to == current_user.id)
            .options(joinedload(InviteUser.inviter), joinedload(InviteUser.company))
        )
        return [InviteUserSchema(
            id=invite[0].id,
            user=invite[0].inviter.username,
            company=invite[0].company.company_name,
            status=invite[0].status.value
        ) for invite in incoming_invites.fetchall()]


    async def get_invited_users_for_company(self, company_id: int, current_user: User):
        company = await get_company_or_404(session=self.session, id=company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        user = await self.session.execute(select(CompanyMember)
                                               .where(CompanyMember.user_id == current_user.id)
                                               .where(CompanyMember.company_id == company.id))
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


    async def accept_invite(self, invite_id: int, current_user: User):
        invite = await self.session.get(InviteUser, invite_id)
        if invite:
            invited_user = await self.session.get(User, invite.invite_to)
            company = await self.session.get(Company, invite.company_id)


            if invited_user.id != current_user.id:
                raise HTTPException(status_code=403, detail="You don't have an invitation")

            company_member = CompanyMember(user=current_user, company=company, role=RoleEnum.MEMBER)
            self.session.add(company_member)
            invite.status = InviteStatusEnum.INVITE
            await self.session.commit()
        else:
            raise HTTPException(status_code=404, detail="Invite not found")


    async def reject_invite(self, invite_id: int, current_user: User):
        invite = await self.session.get(InviteUser, invite_id)
        if not invite:
            raise HTTPException(status_code=404, detail="Invite not found")

        if invite.invite_to == current_user.id:
            invite.status = InviteStatusEnum.DECLINED
            await self.session.commit()
            return {"message": "Invite declined successfully"}
        else:
            raise HTTPException(status_code=403,
                                detail="Permission denied: You can only reject invites that were sent to you")


    async def delete_invite(self, invite_id: int, current_user: User):
        invite = await self.session.get(InviteUser, invite_id)
        if not invite:
            raise HTTPException(status_code=404, detail="Invite not found")

        if invite.invite_from == current_user.id:

            await self.session.delete(invite)
            await self.session.commit()
            return {"message": "Invite deleted successfully"}
        else:
            raise HTTPException(status_code=403, detail="Permission denied: You can only delete invites that you sent")