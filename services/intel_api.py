"""FastAPI service exposing OSINT classification helpers."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import AnyHttpUrl, BaseModel, Field

from agent_zero.intel.predict import classify_text
from agent_zero.intel.pipelines.osint import classify_url
from agent_zero.intel.store import list_findings


class TextClassificationRequest(BaseModel):
    text: str = Field(..., description="Free-form text to classify", min_length=1)
    user: str | None = Field(None, description="User requesting the classification")
    justification: str | None = Field(None, description="Why the classification is needed")


class URLClassificationRequest(BaseModel):
    url: AnyHttpUrl = Field(..., description="URL to fetch and classify")
    user: str | None = Field(None, description="User requesting the fetch")
    justification: str | None = Field(None, description="Why fetching the URL is justified")


class ClassificationResponse(BaseModel):
    label: int
    label_name: str
    probs: list[float]
    risk: float
    iocs: dict[str, list[str]] | None = Field(None, description="Extracted indicators of compromise")
    source_url: str | None = Field(None, description="Original URL if applicable")


class FindingResponse(ClassificationResponse):
    id: int
    ts: int


app = FastAPI(title="Agent Zero Intel API")


def _http_error(exc: Exception) -> HTTPException:
    status = 500
    if isinstance(exc, PermissionError):
        status = 403
    elif isinstance(exc, ValueError):
        status = 400
    elif isinstance(exc, RuntimeError):
        status = 429
    return HTTPException(status_code=status, detail=str(exc))


@app.post("/classify/text", response_model=ClassificationResponse)
def classify_text_endpoint(payload: TextClassificationRequest) -> ClassificationResponse:
    try:
        result = classify_text(payload.text)
    except Exception as exc:  # pragma: no cover - FastAPI will log details
        raise _http_error(exc) from exc

    return ClassificationResponse(**result)


@app.post("/classify/url", response_model=ClassificationResponse)
def classify_url_endpoint(payload: URLClassificationRequest) -> ClassificationResponse:
    try:
        result = classify_url(payload.url, user=payload.user, justification=payload.justification)
    except Exception as exc:  # pragma: no cover - FastAPI will log details
        raise _http_error(exc) from exc

    return ClassificationResponse(**result)


@app.get("/findings", response_model=list[FindingResponse])
def list_findings_endpoint(limit: int = 50) -> list[FindingResponse]:
    try:
        rows = list_findings(limit=limit)
    except Exception as exc:  # pragma: no cover - FastAPI will log details
        raise _http_error(exc) from exc

    return [FindingResponse(**row) for row in rows]


__all__ = [
    "app",
    "TextClassificationRequest",
    "URLClassificationRequest",
    "ClassificationResponse",
    "FindingResponse",
]
