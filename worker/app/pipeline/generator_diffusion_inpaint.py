"""Stable Diffusion inpainting-based colour generator."""

from __future__ import annotations

import torch
from PIL import Image

from app.pipeline.interfaces import Generator
from app.settings import settings

try:
    from diffusers import StableDiffusionInpaintPipeline
    _diffusers_available = True
except ImportError:  # pragma: no cover
    _diffusers_available = False


class DiffusionInpaintGenerator(Generator):
    """Use a Stable Diffusion inpainting model to colourise masked regions."""

    def __init__(self) -> None:
        if not _diffusers_available:
            raise RuntimeError(
                "diffusers is not installed. Run `pip install diffusers`."
            )
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self._pipe = StableDiffusionInpaintPipeline.from_pretrained(
            settings.inpaint_model_id,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        ).to(device)

    def generate(
        self,
        image: Image.Image,
        mask: Image.Image,
        prompt: str,
    ) -> Image.Image:
        """Run the inpainting pipeline and return the generated image."""
        result = self._pipe(
            prompt=prompt,
            image=image.convert("RGB"),
            mask_image=mask.convert("L"),
        )
        return result.images[0]
