"""Abstract interfaces for the ML pipeline stages."""

from __future__ import annotations

from abc import ABC, abstractmethod

from PIL import Image


class Segmenter(ABC):
    """Produce a binary mask that isolates the subject (e.g. face/hair)."""

    @abstractmethod
    def segment(self, image: Image.Image) -> Image.Image:
        """Return a greyscale mask image of the same size as *image*."""


class Generator(ABC):
    """Generate a colourised image given an input and mask."""

    @abstractmethod
    def generate(
        self,
        image: Image.Image,
        mask: Image.Image,
        prompt: str,
    ) -> Image.Image:
        """Return the colourised image."""


class Postprocessor(ABC):
    """Apply post-processing to the generated output."""

    @abstractmethod
    def process(self, original: Image.Image, generated: Image.Image) -> Image.Image:
        """Return the final blended/sharpened image."""
