from dotenv import load_dotenv

load_dotenv(override=True)

from .pages import events, index, login
from .pages.admin import admin, regions, settings, versions
from .pages.clusters import backups, cluster, clusters, jobs, users
from .pages.jobs import job, jobs
