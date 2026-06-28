# Manuel d'utilisation — Projet CAPTCHA IA

## Sommaire

1. [Installation](#1-installation)
2. [Démarrage de l'API](#2-démarrage-de-lapi)
3. [Interface web](#3-interface-web)
4. [API REST](#4-api-rest)
5. [Entraînement des modèles](#5-entraînement-des-modèles)
6. [Génération d'un exemple](#6-génération-dun-exemple)
7. [Fonctionnalités de sécurité](#7-fonctionnalités-de-sécurité)
8. [Dépannage](#8-dépannage)

---

## 1. Installation

### Prérequis

- Python 3.10 ou supérieur
- pip

### Installer les dépendances

```bash
pip install -r requirements.txt
```

Les bibliothèques installées sont :

| Bibliothèque | Rôle |
|---|---|
| Pillow | Génération des images CAPTCHA |
| PyTorch + torchvision | Modèle CNN de reconnaissance |
| FastAPI + Uvicorn | Serveur API REST |
| pyttsx3 | Synthèse vocale (mode audio) |
| python-multipart | Upload de fichiers |
| numpy | Calcul numérique |

---

## 2. Démarrage de l'API

```bash
python run.py api
```

Le serveur démarre sur **http://localhost:8080**.

Pour arrêter le serveur : `Ctrl + C`

---

## 3. Interface web

Ouvrez http://localhost:8080 dans votre navigateur.

### Carte gauche — Générer et valider

![Carte gauche](https://via.placeholder.com/400x200?text=Generer+un+CAPTCHA)

**Étape 1 — Générer un CAPTCHA**

Cliquez sur le bouton **Générer**. Un CAPTCHA de 8 caractères apparaît avec un compte à rebours de 2 minutes.

**Étape 2 — Écouter le CAPTCHA (optionnel)**

Cliquez sur **🔊 Audio** pour entendre les caractères lus à voix haute. Utile si l'image est difficile à lire.

**Étape 3a — Valider manuellement**

Tapez les 8 caractères dans le champ de saisie (lettres majuscules et chiffres), puis cliquez sur **Valider**.

- Message vert ✓ : réponse correcte
- Message rouge ✗ : réponse incorrecte, la réponse attendue est affichée
- Si le compteur atteint 0 : le CAPTCHA expire, générez-en un nouveau

**Étape 3b — Laisser l'IA résoudre**

Cliquez sur **Résoudre (IA)**. L'IA remplit automatiquement la réponse dans le champ de saisie. Cliquez ensuite sur **Valider** pour confirmer.

---

### Carte centrale — CAPTCHA image (CIFAR-10)

Cette carte propose un CAPTCHA visuel : une grille 3×3 d'images réelles issues de CIFAR-10 (avions, voitures, chiens, chats…).

**Étape 1 — Générer la grille**

Cliquez sur **Générer**. Une question s'affiche (ex: "Cliquez sur toutes les images contenant un chien") avec 9 images.

**Étape 2 — Sélectionner les cases**

Cliquez sur chaque image correspondant à la classe demandée. Les cases sélectionnées s'entourent d'un cadre violet.

**Étape 3 — Valider**

Cliquez sur **Valider**. Les cases correctes s'affichent en vert, les erreurs en rouge.

**Étape 4 (optionnel) — Résoudre avec l'IA**

Cliquez sur **Résoudre (IA)** pour laisser le modèle CNN identifier automatiquement les images correspondantes. Nécessite que `python run.py train-image` ait été exécuté au préalable.

---

### Carte droite — Résoudre une image externe

Cette section permet de tester le modèle IA sur n'importe quelle image CAPTCHA enregistrée sur votre ordinateur.

**Étape 1 — Charger une image**

Glissez-déposez une image PNG ou JPG dans la zone pointillée, ou cliquez dessus pour ouvrir l'explorateur de fichiers.

**Étape 2 — Analyser**

Cliquez sur **Analyser avec l'IA**. Le texte détecté s'affiche en grand.

---

## 4. API REST

### GET `/generate`

Génère un nouveau CAPTCHA.

**Réponse :**
```json
{
  "captcha_id": "uuid-de-identification",
  "image": "base64-de-limage-PNG",
  "expires_in": 120
}
```

**Exemple curl :**
```bash
curl http://localhost:8080/generate
```

---

### POST `/validate`

Valide la réponse de l'utilisateur.

**Corps de la requête :**
```json
{
  "captcha_id": "uuid-obtenu-via-generate",
  "answer": "AB12CD34"
}
```

**Réponse succès :**
```json
{
  "valid": true,
  "expected": "AB12CD34"
}
```

**Codes d'erreur :**
| Code | Signification |
|---|---|
| 404 | CAPTCHA introuvable ou déjà utilisé |
| 410 | CAPTCHA expiré (2 minutes dépassées) |
| 429 | Trop de requêtes (limite : 30/min) |

**Exemple curl :**
```bash
curl -X POST http://localhost:8080/validate \
     -H "Content-Type: application/json" \
     -d '{"captcha_id": "votre-id", "answer": "AB12CD34"}'
```

---

### GET `/audio/{captcha_id}`

Retourne le CAPTCHA en audio WAV (synthèse vocale).

**Exemple curl :**
```bash
curl http://localhost:8080/audio/votre-id -o captcha.wav
```

---

### GET `/generate-image`

Génère un CAPTCHA image (grille 3×3 de photos CIFAR-10).

**Réponse :**
```json
{
  "captcha_id": "uuid",
  "cells": ["base64-img-0", "...", "base64-img-8"],
  "question": "Cliquez sur toutes les images contenant un chien",
  "n_target": 3,
  "expires_in": 120
}
```

---

### POST `/validate-image`

Valide la sélection de l'utilisateur.

**Corps de la requête :**
```json
{
  "captcha_id": "uuid",
  "selected": [0, 3, 7]
}
```

**Réponse :**
```json
{
  "valid": true,
  "correct": [0, 3, 7],
  "selected": [0, 3, 7]
}
```

---

### GET `/solve-image/{captcha_id}`

Résout automatiquement le CAPTCHA image par IA.

**Réponse :**
```json
{
  "predicted": [0, 3, 7],
  "correct": [0, 3, 7]
}
```

Nécessite le modèle `models/image_model.pth` (lancez `python run.py train-image`).

---

### POST `/solve`

Résout une image CAPTCHA par IA.

**Corps :** fichier image (multipart/form-data)

**Réponse :**
```json
{
  "text": "AB12CD34"
}
```

**Exemple curl :**
```bash
curl -X POST http://localhost:8080/solve \
     -F "file=@mon_captcha.png"
```

---

## 5. Entraînement des modèles

### Modèle texte (CharCNN)

```bash
python run.py train
```

L'entraînement utilise par défaut :
- 8 000 CAPTCHAs d'entraînement (mix 50% facile / 50% difficile)
- 1 200 CAPTCHAs de validation
- 40 epochs
- Optimiseur Adam avec ReduceLROnPlateau

Le meilleur modèle est sauvegardé dans `models/captcha_model_universal.pth`.

### Personnaliser l'entraînement texte

Éditez `solver/train.py` pour ajuster les paramètres :

```python
train(
    epochs=40,
    batch_size=128,
    lr=1e-3,
    n_train=8000,
    n_val=1200,
    save_path="models/captcha_model_universal.pth",
    hard=None   # None = 50/50, True = difficile, False = facile
)
```

### Modèle image (ImageCNN — CIFAR-10)

```bash
python run.py train-image
```

- Télécharge automatiquement CIFAR-10 (~170 Mo) dans `data/` au premier lancement
- 50 epochs avec augmentation (flip, crop, ColorJitter)
- Scheduler CosineAnnealingLR
- Meilleur modèle sauvegardé dans `models/image_model.pth`

Sur CPU, comptez **1 à 3 heures**. Sur GPU (CUDA), moins de 10 minutes.

---

## 6. Génération d'un exemple

```bash
python run.py demo
```

Génère un CAPTCHA, l'enregistre sous `demo_captcha.png` et l'ouvre automatiquement.

---

## 7. Fonctionnalités de sécurité

### Expiration (2 minutes)

Chaque CAPTCHA est valable 2 minutes après sa génération. Passé ce délai, il est automatiquement supprimé côté serveur et tout tentative de validation retourne une erreur 410.

### Rate limiting

L'API limite chaque adresse IP à **30 requêtes par minute** sur tous les endpoints. Au-delà, une erreur 429 est retournée.

### Usage unique

Chaque CAPTCHA ne peut être validé qu'une seule fois. Une fois soumis (correct ou non), l'ID est supprimé du serveur.

---

## 8. Dépannage

**Le serveur ne démarre pas**
- Vérifiez que le port 8080 est libre : `netstat -ano | findstr :8080`
- Changez le port dans `run.py` si nécessaire

**Erreur "Modèle non trouvé"**
- Lancez d'abord `python run.py train` pour générer le fichier de poids

**Le mode audio ne fonctionne pas**
- Vérifiez que `pyttsx3` est installé : `pip install pyttsx3`
- Sur Windows, le moteur vocal SAPI5 doit être disponible (installé par défaut)

**Précision du modèle texte insuffisante**
- Ré-entraînez avec plus de données : augmentez `n_train` dans `train.py`
- Vérifiez que `CAPTCHA_LENGTH` dans `captcha_gen.py` correspond à celui utilisé lors de l'entraînement

**Erreur "Modèle image non trouvé"**
- Lancez `python run.py train-image` pour entraîner le modèle CIFAR-10
- Le téléchargement de CIFAR-10 (~170 Mo) est automatique au premier lancement

**Le CAPTCHA image ne génère pas de grille**
- Vérifiez que `torchvision` est installé : `pip install torchvision`
- Le dossier `data/` doit être accessible en écriture
