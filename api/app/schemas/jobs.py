"""Pydantic schemas for job-related request/response models."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class JobCreateResponse(BaseModel):
    job_id: str
    upload_url: str = Field(description="Pre-signed S3 URL for image upload")
    status: JobStatus = JobStatus.pending


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    result_url: Optional[str] = Field(
        default=None,
        description="Pre-signed S3 URL for the processed image (when completed)",
    )
    error: Optional[str] = None
