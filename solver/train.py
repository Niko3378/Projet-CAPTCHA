import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from solver.model import CharCNN
from solver.dataset import CaptchaDataset


def train(
    epochs: int = 30,
    batch_size: int = 128,
    lr: float = 1e-3,
    n_train: int = 4000,   # CAPTCHAs → 20 000 crops
    n_val: int = 800,      # CAPTCHAs → 4 000 crops
    save_path: str = "models/captcha_model_universal.pth",
    hard: bool | None = None,
) -> None:
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}", flush=True)

    train_ds = CaptchaDataset(n_train, hard=hard)
    val_ds   = CaptchaDataset(n_val,   hard=hard)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,  num_workers=0)
    val_loader   = DataLoader(val_ds,   batch_size=batch_size, shuffle=False, num_workers=0)

    model     = CharCNN().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=4)
    criterion = nn.CrossEntropyLoss()

    best_acc = 0.0

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            out  = model(imgs)
            loss = criterion(out, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        model.eval()
        correct = total = 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(device), labels.to(device)
                preds = model(imgs).argmax(1)
                correct += (preds == labels).sum().item()
                total   += labels.size(0)

        char_acc  = correct / total * 100
        avg_loss  = total_loss / len(train_loader)

        print(f"Epoch {epoch:2d}/{epochs} | Loss: {avg_loss:.3f} | Char acc: {char_acc:.1f}%", flush=True)
        scheduler.step(char_acc)

        if char_acc > best_acc:
            best_acc = char_acc
            torch.save(model.state_dict(), save_path)
            print(f"  -> Sauvegardé (meilleur: {best_acc:.1f}%)", flush=True)

    print(f"\nTerminé. Meilleure précision caractère: {best_acc:.1f}%", flush=True)


if __name__ == "__main__":
    train()
