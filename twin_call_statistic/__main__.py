import logging
import uvicorn
from sqlalchemy.ext.asyncio import create_async_engine
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from twin_call_statistic.api import twin_operation_router
from twin_call_statistic.configuration import Application, Container
from twin_call_statistic.middleware import log_body
from twin_call_statistic.settings import Settings
from twin_call_statistic.exception_handlers import validation_exception_handler


def create_application():
    """Инициализация приложения"""
    settings = Settings()
    interface_location = "/interface" if settings.interface_opened else None
    docs_location = '/docs' if settings.interface_opened else None
    application = Application(
        debug=settings.debug_enabled,
        title="Сбор статистики с TWIN",
        summary="Служба сбора статистики по звонкам",
        docs_url=docs_location,
        redoc_url=interface_location,
    )
    application.include_router(twin_operation_router)

    database_engine = create_async_engine(
        str(settings.database),
        echo=settings.debug_enabled,
        echo_pool=settings.debug_enabled,
        connect_args={
            "options": "-csearch_path={}".format(settings.database_schema),
        },
    )

    application.container = Container()
    application.container.settings = settings
    application.container.database_engine = database_engine

    application.container.logger = logging.getLogger("uvicorn")

    application.add_exception_handler(
        RequestValidationError, validation_exception_handler
    )
    application.add_middleware(BaseHTTPMiddleware, dispatch=log_body)
    return application


uvicorn.run(app=create_application(), host="0.0.0.0")
