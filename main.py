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
import pycantonese


def fix_左(pos_list: list) -> str:
    """
    Fix "左" to "咗".
    """
    for i, pair in enumerate(pos_list):
        if "左" in pair[0]:
            word, pos = pair
            if i >= 1 and pos_list[i-1][1] == "VERB":
                pos_list[i] = (word.replace("左", "咗"), pos)

    return "".join([pair[0] for pair in pos_list])


def fix_係(pos_list: list) -> str:
    """
    Fix "係" to "喺".
    """
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fix Cantonese typo.')
    parser.add_argument(
        '--input', type=str, help='Input text file, each line is a sentence.')
    args = parser.parse_args()

    with open(args.input, 'r') as f:
        for line in f:
            pos_list = pycantonese.pos_tag(pycantonese.segment(line))
            print(pos_list)
