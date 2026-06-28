import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from solver.image_model import ImageCNN


def train_image(
    epochs: int = 50,
    save_path: str = 'models/image_model.pth',
) -> None:
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Device: {device}', flush=True)

    transform_train = transforms.Compose([
        transforms.RandomHorizontalFlip(),
        transforms.RandomCrop(32, padding=4),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])
    transform_val = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    train_ds = datasets.CIFAR10('data/', train=True,  download=True, transform=transform_train)
    val_ds   = datasets.CIFAR10('data/', train=False, download=True, transform=transform_val)

    train_loader = DataLoader(train_ds, batch_size=128, shuffle=True,  num_workers=0)
    val_loader   = DataLoader(val_ds,   batch_size=128, shuffle=False, num_workers=0)

    model     = ImageCNN().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion = nn.CrossEntropyLoss()

    best_acc = 0.0

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(imgs), labels)
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

        acc      = correct / total * 100
        avg_loss = total_loss / len(train_loader)
        print(f'Epoch {epoch:2d}/{epochs} | Loss: {avg_loss:.3f} | Acc: {acc:.1f}%', flush=True)
        scheduler.step()

        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), save_path)
            print(f'  -> Sauvegarde ({best_acc:.1f}%)', flush=True)

    print(f'\nTermine. Meilleure precision: {best_acc:.1f}%', flush=True)


if __name__ == '__main__':
    train_image()
