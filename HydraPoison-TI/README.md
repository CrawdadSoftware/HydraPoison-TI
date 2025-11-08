# HydraPoison-TI
- Tekst: sobowtóry Unicode + znaki zerowej szerokości + ukryte kanarki w SRT/VTT.
- Obraz: jednoprzebiegowe FGSM na ResNet50 (perturbacja ~8/255) + niewidoczny znak LSB do śledzenia.

## Użycie
# przetworzenie całych katalogów
python -m src.cli.hydrapoison --subs-in data/input/subtitles --subs-out data/output/subtitles_poisoned --imgs-in data/input/images --imgs-out data/output/images_poisoned

# statystyki zatruć dla napisów
python -m src.eval.eval_text data/output/subtitles_poisoned/example.srt

# porównanie predykcji obrazu (top-1)
python -m src.eval.eval_image data/input/images/cat.jpg data/output/images_poisoned/cat.jpg
