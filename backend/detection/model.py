"""Model integration layer for hate speech detection.

This module loads the custom classifier placed under `backend/Classifier/` and
exposes a small, stable API to the rest of the app. It is resilient to
import/load errors and will fall back to None, allowing callers to degrade
gracefully.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Tuple
import contextlib

logger = logging.getLogger(__name__)

_DETECTOR = None  # type: ignore[var-annotated]


def _build_paths() -> dict:
    base_dir = Path(__file__).resolve().parents[1]  # backend/
    classifier_dir = base_dir / "Classifier"
    # Prefer words.json if present; fall back to hate_words.json
    words_json = classifier_dir / "words.json"
    hate_words_json = classifier_dir / "hate_words.json"
    json_path = words_json if words_json.exists() else hate_words_json
    return {
        "json_path": str(json_path) if json_path.exists() else None,
        "model_path": str(classifier_dir / "transformer_classifier_checkpoint_best_best.pth"),
        "tokenizer_path": str(classifier_dir / "tokenizer.json"),
    }


def _try_load_detector():
    global _DETECTOR
    if _DETECTOR is not None:
        return _DETECTOR
    try:
        # Import the user's detector
        # Patch spaCy load to gracefully fall back if the small model isn't installed
        try:
            import spacy as _spacy  # type: ignore
        except Exception:  # pragma: no cover
            _spacy = None  # type: ignore

        @contextlib.contextmanager
        def _patched_spacy_load():
            if _spacy is None:
                yield
                return
            original_load = getattr(_spacy, 'load', None)
            if original_load is None:
                yield
                return
            def safe_load(name, *args, **kwargs):
                try:
                    return original_load(name, *args, **kwargs)
                except Exception:
                    # Fallback to a blank English pipeline so detector can still run
                    return _spacy.blank('en')
            _spacy.load = safe_load  # type: ignore[attr-defined]
            try:
                yield
            finally:
                _spacy.load = original_load  # type: ignore[attr-defined]

        with _patched_spacy_load():
            from Classifier.preprocessor import HateSpeechDetector  # type: ignore

        paths = _build_paths()
        kwargs = {
            # Only pass json_path if available; the user's class may not accept None
            k: v for k, v in {
                "json_path": paths.get("json_path"),
                "model_path": paths["model_path"],
                "tokenizer_path": paths["tokenizer_path"],
            }.items() if v is not None
        }
        _DETECTOR = HateSpeechDetector(**kwargs)
        logger.info("HateSpeechDetector loaded successfully")
    except Exception as exc:  # pragma: no cover
        _DETECTOR = None
        logger.exception("Failed to load HateSpeechDetector: %s", exc)
    return _DETECTOR


def get_detector():
    return _try_load_detector()


def predict_with_model(text: str) -> Optional[Tuple[int, float, str]]:
    """Returns (hate_label, confidence, sentiment) or None if unavailable."""
    detector = get_detector()
    if detector is None:
        return None
    try:
        # The user's detector returns (hate_label, confidence, sentiment)
        return detector.predict(text)
    except Exception as exc:  # pragma: no cover
        logger.exception("Model prediction failed: %s", exc)
        return None


