from typing import Annotated

from fastapi import Depends
from sqlalchemy import and_, select

from app.api.types import DBSession
from app.api.utils.http_exceptions import FORBIDDEN, ORG_INVITATION_NOT_ACCEPTED, ORG_NOT_FOUND
from app.api.utils.user_dependency import LoggedInUID
from app.db.models import OrganizerGroup, OrganizerMember, OrganizerMemberStatus
from app.schemas.orgs import OrgBase


async def get_authorized_org_id(data: OrgBase, uid: LoggedInUID, db: DBSession) -> int:
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
    elif s_perm == OrganizerMemberStatus.INVITED:
        raise ORG_INVITATION_NOT_ACCEPTED

    return s_org_id


AuthorizedOrgID = Annotated[int, Depends(get_authorized_org_id)]
