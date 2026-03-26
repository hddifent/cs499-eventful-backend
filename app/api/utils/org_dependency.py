from typing import Annotated

from fastapi import Depends
from sqlalchemy import and_, select

from app.api.types import DBSession
from app.api.utils.http_exceptions import FORBIDDEN, ORG_INVITATION_NOT_ACCEPTED, ORG_NOT_FOUND
from app.api.utils.user_dependency import LoggedInUID
from app.db.models import OrganizerGroup, OrganizerMember, OrganizerMemberStatus
from app.schemas.orgs import OrgBase


async def get_org_membership_of_user(
    data: OrgBase, uid: LoggedInUID, db: DBSession
) -> tuple[int, OrganizerMemberStatus]:
    q_org_id = (
        select(OrganizerGroup.org_id)
        .where(OrganizerGroup.org_unique_name == data.org_unique_name)
        .limit(1)
    )
    r_org_id = await db.execute(q_org_id)
    s_org_id = r_org_id.scalar_one_or_none()

    if s_org_id == None:
        raise ORG_NOT_FOUND

    q_perm = (
        select(OrganizerMember.status)
        .where(
            and_(
                OrganizerMember.org_id == s_org_id,
                OrganizerMember.user_id == uid,
            )
        )
        .limit(1)
    )
    r_perm = await db.execute(q_perm)
    s_perm = r_perm.scalar_one_or_none()

    if s_perm == None:
        raise FORBIDDEN

    return s_org_id, s_perm


async def get_authorized_org_id(data: OrgBase, uid: LoggedInUID, db: DBSession) -> int:
    org_id, org_member_status = await get_org_membership_of_user(data, uid, db)
    if org_member_status != OrganizerMemberStatus.JOINED:
        raise ORG_INVITATION_NOT_ACCEPTED

    return org_id


async def get_all_org_of_user(uid: LoggedInUID, db: DBSession) -> list[int]:
    q_member = select(OrganizerMember.org_id).where(
        and_(OrganizerMember.user_id == uid, OrganizerMember.status == OrganizerMemberStatus.JOINED)
    )
    r_member = await db.execute(q_member)
    member_org_ids = r_member.scalars().all()

    return list(set(member_org_ids))


OrgMembership = Annotated[tuple[int, OrganizerMemberStatus], Depends(get_org_membership_of_user)]
AuthorizedOrgID = Annotated[int, Depends(get_authorized_org_id)]
JoinedOrgList = Annotated[list[int], Depends(get_all_org_of_user)]
