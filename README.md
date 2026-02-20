# TrueTone

AI-powered image colourisation service built with FastAPI, AWS, and Stable Diffusion.

## Architecture

```
┌─────────────┐      ┌─────────┐      ┌──────────────┐
│  API Service│─────▶│   SQS   │─────▶│   ML Worker  │
│  (FastAPI)  │      └─────────┘      │  (Diffusion) │
└──────┬──────┘                       └──────┬───────┘
       │  S3 pre-signed URLs                 │
       ▼                                     ▼
  ┌─────────┐                          ┌─────────┐
  │   S3    │◀─────────────────────────│   S3    │
  └─────────┘  download/upload images  └─────────┘
       │                                     │
       └──────────┬──────────────────────────┘
                  ▼
            ┌──────────┐
            │ DynamoDB │  (job state)
            └──────────┘
```

### Services

| Service | Description |
|---------|-------------|
| **API** | FastAPI service – accepts upload requests, issues pre-signed S3 URLs, polls job state |
| **Worker** | Long-running process – consumes SQS messages, runs MediaPipe + Stable Diffusion pipeline |

### AWS Resources

| Resource | Purpose |
|----------|---------|
| S3 | Input/output image storage |
| DynamoDB | Job state and result caching |
| SQS | Job queue between API and worker |

## Project Structure

```
truetone-backend/
├── api/
│   └── app/
│       ├── main.py           # FastAPI entry-point
│       ├── settings.py       # Environment-driven config
│       ├── routes/
│       │   ├── uploads.py    # POST /uploads
│       │   └── jobs.py       # GET /jobs/{job_id}
│       ├── storage/
│       │   └── s3_client.py  # Pre-signed URL helpers
│       ├── db/
│       │   └── dynamo_jobs.py
│       ├── queue/
│       │   └── sqs_client.py
│       └── schemas/
│           └── jobs.py
├── worker/
│   └── app/
│       ├── worker.py         # SQS polling loop
│       ├── settings.py
│       ├── storage/s3_client.py
│       ├── db/dynamo_jobs.py
│       ├── queue/sqs_client.py
│       └── pipeline/
│           ├── interfaces.py                    # ABCs
│           ├── segmenter_mediapipe.py           # Foreground mask
│           ├── generator_diffusion_inpaint.py   # SD inpainting
│           ├── postprocess.py                   # Blend & sharpen
│           └── styles.py                        # Style → prompt map
├── shared/
│   └── logging.py            # Shared logger factory
├── Dockerfile.api
├── Dockerfile.worker
├── pyproject.toml
└── .env.example
```

## Quick Start

### Prerequisites

- Python 3.11
- [Poetry](https://python-poetry.org/)
- AWS credentials (or [LocalStack](https://localstack.cloud/) for local dev)

### Installation

```bash
poetry install
```

### Configuration

```bash
cp .env.example .env
# Edit .env with your AWS credentials and resource names
```

### Run the API (development)

```bash
cd api
PYTHONPATH=.. uvicorn app.main:app --reload
```

### Run the Worker (development)

```bash
cd worker
PYTHONPATH=.. python -m app.worker
```

### Docker

```bash
# API
docker build -f Dockerfile.api -t truetone-api .
docker run --env-file .env -p 8000:8000 truetone-api

# Worker
docker build -f Dockerfile.worker -t truetone-worker .
docker run --env-file .env truetone-worker
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/uploads?style=natural` | Create a job and get a pre-signed upload URL |
| `GET`  | `/jobs/{job_id}` | Poll job status and get result URL when complete |
| `GET`  | `/health` | Health check |

## ML Pipeline

1. **Segmentation** – MediaPipe Selfie Segmentation isolates the subject
2. **Generation** – Stable Diffusion inpainting fills in colour guided by a style prompt
3. **Post-processing** – Luminance from original + colour from generated, optional sharpen

## Available Styles

| Style | Description |
|-------|-------------|
| `natural` | Photorealistic, natural skin and hair tones |
| `vivid` | Bold, saturated cinematic colours |
| `vintage` | Warm Kodachrome film look |
| `cool` | Blue-toned colour grading |
| `warm` | Golden-hour warm tones |
