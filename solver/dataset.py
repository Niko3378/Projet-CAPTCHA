import torch
from torch.utils.data import Dataset
from torchvision import transforms
from generator.captcha_gen import generate_captcha, crop_character
from solver.model import CHAR_TO_IDX

_transform = transforms.Compose([
    transforms.Grayscale(),
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
])


class CaptchaDataset(Dataset):
    """
    Génère N CAPTCHAs, découpe chaque caractère, stocke 5×N exemples en mémoire.
    Tâche : classification d'un seul caractère (36 classes).
    hard=True  : 100% CAPTCHAs difficiles (rotation, bruit dense)
    hard=False : 100% CAPTCHAs simples
    hard=None  : mix 50/50
    """

    def __init__(self, n_captchas: int = 4000, hard: bool | None = None):
        mode = "hard" if hard is True else ("easy" if hard is False else "50/50")
        print(f"Génération de {n_captchas} CAPTCHAs [{mode}] ({n_captchas * 5} crops)... ", end="", flush=True)
        self.imgs: list[torch.Tensor] = []
        self.labels: list[int] = []

        for i in range(n_captchas):
            if hard is None:
                use_hard = (i % 2 == 0)
            else:
                use_hard = hard
            img, text, positions = generate_captcha(hard=use_hard)
            for char, x in zip(text, positions):
                crop = crop_character(img, x)
                self.imgs.append(_transform(crop))
                self.labels.append(CHAR_TO_IDX[char])

        print("OK", flush=True)

    def __len__(self) -> int:
        return len(self.imgs)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.imgs[idx], torch.tensor(self.labels[idx], dtype=torch.long)
