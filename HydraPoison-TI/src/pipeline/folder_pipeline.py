# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from typing import Iterable
from tqdm import tqdm

from src.poison.text_poison import SrtPoisoner
from src.poison.image_poison import ImagePoisoner


class FolderPipeline:
    def __init__(self,
                 subs_in: str, subs_out: str,
                 imgs_in: str, imgs_out: str,
                 epsilon: float = 8/255.0,
                 target_class: int | None = None,
                 device: str = "cpu"):
        self.subs_in = Path(subs_in)
        self.subs_out = Path(subs_out)
        self.imgs_in = Path(imgs_in)
        self.imgs_out = Path(imgs_out)
        self.srt = SrtPoisoner()
        self.imgp = ImagePoisoner(epsilon=epsilon, target_class=target_class, device=device)

    @staticmethod
    def _iter_files(root: Path, exts: Iterable[str]):
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in exts:
                yield p

    def run_subtitles(self):
        self.subs_out.mkdir(parents=True, exist_ok=True)
        for p in tqdm(self._iter_files(self.subs_in, {".srt", ".vtt"}), desc="Subtitles"):
            rel = p.relative_to(self.subs_in)
            outp = self.subs_out / rel
            outp.parent.mkdir(parents=True, exist_ok=True)
            self.srt.poison_file(str(p), str(outp), add_canary=True)

    def run_images(self):
        self.imgs_out.mkdir(parents=True, exist_ok=True)
        for p in tqdm(self._iter_files(self.imgs_in, {".jpg", ".jpeg", ".png"}), desc="Images"):
            rel = p.relative_to(self.imgs_in)
            outp = self.imgs_out / rel.with_suffix(".jpg")
            self.imgp.poison_image(str(p), str(outp))

    def run_all(self):
        if self.subs_in.exists():
            self.run_subtitles()
        if self.imgs_in.exists():
            self.run_images()
