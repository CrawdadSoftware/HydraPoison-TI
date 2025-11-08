# -*- coding: utf-8 -*-
from __future__ import annotations

import secrets
import regex as re
from dataclasses import dataclass
from typing import List

# Proste sobowtóry Unicode (dla ludzi wyglądają tak samo, dla tokenizacji nie)
CONFUSABLES = {
    "a": "а",  # cyrylica U+0430
    "e": "е",  # cyrylica U+0435
    "o": "о",  # cyrylica U+043E
    "p": "р",  # cyrylica U+0440
    "c": "с",  # cyrylica U+0441
    "x": "х",  # cyrylica U+0445
    "A": "Α",  # grecka U+0391
    "E": "Ε",  # grecka U+0395
    "O": "Ο",  # grecka U+039F
    "H": "Н",  # cyrylica U+041D
    "K": "Κ",  # grecka U+039A
    "M": "Μ",  # grecka U+039C
    "T": "Τ",  # grecka U+03A4
}
ZWJ = "\u200d"
ZWNJ = "\u200c"
ZWSP = "\u200b"

WORD_RE = re.compile(r"(\p{L}[\p{L}\p{Mn}\p{Nd}]*)", re.UNICODE)


@dataclass
class UnicodeConfusables:
    confusable_rate: float = 0.35
    zw_rate: float = 0.25

    def _confusable_word(self, w: str) -> str:
        out = []
        for ch in w:
            if ch in CONFUSABLES and secrets.randbelow(100) < int(self.confusable_rate * 100):
                out.append(CONFUSABLES[ch])
            else:
                out.append(ch)
        return "".join(out)

    def _zero_width_inject(self, w: str) -> str:
        if len(w) < 2 or self.zw_rate <= 0:
            return w
        pieces = []
        for i, ch in enumerate(w):
            pieces.append(ch)
            if i < len(w) - 1 and secrets.randbelow(100) < int(self.zw_rate * 100):
                pieces.append(secrets.choice([ZWJ, ZWNJ, ZWSP]))
        return "".join(pieces)

    def poison_line(self, text: str) -> str:
        def repl(m):
            w = m.group(0)
            w2 = self._confusable_word(w)
            return self._zero_width_inject(w2)
        return WORD_RE.sub(repl, text)


class CanaryManager:
    """Tworzy ukryte „kanarki” do późniejszego wykrycia wycieku."""
    @staticmethod
    def make_canary(prefix: str = "zxqv-labyrinth") -> str:
        rand = secrets.token_hex(8)
        token = f"{prefix}-{rand}"
        hidden = ZWSP.join(list(token))  # ukrycie zerowej szerokości
        return hidden


class SrtPoisoner:
    """Modyfikuje wyłącznie linie tekstowe w SRT/VTT, zachowuje indeksy i timingi."""
    def __init__(self, conf: UnicodeConfusables | None = None):
        self.conf = conf or UnicodeConfusables()

    def _is_time_or_index(self, line: str) -> bool:
        if re.match(r"^\d+$", line.strip()):
            return True
        if re.match(r"^\d{2}:\d{2}:\d{2}", line.strip()):
            return True
        return False

    def poison_block(self, lines: List[str], add_canary: bool = True) -> List[str]:
        out = []
        injected = False
        canary = CanaryManager.make_canary() if add_canary else None
        for line in lines:
            if self._is_time_or_index(line) or not line.strip():
                out.append(line)
                continue
            pline = self.conf.poison_line(line)
            if add_canary and not injected:
                pline += " " + canary
                injected = True
            out.append(pline)
        return out

    def poison_file(self, in_path: str, out_path: str, add_canary: bool = True) -> None:
        with open(in_path, "r", encoding="utf-8") as f:
            data = f.read().splitlines()
        blocks, buf = [], []
        for ln in data + [""]:
            if ln.strip() == "":
                if buf:
                    blocks.append(buf)
                    buf = []
            else:
                buf.append(ln)
        result = []
        for b in blocks:
            result.extend(self.poison_block(b, add_canary))
            result.append("")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(result))
