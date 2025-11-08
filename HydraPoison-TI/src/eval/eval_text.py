# -*- coding: utf-8 -*-
import regex as re
import sys
from typing import Dict

ZWS = ["\u200b", "\u200c", "\u200d"]

def stats(path: str) -> Dict[str, int]:
    with open(path, "r", encoding="utf-8") as f:
        s = f.read()
    zero_w = sum(s.count(z) for z in ZWS)
    confus = len(re.findall(r"[\p{IsCyrillic}\p{IsGreek}]", s))
    return {"zero_width": zero_w, "confusables": confus, "length": len(s)}

if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(p, stats(p))
