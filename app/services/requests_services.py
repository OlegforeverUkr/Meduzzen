from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload, selectinload

from app.db.models import InviteUser, CompanyMember, Company, User
from app.enums.invite_status import InviteTypeEnum, InviteStatusEnum
from app.enums.roles_users import RoleEnum
from app.repositories.user_repo import UserRepository
from app.schemas.invites import InviteUserSchema
from app.services.handlers_errors import get_company_or_404


class RequestService:

    @staticmethod
    async def get_all_user_requests_service(session, current_user):
        user_requests = await session.execute(
            select(InviteUser)
            .where(and_(InviteUser.user_id == current_user.id, InviteUser.type_invite == InviteTypeEnum.REQUEST))
            .options(joinedload(InviteUser.user), joinedload(InviteUser.company))
        )
        return [InviteUserSchema(id=invite[0].id,
                                 user=invite[0].inviter.username,
                                 company=invite[0].company.company_name,
                                 status=invite[0].status.value
                                 ) for invite in user_requests.fetchall()]

    @staticmethod
    async def get_requests_users_in_company_service(session, company_id, company, current_user):
        user = await session.execute(select(CompanyMember)
                                          .where(and_(CompanyMember.user_id == current_user.id, CompanyMember.company_id == company.id)))
        user = user.scalar_one_or_none()

        if not user or user.role != RoleEnum.OWNER:
            raise HTTPException(status_code=403, detail="You are not allowed to show users to this company")

        members = await session.execute(
            select(CompanyMember)
            .where(and_(CompanyMember.company_id == company_id, CompanyMember.role == RoleEnum.MEMBER))
            .options(selectinload(CompanyMember.user))
        )
        members = members.fetchall()
        member_users = [member.user for member in members]
        return member_users


    @staticmethod
    async def create_request_service(session, invite, current_user):
        company = await get_company_or_404(session=session, company_name=invite.company_name)
        invited_user = await UserRepository(session).get_user_by_username(username=current_user.username)
        create_request = InviteUser(user_id=invited_user.id,
                                    company_id=company.id,
                                    status=InviteStatusEnum.REQUEST,
                                    type_invite=InviteTypeEnum.REQUEST)
        session.add(create_request)
        await session.commit()

        return InviteUserSchema(id=create_request.id,
                                user=invited_user.username,
                                company=company.company_name,
                                status=create_request.status)


    @staticmethod
    async def accept_request_service(session, invite_id, current_user):
        invite = await session.get(InviteUser, invite_id)
        if not invite or invite.type_invite != InviteTypeEnum.REQUEST:
            raise HTTPException(status_code=404, detail="Request not found")

        current_user_info = await session.execute(
            select(CompanyMember)
            .where(and_(CompanyMember.company_id == invite.company_id, CompanyMember.user_id == current_user.id)))
        current_user_info = current_user_info.scalar_one_or_none()

        if not current_user_info or current_user_info.role != RoleEnum.OWNER:
            raise HTTPException(status_code=403, detail="Permission denied: You can only accept requests to join your company")
        company = await session.get(Company, invite.company_id)
        user_invite = await session.get(User, invite.user_id)
        company_member = CompanyMember(user=user_invite, company=company, role=RoleEnum.MEMBER)
        session.add(company_member)

        await session.commit()


    @staticmethod
    async def reject_invite_service(session, invite, current_user):
        current_user_info = await session.execute(
            select(CompanyMember)
            .where(and_(CompanyMember.user_id == current_user.id, CompanyMember.company_id == invite.company_id))
        )
        current_user_info = current_user_info.scalar_one_or_none()

        if not current_user_info or current_user_info.role != RoleEnum.OWNER:
            raise HTTPException(status_code=403,
                                detail="Permission denied: You can only reject requests to join your company")

        invite.status = InviteStatusEnum.DECLINED
        await session.commit()

