"""Hair/skin segmentation using MediaPipe Selfie Segmentation."""

from __future__ import annotations

import numpy as np
from PIL import Image

from app.pipeline.interfaces import Segmenter

try:
    import mediapipe as mp
    _mp_available = True
except ImportError:  # pragma: no cover
    _mp_available = False


class MediaPipeSegmenter(Segmenter):
    """Segment the foreground subject using MediaPipe Selfie Segmentation."""

    def __init__(self, model_selection: int = 1) -> None:
        if not _mp_available:
            raise RuntimeError(
                "mediapipe is not installed. Run `pip install mediapipe`."
            )
        self._selfie_segmentation = mp.solutions.selfie_segmentation.SelfieSegmentation(
            model_selection=model_selection
        )

    def segment(self, image: Image.Image) -> Image.Image:
        """Return an L-mode mask image where 255 = foreground."""
        rgb = np.array(image.convert("RGB"))
        result = self._selfie_segmentation.process(rgb)
        mask_array = (result.segmentation_mask > 0.5).astype(np.uint8) * 255
        return Image.fromarray(mask_array, mode="L")
