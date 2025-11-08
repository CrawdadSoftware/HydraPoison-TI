# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import datetime as dt

root = Path(__file__).resolve().parents[2]  # katalog projektu
subs_in = root / "data/input/subtitles"
imgs_in = root / "data/input/images"
subs_in.mkdir(parents=True, exist_ok=True)
imgs_in.mkdir(parents=True, exist_ok=True)

# 1) przykładowe SRT
srt = subs_in / "sample.srt"
srt.write_text(
    "1\n00:00:00,000 --> 00:00:02,000\nTo jest przykładowy napis testowy.\n\n"
    "2\n00:00:02,000 --> 00:00:04,000\nSprawdzamy odporność modeli NLP.\n\n"
    "3\n00:00:04,000 --> 00:00:06,500\nHydraPoison chroni treści twórców.\n",
    encoding="utf-8"
)

# 2) przykładowy obraz .jpg
img = Image.new("RGB", (640, 400), (242, 242, 242))
d = ImageDraw.Draw(img)
txt = "Sample Image\nHydraPoison"
d.multiline_text((40, 150), txt, fill=(20, 20, 20), spacing=6)
img.save(imgs_in / "sample.jpg", quality=95)

print("OK. Utworzone:")
print("-", srt)
print("-", imgs_in / "sample.jpg")
