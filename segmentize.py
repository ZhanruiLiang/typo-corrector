from __future__ import annotations

import re
from typing import Iterable

import pycantonese
from pycantonese import word_segmentation

class Segmenter(word_segmentation.Segmenter):
    def xpredict(self, sent_strs: Iterable[str]) -> Iterable[str]:
        # The base implementation uses threadpool which only adds overhead.
        return map(self._predict_sent, sent_strs)

_segmenter = Segmenter()


def segment_line(line: str) -> list[str]:
    words = []
    segments = re.split(r"\s+", line)
    for seg in segments:
        words += pycantonese.segment(seg, cls=_segmenter)
    return words

