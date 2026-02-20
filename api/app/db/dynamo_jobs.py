"""DynamoDB helpers for job state management (API service)."""

from __future__ import annotations

from typing import Any

import boto3
from botocore.client import BaseClient

from app.settings import settings


def get_dynamo_client() -> BaseClient:
    kwargs: dict = {"region_name": settings.aws_region}
    if settings.aws_endpoint_url:
        kwargs["endpoint_url"] = settings.aws_endpoint_url
    return boto3.client("dynamodb", **kwargs)


def put_job(job_id: str, status: str, input_key: str) -> None:
    """Create a new job record in DynamoDB."""
    client = get_dynamo_client()
    client.put_item(
        TableName=settings.dynamodb_jobs_table,
        Item={
            "job_id": {"S": job_id},
            "status": {"S": status},
            "input_key": {"S": input_key},
        },
    )


def get_job(job_id: str) -> dict[str, Any] | None:
    """Retrieve a job record by ID. Returns None when not found."""
    client = get_dynamo_client()
    response = client.get_item(
        TableName=settings.dynamodb_jobs_table,
        Key={"job_id": {"S": job_id}},
    )
    item = response.get("Item")
    if item is None:
        return None
    return {k: list(v.values())[0] for k, v in item.items()}
