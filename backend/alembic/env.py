from logging.config import fileConfig
import os
import sys
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

# ---------------------------------------------------------
# Make the backend directory importable
# ---------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(BACKEND_DIR))

# ---------------------------------------------------------
# Load environment variables from backend/.env
# ---------------------------------------------------------

load_dotenv(BACKEND_DIR / ".env")

# ---------------------------------------------------------
# Import database Base and models
# ---------------------------------------------------------

from app.core.database import Base
from app.models.heritage_site import HeritageSite
from app.models.heritage_connection import HeritageConnection
from app.models.heritage_source import HeritageSource
from app.models.heritage_media import HeritageMedia
from app.models.heritage_3d_asset import Heritage3DAsset
from app.models.import_batch import ImportBatch

# ---------------------------------------------------------
# Alembic Config object
# ---------------------------------------------------------

config = context.config

# ---------------------------------------------------------
# Configure logging
# ---------------------------------------------------------

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------
# Get DATABASE_URL from .env
# ---------------------------------------------------------

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError(
        "DATABASE_URL is not set in backend/.env"
    )

config.set_main_option(
    "sqlalchemy.url",
    database_url,
)

# ---------------------------------------------------------
# Metadata for 'autogenerate'
# ---------------------------------------------------------

target_metadata = Base.metadata


# ---------------------------------------------------------
# Offline migrations
# ---------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------
# Online migrations
# ---------------------------------------------------------

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {},
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
