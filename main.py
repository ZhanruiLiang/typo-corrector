"""
主要檢查嘅錯別字（錯字 -> 正字）：
4. 係系喺
5. 個 -> 嗰

Example usage:

  python3 main.py sample.txt
  python3 main.py --outdir /tmp sample-0.txt sample-1.txt sample-2.txt
"""

import argparse
import pathlib
import re
from typing import TextIO

import pycantonese


han = r'\u3006\u3007\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002ebef\U00030000-\U0003134f'
full_width_punct = r'\uFF00-\uFFEF'
cjk_punct = r'\u3000-\u303F'
kana = r'\u3040-\u309f\u30a0-\u30ff\u31F0-\u31FF'
hangul = r'\uAC00-\uD7AF\u1100-\u11ff'

cjk_regex = '[{}{}{}{}]'.format(han,
                                full_width_punct, cjk_punct, kana, hangul)
non_cjk_regex = '[^{}{}{}{}]'.format(
    han, full_width_punct, cjk_punct, kana, hangul)
regular_typos: list[tuple[re.Pattern, str]] = []

# Debugging purpose
pos_file = open('pos.txt', 'w', encoding='utf-8')


def segment_line(line: str) -> list[str]:
    words = []
    segments = re.split("\s+", line)
    for seg in segments:
        words += pycantonese.segment(seg)
    return words


def fix_space(line: str) -> str:
    """
    Remove spaces between Han characters and non-Han characters.
    """
    cjk_pattern = '(?<={})\s+(?={})'.format(cjk_regex, cjk_regex)
    line = re.sub(cjk_pattern, '', line)
    number_pattern = '(?<={})\s+(?={})'.format(r'[\d.,]', r'[\d.,]')
    return re.sub(number_pattern, '', line)


def fix_regular_typo(line: str) -> str:
    """
    Regular typo means that they can be simply replaced by a regular expression.
    Fixing them does not require any context information.
    """
    for typo, replace in regular_typos:
        line = typo.sub(replace, line)
    return line


def fix_contextual_typo(line: str) -> str:
    """
    Contextual typo means that they can be fixed by using the context information.

    List of typos:
    1. 係系喺
    2. 個 -> 嗰
    3. 咁 -> 噉
    4. 無 -> 冇
    5. D -> 啲
    6. 比 -> 畀
    7. 既 -> 嘅
    8. 左 -> 咗
    """

    pos_list = pycantonese.pos_tag(segment_line(line))

    # Debugging purpose
    print(pos_list, file=pos_file)

    for i, pair in enumerate(pos_list):
        word, pos = pair
        length = len(pos_list)
        prev_pos = pos_list[i - 1][1] if i > 0 else ''
        next_word = pos_list[i + 1][0] if i < length - 1 else ''
        next_pos = pos_list[i + 1][1] if i < length - 1 else ''

        # 左 -> 咗
        # 如果 左 字前面係一個動詞，噉就改成 咗
        if "左" in pair[0]:
            if prev_pos == "VERB":
                pos_list[i] = (word.replace("左", "咗"), pos)
        # 既 -> 嘅
        # 如果 既 字前面係一個名詞/動詞/形容詞/副詞，句子後面又冇"又 ADV/ADJ/VERB"嘅結構，噉就改成 嘅
        elif word == "既":
            if i >= 1 and pos_list[i-1][1] in ["PRON", "NOUN", "ADJ", "ADV", "VERB"]:
                # 句子後面冇 "又 ADV/ADJ/VERB" 嘅結構
                if "又" in "".join([pair[0] for pair in pos_list[i:]]) and next_pos not in ["ADJ", "ADV", "VERB"]:
                    pass
                else:
                    pos_list[i] = ("嘅", pos)
        # 黎 -> 嚟
        # 如果 黎 字係動詞，就改成 嚟
        elif word == "黎" and pos == "VERB":
            pos_list[i] = ("嚟", pos)
        # 野 -> 嘢
        # 如果係隻名詞，就改成 嘢
        # 包埋動詞同X係因為 pycantonese 有時會識別成動詞
        elif word == "野":
            if pos in ["NOUN",  "X", "PRON"]:
                pos_list[i] = ("嘢", pos)
            elif prev_pos in ["VERB"]:
                pos_list[i] = ("嘢", pos)
        # 咁/甘 -> 噉, 甘 -> 咁
        # 如果前面係形容詞、副詞，或者後面後動詞、名詞、代詞，就係 噉
        # 如果後面係形容詞、副詞，就係 咁
        elif word == "咁" or (word == "甘" and pos not in ["VERB", "NOUN"]):
            if i == length - 1:
                pos_list[i] = ("噉", pos)
            else:
                if next_pos in ["ADJ", "ADV"]:
                    pos_list[i] = ("咁", pos)
                elif next_pos in ["VERB", "NOUN", "PRON", "PART", "AUX"] or (prev_pos in ["ADJ", "ADV"]):
                    pos_list[i] = ("噉", pos)
                elif prev_pos in ["ADJ", "ADV"]:
                    pos_list[i] = ("噉", pos)
        # 比 -> 畀
        # 如果後面第一個詞係名詞，且第二個詞係形容詞、副詞，就係 比
        elif word == "比":
            if i <= length-3 and pos_list[i+2][1] in ["ADJ", "ADV"]:
                pass
            else:
                pos_list[i] = ("畀", pos)
        # 俾 -> 畀
        elif word == "俾":
            pos_list[i] = ("畀", pos)
        # 個 -> 嗰
        # 係系喺
        # 無 -> 冇
        elif word == "無":
            if i <= length-2 and pos_list[i+1][1] == ["NOUN", "ADP"]:
                pos_list[i] = ("冇", pos)
        # d/D -> 啲
        elif word in ["d", "D"]:
            if re.compile(cjk_regex).search(next_word):
                pos_list[i] = ("啲", pos)
            elif prev_pos in ["ADJ", "ADV"]:
                pos_list[i] = ("啲", pos)
        # 以下詞嘅修復需要用到句子詞性同上下文信息
        elif word == "宜家":
            if any(word in line for word in ["傢俬", "傢俱", "家居"]):
                pass
            else:
                pos_list[i] = (word.replace("宜家", "而家"), pos)

    line = " ".join([pair[0] for pair in pos_list])

    return line


def correct(input: TextIO, output: TextIO):
    """Corrects typos from input file and write to output file."""
    for line in input:
        fixed = fix_regular_typo(line.strip())
        fixed = fix_contextual_typo(fixed)
        fixed = fix_space(fixed)
        output.write(fixed + "\n")


def main():
    parser = argparse.ArgumentParser(description='Fix Cantonese typo.')
    parser.add_argument(
        'inputs', type=str, nargs='+',
        help='Input text file, each line is a sentence.')
    parser.add_argument(
        'outdir', type=str, default="output", nargs='?',
        help='Output directory.')
    args = parser.parse_args()

    # Read regular typos
    for line in open('regular.txt', 'r', encoding='utf-8'):
        typo, replace = line.strip().split(',')
        regular_typos.append((re.compile(typo), replace))

    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for input in map(pathlib.Path, args.inputs):
        output = outdir / input.name
        with (open(input, 'r', encoding='utf-8') as input_f, 
              open(output, 'w', encoding='utf-8') as output_f):
            correct(input_f, output_f)

if __name__ == "__main__":
    main()