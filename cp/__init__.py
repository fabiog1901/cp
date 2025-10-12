from dotenv import load_dotenv

load_dotenv(override=True)

from .pages import (
    cluster_backups,
    cluster_jobs,
    cluster_overview,
    cluster_users,
    clusters,
    events,
    index,
    job_overview,
    jobs,
    login,
    settings,
)
