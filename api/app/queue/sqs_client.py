"""SQS helpers for enqueueing jobs (API service)."""

from __future__ import annotations

import json

import boto3
from botocore.client import BaseClient

from app.settings import settings


def get_sqs_client() -> BaseClient:
    kwargs: dict = {"region_name": settings.aws_region}
    if settings.aws_endpoint_url:
        kwargs["endpoint_url"] = settings.aws_endpoint_url
    return boto3.client("sqs", **kwargs)


def enqueue_job(job_id: str, input_key: str, style: str) -> None:
    """Send a job message to the SQS queue."""
    client = get_sqs_client()
    client.send_message(
        QueueUrl=settings.sqs_queue_url,
        MessageBody=json.dumps(
            {"job_id": job_id, "input_key": input_key, "style": style}
        ),
    )
