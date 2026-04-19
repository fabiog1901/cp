import os

from dotenv import load_dotenv

from .infra.logging import configure_logging

load_dotenv(override=True)

DB_URL = os.getenv("DB_URL", "sqlite.cp")
DB_ENGINE = "postgres" if DB_URL.startswith("postgres") else "sqlite"
configure_logging()
