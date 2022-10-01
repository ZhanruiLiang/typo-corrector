import functools
import re
from typing import Callable

import pycantonese

class Context:
    pos_list: list[tuple[str, str]]
    i: int
    word: str
    pos: str
    next_word: str = ""
    next_pos: str = ""
    prev_word: str = ""
    prev_pos: str = ""

    @property
    def suffix(self):
        """Suffix starting from current index."""
        return ''.join(x[0] for x in self.pos_list[self.i:])

    def replace_word(self, word: str):
        self.pos_list[self.i] = word, self.pos_list[self.i][1]


class Pos:
    NONE = ""
    NOUN = "NOUN"
    VERB = "VERB"
    PRON = "PRON"
    ADJ = "ADJ"
    ADV = "ADV"
    X = "X"


_handlers: dict[str, Callable[[Context], None]] = {}


def contextual_rule(word: str):
    """Decorator for registering a contextual typo correction rule."""

    def deco(f):
        _handlers[word] = f
        return f
    return deco


@contextual_rule("左")
def _(c: Context):
    """左 -> 咗: 如果 左 字前面係一個動詞，噉就改成 咗."""
    if c.prev_pos == Pos.VERB:
        c.replace_word("咗")

@contextual_rule("黎")
def _(c: Context):
    """黎 -> 嚟: 如果 黎 字係動詞，就改成 嚟."""
    if c.pos == Pos.VERB:
        c.replace_word("嚟")

@contextual_rule("野")
def _(c: Context):
    """野 -> 嘢: 如果係隻名詞，就改成 嘢. 包埋動詞同X係因為 pycantonese 有時會識別成動詞."""
    if c.pos in ["NOUN",  "X", "PRON"] or c.prev_pos in ["VERB"]:
        c.replace_word("嘢")

@contextual_rule("既")
def _(c: Context):
    """既 -> 嘅: 如果 既 字前面係一個名詞/動詞/形容詞/副詞，句子後面又冇"又 ADV/ADJ/VERB"嘅結構，噉就改成 嘅."""
    if c.prev_pos not in (Pos.PRON, Pos.NOUN, Pos.ADJ, Pos.ADV, Pos.VERB):
        return
    # 句子後面冇 "又 ADV/ADJ/VERB" 嘅結構
    if "又" in c.suffix and c.next_pos not in (Pos.ADJ, Pos.ADV, Pos.VERB):
        return
    c.replace_word("嘅")

# TODO: add more rules from main.py.


def segment_line(line: str) -> list[str]:
    words = []
    segments = re.split("\s+", line)
    for seg in segments:
        words += pycantonese.segment(seg)
    return words


def apply_contextual_rules(line: str):
    ctx = Context()
    ctx.pos_list = pycantonese.pos_tag(segment_line(line))
    for ctx.i, (ctx.word, ctx.pos) in enumerate(ctx.pos_list):
        ctx.prev_word = ctx.word
        ctx.prev_pos = ctx.pos
        if ctx.i + 1 < len(ctx.pos_list):
            ctx.next_word, ctx.next_word = ctx.pos_list[ctx.i+1]
        else:
            ctx.next_word, ctx.next_word = '', Pos.NONE

        rule_handler = _handlers.get(ctx.word, None)
        if rule_handler:
            rule_handler(ctx)

    return ''.join(w for w, _ in ctx.pos_list)
