# Projet CAPTCHA IA

Génération et résolution automatique de CAPTCHAs par intelligence artificielle — pipeline complet : **génération → entraînement → inférence → API REST**.

## Fonctionnalités

- **CAPTCHA texte** — images 8 caractères (lettres + chiffres, bruit, distorsion, mode facile/difficile)
- **CAPTCHA image** — grille 3×3 de photos CIFAR-10 à classer (avion, voiture, chien…)
- **Résolution IA texte** — CharCNN entraîné from scratch (~95% de précision)
- **Résolution IA image** — ResNet-18 préentraîné ImageNet, adapté CIFAR-10 (**95.0%** de précision)
- **Mode audio** — synthèse vocale des caractères (pyttsx3, offline)
- **API REST** — FastAPI avec rate limiting, expiration et usage unique
- **Interface web** — 3 cartes (texte, image, upload externe)

## Démarrage rapide

```bash
pip install -r requirements.txt
python run.py api
```

Ouvrez **http://localhost:8080** dans votre navigateur.

## Entraînement des modèles

```bash
# Modèle texte (CharCNN)
python run.py train

# Modèle image (ResNet-18 — télécharge CIFAR-10 ~170 Mo au premier lancement)
python run.py train-image

# Générer un exemple de CAPTCHA
python run.py demo
```

## API REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/generate` | Génère un CAPTCHA texte |
| POST | `/validate` | Valide la réponse utilisateur |
| GET | `/audio/{id}` | CAPTCHA en audio WAV |
| POST | `/solve` | Résout une image par IA |
| GET | `/generate-image` | Génère un CAPTCHA image (grille 3×3) |
| POST | `/validate-image` | Valide la sélection utilisateur |
| GET | `/solve-image/{id}` | Résout le CAPTCHA image par IA |
| GET | `/` | Interface web |

## Sécurité

- Expiration automatique après **2 minutes**
- **Usage unique** par CAPTCHA
- **Rate limiting** : 30 requêtes/minute par IP

## Performances

| Modèle | Architecture | Précision |
|--------|-------------|-----------|
| Texte | CharCNN (custom, from scratch) | ~95% |
| Image | ResNet-18 (ImageNet pretrained, 25 epochs) | **95.0%** |

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Génération images | Pillow |
| Modèle texte | PyTorch — CharCNN |
| Modèle image | PyTorch — ResNet-18 (torchvision) |
| Dataset image | CIFAR-10 |
| API REST | FastAPI + Uvicorn |
| Audio | pyttsx3 (TTS offline) |
| Frontend | HTML / CSS / JavaScript |

## Structure

```
├── api/
│   └── main.py                        # API FastAPI
├── generator/
│   ├── captcha_gen.py                 # Génération CAPTCHA texte (Pillow)
│   └── image_captcha_gen.py           # Génération CAPTCHA image (CIFAR-10)
├── solver/
│   ├── model.py                       # CharCNN (texte)
│   ├── image_model.py                 # ResNet-18 adapté CIFAR-10
│   ├── train.py                       # Entraînement texte
│   ├── image_train.py                 # Entraînement image
│   ├── predict.py                     # Inférence texte
│   └── image_predict.py               # Inférence image
├── models/
│   ├── captcha_model_universal.pth    # Poids modèle texte
│   └── image_model.pth                # Poids modèle image (ResNet-18)
├── web/
│   └── index.html                     # Interface de démonstration
├── run.py                             # Point d'entrée CLI
└── MANUEL.md                          # Documentation complète
```

## Prérequis

- Python 3.10+
- PyTorch + torchvision
- FastAPI + Uvicorn
- Pillow, pyttsx3, numpy
