from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple
import cv2
import numpy as np
try:
    from .config import BadgeConfig, ROI
except ImportError:
    from config import BadgeConfig, ROI

H2S_LEVEL_THRESHOLDS = {
    "LOW": 185.0,
    "MODERATE": 120.0,
    "DARK": 75.0,
}
@dataclass
class ImageQualityResult:
    status: str
    blur_score: float
    brightness_mean: float
    brightness_std: float
    overexposed_fraction: float
    underexposed_fraction: float
    reasons: list[str]

    def to_dict(self) -> dict:
        return {
            "image_quality": self.status,
            "blur_score": round(float(self.blur_score), 3),
            "brightness_mean": round(float(self.brightness_mean), 3),
            "brightness_std": round(float(self.brightness_std), 3),
            "overexposed_fraction": round(float(self.overexposed_fraction), 5),
            "underexposed_fraction": round(float(self.underexposed_fraction), 5),
            "reasons": self.reasons,
        }

def load_image(image_path: str | Path) -> np.ndarray:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Could not decode image: {path}")
    return image

def check_image_quality(
    image_bgr: np.ndarray,
    blur_threshold: float = 80.0,
    brightness_low: float = 35.0,
    brightness_high: float = 225.0,
    clipped_fraction_threshold: float = 0.08,
) -> ImageQualityResult:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    value = hsv[:, :, 2].astype(np.float32)
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness_mean = float(value.mean())
    brightness_std = float(value.std())
    overexposed_fraction = float(np.mean(value >= 250.0))
    underexposed_fraction = float(np.mean(value <= 5.0))
    reasons: list[str] = []
    if blur_score < blur_threshold:
        reasons.append(f"blur_score<{blur_threshold}")
    if brightness_mean < brightness_low:
        reasons.append(f"brightness<{brightness_low}")
    if brightness_mean > brightness_high:
        reasons.append(f"brightness>{brightness_high}")
    if overexposed_fraction > clipped_fraction_threshold:
        reasons.append("too_many_overexposed_pixels")
    if underexposed_fraction > clipped_fraction_threshold:
        reasons.append("too_many_underexposed_pixels")

    status = "GOOD" if not reasons else "BAD"
    return ImageQualityResult(
        status=status,
        blur_score=blur_score,
        brightness_mean=brightness_mean,
        brightness_std=brightness_std,
        overexposed_fraction=overexposed_fraction,
        underexposed_fraction=underexposed_fraction,
        reasons=reasons,
    )
def crop_normalized(image_bgr: np.ndarray, roi: ROI) -> np.ndarray:
    roi.validate()
    height, width = image_bgr.shape[:2]
    x1 = int(round(roi.x * width))
    y1 = int(round(roi.y * height))
    x2 = int(round((roi.x + roi.width) * width))
    y2 = int(round((roi.y + roi.height) * height))
    crop = image_bgr[y1:y2, x1:x2]
    if crop.size == 0:
        raise ValueError("ROI produced an empty crop.")
    return crop

def four_point_warp(
    image_bgr: np.ndarray,
    corners_xy: np.ndarray,
    output_size: Tuple[int, int],
) -> np.ndarray:
    """Perspective-warp four ordered corners into a canonical frame.

    corners order: top-left, top-right, bottom-right, bottom-left.
    """
    corners = np.asarray(corners_xy, dtype=np.float32)
    if corners.shape != (4, 2):
        raise ValueError("corners_xy must have shape (4, 2).")
    width, height = output_size
    dst = np.array(
        [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
        dtype=np.float32,
    )
    matrix = cv2.getPerspectiveTransform(corners, dst)
    return cv2.warpPerspective(image_bgr, matrix, (width, height))

def detect_qr_corners(image_bgr: np.ndarray) -> Optional[np.ndarray]:
    """Return QR corners when OpenCV's detector can identify one."""
    detector = cv2.QRCodeDetector()
    result = detector.detect(image_bgr)
    if not result:
        return None
    found, points = result
    if not found or points is None:
        return None
    points = np.asarray(points, dtype=np.float32).reshape(-1, 2)
    if points.shape != (4, 2):
        return None
    return points

def classify_h2s_strip(image_bgr: np.ndarray, config: BadgeConfig) -> Dict[str, object]:
    """Determine whether the H2S strip indicates a safe or unsafe level.

    For this passive strip, lighter colors indicate lower H2S exposure while darker
    colors indicate higher exposure. The threshold is tuned for a phone-camera shot
    taken under typical lighting, with a margin to avoid false "safe" reads from
    partially dark images.
    """
    config.validate()
    sensor = crop_normalized(image_bgr, config.sensor_roi)
    hsv = cv2.cvtColor(sensor, cv2.COLOR_BGR2HSV)
    value = hsv[:, :, 2].astype(np.float32)
    mean_value = float(value.mean())
    std_value = float(value.std())
    dark_fraction = float(np.mean(value <= H2S_LEVEL_THRESHOLDS["DARK"]))

    if mean_value >= H2S_LEVEL_THRESHOLDS["LOW"] and dark_fraction < 0.15:
        level = "LOW"
        status = "SAFE"
    elif mean_value >= H2S_LEVEL_THRESHOLDS["MODERATE"] and dark_fraction < 0.45:
        level = "MODERATE"
        status = "UNSAFE"
    else:
        level = "HIGH"
        status = "UNSAFE"

    return {
        "status": status,
        "level": level,
        "brightness_mean": round(mean_value, 3),
        "brightness_std": round(std_value, 3),
        "dark_fraction": round(dark_fraction, 3),
        "safe": status == "SAFE",
        "method": "h2s_sensor_roi",
    }


def normalize_badge(image_bgr: np.ndarray, config: BadgeConfig) -> Tuple[np.ndarray, Dict[str, object]]:
    """Normalize the badge without QR-code assumptions; keep the camera image framed for strip analysis."""
    config.validate()
    resized = cv2.resize(image_bgr, config.canonical_size, interpolation=cv2.INTER_AREA)
    return resized, {"method": "resize_only", "qr_detected": False, "strip_analysis": True}
