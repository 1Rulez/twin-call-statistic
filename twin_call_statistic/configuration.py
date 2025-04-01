import logging

from fastapi import FastAPI
from fastapi import Request as BaseRequest
from fastapi.datastructures import State
from sqlalchemy.ext.asyncio import AsyncEngine
from twin_call_statistic.settings import Settings


class Container(State):
    settings: Settings
    database_engine: AsyncEngine
    logger: logging.Logger


class Application(FastAPI):
    container: Container


class Request(BaseRequest):
    @property
    def app(self) -> Application:
        return super().app
