"""FastAPI service exposing OSINT classification helpers."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agent_zero.intel.predict import classify_text


class ClassificationRequest(BaseModel):
    text: str = Field(..., description="Free-form text to classify", min_length=1)


class ClassificationResponse(BaseModel):
    label: str
    confidence: float
    keywords: list[str]


app = FastAPI(title="Agent Zero Intel API")


@app.post("/classify/text", response_model=ClassificationResponse)
def classify_text_endpoint(payload: ClassificationRequest) -> ClassificationResponse:
    """Classify raw text and return the structured prediction."""

    try:
        result = classify_text(payload.text)
    except Exception as exc:  # pragma: no cover - FastAPI will log details
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ClassificationResponse(**result)


__all__ = ["app", "ClassificationRequest", "ClassificationResponse"]
