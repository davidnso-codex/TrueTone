"""Worker entry-point: polls SQS and processes colouring jobs."""

from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # worker/ on PYTHONPATH

from PIL import Image

from shared.logging import get_logger

from app.db.dynamo_jobs import update_job_status
from app.pipeline.generator_diffusion_inpaint import DiffusionInpaintGenerator
from app.pipeline.postprocess import BlendPostprocessor
from app.pipeline.segmenter_mediapipe import MediaPipeSegmenter
from app.pipeline.styles import get_prompt
from app.queue.sqs_client import delete_message, receive_messages
from app.settings import settings
from app.storage.s3_client import download_image, upload_image

logger = get_logger(__name__)


def process_job(
    job_id: str,
    input_key: str,
    style: str,
    segmenter: MediaPipeSegmenter,
    generator: DiffusionInpaintGenerator,
    postprocessor: BlendPostprocessor,
) -> None:
    """Download, run the ML pipeline, upload the result, update job state."""
    logger.info("Processing job %s (style=%s)", job_id, style)
    update_job_status(job_id, status="processing")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "input.jpg"
        output_path = tmp_path / "output.jpg"

        download_image(input_key, input_path)

        image = Image.open(input_path)

        mask = segmenter.segment(image)
        prompt = get_prompt(style)
        generated = generator.generate(image, mask, prompt)
        result = postprocessor.process(image, generated)

        result.save(str(output_path), format="JPEG")

        output_key = f"outputs/{job_id}.jpg"
        upload_image(output_path, output_key)

    update_job_status(job_id, status="completed", output_key=output_key)
    logger.info("Job %s completed – output at %s", job_id, output_key)


def run() -> None:
    """Main polling loop."""
    logger.info(
        "Worker started. Polling SQS queue: %s", settings.sqs_queue_url or "(not set)"
    )

    # Initialise ML pipeline components once at startup to avoid per-job overhead.
    segmenter = MediaPipeSegmenter()
    generator = DiffusionInpaintGenerator()
    postprocessor = BlendPostprocessor()

    while True:
        try:
            messages = receive_messages()
        except Exception:
            logger.exception("Error receiving messages from SQS – retrying in 5 s")
            time.sleep(5)
            continue

        for msg in messages:
            body = msg["body"]
            job_id = body.get("job_id", "unknown")
            try:
                process_job(
                    job_id=job_id,
                    input_key=body["input_key"],
                    style=body.get("style", "natural"),
                    segmenter=segmenter,
                    generator=generator,
                    postprocessor=postprocessor,
                )
                delete_message(msg["receipt_handle"])
            except Exception as exc:
                logger.exception("Failed to process job %s", job_id)
                update_job_status(job_id, status="failed", error=str(exc))


if __name__ == "__main__":
    run()
