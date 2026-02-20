"""Post-processing step: blend the generated image back onto the original."""

from __future__ import annotations

from PIL import Image, ImageFilter

from app.pipeline.interfaces import Postprocessor


class BlendPostprocessor(Postprocessor):
    """Composite the generated colours onto the original image and sharpen."""

    def __init__(self, sharpen: bool = True) -> None:
        self._sharpen = sharpen

    def process(self, original: Image.Image, generated: Image.Image) -> Image.Image:
        """
        Blend *generated* colours onto *original* structure.

        The luminance channel is taken from *original* and colour channels
        from *generated*, preserving fine detail.
        """
        orig_lab = original.convert("LAB")
        gen_lab = generated.convert("LAB")

        orig_l, _, _ = orig_lab.split()
        _, gen_a, gen_b = gen_lab.split()

        blended = Image.merge("LAB", (orig_l, gen_a, gen_b)).convert("RGB")

        if self._sharpen:
            blended = blended.filter(ImageFilter.SHARPEN)

        return blended
