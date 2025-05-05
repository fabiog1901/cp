from dotenv import load_dotenv

load_dotenv(override=True)

from .pages import (cluster_overview, clusters, index, job_overview, jobs,
                    login, settings)
