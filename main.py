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
"""

import argparse
import re

import pycantonese


def fix_line(line: str) -> str:
    """
    Fix "左" to "咗".
    """

    # 修復 地 -> 哋
    line = re.sub("我地", "我哋", line)
    line = re.sub("你地", "你哋", line)
    line = re.sub("佢地", "佢哋", line)

    # 修復 宜家 -> 而家
    line = re.sub("佢地", "佢哋", line)

    # 以下字嘅修復需要用到句子詞性同上下文信息
    pos_list = pycantonese.pos_tag(pycantonese.segment(line))

    for i, pair in enumerate(pos_list):
        word, pos = pair
        # 修復 左 -> 咗
        # 如果 左 字前面係一個動詞，噉就改成 咗
        if "左" in pair[0]:
            if i >= 1 and pos_list[i-1][1] == "VERB":
                pos_list[i] = (word.replace("左", "咗"), pos)
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
    with open(args.input, 'r') as f:
        for line in f:
            fixed_line = fix_line(line)

            output.writelines(fixed_line+"\n")
