from __future__ import annotations
from typing import Dict, Iterable
import cv2
import numpy as np
from skimage.color import deltaE_ciede2000, rgb2lab
try:
    from .config import BadgeConfig
    from .image_pipeline import crop_normalized
except ImportError:
    from config import BadgeConfig
    from image_pipeline import crop_normalized
def _channel_stats(arr: np.ndarray, prefix: str) -> Dict[str, float]:
    flattened = arr.reshape(-1, arr.shape[-1]).astype(np.float32)
    result: Dict[str, float] = {}
    for index in range(flattened.shape[1]):
        values = flattened[:, index]
        result[f"{prefix}_{index}_mean"] = float(np.mean(values))
        result[f"{prefix}_{index}_std"] = float(np.std(values))
    return result

def _rgb_to_lab_cv(rgb_uint8: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(rgb_uint8, cv2.COLOR_RGB2LAB)

def extract_patch_rgb_lab(patch_bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    patch_rgb = cv2.cvtColor(patch_bgr, cv2.COLOR_BGR2RGB)
    patch_lab = rgb2lab(patch_rgb.astype(np.float32) / 255.0)
    return patch_rgb, patch_lab

def extract_features(badge_bgr: np.ndarray, config: BadgeConfig) -> Dict[str, float]:
    config.validate()
    sensor = crop_normalized(badge_bgr, config.sensor_roi)
    sensor_rgb = cv2.cvtColor(sensor, cv2.COLOR_BGR2RGB)
    sensor_hsv = cv2.cvtColor(sensor_rgb, cv2.COLOR_RGB2HSV)
    sensor_lab = rgb2lab(sensor_rgb.astype(np.float32) / 255.0)
    features: Dict[str, float] = {}
    features.update(_channel_stats(sensor_rgb, "rgb"))
    features.update(_channel_stats(sensor_hsv, "hsv"))
    features.update(_channel_stats(sensor_lab, "lab"))

    lab_flat = sensor_lab.reshape(-1, 3)
    for idx, name in enumerate(("L", "a", "b")):
        features[f"lab_{name}_mean"] = float(lab_flat[:, idx].mean())
        features[f"lab_{name}_std"] = float(lab_flat[:, idx].std())

    sensor_mean_rgb = sensor_rgb.reshape(-1, 3).mean(axis=0).astype(np.float32) / 255.0
    sensor_mean_lab = rgb2lab(sensor_mean_rgb.reshape(1, 1, 3)).reshape(3)
    for name, roi in config.reference_rois.items():
        ref = crop_normalized(badge_bgr, roi)
        ref_rgb, ref_lab = extract_patch_rgb_lab(ref)
        ref_mean_lab = ref_lab.reshape(-1, 3).mean(axis=0)
        distance = float(deltaE_ciede2000(sensor_mean_lab.reshape(1, 1, 3), ref_mean_lab.reshape(1, 1, 3))[0, 0])
        features[f"deltaE_sensor_to_{name}"] = distance
        features[f"ref_{name}_rgb_mean_r"] = float(ref_rgb[..., 0].mean())
        features[f"ref_{name}_rgb_mean_g"] = float(ref_rgb[..., 1].mean())
        features[f"ref_{name}_rgb_mean_b"] = float(ref_rgb[..., 2].mean())

    hsv = sensor_hsv.astype(np.float32)
    features["sensor_brightness_mean"] = float(hsv[..., 2].mean())
    return features

def build_feature_row(
    image_id: str,
    dose_ppmh: float | None,
    image_path: str,
    features: Dict[str, float],
) -> Dict[str, object]:
    row: Dict[str, object] = {"image_id": image_id, "image_path": image_path}
    if dose_ppmh is not None:
        row["dose_ppmh"] = float(dose_ppmh)
    row.update(features)
    return row
