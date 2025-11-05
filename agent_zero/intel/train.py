"""Training helper for the intel text classifier.

The dataset intentionally stays tiny so that a developer can quickly train the
model locally and persist the weights into ``models/classifier.keras``.  This is
sufficient for smoke tests while still exercising the TensorFlow/Keras
integration that the runtime path depends on.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Tuple

import numpy as np

from .models import build_text_classifier
from .predict import simple_tokenize

MODEL_PATH = Path(os.environ.get("INTEL_MODEL_PATH", "models/classifier.keras"))


def make_toy_dataset() -> Tuple[np.ndarray, np.ndarray]:
    """Return a minimal dataset for quick experiments and CI checks."""

    X = [
        "phishing indicators and email lures",
        "benign product release notes",
        "malware c2 ip and hashes observed",
        "sports news about local team",
        "credential stuffing advisory",
        "travel blog itinerary",
    ]
    y = [1, 0, 2, 0, 1, 0]  # 0=benign, 1=threat-advisory, 2=ioc-ish (example)

    tokenised = [simple_tokenize(text)[0] for text in X]
    X_tok = np.vstack(tokenised).astype("int32")
    y_arr = np.asarray(y, dtype="int32")
    return X_tok, y_arr


def main() -> None:
    model = build_text_classifier(num_classes=3)
    X, y = make_toy_dataset()
    model.fit(X, y, epochs=3, batch_size=2, verbose=2)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    model.save(MODEL_PATH.as_posix())
    print(f"Saved to {MODEL_PATH.as_posix()}")


if __name__ == "__main__":  # pragma: no cover - manual entry point
    main()
