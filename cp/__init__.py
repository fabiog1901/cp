from dotenv import load_dotenv

load_dotenv(override=True)

from .pages import (
    cluster_jobs,
    cluster_backups,
    cluster_overview,
    clusters,
    events,
    index,
    job_overview,
    jobs,
    login,
    settings,
)
