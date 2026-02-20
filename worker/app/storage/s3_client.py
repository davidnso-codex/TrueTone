"""S3 client helpers for the worker service."""

from __future__ import annotations

from pathlib import Path

import boto3
from botocore.client import BaseClient

from app.settings import settings


def get_s3_client() -> BaseClient:
    kwargs: dict = {"region_name": settings.aws_region}
    if settings.aws_endpoint_url:
        kwargs["endpoint_url"] = settings.aws_endpoint_url
    return boto3.client("s3", **kwargs)


def download_image(key: str, local_path: Path) -> None:
    """Download an S3 object to *local_path*."""
    client = get_s3_client()
    client.download_file(settings.s3_bucket, key, str(local_path))


def upload_image(local_path: Path, key: str) -> None:
    """Upload *local_path* to S3 under *key*."""
    client = get_s3_client()
    client.upload_file(str(local_path), settings.s3_bucket, key)
