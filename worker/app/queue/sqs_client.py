"""SQS helpers for consuming jobs (worker service)."""

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


def receive_messages() -> list[dict]:
    """Poll SQS and return a list of parsed message payloads with receipt handles."""
    client = get_sqs_client()
    response = client.receive_message(
        QueueUrl=settings.sqs_queue_url,
        MaxNumberOfMessages=settings.sqs_max_messages,
        WaitTimeSeconds=settings.sqs_wait_time_seconds,
        AttributeNames=["All"],
    )
    messages = []
    for msg in response.get("Messages", []):
        messages.append(
            {
                "receipt_handle": msg["ReceiptHandle"],
                "body": json.loads(msg["Body"]),
            }
        )
    return messages


def delete_message(receipt_handle: str) -> None:
    """Remove a successfully processed message from the queue."""
    client = get_sqs_client()
    client.delete_message(
        QueueUrl=settings.sqs_queue_url,
        ReceiptHandle=receipt_handle,
    )
