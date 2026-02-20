"""S3 client helpers for the API service."""

from __future__ import annotations

import boto3
from botocore.client import BaseClient

from app.settings import settings


def get_s3_client() -> BaseClient:
    """Return a boto3 S3 client, optionally pointed at a local endpoint."""
    kwargs: dict = {"region_name": settings.aws_region}
    if settings.aws_endpoint_url:
        kwargs["endpoint_url"] = settings.aws_endpoint_url
    return boto3.client("s3", **kwargs)


def generate_presigned_upload_url(key: str, expires_in: int = 3600) -> str:
    """Generate a pre-signed PUT URL so clients can upload directly to S3."""
    client = get_s3_client()
    return client.generate_presigned_url(
        "put_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=expires_in,
        HttpMethod="PUT",
    )


def generate_presigned_download_url(key: str, expires_in: int = 3600) -> str:
    """Generate a pre-signed GET URL for downloading a processed image."""
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=expires_in,
    )
