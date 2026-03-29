from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.exceptions import RequestErrorModel

from ..auth import get_access_scope, get_audit_actor, require_readonly, require_user
from ..infra import get_jobs_service
from ..models import Job, JobDetailsResponse, JobRescheduleResponse
from ..services.errors import (
    ServiceAuthorizationError,
    ServiceError,
    ServiceNotFoundError,
    ServiceUnavailableError,
    ServiceValidationError,
)
from ..services.jobs import JobsService

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


def _raise_http_from_service_error(err: ServiceError) -> None:
    if isinstance(err, ServiceNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=err.user_message,
        )
    if isinstance(err, ServiceValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.user_message,
        )
    if isinstance(err, ServiceAuthorizationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=err.user_message,
        )
    if isinstance(err, ServiceUnavailableError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=err.user_message,
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=err.user_message,
    )


@router.get("/")
async def list_jobs(
    claims: dict = Depends(require_readonly),
    service: JobsService = Depends(get_jobs_service),
) -> list[Job]:
    groups, is_admin = get_access_scope(claims)
    try:
        return service.list_visible_jobs(groups, is_admin)
    except ServiceError as err:
        _raise_http_from_service_error(err)


@router.get(
    "/{job_id}",
    responses={
        404: {
            "model": RequestErrorModel,
            "description": "Job not found.",
        },
    },
)
async def get_job(
    job_id: int,
    claims: dict = Depends(require_readonly),
    service: JobsService = Depends(get_jobs_service),
) -> Job:
    groups, is_admin = get_access_scope(claims)
    try:
        job = service.get_job_for_user(job_id, groups, is_admin)
    except ServiceError as err:
        _raise_http_from_service_error(err)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' was not found.",
        )

    return job


@router.get(
    "/{job_id}/details",
    response_model=JobDetailsResponse,
    responses={
        404: {
            "model": RequestErrorModel,
            "description": "Job not found.",
        },
    },
)
async def get_job_details(
    job_id: int,
    claims: dict = Depends(require_readonly),
    service: JobsService = Depends(get_jobs_service),
) -> JobDetailsResponse:
    groups, is_admin = get_access_scope(claims)
    try:
        details = service.get_job_details_for_user(job_id, groups, is_admin)
    except ServiceError as err:
        _raise_http_from_service_error(err)

    if details is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' was not found.",
        )

    return JobDetailsResponse(**details)


@router.post(
    "/{job_id}/reschedule",
    response_model=JobRescheduleResponse,
    responses={
        404: {
            "model": RequestErrorModel,
            "description": "Job not found.",
        },
    },
)
async def reschedule_job(
    job_id: int,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: JobsService = Depends(get_jobs_service),
) -> JobRescheduleResponse:
    groups, is_admin = get_access_scope(claims)
    try:
        new_job_id = service.enqueue_job_reschedule(
            job_id,
            groups,
            is_admin,
            actor_id,
        )
    except ServiceError as err:
        _raise_http_from_service_error(err)

    return JobRescheduleResponse(job_id=new_job_id)
