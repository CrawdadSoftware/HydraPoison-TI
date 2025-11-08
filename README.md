# HydraPoison-TI
Narzędzie do „zatruwania” danych w dwóch modalnościach: tekst (SRT/VTT) i obraz (JPG/PNG). Dla człowieka bez zmian, dla modeli AI gorsza tokenizacja/ekstrakcja i zmylenie ekstraktorów cech. Dodaje też „kanarki” do wykrywania nielegalnego użycia treści.

---

A dual-modality data poisoning toolkit for text (SRT/VTT) and images (JPG/PNG). Visually unchanged for humans, but degrades AI tokenization/feature extraction and embeds canary strings to detect unauthorized model training or scraping.

## Key features
- **Text poisoning (SRT/VTT):** Unicode confusables + zero-width characters + hidden **canaries**.
- **Image poisoning (JPG/PNG):** lightweight **FGSM** adversarial perturbation on ResNet50 + **LSB** watermark for tracking.
- **Batch pipeline:** process entire folders with a single CLI command.
- **Evaluation scripts:** quick stats for text and top-1 check for images.

How it works (short)

Text: confusable Unicode letters (e.g., Latin “a” vs Cyrillic “а”) and zero-width characters alter tokenization for LLMs without changing human perception. Hidden canary phrases help prove data misuse.

Image: single-step FGSM nudges pixels toward adversarial directions that confuse feature extractors while remaining imperceptible. Optional LSB watermark supports provenance checks.

## References / inspiration

Nightshade / Glaze (UChicago)
Unicode TR39 (confusables), zero-width characters
FGSM adversarial examples (Goodfellow et al.)
„Poisoned subtitles” demos, AI Labyrinth anti-scraping ideas

MIT License
Copyright (c) 2025 CrawdadSoftware

Permission is hereby granted, free of charge, to any person obtaining a copy
...


## Install
```bash
python -m venv .venv
# Windows
. .venv/Scripts/activate
# Linux/macOS
# source .venv/bin/activate
pip install -r requirements.txt

Run poisoning:
python -m src.cli.hydrapoison \
  --subs-in data/input/subtitles \
  --subs-out data/output/subtitles_poisoned \
  --imgs-in data/input/images \
  --imgs-out data/output/images_poisoned \
  --epsilon 0.03 \
  --device cpu

Evaluate:
# text stats
python -m src.eval.eval_text data/output/subtitles_poisoned/your.srt
# image top-1 before vs after
python -m src.eval.eval_image data/input/images/img.jpg
python -m src.eval.eval_image data/output/images_poisoned/img.jpg  
