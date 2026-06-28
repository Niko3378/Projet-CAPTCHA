import io
import uuid
import base64
import sys
import os
import time
import asyncio
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from generator.captcha_gen import generate_captcha
from generator.image_captcha_gen import generate_image_captcha, CIFAR_CLASSES_FR
from solver.predict import predict_bytes
from solver.image_predict import solve_image_captcha

app = FastAPI(title="CAPTCHA API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Stockage avec expiration ---
CAPTCHA_TTL = 120  # 2 minutes

# { captcha_id: (text, expires_at) }
_store: dict[str, tuple[str, float]] = {}


def _cleanup():
    now = time.time()
    expired = [k for k, (_, exp) in list(_store.items()) if now > exp]
    for k in expired:
        del _store[k]


# --- Rate limiting ---
RATE_WINDOW = 60   # fenêtre en secondes
RATE_MAX    = 30   # requêtes max par fenêtre par IP

_rate_data: dict[str, list[float]] = defaultdict(list)


def _check_rate(ip: str) -> bool:
    now = time.time()
    _rate_data[ip] = [t for t in _rate_data[ip] if now - t < RATE_WINDOW]
    if len(_rate_data[ip]) >= RATE_MAX:
        return False
    _rate_data[ip].append(now)
    return True


# --- Génération audio (pyttsx3, thread dédié) ---
_tts_executor = ThreadPoolExecutor(max_workers=1)


def _generate_wav(text: str) -> bytes:
    import pyttsx3, tempfile
    try:
        import pythoncom
        pythoncom.CoInitialize()
    except ImportError:
        pass

    engine = pyttsx3.init()
    engine.setProperty('rate', 110)
    engine.setProperty('volume', 1.0)
    spoken = ", ".join(list(text))

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        path = f.name

    engine.save_to_file(spoken, path)
    engine.runAndWait()
    engine.stop()

    with open(path, 'rb') as f:
        data = f.read()
    os.unlink(path)
    return data


# Image CAPTCHA store : { id: (class_fr, target_idx, correct, cell_bytes, expires_at) }
_image_store: dict[str, tuple[str, int, list[int], list[bytes], float]] = {}


def _cleanup_images():
    now = time.time()
    for k in [k for k, v in list(_image_store.items()) if now > v[4]]:
        del _image_store[k]


# --- Modèles Pydantic ---
class ValidateRequest(BaseModel):
    captcha_id: str
    answer: str


class ValidateImageRequest(BaseModel):
    captcha_id: str
    selected: list[int]


# --- Endpoints ---

@app.get("/generate")
def generate(request: Request):
    ip = request.client.host
    if not _check_rate(ip):
        raise HTTPException(status_code=429, detail="Trop de requêtes — réessayez dans une minute")

    _cleanup()
    img, text, _ = generate_captcha()
    captcha_id = str(uuid.uuid4())
    _store[captcha_id] = (text, time.time() + CAPTCHA_TTL)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()

    return {"captcha_id": captcha_id, "image": img_b64, "expires_in": CAPTCHA_TTL}


@app.post("/validate")
def validate(req: ValidateRequest, request: Request):
    ip = request.client.host
    if not _check_rate(ip):
        raise HTTPException(status_code=429, detail="Trop de requêtes")

    _cleanup()
    entry = _store.pop(req.captcha_id, None)
    if entry is None:
        raise HTTPException(status_code=404, detail="CAPTCHA introuvable ou expiré")

    text, expires_at = entry
    if time.time() > expires_at:
        raise HTTPException(status_code=410, detail="CAPTCHA expiré (3 minutes dépassées)")

    return {"valid": req.answer.upper() == text, "expected": text}


@app.get("/audio/{captcha_id}")
async def audio(captcha_id: str):
    _cleanup()
    entry = _store.get(captcha_id)
    if entry is None or time.time() > entry[1]:
        raise HTTPException(status_code=404, detail="CAPTCHA introuvable ou expiré")

    text = entry[0]
    loop = asyncio.get_event_loop()
    try:
        wav_data = await loop.run_in_executor(_tts_executor, _generate_wav, text)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Synthèse audio indisponible : {e}")

    return StreamingResponse(
        io.BytesIO(wav_data),
        media_type="audio/wav",
        headers={"Content-Disposition": "inline; filename=captcha.wav"},
    )


@app.post("/solve")
async def solve(request: Request, file: UploadFile = File(...)):
    ip = request.client.host
    if not _check_rate(ip):
        raise HTTPException(status_code=429, detail="Trop de requêtes")

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


@app.get("/generate-image")
def generate_image_endpoint(request: Request):
    ip = request.client.host
    if not _check_rate(ip):
        raise HTTPException(status_code=429, detail="Trop de requêtes")
    _cleanup_images()

    try:
        cell_bytes, target_idx, correct = generate_image_captcha()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Erreur génération image : {e}")

    captcha_id = str(uuid.uuid4())
    class_fr   = CIFAR_CLASSES_FR[target_idx]
    _image_store[captcha_id] = (class_fr, target_idx, correct, cell_bytes, time.time() + CAPTCHA_TTL)

    cells_b64 = [base64.b64encode(b).decode() for b in cell_bytes]
    return {
        "captcha_id": captcha_id,
        "cells": cells_b64,
        "question": f"Cliquez sur toutes les images contenant un(e) {class_fr}",
        "n_target": len(correct),
        "expires_in": CAPTCHA_TTL,
    }


@app.post("/validate-image")
def validate_image_endpoint(req: ValidateImageRequest, request: Request):
    ip = request.client.host
    if not _check_rate(ip):
        raise HTTPException(status_code=429, detail="Trop de requêtes")
    _cleanup_images()

    entry = _image_store.pop(req.captcha_id, None)
    if entry is None:
        raise HTTPException(status_code=404, detail="CAPTCHA introuvable ou expiré")

    class_fr, _, correct, _, expires_at = entry
    if time.time() > expires_at:
        raise HTTPException(status_code=410, detail="CAPTCHA expiré")

    valid = sorted(req.selected) == correct
    return {"valid": valid, "correct": correct, "selected": req.selected}


@app.get("/solve-image/{captcha_id}")
def solve_image_endpoint(captcha_id: str):
    entry = _image_store.get(captcha_id)
    if entry is None or time.time() > entry[4]:
        raise HTTPException(status_code=404, detail="CAPTCHA introuvable ou expiré")

    class_fr, target_idx, correct, cell_bytes, _ = entry
    try:
        predicted = solve_image_captcha(cell_bytes, target_idx)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Modèle image non entraîné. Lancez : python run.py train-image",
        )
    return {"predicted": predicted, "correct": correct}


@app.get("/", response_class=HTMLResponse)
def index():
    html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web", "index.html")
    with open(html_path, encoding="utf-8") as f:
        return f.read()
