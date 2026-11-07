import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Base backend directory
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables
load_dotenv(BACKEND_DIR / ".env")


class Settings:
    """
    Application configuration loaded from environment variables.
    """

    PROJECT_NAME: str = "3D BHARAT"
    PROJECT_VERSION: str = "0.1.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Storage Abstraction Settings
    STORAGE_LOCAL_ROOT: Path = Path(
        os.getenv("STORAGE_LOCAL_ROOT", str(BACKEND_DIR / "storage" / "uploads"))
    ).resolve()

    MAX_MEDIA_FILE_SIZE_BYTES: int = int(
        os.getenv("MAX_MEDIA_FILE_SIZE_BYTES", str(50 * 1024 * 1024))
    )  # 50 MB
    MAX_3D_FILE_SIZE_BYTES: int = int(
        os.getenv("MAX_3D_FILE_SIZE_BYTES", str(200 * 1024 * 1024))
    )  # 200 MB

    # CORS Whitelist Configuration
    # Defaults to development origins if not explicitly set
    _cors_raw: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )

    @property
    def CORS_ORIGINS(self) -> List[str]:
        raw = self._cors_raw.strip()
        if not raw:
            return ["http://localhost:5173", "http://127.0.0.1:5173"]

        origins = [origin.strip() for origin in raw.split(",") if origin.strip()]

        # Security check: never allow wildcard '*' with credentials
        if "*" in origins:
            # Fall back to safe development origins if wildcard is accidentally configured
            origins = [o for o in origins if o != "*"]
            if not origins:
                origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

        return origins


settings = Settings()
