import io
import uuid
import base64
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from generator.captcha_gen import generate_captcha
from solver.predict import predict_bytes

app = FastAPI(title="CAPTCHA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# { captcha_id: expected_text }
_store: dict[str, str] = {}


class ValidateRequest(BaseModel):
    captcha_id: str
    answer: str


@app.get("/generate")
def generate():
    img, text, _ = generate_captcha()
    captcha_id = str(uuid.uuid4())
    _store[captcha_id] = text

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()

    return {"captcha_id": captcha_id, "image": img_b64}


@app.post("/validate")
def validate(req: ValidateRequest):
    expected = _store.pop(req.captcha_id, None)
    if expected is None:
        raise HTTPException(status_code=404, detail="CAPTCHA introuvable ou expiré")
    return {"valid": req.answer.upper() == expected, "expected": expected}


@app.post("/solve")
async def solve(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image")
    data = await file.read()
    try:
        text = predict_bytes(data)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Modèle non entraîné. Lancez d'abord : python run.py train",
        )
    return {"text": text}


@app.get("/", response_class=HTMLResponse)
def index():
    html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web", "index.html")
    with open(html_path, encoding="utf-8") as f:
        return f.read()
