"""User-facing prediction helpers for OSINT classifiers."""
from __future__ import annotations

import os
import threading
from typing import Dict, List

import numpy as np

from .models import SimpleTextClassifier, build_text_classifier
from .store import save_finding

DEFAULT_LABELS: Dict[int, str] = {
    0: "benign",
    1: "threat-advisory",
    2: "ioc-ish",
}
MODEL_PATH = os.environ.get("INTEL_MODEL_PATH", "models/classifier.keras")

_model = None
_model_lock = threading.Lock()


def _get_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                if os.path.exists(MODEL_PATH):
                    _model = SimpleTextClassifier.load(MODEL_PATH)
                else:
                    _model = build_text_classifier(num_classes=len(DEFAULT_LABELS))
    return _model


def simple_tokenize(text: str, seq_len: int = 256, vocab_size: int = 20_000) -> np.ndarray:
    ids = [ord(c) % vocab_size for c in text.lower() if c.isprintable()]
    ids = ids[:seq_len] + [0] * max(0, seq_len - len(ids))
    return np.array([ids], dtype="int32")


def classify_text(text: str, *, persist: bool = True) -> Dict[str, object]:
    x = simple_tokenize(text)
    model = _get_model()
    y = model.predict(x, verbose=0)
    probs: List[float] = y[0].astype("float64").tolist()
    label = int(y.argmax(axis=-1)[0])
    label_name = DEFAULT_LABELS.get(label, str(label))

    # Compute risk lazily to avoid import cycles at module load time.
    from .pipelines import osint as _osint_utils  # pylint: disable=import-outside-toplevel

    risk = _osint_utils.risk_score(label, probs)
    result: Dict[str, object] = {
        "label": label,
        "label_name": label_name,
        "probs": probs,
        "risk": risk,
    }

    if persist:
        save_finding({**result, "source_url": None})

    return result


__all__ = ["classify_text", "simple_tokenize", "DEFAULT_LABELS"]
