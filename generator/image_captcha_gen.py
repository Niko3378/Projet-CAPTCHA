import io
import random
from PIL import Image
import torchvision.datasets as datasets

CIFAR_CLASSES_FR = [
    'avion', 'voiture', 'oiseau', 'chat', 'cerf',
    'chien', 'grenouille', 'cheval', 'bateau', 'camion',
]

GRID_SIZE = 3
CELL_PX   = 80

_dataset       = None
_class_indices = None


def _load():
    global _dataset, _class_indices
    if _dataset is not None:
        return
    print("Téléchargement CIFAR-10...", flush=True)
    _dataset = datasets.CIFAR10(root='data/', train=True, download=True)
    _class_indices = {}
    for i, (_, label) in enumerate(_dataset):
        _class_indices.setdefault(label, []).append(i)
    print("CIFAR-10 prêt.", flush=True)


def generate_image_captcha(n_target: int = 3) -> tuple[list[bytes], int, list[int]]:
    """
    Retourne (cell_png_bytes × 9, target_class_idx, correct_positions).
    correct_positions : indices de cellules (0-8) contenant la cible.
    """
    _load()
    target   = random.randint(0, 9)
    n_cells  = GRID_SIZE * GRID_SIZE
    n_other  = n_cells - n_target

    t_imgs = random.sample(_class_indices[target], n_target)
    others = [c for c in range(10) if c != target]
    o_imgs = [random.choice(_class_indices[random.choice(others)]) for _ in range(n_other)]

    positions = list(range(n_cells))
    random.shuffle(positions)
    correct = sorted(positions[:n_target])

    arrangement = {}
    for i, pos in enumerate(positions):
        arrangement[pos] = t_imgs[i] if i < n_target else o_imgs[i - n_target]

    cell_bytes = []
    for pos in range(n_cells):
        img, _ = _dataset[arrangement[pos]]
        img = img.resize((CELL_PX, CELL_PX), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        cell_bytes.append(buf.getvalue())

    return cell_bytes, target, correct
