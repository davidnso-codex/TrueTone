"""FastAPI application entry-point."""

from fastapi import FastAPI

from app.routes import jobs, uploads

app = FastAPI(
    title="TrueTone API",
    description="Submit greyscale images for AI-driven colourisation.",
    version="0.1.0",
)

app.include_router(uploads.router)
app.include_router(jobs.router)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
