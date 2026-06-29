import io
import torch
from PIL import Image
from torchvision import transforms
from solver.image_model import build_resnet18_cifar

_transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
])

_model  = None
_device = None


def load_image_model(path: str = 'models/image_model.pth') -> None:
    global _model, _device
    _device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    _model  = build_resnet18_cifar().to(_device)
    _model.load_state_dict(torch.load(path, map_location=_device, weights_only=True))
    _model.eval()
    print(f'Modele image charge depuis {path}')


def predict_cell(cell_bytes: bytes, model_path: str = 'models/image_model.pth') -> int:
    global _model
    if _model is None:
        load_image_model(model_path)
    img    = Image.open(io.BytesIO(cell_bytes)).convert('RGB')
    tensor = _transform(img).unsqueeze(0).to(_device)
    with torch.no_grad():
        return _model(tensor).argmax(1).item()


def solve_image_captcha(cell_bytes_list: list[bytes], target_class: int) -> list[int]:
    return [i for i, b in enumerate(cell_bytes_list) if predict_cell(b) == target_class]
