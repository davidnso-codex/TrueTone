"""Worker application settings loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # AWS region
    aws_region: str = "us-east-1"

    # S3
    s3_bucket: str = "truetone-images"

    # DynamoDB
    dynamodb_jobs_table: str = "truetone-jobs"

    # SQS
    sqs_queue_url: str = ""
    sqs_wait_time_seconds: int = 20
    sqs_max_messages: int = 1

    # Optional LocalStack / custom endpoint for local dev
    aws_endpoint_url: str | None = None

    # Diffusion model identifier (HuggingFace hub or local path)
    inpaint_model_id: str = "runwayml/stable-diffusion-inpainting"


settings = Settings()
