"""DynamoDB helpers for job state management (worker service)."""

from __future__ import annotations

import boto3
from botocore.client import BaseClient

from app.settings import settings


def get_dynamo_client() -> BaseClient:
    kwargs: dict = {"region_name": settings.aws_region}
    if settings.aws_endpoint_url:
        kwargs["endpoint_url"] = settings.aws_endpoint_url
    return boto3.client("dynamodb", **kwargs)


def update_job_status(
    job_id: str,
    status: str,
    output_key: str | None = None,
    error: str | None = None,
) -> None:
    """Update the status (and optionally output_key/error) for a job."""
    client = get_dynamo_client()

    update_expr_parts = ["#s = :status"]
    expr_names: dict = {"#s": "status"}
    expr_values: dict = {":status": {"S": status}}

    if output_key is not None:
        update_expr_parts.append("output_key = :output_key")
        expr_values[":output_key"] = {"S": output_key}

    if error is not None:
        update_expr_parts.append("#e = :error")
        expr_names["#e"] = "error"
        expr_values[":error"] = {"S": error}

    client.update_item(
        TableName=settings.dynamodb_jobs_table,
        Key={"job_id": {"S": job_id}},
        UpdateExpression="SET " + ", ".join(update_expr_parts),
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values,
    )
