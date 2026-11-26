import os

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import make_url


def run_migrations():
    database_url = make_url(os.environ["DATABASE_URL"])
    if database_url.drivername in {"postgres", "postgresql"}:
        database_url = database_url.set(drivername="postgresql+psycopg")

    if context.is_offline_mode():
        context.configure(url=database_url, literal_binds=True)
        with context.begin_transaction():
            context.run_migrations()
        return

    engine = create_engine(database_url, poolclass=pool.NullPool)
    try:
        with engine.connect() as connection:
            context.configure(connection=connection)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


run_migrations()
