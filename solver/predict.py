import io
import torch
from PIL import Image
from torchvision import transforms
from generator.captcha_gen import (
    CAPTCHA_LENGTH, CHAR_W, IMG_WIDTH,
    crop_character,
)
from solver.model import CharCNN, IDX_TO_CHAR

_transform = transforms.Compose([
    transforms.Grayscale(),
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
])

_model: CharCNN | None = None
_device: torch.device | None = None

# Positions x estimées des caractères dans l'image 200x60
_CHAR_X = [8 + i * CHAR_W for i in range(CAPTCHA_LENGTH)]


def load_model(path: str = "models/captcha_model_universal.pth") -> None:
    global _model, _device
    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _model = CharCNN().to(_device)
    _model.load_state_dict(torch.load(path, map_location=_device, weights_only=True))
    _model.eval()
    print(f"Modèle chargé depuis {path}")


def predict(image: Image.Image, model_path: str = "models/captcha_model_universal.pth") -> str:
    global _model
    if _model is None:
        load_model(model_path)

    chars = []
    for x in _CHAR_X:
        crop   = crop_character(image, x)
        tensor = _transform(crop).unsqueeze(0).to(_device)
        with torch.no_grad():
            idx = _model(tensor).argmax(1).item()
        chars.append(IDX_TO_CHAR[idx])
    return ''.join(chars)


def predict_bytes(data: bytes, model_path: str = "models/captcha_model_universal.pth") -> str:
    return predict(Image.open(io.BytesIO(data)), model_path)
