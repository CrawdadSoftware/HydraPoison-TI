# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional, Tuple
from pathlib import Path

import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F
import torchvision.transforms as T
from torchvision import models
from tqdm import tqdm


def _to_tensor(img: Image.Image) -> torch.Tensor:
    tfm = T.Compose([
        T.Resize(256, interpolation=T.InterpolationMode.BICUBIC),
        T.CenterCrop(224),
        T.ToTensor()
    ])
    return tfm(img).unsqueeze(0)  # [1,3,224,224]


def _from_tensor(t: torch.Tensor, src_size: Tuple[int, int]) -> Image.Image:
    t = t.detach().clamp(0, 1).squeeze(0)
    img = T.ToPILImage()(t)
    return img.resize(src_size, Image.BICUBIC)


@dataclass
class FGSMAdversary:
    epsilon: float = 8 / 255.0  # L_inf
    target_class: Optional[int] = None  # 0..999 lub None
    device: str = "cpu"

    def __post_init__(self):
        self.model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2).to(self.device)
        self.model.eval()
        self.norm = T.Normalize(mean=[0.485, 0.456, 0.406],
                                std=[0.229, 0.224, 0.225])

    def generate(self, img: Image.Image) -> Image.Image:
        orig_size = img.size
        x = _to_tensor(img).to(self.device)                     # [1,3,224,224]
        x_norm = self.norm(x.clone())
        x_norm.requires_grad_(True)

        logits = self.model(x_norm)

        if self.target_class is not None:
            y = torch.tensor([self.target_class], dtype=torch.long, device=self.device)
            loss = F.cross_entropy(logits, y)
        else:
            # untargeted: zwiększamy stratę dla klasy oryginalnej
            y = logits.argmax(dim=1)
            loss = -F.cross_entropy(logits, y)

        loss.backward()
        grad_sign = x_norm.grad.detach().sign()
        # Odnormowanie gradientu do przestrzeni pikseli
        inv_std = torch.tensor([0.229, 0.224, 0.225], device=self.device).view(1,3,1,1)
        grad_px = grad_sign / inv_std

        x_adv = x + self.epsilon * grad_px
        x_adv = x_adv.clamp(0, 1)

        return _from_tensor(x_adv.cpu(), orig_size)


class LSBWatermarker:
    """Prosty znak wodny LSB dla śledzenia obrazu. Wstawia 64-bit UUID w kanał L na drobnym podpróbkowaniu."""
    @staticmethod
    def _uuid_bits() -> np.ndarray:
        import secrets
        u = secrets.token_bytes(8)  # 64 bity
        bits = np.unpackbits(np.frombuffer(u, dtype=np.uint8))
        return bits

    @staticmethod
    def embed(image: Image.Image) -> Image.Image:
        img = image.convert("RGB")
        w, h = img.size
        arr = np.array(img, dtype=np.uint8)

        # pracujemy w przestrzeni luma jak w Y' (proste przybliżenie)
        L = (0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]).astype(np.uint8)

        bits = LSBWatermarker._uuid_bits()
        step_x = max(1, w // bits.size)
        step_y = max(1, h // 8)

        idx = 0
        for by in range(0, h, step_y):
            for bx in range(0, w, step_x):
                if idx >= bits.size:
                    break
                # podmień LSB w czerwonym kanale, minimalna ingerencja
                arr[by, bx, 0] = (arr[by, bx, 0] & 0xFE) | int(bits[idx])
                idx += 1
            if idx >= bits.size:
                break

        return Image.fromarray(arr, mode="RGB")


@dataclass
class ImagePoisoner:
    epsilon: float = 8/255.0
    target_class: Optional[int] = None
    device: str = "cpu"
    embed_watermark: bool = True

    def __post_init__(self):
        self.adv = FGSMAdversary(self.epsilon, self.target_class, self.device)

    def poison_image(self, in_path: str, out_path: str) -> None:
        img = Image.open(in_path).convert("RGB")
        adv = self.adv.generate(img)
        if self.embed_watermark:
            adv = LSBWatermarker.embed(adv)
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        adv.save(out_path, quality=95)
