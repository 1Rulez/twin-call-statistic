from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database: PostgresDsn
    database_schema: str
    debug_enabled: bool
    interface_opened: bool
    twin_auth_url: str
    twin_contacts_url: str
    date_start: str = '2025-02-24'
