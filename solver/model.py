import torch
import torch.nn as nn

CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
NUM_CLASSES = len(CHARS)   # 36
CAPTCHA_LENGTH = 5
CHAR_TO_IDX = {c: i for i, c in enumerate(CHARS)}
IDX_TO_CHAR = {i: c for i, c in enumerate(CHARS)}

# Entrée : crop d'un seul caractère, redimensionné en 32x32 (grayscale)
# Tâche : classification 36 classes


class CharCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),  # 32x16x16
            nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2), # 64x8x8
            nn.Conv2d(64, 64, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2), # 64x4x4
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),           # 64*4*4 = 1024
            nn.Linear(1024, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, NUM_CLASSES),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))


# Alias pour la compatibilité avec l'ancien code
CaptchaCNN = CharCNN
