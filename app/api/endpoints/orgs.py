from fastapi import APIRouter, status
from sqlalchemy import and_, select

from app.api.types import DBSession
from app.api.utils.http_exceptions import (
    FORBIDDEN,
    NOT_IMPLEMENTED,
    ORG_DNAME_ALREADY_REGISTERED,
    ORG_INVITATION_NOT_ACCEPTED,
    ORG_NOT_FOUND,
    ORG_UNAME_ALREADY_REGISTERED,
)
from app.api.utils.user_dependency import LoggedInUID
from app.db.models import OrganizerGroup, OrganizerMember, OrganizerMemberStatus
from app.schemas.orgs import OrgCreate

router = APIRouter()


@router.post(
    "/new",
    status_code=status.HTTP_201_CREATED,
)
async def create_org(data: OrgCreate, uid: LoggedInUID, db: DBSession):
    q_existing_uname = (
        select(OrganizerGroup.org_id)
        .where(OrganizerGroup.org_unique_name == data.org_unique_name)
        .limit(1)
    )
    r_existing_uname = await db.execute(q_existing_uname)
    s_existing_uname = r_existing_uname.scalar_one_or_none()
    if s_existing_uname != None:
        raise ORG_UNAME_ALREADY_REGISTERED

    q_existing_dname = (
        select(OrganizerGroup.org_id)
        .where(OrganizerGroup.org_display_name == data.org_display_name)
        .limit(1)
    )
    r_existing_dname = await db.execute(q_existing_dname)
    s_existing_dname = r_existing_dname.scalar_one_or_none()
    if s_existing_dname != None:
        raise ORG_DNAME_ALREADY_REGISTERED

    new_org = OrganizerGroup(
        org_unique_name=data.org_unique_name,
        org_display_name=data.org_display_name,
        org_head_user_id=uid,
    )

    db.add(new_org)
    await db.commit()

    return {"message": "Organization Created"}


@router.get(
    "/{org_unique_name}",
    status_code=status.HTTP_200_OK,
)
async def get_org_by_uname(org_unique_name: str, uid: LoggedInUID, db: DBSession):
    q_org_id = (
        select(OrganizerGroup.org_id)
        .where(OrganizerGroup.org_unique_name == org_unique_name)
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
    elif s_perm == OrganizerMemberStatus.INVITED:
        raise ORG_INVITATION_NOT_ACCEPTED

    raise NOT_IMPLEMENTED


# FIXME
@router.post(
    "/{org_unique_name}/invite/{username}",
    status_code=status.HTTP_200_OK,
)
async def invite_member(org_unique_name: str, username: str, uid: LoggedInUID, db: DBSession):
    raise NOT_IMPLEMENTED


@router.post(
    "/{org_unique_name}/revoke/{username}",
    status_code=status.HTTP_200_OK,
)
async def revoke_member(org_unique_name: str, username: str, uid: LoggedInUID, db: DBSession):
    raise NOT_IMPLEMENTED


@router.post(
    "/{org_unique_name}/acceptinvite",
    status_code=status.HTTP_200_OK,
)
async def accept_invite(org_unique_name: str, uid: LoggedInUID, db: DBSession):
    raise NOT_IMPLEMENTED


@router.post(
    "/{org_unique_name}/rejectinvite",
    status_code=status.HTTP_200_OK,
)
async def reject_invite(org_unique_name: str, uid: LoggedInUID, db: DBSession):
    raise NOT_IMPLEMENTED
