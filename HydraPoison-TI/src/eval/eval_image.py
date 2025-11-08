# -*- coding: utf-8 -*-
import sys
from PIL import Image
import torch
from torchvision import models, transforms as T

def predict_top1(img_path: str) -> int:
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
    model.eval()
    tfm = T.Compose([
        T.Resize(256),
        T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
    ])
    x = tfm(Image.open(img_path).convert("RGB")).unsqueeze(0)
    with torch.no_grad():
        logits = model(x)
    return int(logits.argmax(dim=1).item())

if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(p, predict_top1(p))
