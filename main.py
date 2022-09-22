"""
主要檢查嘅錯別字（錯字 -> 正字）：
4. 係系喺
5. 個 -> 嗰
6. 咁 -> 噉
8. 無 -> 冇
10. D -> 啲
11. 比 -> 畀
"""

import argparse
import re

import pycantonese

# han_regex = re.compile(
# r'[\u3006\u3007\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002ebef\U00030000-\U0003134f]')

han_regex = r'[\u3006\u3007\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002ebef\U00030000-\U0003134f]'


def is_han(char: str) -> bool:
    """
    Check if a character is a Chinese character.
    """
    return bool(han_regex.fullmatch(char))


def fix_space(line: str) -> str:
    pattern = r'(?<=' + han_regex + r')\s+(?=' + han_regex + r')'
    return re.sub(pattern, '', line)


def fix_regular_typo(line: str) -> str:
    """
    Regular typo means that they can be simply replaced by a regular expression.
    Fixing them does not require any context information.
    """
    for r in regular_typos:
        line = re.sub(r[0], r[1], line)
    return line


pos_file = open('pos.txt', 'w', encoding='utf-8')


def fix_line(line: str) -> str:
    """
    """

    line = fix_regular_typo(line)

    # 以下字嘅修復需要用到句子詞性同上下文信息
    pos_list = pycantonese.pos_tag(pycantonese.segment(line))
    print(pos_list, file=pos_file)

    for i, pair in enumerate(pos_list):
        word, pos = pair
        # 左 -> 咗
        # 如果 左 字前面係一個動詞，噉就改成 咗
        if "左" in pair[0]:
            if i >= 1 and pos_list[i-1][1] == "VERB":
                pos_list[i] = (word.replace("左", "咗"), pos)
        # 既 -> 嘅
        # 如果 既 字前面係一個名詞/動詞/形容詞/副詞，句子後面又冇"又 ADV/ADJ/VERB"嘅結構，噉就改成 嘅
        if pair[0] == "既":
            if i >= 1 and pos_list[i-1][1] in ["PRON", "NOUN", "ADJ", "ADV", "VERB"]:
                # 句子後面冇 "又 ADV/ADJ/VERB" 嘅結構
                if "又" in "".join([pair[0] for pair in pos_list[i:]]) and pos_list[i+1][1] not in ["ADJ", "ADV", "VERB"]:
                    pass
                else:
                    pos_list[i] = ("嘅", pos)
        # 黎 -> 嚟
        # 如果 黎 字係動詞，就改成 嚟
        if pair[0] == "黎" and pos == "VERB":
            pos_list[i] = ("嚟", pos)
        # 野 -> 嘢
        # 如果係隻名詞，就改成 嘢
        # 包埋動詞同X係因為 pycantonese 有時會識別成動詞
        if pair[0] == "野" and pos in ["NOUN", "VERB", "X"]:
            pos_list[i] = ("嘢", pos)
        # 咁/甘 -> 噉, 甘 -> 咁
        # 如果前面係形容詞、副詞，或者後面後動詞、名詞、代詞，就係 噉
        # 如果後面係形容詞、副詞，就係 咁
        if pair[0] == "咁" or (pair[0] == "甘" and pair[1] not in ["VERB", "NOUN"]):
            if i == len(pos_list) - 1:
                pos_list[i] = ("噉", pos)
            else:
                next_word_pos = pos_list[i+1][1]
                prev_word_pos = pos_list[i-1][1]
                if next_word_pos in ["ADJ", "ADV"]:
                    pos_list[i] = ("咁", pos)
                elif next_word_pos in ["VERB", "NOUN", "PRON", "PART", "AUX"] or (i >= 1 and prev_word_pos in ["ADJ", "ADV"]):
                    pos_list[i] = ("噉", pos)
                elif prev_word_pos in ["ADJ", "ADV"]:
                    pos_list[i] = ("噉", pos)

        # 以下詞嘅修復需要用到句子詞性同上下文信息
        if pair[0] == "宜家":
            if any(word in line for word in ["傢俬", "傢俱", "家居"]):
                pass
            else:
                pos_list[i] = (word.replace("宜家", "而家"), pos)

    line = " ".join([pair[0] for pair in pos_list])

    return line


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
