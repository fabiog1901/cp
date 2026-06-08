"""CP remote worker adapters for cpkit Ansible playbook runners."""

from cpkit.playbooks import (
    AnsibleRunner,
    LiteAnsibleRunner,
    LiteRunnerResult,
    RunnerResult,
)

from ...infra import get_repo
from ...models import JobState


class MyRunner(AnsibleRunner):
    def __init__(
        self,
        job_id: int,
        counter: int = 0,
    ):
        super().__init__(
            repo=get_repo(),
            job_id=job_id,
            counter=counter,
            running_status=JobState.RUNNING,
            completed_status=JobState.COMPLETED,
            failed_status=JobState.FAILED,
        )

    my_event_handler = AnsibleRunner.event_handler
    my_status_handler = AnsibleRunner.status_handler


class MyRunnerLite(LiteAnsibleRunner):
    def __init__(
        self,
        job_id: int,
    ):
        super().__init__(
            repo=get_repo(),
            job_id=job_id,
        )

    my_event_handler = LiteAnsibleRunner.event_handler
    my_status_handler = LiteAnsibleRunner.status_handler


__all__ = [
    "LiteRunnerResult",
    "MyRunner",
    "MyRunnerLite",
    "RunnerResult",
]
