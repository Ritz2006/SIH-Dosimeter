from __future__ import annotations
import os
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import tempfile
try:
  from .config import DEFAULT_CONFIG
  from .image_pipeline import classify_h2s_strip
  from .inference import predict_dose
except ImportError:
  from config import DEFAULT_CONFIG
  from image_pipeline import classify_h2s_strip
  from inference import predict_dose

app = FastAPI(title="H2S Dosimeter AIML Service", version="0.1.0")
MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "dose_model.joblib"
MAX_IMAGE_BYTES = int(os.getenv("MAX_IMAGE_BYTES", str(10 * 1024 * 1024)))
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin.strip()]
app.add_middleware(
  CORSMiddleware,
  allow_origins=CORS_ORIGINS or ["*"],
  allow_credentials=False,
  allow_methods=["GET", "POST", "OPTIONS"],
  allow_headers=["*"],
)

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_available": MODEL_PATH.exists()}

@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
    <html>
      <head><title>H2S Strip Camera</title></head>
      <body style="font-family: sans-serif; padding: 2rem;">
        <h2>H2S Strip Camera Check</h2>
        <video id="video" width="640" height="480" autoplay playsinline></video>
        <br/>
        <button id="capture">Capture photo</button>
        <canvas id="canvas" width="640" height="480" style="display:none"></canvas>
        <form id="uploadForm" method="post" action="/analyze-strip" enctype="multipart/form-data">
          <input id="imageInput" name="file" type="file" accept="image/*" capture="environment" />
          <button type="submit">Analyze image</button>
        </form>
        <script>
          const video = document.getElementById('video');
          const canvas = document.getElementById('canvas');
          const form = document.getElementById('uploadForm');
          const fileInput = document.getElementById('imageInput');
          navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false })
            .then((stream) => { video.srcObject = stream; })
            .catch((err) => { console.error('Camera access denied:', err); });
          document.getElementById('capture').onclick = () => {
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            canvas.toBlob((blob) => {
              const file = new File([blob], 'h2s-strip.jpg', { type: 'image/jpeg' });
              const dataTransfer = new DataTransfer();
              dataTransfer.items.add(file);
              fileInput.files = dataTransfer.files;
              form.requestSubmit();
            }, 'image/jpeg', 0.9);
          };
        </script>
      </body>
    </html>
    """


@app.post("/analyze-strip")
async def analyze_strip(file: UploadFile = File(...)) -> dict:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Upload an image file.")
    data = await file.read()
    if len(data) > MAX_IMAGE_BYTES:
      raise HTTPException(status_code=413, detail="Image file is too large.")
    image = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image data.")
    result = classify_h2s_strip(image, DEFAULT_CONFIG)
    return {
        "h2s_status": result["status"],
        "h2s_level": result["level"],
        "safe": result["safe"],
        "brightness_mean": result["brightness_mean"],
        "brightness_std": result["brightness_std"],
        "method": result["method"],
    }


@app.post("/estimate-dose")
async def estimate_dose(file: UploadFile = File(...)) -> dict:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Upload an image file.")
    data = await file.read()
    if len(data) > MAX_IMAGE_BYTES:
      raise HTTPException(status_code=413, detail="Image file is too large.")
    image = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image data.")

    if not MODEL_PATH.exists():
        result = classify_h2s_strip(image, DEFAULT_CONFIG)
        return {
            "dose_ppm_h": None,
            "confidence": None,
            "image_quality": "GOOD",
            "badge_status": result["status"],
          "h2s_status": result["status"],
            "h2s_level": result["level"],
            "safe": result["safe"],
            "method": result["method"],
          "model_available": False,
            "note": "No trained model is available yet; classification is based on the H2S strip color in the captured image.",
        }

    with tempfile.NamedTemporaryFile(suffix=Path(file.filename or "badge.jpg").suffix, delete=False) as temp:
        temp.write(data)
        temp_path = temp.name
    try:
      prediction = predict_dose(temp_path, MODEL_PATH)
      classification = classify_h2s_strip(image, DEFAULT_CONFIG)
      return {
        **prediction,
        "h2s_status": classification["status"],
        "h2s_level": classification["level"],
        "safe": classification["safe"],
        "method": classification["method"],
        "model_available": True,
      }
    finally:
        Path(temp_path).unlink(missing_ok=True)
