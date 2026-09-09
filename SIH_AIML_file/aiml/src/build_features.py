from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
try:
    from .config import DEFAULT_CONFIG
    from .features import build_feature_row, extract_features
    from .image_pipeline import check_image_quality, load_image, normalize_badge
except ImportError:
    from config import DEFAULT_CONFIG
    from features import build_feature_row, extract_features
    from image_pipeline import check_image_quality, load_image, normalize_badge

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
def main() -> None:
    parser = argparse.ArgumentParser(description="Extract AIML features from badge images using metadata.csv.")
    parser.add_argument("--metadata", default="dataset/metadata_template.csv")
    parser.add_argument("--output", default="dataset/processed/features.csv")
    args = parser.parse_args()

    metadata = pd.read_csv(args.metadata)
    required = {"image_id", "dose_ppmh", "image_path"}
    missing = required - set(metadata.columns)
    if missing:
        raise ValueError(f"Missing metadata columns: {sorted(missing)}")

    rows = []
    skipped = []
    for _, item in metadata.iterrows():
        path = Path(str(item["image_path"]))
        if not path.exists() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            skipped.append((item["image_id"], "missing_or_unsupported_image"))
            continue
        try:
            image = load_image(path)
            quality = check_image_quality(image)
            if quality.status != "GOOD":
                skipped.append((item["image_id"], "bad_image_quality"))
                continue
            badge, _ = normalize_badge(image, DEFAULT_CONFIG)
            features = extract_features(badge, DEFAULT_CONFIG)
            row = build_feature_row(str(item["image_id"]), float(item["dose_ppmh"]), str(path), features)
            for column in metadata.columns:
                if column not in row:
                    row[column] = item[column]
            rows.append(row)
        except Exception as exc:  # keep one bad image from stopping the full batch
            skipped.append((item["image_id"], f"error:{type(exc).__name__}"))

    result = pd.DataFrame(rows)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    print(f"Wrote {len(result)} rows to {output}")
    if skipped:
        print(f"Skipped {len(skipped)} rows:")
        for image_id, reason in skipped:
            print(f"  {image_id}: {reason}")

if __name__ == "__main__":
    main()
