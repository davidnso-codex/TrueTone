"""Upload routes – returns a pre-signed S3 URL and creates a pending job."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query

from app.db.dynamo_jobs import put_job
from app.queue.sqs_client import enqueue_job
from app.schemas.jobs import JobCreateResponse, JobStatus
from app.settings import settings
from app.storage.s3_client import generate_presigned_upload_url

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("", response_model=JobCreateResponse, status_code=201)
def create_upload(
    style: str = Query(default="natural", description="Target colour style"),
) -> JobCreateResponse:
    """
    Create a new colouring job.

    Returns a pre-signed S3 PUT URL so the client can upload the image
    directly to S3, and a *job_id* to poll for results.
    """
    job_id = str(uuid.uuid4())
    input_key = f"inputs/{job_id}.jpg"

    try:
        upload_url = generate_presigned_upload_url(input_key)
        put_job(job_id=job_id, status=JobStatus.pending.value, input_key=input_key)
        enqueue_job(job_id=job_id, input_key=input_key, style=style)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable") from exc

    return JobCreateResponse(
        job_id=job_id,
        upload_url=upload_url,
        status=JobStatus.pending,
    )
