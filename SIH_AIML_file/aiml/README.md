# H2S Dosimeter AIML

## Status

The image pipeline and API are ready for frontend/backend integration. A trained dose model is not included yet, so `/estimate-dose` currently returns strip classification with `dose_ppm_h: null` until `models/dose_model.joblib` is generated.

## Run locally

Create a fresh environment rather than sharing `.venv`:

```bash
cd aiml
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python -m uvicorn src.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Check it with:

```bash
curl http://127.0.0.1:8000/health
```

Set frontend origins as a comma-separated environment variable when the frontend runs on another origin:

```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173 python -m uvicorn src.main:app --reload
```

## API contract

Upload an image as multipart form data using the field name `file`:

```bash
curl -X POST -F "file=@path/to/strip.jpg" http://127.0.0.1:8000/analyze-strip
curl -X POST -F "file=@path/to/strip.jpg" http://127.0.0.1:8000/estimate-dose
```

`/analyze-strip` returns `h2s_status`, `h2s_level`, `safe`, brightness values, and `method`.

`/estimate-dose` always returns the stable fields `dose_ppm_h`, `confidence`, `image_quality`, `badge_status`, `h2s_status`, `h2s_level`, `safe`, `method`, and `model_available`. `dose_ppm_h` and `confidence` are `null` when no trained model is available.

## Train the dose model

Add labelled images and metadata, then build features and train from the project root:

```bash
python -m src.build_features --metadata dataset/metadata_template.csv --output dataset/processed/features.csv
python -m src.train --features dataset/processed/features.csv --model-out models/dose_model.joblib --metrics-out results/model_metrics.csv
```

The training code excludes capture metadata such as temperature and humidity from the image-only model schema, so the saved model matches API inference features.
