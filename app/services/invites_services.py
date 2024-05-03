from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db.models import CompanyMember, InviteUser, User, Company
from app.enums.invite_status import InviteStatusEnum, InviteTypeEnum
from app.enums.roles_users import RoleEnum
from app.repositories.user_repo import UserRepository
from app.schemas.invites import InviteUserSchema


class InvitesServices:

    @staticmethod
    async def create_invite_service(session, current_user, company, username):
        user_created = await session.execute(select(CompanyMember)
                                               .where(CompanyMember.user_id == current_user.id)
                                               .where(CompanyMember.company_id == company.id))
        user_created = user_created.scalar_one_or_none()

        if not user_created or user_created.role != RoleEnum.OWNER:
            raise HTTPException(status_code=403, detail="You are not allowed to invite users to this company")

        invited_user = await UserRepository(session).get_user_by_username(username=username)

        created_invite = InviteUser(user_id=invited_user.id,
                                    company_id=company.id,
                                    status=InviteStatusEnum.REQUEST,
                                    type_invite=InviteTypeEnum.INVITE)
        session.add(created_invite)
        await session.commit()

        return InviteUserSchema(id=created_invite.id,
                                user=invited_user.username,
                                company=company.company_name,
                                status=created_invite.status)


    @staticmethod
    async def get_all_incoming_invites_service(session, current_user):
        incoming_invites = await session.execute(
            select(InviteUser)
            .where(InviteUser.user_id == current_user.id)
            .options(joinedload(InviteUser.user), joinedload(InviteUser.company))
        )
        return [InviteUserSchema(
            id=invite[0].id,
            user=invite[0].user.username,
            company=invite[0].company.company_name,
            status=invite[0].status.value
        ) for invite in incoming_invites.fetchall()]


    @staticmethod
    async def accept_invite_service(session, invite, current_user):
        invited_user = await session.get(User, invite.user_id)
        company = await session.get(Company, invite.company_id)

        if invited_user.id != current_user.id:
            raise HTTPException(status_code=403, detail="You don't have an invitation")

        company_member = CompanyMember(user=current_user, company=company, role=RoleEnum.MEMBER)
        session.add(company_member)
        invite.status = InviteStatusEnum.INVITE
        await session.commit()


    @staticmethod
    async def delete_invite_or_request_service(session, invite, current_user):
        inviter_company_member = await session.execute(
            select(CompanyMember)
            .where((CompanyMember.user_id == invite.user_id) & (CompanyMember.company_id == invite.company_id))
        )
        inviter_company_member = inviter_company_member.scalar_one_or_none()

        if not inviter_company_member or inviter_company_member.role != RoleEnum.OWNER:
            raise HTTPException(status_code=403, detail="Permission denied: You can only delete invites that you sent")

        if invite.user_id == current_user.id:
            await session.delete(invite)
            await session.commit()
            return {"message": "Invite deleted successfully"}
        else:
            raise HTTPException(status_code=403, detail="Permission denied: You can only delete invites that you sent")

