# HydraPoison-TI
Narzędzie do „zatruwania” danych w dwóch modalnościach: tekst (SRT/VTT) i obraz (JPG/PNG). Dla człowieka bez zmian, dla modeli AI gorsza tokenizacja/ekstrakcja i zmylenie ekstraktorów cech. Dodaje też „kanarki” do wykrywania nielegalnego użycia treści.

A dual-modality data poisoning toolkit for text (SRT/VTT) and images (JPG/PNG). Visually unchanged for humans, but degrades AI tokenization/feature extraction and embeds canary strings to detect unauthorized model training or scraping.

## Key features
- **Text poisoning (SRT/VTT):** Unicode confusables + zero-width characters + hidden **canaries**.
- **Image poisoning (JPG/PNG):** lightweight **FGSM** adversarial perturbation on ResNet50 + **LSB** watermark for tracking.
- **Batch pipeline:** process entire folders with a single CLI command.
- **Evaluation scripts:** quick stats for text and top-1 check for images.

## Install
```bash
python -m venv .venv
# Windows
. .venv/Scripts/activate
# Linux/macOS
# source .venv/bin/activate
pip install -r requirements.txt
