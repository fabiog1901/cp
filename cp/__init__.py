from dotenv import load_dotenv

load_dotenv(override=True)

from .webapp.pages import events, index, login
from .webapp.pages.admin import admin, playbooks, regions, settings, versions
from .webapp.pages.clusters import backups, cluster, clusters, dashboard, jobs, users
from .webapp.pages.jobs import job, jobs
