from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
import numpy as np
from skimage.color import rgb2lab
from config import BadgeConfig
from image_pipeline import crop_normalized
@dataclass
class ColorCalibration:
    """Affine RGB calibration: corrected_rgb = observed_augmented @ matrix."""
    matrix: np.ndarray

    def transform(self, rgb: np.ndarray) -> np.ndarray:
        values = np.asarray(rgb, dtype=np.float64).reshape(-1, 3)
        aug = np.concatenate([values, np.ones((len(values), 1))], axis=1)
        corrected = aug @ self.matrix
        return np.clip(corrected, 0.0, 255.0).reshape(np.asarray(rgb).shape)

def fit_affine_calibration(
    observed_rgb: np.ndarray,
    target_rgb: np.ndarray,
    ridge: float = 1e-8,
) -> ColorCalibration:
    observed = np.asarray(observed_rgb, dtype=np.float64).reshape(-1, 3)
    target = np.asarray(target_rgb, dtype=np.float64).reshape(-1, 3)
    if observed.shape != target.shape or observed.shape[0] < 4:
        raise ValueError("Need matching observed/target RGB arrays with at least 4 patches.")

    x = np.concatenate([observed, np.ones((len(observed), 1))], axis=1)
    xtx = x.T @ x
    reg = ridge * np.eye(xtx.shape[0])
    matrix = np.linalg.solve(xtx + reg, x.T @ target)
    return ColorCalibration(matrix=matrix)
def collect_reference_observations(badge_bgr: np.ndarray, config: BadgeConfig) -> tuple[np.ndarray, np.ndarray, list[str]]:
    observed, targets, names = [], [], []
    for name, roi in config.reference_rois.items():
        crop = crop_normalized(badge_bgr, roi)
        rgb = crop[..., ::-1]
        observed.append(rgb.reshape(-1, 3).mean(axis=0))
        targets.append(np.asarray(config.reference_targets_rgb[name], dtype=float))
        names.append(name)
    return np.asarray(observed), np.asarray(targets), names

def calibrate_badge_rgb(badge_bgr: np.ndarray, config: BadgeConfig) -> tuple[np.ndarray, ColorCalibration]:
    observed, targets, _ = collect_reference_observations(badge_bgr, config)
    calibration = fit_affine_calibration(observed, targets)
    rgb = badge_bgr[..., ::-1]
    corrected_rgb = calibration.transform(rgb)
    corrected_bgr = corrected_rgb[..., ::-1].astype(np.uint8)
    return corrected_bgr, calibration
