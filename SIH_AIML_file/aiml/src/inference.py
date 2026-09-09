from __future__ import annotations
from pathlib import Path
import numpy as np
try:
    from .config import BadgeConfig, DEFAULT_CONFIG, MODEL_SCHEMA_VERSION
    from .image_pipeline import check_image_quality, load_image, normalize_badge
    from .features import extract_features
    from .model import load_model
except ImportError:
    from config import BadgeConfig, DEFAULT_CONFIG, MODEL_SCHEMA_VERSION
    from image_pipeline import check_image_quality, load_image, normalize_badge
    from features import extract_features
    from model import load_model
def _confidence_from_residuals(prediction: float, residual_std: float | None) -> float | None:
    """
    Heuristic confidence for MVP only; must be documented as non-calibrated.

    Uses the held-out test-set residual std (saved by train.py) relative
    to the predicted dose: a wide residual spread compared to the
    predicted value means the model was noisy for doses in this range,
    so confidence drops. This is NOT a statistically calibrated
    interval -- just a rough, explainable heuristic for the MVP demo.
    """
    if residual_std is None:
        return None
    scale = max(float(residual_std), 1e-6)
    score = float(np.exp(-scale / max(abs(prediction), 1e-6)))
    return float(np.clip(score, 0.0, 1.0))

def predict_dose(image_path: str | Path, model_path: str | Path, config: BadgeConfig | None = None) -> dict:
    config = config or DEFAULT_CONFIG
    image = load_image(image_path)
    quality = check_image_quality(image)
    if quality.status != "GOOD":
        return {
            "dose_ppm_h": None,
            "confidence": None,
            "image_quality": "BAD",
            "badge_status": "RETAKE_REQUIRED",
            "quality_details": quality.to_dict(),
        }
    badge, geometry = normalize_badge(image, config)
    features = extract_features(badge, config)
    model, feature_names, residual_std = load_model(model_path)
    if not feature_names:
        raise ValueError("Model artifact does not contain feature names.")
    x = np.asarray([[features.get(name, 0.0) for name in feature_names]], dtype=float)
    prediction = float(model.predict(x)[0])
    dose = max(0.0, prediction)
    confidence = _confidence_from_residuals(dose, residual_std)
    return {
        "dose_ppm_h": dose,
        "confidence": confidence,
        "image_quality": "GOOD",
        "badge_status": "VALID",
        "model_schema_version": MODEL_SCHEMA_VERSION,
        "geometry": geometry,
        "quality_details": quality.to_dict(),
        "confidence_note": (
            "Confidence is a heuristic derived from the model's held-out "
            "test residuals, not a statistically calibrated interval."
            if confidence is not None
            else "Confidence unavailable: model was saved without a residual_std (retrain with the current train.py)."
        ),
    }
