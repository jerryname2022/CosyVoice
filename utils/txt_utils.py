#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# Copyright FunASR (https://github.com/alibaba-damo-academy/FunClip). All Rights Reserved.
#  MIT License  (https://opensource.org/licenses/MIT)

from utils.file_utils import read_lines
from utils.log_utils import log_time
from pypinyin import lazy_pinyin


def is_text(char):
    """判断字符是否为字母或数字。"""
    return char.isalpha() or char.isdigit()


def texts_to_pinyins(texts):
    pinyins = []
    for text in texts:
        # clear = ""
        for char in text:
            if is_text(char):
                charPinyin = lazy_pinyin(char.strip())  # []
                pinyins.extend(charPinyin)

    return pinyins


def split_texts(text, length):
    return [text[i:i + length] for i in range(0, len(text), length)]


def longest_common_subsequence(text0, text1):
    len0, len1 = len(text0), len(text1)
    dp = [[0] * (len1 + 1) for _ in range(len0 + 1)]

    # 计算LCS的动态规划表
    for i in range(1, len0 + 1):
        for j in range(1, len1 + 1):
            if text0[i - 1] == text1[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp  # 只返回动态规划表


def get_lcs_indices(dp, text0, text1):
    indices = []
    i, j = len(dp) - 1, len(dp[0]) - 1
    while i > 0 and j > 0:
        if text0[i - 1] == text1[j - 1]:
            indices.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return indices[::-1]


def align_texts(text0, text1, marker="*"):
    dp = longest_common_subsequence(text0, text1)  # 只接收dp
    lcs_indices = get_lcs_indices(dp, text0, text1)

    result0, result1 = [], []
    index0, index1 = 0, 0

    for i, j in lcs_indices:
        while index0 < i or index1 < j:
            if index0 < i:
                result0.append(text0[index0])
                index0 += 1
            else:
                result0.append(marker)

            if index1 < j:
                result1.append(text1[index1])
                index1 += 1
            else:
                result1.append(marker)

        result0.append(text0[i])
        result1.append(text1[j])
        index0 += 1
        index1 += 1

    while index0 < len(text0):
        result0.append(text0[index0])
        result1.append(marker)
        index0 += 1

    while index1 < len(text1):
        result0.append(marker)
        result1.append(text1[index1])
        index1 += 1

    return result0, result1


def reset_texts(srtTexts, rightTexts):
    srtPinyins = texts_to_pinyins(srtTexts)
    txtPinyins = texts_to_pinyins(rightTexts)

    resetTexts = {}
    srtTextLines = []
    rightTextLines = []

    line = 0
    index = 0
    for text in srtTexts:
        text = text.strip()
        for char in text:
            if is_text(char):
                srtTextLines.append(line)
                index += 1
        line += 1

    log_time("START ... ")
    srtAlign, rightAlign = align_texts(srtPinyins, txtPinyins)
    log_time("END ... ")  # 6628

    if len(srtAlign) == len(rightAlign):

        index = 0
        line = 0
        for i in range(len(srtAlign)):
            srtChar = srtAlign[i]
            txtChar = rightAlign[i]

            if is_text(srtChar):
                line = srtTextLines[index]
                index += 1

            if is_text(txtChar):
                rightTextLines.append(line)

        index = 0
        line = 0
        for text in rightTexts:
            text = text.strip()
            for char in text:
                if is_text(char):
                    line = rightTextLines[index]
                    index += 1

                present: bool = str(line) in resetTexts.keys()
                if not present:
                    resetTexts[str(line)] = char
                else:
                    resetTexts[str(line)] += char

    return resetTexts


if __name__ == '__main__':
    srtTextsFile = '../1_srt.txt'
    textsFile = '../1.txt'

    srtLines = read_lines(srtTextsFile)
    txtLines = read_lines(textsFile)

    resetLines = reset_texts(srtLines, txtLines)

    print(resetLines)
