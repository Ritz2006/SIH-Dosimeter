from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple
import numpy as np

MODEL_SCHEMA_VERSION = "1"

@dataclass(frozen=True)
class ROI:
    """Rectangle in normalized image coordinates: x, y, width, height in [0, 1]."""
    x: float
    y: float
    width: float
    height: float

    def validate(self) -> None:
        values = (self.x, self.y, self.width, self.height)
        if not all(0.0 <= v <= 1.0 for v in values):
            raise ValueError("ROI values must be between 0 and 1.")
        if self.width <= 0 or self.height <= 0 or self.x + self.width > 1 or self.y + self.height > 1:
            raise ValueError("ROI must be positive and fit inside the normalized image.")

@dataclass
class BadgeConfig:
    canonical_size: Tuple[int, int] = (1200, 800)  # width, height
    sensor_roi: ROI = field(default_factory=lambda: ROI(0.35, 0.30, 0.30, 0.40))
    reference_rois: Dict[str, ROI] = field(default_factory=dict)
    reference_targets_rgb: Dict[str, Tuple[float, float, float]] = field(default_factory=dict)

    def validate(self) -> None:
        self.sensor_roi.validate()
        if set(self.reference_rois) != set(self.reference_targets_rgb):
            raise ValueError("reference_rois and reference_targets_rgb must have identical keys.")
        for roi in self.reference_rois.values():
            roi.validate()
        for name, rgb in self.reference_targets_rgb.items():
            arr = np.asarray(rgb, dtype=float)
            if arr.shape != (3,) or np.any(arr < 0) or np.any(arr > 255):
                raise ValueError(f"Reference target '{name}' must be an RGB triple in [0, 255].")
DEFAULT_CONFIG = BadgeConfig()
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_RAW = PROJECT_ROOT / "dataset" / "raw"
DATASET_PROCESSED = PROJECT_ROOT / "dataset" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "results"
