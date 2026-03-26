from fastapi import APIRouter, status
from sqlalchemy import and_, delete, select
from sqlalchemy.orm import joinedload, selectinload

from app.api.types import DBSession
from app.api.utils.http_exceptions import (
    BAD_REQUEST,
    FORBIDDEN,
    ORG_ALREADY_INVITED,
    ORG_DNAME_ALREADY_REGISTERED,
    ORG_INVITATION_NOT_ACCEPTED,
    ORG_NOT_FOUND,
    ORG_UNAME_ALREADY_REGISTERED,
    SHOULD_NOT_HAPPEN,
)
from app.api.utils.org_dependency import AuthorizedOrgID, OrgMembership
from app.api.utils.user_dependency import LoggedInUID
from app.db.models import OrganizerGroup, OrganizerMember, OrganizerMemberStatus, User
from app.schemas.orgs import (
    OrgCreate,
    OrgMemberAction,
    OrgPagePrivateResponse,
    OrgPagePublicResponse,
)

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
    await db.flush()

    new_org_member = OrganizerMember(
        user_id=uid,
        org_id=new_org.org_id,
        status=OrganizerMemberStatus.JOINED,
    )

    db.add(new_org_member)
    await db.commit()

    return {"message": "Organization created."}


@router.get(
    "/profile/{org_unique_name}",
    status_code=status.HTTP_200_OK,
    response_model=OrgPagePublicResponse,
)
async def get_org_by_uname(org_unique_name: str, db: DBSession):
    q_org = select(OrganizerGroup).where(OrganizerGroup.org_unique_name == org_unique_name).limit(1)
    r_org = await db.execute(q_org)
    s_org = r_org.scalar_one_or_none()

    if s_org == None:
        raise ORG_NOT_FOUND

    return s_org


@router.get(
    "/profile/{org_unique_name}/full",
    status_code=status.HTTP_200_OK,
    response_model=OrgPagePrivateResponse,
)
async def get_full_org_by_uname(org_unique_name: str, uid: LoggedInUID, db: DBSession):
    q_org = (
        select(OrganizerGroup)
        .where(OrganizerGroup.org_unique_name == org_unique_name)
        .options(
            joinedload(OrganizerGroup.head_user),
            selectinload(OrganizerGroup.org_members).joinedload(OrganizerMember.user),
        )
        .limit(1)
    )
    r_org = await db.execute(q_org)
    s_org = r_org.scalar_one_or_none()

    if s_org == None:
        raise ORG_NOT_FOUND

    org_members = {m.user_id: m.status for m in s_org.org_members}
    user_perm = org_members.get(uid)

    if user_perm == None:
        raise FORBIDDEN
    elif user_perm == OrganizerMemberStatus.INVITED:
        raise ORG_INVITATION_NOT_ACCEPTED

    return s_org


@router.post(
    "/invite",
    status_code=status.HTTP_200_OK,
)
async def invite_member(data: OrgMemberAction, org_id: AuthorizedOrgID, db: DBSession):
    q_uid = select(User.user_id).where(User.username == data.username).limit(1)
    r_uid = await db.execute(q_uid)
    s_uid = r_uid.scalar_one_or_none()

    if s_uid == None:
        raise BAD_REQUEST

    q_existing_member = (
        select(OrganizerMember)
        .where(
            and_(
                OrganizerMember.org_id == org_id,
                OrganizerMember.user_id == s_uid,
            )
        )
        .limit(1)
    )
    r_existing_member = await db.execute(q_existing_member)
    s_existing_member = r_existing_member.scalar_one_or_none()

    if s_existing_member != None:
        raise ORG_ALREADY_INVITED

    new_org_member = OrganizerMember(
        user_id=s_uid,
        org_id=org_id,
        status=OrganizerMemberStatus.INVITED,
    )

    db.add(new_org_member)
    await db.commit()

    return {"message": "User invited."}


@router.post(
    "/revoke",
    status_code=status.HTTP_200_OK,
)
async def revoke_member(data: OrgMemberAction, org_id: AuthorizedOrgID, db: DBSession):
    q_uid = select(User.user_id).where(User.username == data.username).limit(1)
    r_uid = await db.execute(q_uid)
    s_uid = r_uid.scalar_one_or_none()

    if s_uid != None:
        q_delete = delete(OrganizerMember).where(
            and_(
                OrganizerMember.org_id == org_id,
                OrganizerMember.user_id == s_uid,
            )
        )
        await db.execute(q_delete)
        await db.commit()

    return {"message": "User revoked."}


@router.post(
    "/acceptinvite",
    status_code=status.HTTP_200_OK,
)
async def accept_invite(uid: LoggedInUID, org_membership: OrgMembership, db: DBSession):
    org_id, org_member_status = org_membership
    if org_member_status != OrganizerMemberStatus.INVITED:
        raise BAD_REQUEST

    q_member = (
        select(OrganizerMember)
        .where(
            and_(
                OrganizerMember.org_id == org_id,
                OrganizerMember.user_id == uid,
            )
        )
        .limit(1)
    )
    r_member = await db.execute(q_member)
    s_member = r_member.scalar_one_or_none()

    if s_member == None:
        raise SHOULD_NOT_HAPPEN  # as org_membership is a dependency

    s_member.status = OrganizerMemberStatus.JOINED
    await db.commit()

    return {"message": "Organizer Group joined successfully."}


@router.post(
    "/rejectinvite",
    status_code=status.HTTP_200_OK,
)
async def reject_invite(uid: LoggedInUID, org_membership: OrgMembership, db: DBSession):
    org_id, org_member_status = org_membership
    if org_member_status != OrganizerMemberStatus.INVITED:
        raise BAD_REQUEST

    # TODO: Maybe change to OrganizerMemberStatus.REJECTED instead?
    q_delete = delete(OrganizerMember).where(
        and_(
            OrganizerMember.org_id == org_id,
            OrganizerMember.user_id == uid,
        )
    )
    await db.execute(q_delete)
    await db.commit()

    return {"message": "Organizer Group invitation rejected."}
