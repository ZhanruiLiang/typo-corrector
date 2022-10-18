"""
Example usage:

    $ python3 main.py sample.txt
    $ python3 main.py --outdir /tmp sample-0.txt sample-1.txt sample-2.txt
"""

from __future__ import annotations

import argparse
import itertools
import pathlib
import re
import time
import tqdm
from concurrent import futures
from typing import TextIO

import rules

regular_typos: list[tuple[re.Pattern, str]] = []


def fix_regular_typo(line: str) -> str:
    """
    Regular typo means that they can be simply replaced by a regular expression.
    Fixing them does not require any context information.
    """
    for typo, replace in regular_typos:
        line = typo.sub(replace, line)
    return line

    
def correct_line(line: str) -> str:
    fixed = fix_regular_typo(line.strip())
    return rules.apply_contextual_rules(fixed)


def correct(pool: futures.ProcessPoolExecutor, input: TextIO, output: TextIO) -> None:
    """
    Corrects typos from input file and write to output file.
    """
    inputs = list(input)
    # Keep a moderate chunksize to reduce process pool overhead.
    for line in tqdm.tqdm(pool.map(correct_line, inputs, chunksize=1024), total=len(inputs)):
        output.write(line + "\n")


def main():
    parser = argparse.ArgumentParser(description="Fix Cantonese typo.")
    parser.add_argument(
        "--inputs", type=str, nargs="+",
        help="Input text files, each line is a sentence. If the input is a folder, all text files will be globbed.")
    parser.add_argument(
        "--outdir", type=str, default="output", nargs="?",
        help="Output directory. Defaults to ‘output’.")
    parser.add_argument(
        "--parallel", type=int, default=0, nargs="?",
        help="Number of processes to run in parallel. Set to 0 for auto detect.")
    args = parser.parse_args()

    # Read regular typos
    for line in open("regular.txt", "r", encoding="utf-8"):
        typo, replace = line.strip().split(",")
        regular_typos.append((re.compile(typo), replace))

    outdir = pathlib.Path(args.outdir)
    with futures.ProcessPoolExecutor(args.parallel or None) as pool:
        for input, output in itertools.chain.from_iterable(
            [(input, input.name)] if input.is_file() else [
                (path, path.relative_to(input)) for path in input.rglob("*.txt")]
            for input in map(pathlib.Path, args.inputs)
        ):
            output = outdir / output
            output.parent.mkdir(parents=True, exist_ok=True)
            print(f"Correcting {input} -> {output}")
            with open(input, "r", encoding="utf-8") as input_f, open(output, "w", encoding="utf-8") as output_f:
                correct(pool, input_f, output_f)


if __name__ == "__main__":
    main()
