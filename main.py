"""
Example usage:

    $ python3 main.py sample.txt
    $ python3 main.py --outdir /tmp sample-0.txt sample-1.txt sample-2.txt
"""

import argparse
import pathlib
import re
from typing import TextIO, List, Tuple

import pycantonese

import rules

regular_typos: List[Tuple[re.Pattern, str]] = []


def fix_regular_typo(line: str) -> str:
    """
    Regular typo means that they can be simply replaced by a regular expression.
    Fixing them does not require any context information.
    """
    for typo, replace in regular_typos:
        line = typo.sub(replace, line)
    return line


def correct(input: TextIO, output: TextIO) -> None:
    """
    Corrects typos from input file and write to output file.
    """
    for line in input:
        fixed = fix_regular_typo(line.strip())
        fixed = rules.apply_contextual_rules(fixed)
        output.write(fixed + "\n")


def main():
    parser = argparse.ArgumentParser(description='Fix Cantonese typo.')
    parser.add_argument(
        '--inputs', type=str, nargs='+',
        help='Input text file, each line is a sentence.')
    parser.add_argument(
        '--outdir', type=str, default="output", nargs='?',
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
        with open(input, 'r', encoding='utf-8') as input_f, open(output, 'w', encoding='utf-8') as output_f:
            correct(input_f, output_f)


if __name__ == "__main__":
    main()
