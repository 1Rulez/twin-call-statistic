from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from twin_call_statistic.adapters.twin import TwinRepository
from twin_call_statistic.configuration import Request
from twin_call_statistic.api.crud import get_twin_accounts, get_from_date, save_contacts

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

        request.app.container.logger.info(f"accounts {accounts}")
        if not accounts:
            raise HTTPException(
                status_code=404, detail="Список аккаунтов для сбора пуст"
            )

        accounts = [
            {"login": acc.twin_login, "pass": acc.twin_password, "field": acc.fields}
            for acc in accounts
        ]
        for account in accounts:
            login, password, fields = (
                account["login"],
                account["pass"],
                account["fields"],
            )
            twin = await get_twin_repo(
                request, login, password
            )
            token = await twin.get_auth_token()
            from_date = await get_from_date(session, login)
            from_date = (
                from_date if from_date else request.app.container.settings.date_start
            )
            await save_contacts(
                twin=twin,
                token=token,
                project=login,
                session=session,
                from_=from_date,
                fields_=fields,
            )
            await session.commit()
