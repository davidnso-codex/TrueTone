"""Job status routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.db.dynamo_jobs import get_job
from app.schemas.jobs import JobStatus, JobStatusResponse
from app.storage.s3_client import generate_presigned_download_url

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str) -> JobStatusResponse:
    """Retrieve the current status of a colouring job."""
    item = get_job(job_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Job not found")

    status = JobStatus(item["status"])
    result_url: str | None = None

    if status == JobStatus.completed:
        output_key = item.get("output_key", f"outputs/{job_id}.jpg")
        result_url = generate_presigned_download_url(output_key)

    return JobStatusResponse(
        job_id=job_id,
        status=status,
        result_url=result_url,
        error=item.get("error"),
    )
