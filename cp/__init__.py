import os

from dotenv import load_dotenv

from .infra.logging import configure_logging

load_dotenv(override=True)

DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()
DB_URL = os.getenv("DB_URL", "sqlite.cp")
configure_logging()
