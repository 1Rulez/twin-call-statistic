from logging.config import fileConfig

from alembic import context
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from sqlalchemy import NullPool, create_engine

from twin_call_statistic.models import Base


class Settings(BaseSettings):
    database: PostgresDsn
    database_schema: str


settings = Settings()

if context.config.config_file_name:
    fileConfig(context.config.config_file_name)


def run_migrations_online() -> None:
    engine = create_engine(
        str(settings.database),
        poolclass=NullPool,
        connect_args={
            "options": "-csearch_path={}".format(settings.database_schema),
        },
    )

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise NotImplementedError("Офлайн режим не поддерживается")
else:
    run_migrations_online()
