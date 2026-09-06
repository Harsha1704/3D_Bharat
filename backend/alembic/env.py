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
    raise RuntimeError(
        "DATABASE_URL is not configured in backend/.env"
    )

config.set_main_option(
    "sqlalchemy.url",
    database_url.replace("%", "%%"),
)

# ---------------------------------------------------------
# SQLAlchemy metadata
# ---------------------------------------------------------

target_metadata = Base.metadata
def include_object(
    object,
    name,
    type_,
    reflected,
    compare_to,
):
    """
    Tell Alembic which database objects should be
    included in schema comparisons.
    """

    # PostGIS creates this table automatically.
    # It is not owned by our application.
    if type_ == "table" and name == "spatial_ref_sys":
        return False

    return True

# ---------------------------------------------------------
# Offline migration
# ---------------------------------------------------------

def run_migrations_offline() -> None:
    """
    Run migrations without creating a database connection.
    """

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
        compare_type=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------
# Online migration
# ---------------------------------------------------------

def run_migrations_online() -> None:
    """
    Run migrations using an active database connection.
    """

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------
# Run appropriate migration mode
# ---------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()