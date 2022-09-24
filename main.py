"""
主要檢查嘅錯別字（錯字 -> 正字）：
4. 係系喺
5. 個 -> 嗰
10. D -> 啲
12.岩啱
"""

import argparse
import re

import pycantonese


han = r'\u3006\u3007\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002ebef\U00030000-\U0003134f'
full_width_punct = r'\uFF00-\uFFEF'
cjk_punct = r'\u3000-\u303F'
kana = r'\u3040-\u309f\u30a0-\u30ff\u31F0-\u31FF'
hangul = r'\uAC00-\uD7AF\u1100-\u11ff'

han_regex = '[{}{}{}{}]'.format(han, full_width_punct, cjk_punct, kana, hangul)

# Debugging purpose
pos_file = open('pos.txt', 'w', encoding='utf-8')


# def separate_han(s):
#   s = f"\t{s}\t"  # hack to make sure that the non-chinese is always the first and last
#   other = re.split(u'[\u4E00-\u9FFF]+', s)
#   han = [x for x in re.split(u'[^\u4E00-\u9FFF]+', s) if x]
#   assert len(other) == len(han) + 1
#   return han, other

# def process_han(s):
#   """Colors it red. Placeholder for spell correction!
#   """
#   RED='\033[0;31m'
#   NC='\033[0m' # No Color
#   return f"{RED}{s}{NC}"

# def process_text(s):
#   han, other = separate_han(s)
#   han = [process_han(h) for h in han] + ["\t"]
#   out = "".join([f"{o}{h}" for o, h in zip(other, han)]).strip()
#   print(out)

# for s_i in s:
#   process_text(s_i)


def fix_space(line: str) -> str:
    pattern = '(?<={})\s+(?={})'.format(han_regex, han_regex)
    return re.sub(pattern, '', line)


def fix_regular_typo(line: str) -> str:
    """
    Regular typo means that they can be simply replaced by a regular expression.
    Fixing them does not require any context information.
    """
    for r in regular_typos:
        line = re.sub(r[0], r[1], line)
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

    pos_list = pycantonese.pos_tag(pycantonese.segment(line))

    # Debugging purpose
    print(pos_list, file=pos_file)

    for i, pair in enumerate(pos_list):
        word, pos = pair
        length = len(pos_list)
        prev_word = pos_list[i - 1][0] if i > 0 else ''
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
        if word == "既":
            if i >= 1 and pos_list[i-1][1] in ["PRON", "NOUN", "ADJ", "ADV", "VERB"]:
                # 句子後面冇 "又 ADV/ADJ/VERB" 嘅結構
                if "又" in "".join([pair[0] for pair in pos_list[i:]]) and pos_list[i+1][1] not in ["ADJ", "ADV", "VERB"]:
                    pass
                else:
                    pos_list[i] = ("嘅", pos)
        # 黎 -> 嚟
        # 如果 黎 字係動詞，就改成 嚟
        if word == "黎" and pos == "VERB":
            pos_list[i] = ("嚟", pos)
        # 野 -> 嘢
        # 如果係隻名詞，就改成 嘢
        # 包埋動詞同X係因為 pycantonese 有時會識別成動詞
        if word == "野":
            if pos in ["NOUN",  "X", "PRON"]:
                pos_list[i] = ("嘢", pos)
            elif prev_pos in ["VERB"]:
                pos_list[i] = ("嘢", pos)
        # 咁/甘 -> 噉, 甘 -> 咁
        # 如果前面係形容詞、副詞，或者後面後動詞、名詞、代詞，就係 噉
        # 如果後面係形容詞、副詞，就係 咁
        if word == "咁" or (word == "甘" and pos not in ["VERB", "NOUN"]):
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
        if word == "比":
            if i <= length-3 and pos_list[i+2][1] in ["ADJ", "ADV"]:
                pass
            else:
                pos_list[i] = ("畀", pos)
        # 個 -> 嗰
        # 係系喺
        # 無 -> 冇
        if word == "無":
            if i <= length-2 and pos_list[i+1][1] == ["NOUN", "ADP"]:
                pos_list[i] = ("冇", pos)
        # d/D -> 啲

        # 以下詞嘅修復需要用到句子詞性同上下文信息
        if word == "宜家":
            if any(word in line for word in ["傢俬", "傢俱", "家居"]):
                pass
            else:
                pos_list[i] = (word.replace("宜家", "而家"), pos)

    line = " ".join([pair[0] for pair in pos_list])

    return line


def fix_line(line: str) -> str:
    """
    Every line is fixed for regular typos and contextual typos
    """

    line = fix_regular_typo(line)
    line = fix_contextual_typo(line)
    return line.strip()
    # 以下字嘅修復需要用到句子詞性同上下文信息


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fix Cantonese typo.')
    parser.add_argument(
        '--input', type=str, help='Input text file, each line is a sentence.')
    args = parser.parse_args()

    # Read regular typos
    regular_typos = []
    lines = open('regular.txt', 'r', encoding='utf-8').readlines()
    for line in lines:
        pair = line.strip().split(',')
        regular_typos.append((re.compile(pair[0]), pair[1]))

    output = open("output.txt", "w", encoding="utf-8")
    with open(args.input, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            fixed_line = fix_space(fix_line(line))

            output.writelines(fixed_line+"\n")
