from typing import Sequence
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select, desc, insert, RowMapping
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from twin_call_statistic.adapters.twin import TwinRepository
from twin_call_statistic.models import TwinProjects, CallInfo
from twin_call_statistic.api.schemas import ContactSchema


async def get_twin_accounts(session: AsyncSession) -> Sequence[RowMapping]:
    stmt = select(
        TwinProjects.twin_login,
        TwinProjects.twin_password,
        TwinProjects.fields,
        TwinProjects.date_start,
        TwinProjects.bot_id,
    ).where(TwinProjects.is_active.is_(True))
    return (await session.execute(stmt)).mappings().all()


async def get_from_date(session: AsyncSession, project: str) -> datetime | None:
    stmt = (
        select(CallInfo.createdAt)
        .where(CallInfo.project == project)
        .order_by(desc(CallInfo.createdAt))
        .limit(1)
    )
    result = await session.execute(stmt)
    date = result.scalars().first()
    if date:
        # -3 часа от мск, в utc, и -1 час для сбора за прошлый час
        dt_str = date.replace(minute=0, second=0) - timedelta(hours=4)
        return dt_str


async def save_contacts(
    twin: TwinRepository,
    token: str,
    project: str,
    session: AsyncSession,
    from_: datetime,
    limit: int = 1000,
    page: int = 0,
    fields_: dict = None,
    bot_id: UUID = None,
) -> dict | None:

    params = await prepare_params(
        limit=limit, page=page, fields_=fields_, bot_id=bot_id, from_=from_
    )

    contacts = await twin.get_call_data(token, params=params)

    if not contacts.get("items"):
        return None

    contacts_model = [ContactSchema(**contact) for contact in contacts.get("items")]

    contacts_db_dicts = [
        data_call.model_dump(exclude={"variablesString"})
        for data_call in contacts_model
        if data_call.currentStatusName not in ["INPROGRESS", "DIAL"]
    ]

    for contact_dict in contacts_db_dicts:
        contact_dict["project"] = project

    stmt = insert(CallInfo).values(contacts_db_dicts)
    stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
    await session.execute(stmt)

    if int(contacts.get("count")) / 1000 > page + 1:
        return await save_contacts(
            twin=twin,
            token=token,
            project=project,
            session=session,
            limit=limit,
            page=page + 1,
            from_=from_,
            fields_=fields_,
        )


async def prepare_params(
    limit: int, page: int, fields_: dict, bot_id: UUID, from_: datetime
) -> dict:

    params = {"limit": limit, "page": page}

    if from_:
        params["from"] = from_.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    if bot_id:
        params["botId"] = str(bot_id)

    to = datetime.now().replace(minute=0, second=0) - timedelta(hours=1)
    params["to"] = to.strftime("%Y-%m-%dT%H:%M:%S+00:00")

    if fields_:
        params["fields"] = ", ".join(i for i in fields_ if fields_[i] is True)

    return params
