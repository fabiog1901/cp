import os

from dotenv import load_dotenv

from .infra.logging import configure_logging

load_dotenv(override=True)

DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()
DB_URL = os.getenv("DB_URL", "sqlite.kloigos")
configure_logging()

# from .webapp.pages import events, index, login
# from .webapp.pages.admin import admin, playbooks, regions, settings, versions
# from .webapp.pages.clusters import backups, cluster, clusters, dashboard, jobs, users
# from .webapp.pages.jobs import job, jobs
