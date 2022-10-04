# 粵文錯別字修正器

[![license](https://img.shields.io/github/license/DAVFoundation/captain-n3m0.svg?style=flat-square)](https://github.com/DAVFoundation/captain-n3m0/blob/master/LICENSE)

呢個係隻粵文錯別字修正器，會自動改正常見嘅粵文錯別字。

本修正器採用嘅正字法見 [粵文常見錯別字](https://jyutping.org/blog/typo/)

## 依賴

- Python >= 3.9
- PyCantonese

## 用法

隻修正器可以輸入多個文檔，然後默認輸出到 `/output` 度。佢默認輸入文件入面每一行都係一句話。運行下面嘅命令就得：

```bash
# 可以指定輸出路徑
python3 main.py --inputs input1.txt input2.txt --outdir output
# 亦可以剩係指定輸入，輸出會默認喺 /output
python3 main.py --inputs input.txt
```

# Cantonese typo auto corrector

This is a Cantonese typo corrector, it auto corrects common Cantonese typos in the input texts.

The orthography of this corrector is from [粵文常見錯別字](https://jyutping.org/blog/typo/)

## Dependencies

- Python >= 3.9
- PyCantonese

## How to use

This typo corrector takes in one or more input text files, and outputs the corrected texts in the `output_dir`. It assumes each line in the input text file is one sentence.

To use the corrector, run the command:

```bash
# Specify the output dir
python3 main.py --inputs input1.txt input2.txt --outdir output
# Or put the input files only, output will be in /output by default
python3 main.py --inputs input.txt
```
