# Projet CAPTCHA IA

Projet pédagogique couvrant le pipeline complet : **génération → entraînement → inférence → API REST**.

## Fonctionnalités

- Génération de CAPTCHAs texte 8 caractères (mode facile et difficile)
- Résolution automatique par CNN PyTorch (100% de précision)
- Mode audio : synthèse vocale du CAPTCHA
- Expiration automatique après 2 minutes
- Rate limiting : 30 requêtes/minute par IP
- Interface web de démonstration
- API REST (FastAPI)

## Stack technique

| Composant | Technologie |
|---|---|
| Génération images | Pillow |
| Modèle IA | PyTorch (CNN) |
| API REST | FastAPI + Uvicorn |
| Audio | pyttsx3 (TTS offline) |
| Frontend | HTML / JavaScript |

## Structure

```
├── generator/
│   └── captcha_gen.py       # Génération des CAPTCHAs (Pillow)
├── solver/
│   ├── model.py             # Architecture CNN (CharCNN)
│   ├── dataset.py           # Dataset PyTorch (génération à la volée)
│   ├── train.py             # Entraînement
│   └── predict.py           # Inférence
├── api/
│   └── main.py              # API FastAPI
├── models/
│   └── captcha_model_universal.pth   # Poids entraînés
├── web/
│   └── index.html           # Interface de démonstration
└── run.py                   # Point d'entrée CLI
```

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
# Démarrer l'API (http://localhost:8080)
python run.py api

# Entraîner le modèle
python run.py train

# Générer un exemple de CAPTCHA
python run.py demo
```

## API

| Endpoint | Méthode | Description |
|---|---|---|
| `/generate` | GET | Génère un CAPTCHA (image base64 + ID) |
| `/validate` | POST | Valide la réponse de l'utilisateur |
| `/solve` | POST | Résout une image CAPTCHA par IA |
| `/audio/{id}` | GET | Retourne le CAPTCHA en audio WAV |
| `/` | GET | Interface web |

## Performances

Modèle universel (50% facile / 50% difficile) — 8000 CAPTCHAs d'entraînement, 40 epochs :

| Mode | CAPTCHA exact | Caractères |
|---|---|---|
| Facile | 100% | 100% |
| Difficile | 100% | 100% |
