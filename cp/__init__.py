import os

from dotenv import load_dotenv

from cpkit.logging import configure_logging

load_dotenv(override=True)

DB_URL = os.getenv("DB_URL")
configure_logging(default_journald_identifier="cp")
