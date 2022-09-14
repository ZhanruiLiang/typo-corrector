"""
主要檢查嘅錯別字（錯字 -> 正字）：

1. 左 -> 咗
2. 係 -> 喺
3. 既 -> 嘅
4. 地 -> 哋
5. 個 -> 嗰
6. 咁 -> 噉
7. 野 -> 嘢
8. 無 -> 冇
9. 黎 -> 嚟
10. D -> 啲
11. 宜家 -> 而家
"""

import argparse
import re

import pycantonese


def fix_line(line: str) -> str:
    """
    """

    # 地 -> 哋
    line = re.sub("我地", "我哋", line)
    line = re.sub("你地", "你哋", line)
    line = re.sub("佢地", "佢哋", line)

    # 宜家 -> 而家
    line = re.sub("宜家", "而家", line)
    line = re.sub(r"[oO]既", "嘅", line)

    # 以下字嘅修復需要用到句子詞性同上下文信息
    pos_list = pycantonese.pos_tag(pycantonese.segment(line))

    # print(pos_list)

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
                    pos_list[i] = (word.replace("既", "嘅"), pos)
        # 黎 -> 嚟
        # 如果 黎 字係動詞，就改成 嚟
        if pair[0] == "黎" and pos == "VERB":
            pos_list[i] = (word.replace("黎", "嚟"), pos)
        # 宜家 -> 而家
        if pair[0] == "宜家":
            next_word = pos_list[i+1][0]
            if next_word != ("傢俬" or "傢俱" or "家居"):
                pos_list[i] = (word.replace("宜家", "而家"), pos)

    line = "".join([pair[0] for pair in pos_list])

    return line


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fix Cantonese typo.')
    parser.add_argument(
        '--input', type=str, help='Input text file, each line is a sentence.')
    args = parser.parse_args()

    output = open("output.txt", "w", encoding="utf-8")
    with open(args.input, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip().replace(" ", "")
            fixed_line = fix_line(line)
            output.writelines(fixed_line+"\n")
