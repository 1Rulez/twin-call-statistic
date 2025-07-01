import logging
from fastapi.responses import JSONResponse
from fastapi import status, Request
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger("uvicorn")


class NotAccountException(Exception):
    pass


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request.app.container.logger.error(exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=None,
    )
