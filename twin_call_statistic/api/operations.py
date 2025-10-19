from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from twin_call_statistic.adapters.twin import TwinRepository
from twin_call_statistic.adapters.telegram import Telegram
from twin_call_statistic.api.schemas import AccountsSchema
from twin_call_statistic.configuration import Request
from twin_call_statistic.api.crud import (
    get_twin_accounts,
    get_from_date,
    save_contacts,
    get_last_updated_project,
)

twin_operation_router = APIRouter()


def get_session(request: Request) -> AsyncSession:
    return AsyncSession(bind=request.app.container.database_engine)


async def get_twin_repo(request: Request, login: str, password: str) -> TwinRepository:
    auth_url = request.app.container.settings.twin_auth_url
    contacts_url = request.app.container.settings.twin_contacts_url
    twin_operation = TwinRepository(
        auth_url=auth_url, contacts_url=contacts_url, login=login, password=password
    )
    return twin_operation


@twin_operation_router.post("/receive_contacts")
async def receive_contacts_info(request: Request):
    async with get_session(request) as session:
        accounts = await get_twin_accounts(session)

        if not accounts:
            raise HTTPException(
                status_code=404, detail="Список аккаунтов для сбора пуст"
            )

        accounts = [AccountsSchema(**acc) for acc in accounts]

        for account in accounts:
            twin = await get_twin_repo(
                request, account.twin_login, account.twin_password
            )
            token = await twin.get_auth_token()
            from_date = await get_from_date(session, account.twin_login)
            if not from_date:
                from_date = account.date_start

            await save_contacts(
                twin=twin,
                token=token,
                project=account.twin_login,
                session=session,
                from_=from_date,
                fields_=account.fields,
                bot_id=account.bot_id,
            )
            await session.commit()


@twin_operation_router.get("/last-updated")
async def get_last_updated_time(request: Request):

    date_now = datetime.now() - timedelta(hours=3)

    async with get_session(request) as session:
        projects = await get_last_updated_project(session)

        for project in projects:
            pr_date: datetime = project.get("last_date") + timedelta(hours=3)
            tg_token = project.get("tg_token")
            tg_chat_id = project.get("tg_chat_id")
            if 3 > date_now.hour < 23:
                return
            if pr_date.replace(tzinfo=None) > date_now:
                continue

            message = f"""❌ALERT❌ \nЗвонков по проекту {project.get("project")} нет уже 3 часа"""

            await Telegram(tg_token, tg_chat_id).send_telegram_message(message)
