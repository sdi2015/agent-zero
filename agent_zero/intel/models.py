"""Model builders for the Agent Zero intel classifiers."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass
class SimpleTextClassifier:
    """Tiny classifier that averages token vectors per class."""

    num_classes: int
    seq_len: int = 256
    vocab_size: int = 20_000
    class_embeddings: np.ndarray = field(init=False)
    class_counts: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        self.class_embeddings = np.zeros((self.num_classes, self.seq_len), dtype="float32")
        self.class_counts = np.zeros(self.num_classes, dtype="float32")

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 1, batch_size: int = 32, verbose: int = 0) -> None:
        # Simple averaging classifier; epochs/batch_size kept for API compatibility.
        del epochs, batch_size  # Unused but kept for signature parity.
        for row, label in zip(X, y, strict=False):
            self.class_embeddings[label] += row.astype("float32")
            self.class_counts[label] += 1

        counts = np.maximum(self.class_counts[:, None], 1.0)
        self.class_embeddings = self.class_embeddings / counts

        if verbose:
            print("Training complete using mean token vectors")

    def predict(self, X: np.ndarray, verbose: int = 0) -> np.ndarray:
        del verbose  # interface compatibility
        X = X.astype("float32")
        if not np.any(self.class_counts):
            return np.full((X.shape[0], self.num_classes), 1.0 / self.num_classes, dtype="float32")

        distances = []
        for row in X:
            diff = self.class_embeddings - row
            dist = np.linalg.norm(diff, axis=1)
            distances.append(dist)
        distances_arr = np.vstack(distances)
        logits = -distances_arr
        exp_logits = np.exp(logits - logits.max(axis=1, keepdims=True))
        probs = exp_logits / exp_logits.sum(axis=1, keepdims=True)
        return probs.astype("float32")

    def save(self, path: str) -> None:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("wb") as handle:
            np.savez(
                handle,
                num_classes=self.num_classes,
                seq_len=self.seq_len,
                vocab_size=self.vocab_size,
                class_embeddings=self.class_embeddings,
                class_counts=self.class_counts,
            )

    @classmethod
    def load(cls, path: str) -> "SimpleTextClassifier":
        with np.load(path) as data:
            model = cls(
                num_classes=int(data["num_classes"]),
                seq_len=int(data["seq_len"]),
                vocab_size=int(data["vocab_size"]),
            )
            model.class_embeddings = data["class_embeddings"].astype("float32")
            model.class_counts = data["class_counts"].astype("float32")
        return model


def build_text_classifier(num_classes: int = 3, *, seq_len: int = 256, vocab_size: int = 20_000) -> SimpleTextClassifier:
    return SimpleTextClassifier(num_classes=num_classes, seq_len=seq_len, vocab_size=vocab_size)


__all__ = ["build_text_classifier", "SimpleTextClassifier"]
