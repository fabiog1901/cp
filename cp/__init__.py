from dotenv import load_dotenv

load_dotenv(override=True)

from .pages import events, index, login
from .pages.admin import admin, playbooks, regions, settings, versions
from .pages.clusters import backups, cluster, clusters, dashboard, jobs, users
from .pages.jobs import job, jobs
