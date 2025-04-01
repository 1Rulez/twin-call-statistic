import json
import traceback
from fastapi import Request


async def log_body(request: Request, call_next):
    body = await request.body()
    try:
        return await call_next(request)
    except Exception as error:
        request.app.container.logger.error(traceback.format_exc())
        if body:
            json_body = json.loads(body.decode("utf-8"))
            request.app.container.logger.error(f"Event: {json_body}")
        raise error
