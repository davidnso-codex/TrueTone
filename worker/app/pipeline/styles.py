"""Style definitions mapping style names to diffusion prompts."""

from __future__ import annotations

# Maps style slug -> text prompt fed to the inpainting model
STYLE_PROMPTS: dict[str, str] = {
    "natural": (
        "a photorealistic portrait with natural skin tones and realistic hair colour, "
        "high quality, soft lighting"
    ),
    "vivid": (
        "a vibrant portrait with bold, saturated colours, cinematic lighting, "
        "high quality"
    ),
    "vintage": (
        "a vintage film photograph portrait, warm tones, slight grain, "
        "Kodachrome colour palette"
    ),
    "cool": (
        "a portrait with cool blue-toned colour grading, soft shadows, "
        "high quality photography"
    ),
    "warm": (
        "a portrait with warm golden-hour colour grading, orange and yellow tones, "
        "high quality photography"
    ),
}

DEFAULT_STYLE = "natural"


def get_prompt(style: str) -> str:
    """Return the diffusion prompt for *style*, falling back to the default."""
    return STYLE_PROMPTS.get(style, STYLE_PROMPTS[DEFAULT_STYLE])
