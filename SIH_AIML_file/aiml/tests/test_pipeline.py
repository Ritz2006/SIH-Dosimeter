import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config import BadgeConfig, ROI
from image_pipeline import check_image_quality, classify_h2s_strip, four_point_warp
from train import prepare_xy
def test_good_quality_image():
    # Textured synthetic image: useful edges but no clipped/very dark regions.
    rng = np.random.default_rng(7)
    image = rng.integers(60, 200, size=(300, 400, 3), dtype=np.uint8)
    image = image.astype(np.uint8)
    result = check_image_quality(image, blur_threshold=1.0)
    assert result.status == "GOOD"
def test_roi_validation():
    config = BadgeConfig(sensor_roi=ROI(0.1, 0.1, 0.5, 0.5))
    config.validate()
def test_perspective_warp_shape():
    image = np.zeros((100, 120, 3), dtype=np.uint8)
    corners = np.array([[10, 10], [110, 12], [108, 90], [12, 88]], dtype=np.float32)
    warped = four_point_warp(image, corners, (64, 48))
    assert warped.shape == (48, 64, 3)


def test_h2s_strip_classification_levels():
    config = BadgeConfig(sensor_roi=ROI(0.2, 0.2, 0.6, 0.5))

    safe_image = np.full((200, 300, 3), (200, 220, 180), dtype=np.uint8)
    safe_result = classify_h2s_strip(safe_image, config)
    assert safe_result["status"] == "SAFE"
    assert safe_result["level"] == "LOW"

    unsafe_image = np.full((200, 300, 3), (60, 60, 50), dtype=np.uint8)
    unsafe_result = classify_h2s_strip(unsafe_image, config)
    assert unsafe_result["status"] == "UNSAFE"
    assert unsafe_result["level"] in {"HIGH", "MODERATE"}


def test_training_excludes_metadata_not_available_at_inference():
    frame = pd.DataFrame(
        {
            "image_id": ["one", "two", "three", "four", "five"],
            "image_path": ["one.jpg", "two.jpg", "three.jpg", "four.jpg", "five.jpg"],
            "dose_ppmh": [1, 2, 3, 4, 5],
            "temperature": [20, 20, 21, 21, 22],
            "RH": [40, 45, 50, 55, 60],
            "sensor_mean": [10, 20, 30, 40, 50],
        }
    )
    features, _ = prepare_xy(frame)
    assert list(features.columns) == ["sensor_mean"]
