#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# Copyright FunASR (https://github.com/alibaba-damo-academy/FunClip). All Rights Reserved.
#  MIT License  (https://opensource.org/licenses/MIT)

from utils.file_utils import read_lines
from utils.log_utils import log_time
from pypinyin import lazy_pinyin
import math


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


def alignment_score(listA, listB, alignment=''):
    lenA = len(listA)
    lenB = len(listB)
    if lenA == lenB:
        score = 0
        for index in range(lenA):
            charA = listA[index]
            charB = listB[index]
            if charA == alignment or charB == alignment:
                continue
            if charA == charB:
                score += 1
        return score / lenA

    return 0


def alignment_list(list0, list1, alignment='*'):
    order0Sames = []
    order1Sames = []
    reverse0Sames = []
    reverse1Sames = []

    alignment0 = []
    alignment1 = []

    index1 = -1
    for i in range(len(list0)):
        item0 = list0[i]
        for j in range(len(list1)):
            item1 = list1[j]

            if item0 == item1 and j > index1:
                order0Sames.append(i)
                order1Sames.append(j)
                index1 = j
                break

    reverse0Sames = []
    reverse1Sames = []

    index1 = -1
    for i in range(len(list1)):
        item1 = list1[i]
        for j in range(len(list0)):
            item0 = list0[j]

            if item0 == item1 and j > index1:
                reverse0Sames.append(i)
                reverse1Sames.append(j)
                index1 = j
                break

    order = max(len(order0Sames), len(reverse0Sames)) == len(order0Sames)
    # print("reverse", reverse0Sames, reverse1Sames)

    same0 = order0Sames
    same1 = order1Sames
    data0 = list0
    data1 = list1
    if not order:
        same0 = reverse0Sames
        same1 = reverse1Sames
        data0 = list1
        data1 = list0

    flag0 = 0
    flag1 = 0
    lastIndex0 = 0
    lastIndex1 = 0
    if len(same0) > 0:

        for i in range(len(same0)):
            index0 = same0[i]
            index1 = same1[i]
            count0 = index0 - lastIndex0
            count1 = index1 - lastIndex1
            count = int(math.fabs(count0 - count1))

            for j in range(count):
                if flag0 < index0:
                    alignment0.append(data0[flag0])
                    flag0 += 1
                else:
                    alignment0.append(alignment)

                if flag1 < index1:
                    alignment1.append(data1[flag1])
                    flag1 += 1
                else:
                    alignment1.append(alignment)

            alignment0.append(data0[flag0])
            alignment1.append(data1[flag1])
            flag1 += 1
            flag0 += 1
            # print("flag0", flag0, "flag1", flag1)

            lastIndex0 = index0
            lastIndex1 = index1

        if flag0 < len(data0) or flag1 < len(data1):

            count0 = len(data0) - flag0
            count1 = len(data1) - flag1
            count = max(count0, count1)

            # print(count0, count1, count)
            for j in range(count):
                if flag0 < len(data0):
                    alignment0.append(data0[flag0])
                    flag0 += 1
                else:
                    alignment0.append(alignment)

                if flag1 < len(data1):
                    alignment1.append(data1[flag1])
                    flag1 += 1
                else:
                    alignment1.append(alignment)
            # print("flag0", flag0, "flag1", flag1)
        if not order:
            tmp = alignment0
            alignment0 = alignment1
            alignment1 = tmp
    else:
        resize = max(len(list0), len(list1))

        data0 = list0
        data1 = list1
        back = resize == len(data1)

        if back:
            data0 = list1
            data1 = list0

        for i in range(resize - len(data1)):
            data1.append(alignment)

        alignment0 = data0
        alignment1 = data1

        if back:
            tmp = alignment0
            alignment0 = alignment1
            alignment1 = tmp

    # print(data0, data1)
    # print(alignment0, alignment1)
    return alignment0, alignment1


def splitList(list0, list1, minCount=10):
    # print(len(list0), len(list1))

    result0, result1 = [], []

    count = minCount
    j = 0
    jump = 0
    for i in range(len(list0)):
        if i < jump:
            continue
        if (min(len(list0), i + count) - i) <= 0:
            break
        sub0 = list0[i: min(len(list0), i + count)]

        for z in range(len(list1)):
            if z < j:
                continue

            sub1 = list1[z: min(len(list1), z + count)]
            score = alignment_score(sub0, sub1)

            if score > 0.99:
                while score > 0.99:
                    count += 1
                    sub0 = list0[i: min(len(list0), i + count)]
                    sub1 = list1[z: min(len(list1), z + count)]
                    score = alignment_score(sub0, sub1)

                    if (i + count) > len(list0) or (z + count) > len(list1):
                        break

                count -= 1
                sub0 = list0[i: min(len(list0), i + count)]
                sub1 = list1[z: min(len(list1), z + count)]

                result0.append((i, min(len(list0), i + count)))
                result1.append((z, min(len(list1), z + count)))
                # print(i, sub0)
                # print(z, sub1)

                jump = i + count
                j = z
                count = minCount
                break

    return result0, result1


def alignment_list2(srtList, txtList, alignment="", minCount=2):
    splitCount = minCount
    while True:
        result0, result1 = splitList(srtList, txtList, minCount=splitCount)

        srtResult = []
        txtResult = []

        last0 = 0
        last1 = 0
        count0 = 0
        count1 = 0
        for i in range(len(result0)):
            split0 = result0[i]
            split1 = result1[i]

            sub0 = []
            sub1 = []
            if split0[0] - last0 > 0:
                sub0 = srtList[last0: split0[0]]
                count0 += len(sub0)

            if split1[0] - last1 > 0:
                sub1 = txtList[last1: split1[0]]
                count1 += len(sub1)

            if len(sub0) > 0 or len(sub1) > 0:
                sub0Format, sub1Format = alignment_list(sub0, sub1, alignment=alignment)
                # # print(last0, split0[0], sub0)
                # # print(last1, split1[0], sub1)
                # # print("1", sub0Format)
                # # print("3", sub1Format)

                srtResult += sub0Format
                txtResult += sub1Format

            sub0 = []
            sub1 = []

            if split0[1] - split0[0] > 0:
                sub0 = srtList[split0[0]: split0[1]]
                count0 += len(sub0)

            if split1[1] - split1[0] > 0:
                sub1 = txtList[split1[0]: split1[1]]
                count1 += len(sub1)

            if len(sub0) > 0 or len(sub1) > 0:
                sub0Format, sub1Format = alignment_list(sub0, sub1, alignment=alignment)
                # print(split0[0], split0[1], sub0)
                # print(split1[0], split1[1], sub1)
                # print("1", sub0Format)
                # print("3", sub1Format)

                srtResult += sub0Format
                txtResult += sub1Format

            last0 = split0[1]
            last1 = split1[1]

        if last0 < len(srtList) or last1 < len(txtList):
            sub0 = []
            sub1 = []

            if len(srtList) - last0 > 0:
                sub0 = srtList[last0: len(srtList)]
                count0 += len(sub0)

            if len(txtList) - last1 > 0:
                sub1 = txtList[last1:len(txtList)]
                count1 += len(sub1)

            if len(sub0) > 0 or len(sub1) > 0:
                sub0Format, sub1Format = alignment_list(sub0, sub1, alignment=alignment)

                # sub0Format, sub1Format = alignmentList(sub0, sub1, alignment=alignment)
                # print(last0, len(srtList), sub0)
                # print(last1, len(txtList), sub1)
                # print("1", sub0Format)
                # print("3", sub1Format)

                srtResult += sub0Format
                txtResult += sub1Format

        if len(srtList) == count0 and len(txtList) == count1:
            break
        else:
            splitCount += 1

        # print("alignmentPinyinList", len(srtList), len(txtList))
        # print("alignmentPinyinList", count0, count1, "splitCount", splitCount)

    return srtResult, txtResult


def alignmentPinyinList(srtList, txtList, alignment="", minCount=2):
    splitCount = minCount
    while True:
        result0, result1 = splitList(srtList, txtList, minCount=splitCount)

        srtResult = []
        txtResult = []

        last0 = 0
        last1 = 0
        count0 = 0
        count1 = 0
        for i in range(len(result0)):
            split0 = result0[i]
            split1 = result1[i]

            sub0 = []
            sub1 = []
            if split0[0] - last0 > 0:
                sub0 = srtList[last0: split0[0]]
                count0 += len(sub0)

            if split1[0] - last1 > 0:
                sub1 = txtList[last1: split1[0]]
                count1 += len(sub1)

            if len(sub0) > 0 or len(sub1) > 0:
                if len(sub0) > 20 and len(sub1) > 20:
                    sub0Format, sub1Format = alignment_list2(sub0, sub1, alignment=alignment, minCount=2)
                else:
                    sub0Format, sub1Format = alignment_list(sub0, sub1, alignment=alignment)
                # # print(last0, split0[0], sub0)
                # # print(last1, split1[0], sub1)
                # # print("1", sub0Format)
                # # print("3", sub1Format)

                srtResult += sub0Format
                txtResult += sub1Format

            sub0 = []
            sub1 = []

            if split0[1] - split0[0] > 0:
                sub0 = srtList[split0[0]: split0[1]]
                count0 += len(sub0)

            if split1[1] - split1[0] > 0:
                sub1 = txtList[split1[0]: split1[1]]
                count1 += len(sub1)

            if len(sub0) > 0 or len(sub1) > 0:
                sub0Format, sub1Format = alignment_list(sub0, sub1, alignment=alignment)
                # print(split0[0], split0[1], sub0)
                # print(split1[0], split1[1], sub1)
                # print("1", sub0Format)
                # print("3", sub1Format)

                srtResult += sub0Format
                txtResult += sub1Format

            last0 = split0[1]
            last1 = split1[1]

        if last0 < len(srtList) or last1 < len(txtList):
            sub0 = []
            sub1 = []

            if len(srtList) - last0 > 0:
                sub0 = srtList[last0: len(srtList)]
                count0 += len(sub0)

            if len(txtList) - last1 > 0:
                sub1 = txtList[last1:len(txtList)]
                count1 += len(sub1)

            if len(sub0) > 0 or len(sub1) > 0:
                sub0Format, sub1Format = alignment_list(sub0, sub1, alignment=alignment)

                # sub0Format, sub1Format = alignmentList(sub0, sub1, alignment=alignment)
                # print(last0, len(srtList), sub0)
                # print(last1, len(txtList), sub1)
                # print("1", sub0Format)
                # print("3", sub1Format)

                srtResult += sub0Format
                txtResult += sub1Format

        if len(srtList) == count0 and len(txtList) == count1:
            break
        else:
            splitCount += 1

        # print("alignmentPinyinList", len(srtList), len(txtList))
        # print("alignmentPinyinList", count0, count1, "splitCount", splitCount)

    return srtResult, txtResult


def reset_texts(srtLines, rightLines):
    srtPinyins = texts_to_pinyins(srtLines)
    txtPinyins = texts_to_pinyins(rightLines)

    srtTexts = ""
    rightTexts0 = ""
    srtLineIndexs = []
    txtLines = {}
    resetLines = {}

    flag = 0
    for line in srtLines:
        line = line.strip()
        for char in line:
            if is_text(char):
                srtTexts += char
                srtLineIndexs.append(flag)
        flag += 1

    for line in rightLines:
        line = line.strip()
        for char in line:
            if is_text(char):
                rightTexts0 += char

    srtTexts = srtTexts.strip()
    rightTexts0 = rightTexts0.strip()

    print(len(srtPinyins), len(srtTexts), len(txtPinyins), len(rightTexts0), len(srtLineIndexs))

    log_time("START ... ")
    srtPinyinFormat, rightPinyinFormat = alignmentPinyinList(srtPinyins, txtPinyins)
    log_time("END ... ")  # 6628

    # print(len(srtPinyinFormat))
    # print(len(rightPinyinFormat))

    if len(srtPinyinFormat) == len(rightPinyinFormat):

        srtCount = 0
        txtCount = 0
        for index in range(len(srtPinyinFormat)):
            srtChar = srtPinyinFormat[index]
            txtChar = rightPinyinFormat[index]

            if is_text(srtChar):
                srtCount += 1

            if is_text(txtChar):
                txtCount += 1

        print(srtCount, len(srtTexts), txtCount, len(rightTexts0))

        if srtCount == len(srtTexts) and txtCount == len(rightTexts0):

            srtCount = 0
            txtCount = 0

            for i in range(len(srtPinyinFormat)):

                line = srtLineIndexs[srtCount]
                charSrt = srtPinyinFormat[i]
                charTxt = rightPinyinFormat[i]

                if is_text(charSrt):
                    srtCount += 1

                if is_text(charTxt):
                    present: bool = str(line) in txtLines.keys()
                    if not present:
                        txtLines[str(line)] = rightTexts0[txtCount]
                    else:
                        txtLines[str(line)] += rightTexts0[txtCount]

                    txtCount += 1

            print(len(txtLines), srtCount, txtCount)

            lines = list(txtLines.keys())
            txtCount = 0

            lineIndex = 0
            line = lines[lineIndex]
            txt1 = txtLines[str(line)].strip()

            for txt0 in rightLines:
                txt0 = txt0.strip()

                for char in txt0:

                    if is_text(char):
                        if txtCount >= len(txt1):
                            lineIndex += 1
                            txtCount = 0
                            if lineIndex < len(lines):
                                line = lines[lineIndex]
                                txt1 = txtLines[str(line)].strip()
                                resetLines[str(line)] = char
                        else:
                            present: bool = str(line) in resetLines.keys()
                            if not present:
                                resetLines[str(line)] = char
                            else:
                                resetLines[str(line)] += char
                        txtCount += 1
                    else:
                        present: bool = str(line) in resetLines.keys()
                        if not present:
                            resetLines[str(line)] = char
                        else:
                            resetLines[str(line)] += char

            # for key in resetLines.keys():
            #     txt = resetLines[key].strip()
            #     print(int(key) + 1, txt)

    return resetLines


def best_similar(list0, list1, minCount=2):
    result0, result1 = (), ()

    count = minCount
    j = 0
    jump = 0
    lastCount = 0

    for i in range(len(list0)):
        if i < jump:
            continue
        if (min(len(list0), i + count) - i) <= 0:
            break
        sub0 = list0[i: min(len(list0), i + count)]

        for z in range(len(list1)):
            if z < j:
                continue

            sub1 = list1[z: min(len(list1), z + count)]
            score = alignment_score(sub0, sub1)

            if score > 0.99:
                while score > 0.99:
                    count += 1
                    sub0 = list0[i: min(len(list0), i + count)]
                    sub1 = list1[z: min(len(list1), z + count)]
                    score = alignment_score(sub0, sub1)

                    if (i + count) > len(list0) or (z + count) > len(list1):
                        break

                count -= 1

                if max(count, lastCount) == count:
                    result0 = (i, min(len(list0), i + count))
                    result1 = (z, min(len(list1), z + count))
                    lastCount = count

                jump = i + count
                j = z
                count = minCount
                break

    return result0, result1


def split_list(list0, list1, minCount=5):
    result0, result1 = [], []

    data0 = list0
    data1 = list1

    # while True:

    index0, index1 = best_similar(data0, data1)

    if len(index0) >= 2 and (index0[1] - index0[0]) >= minCount:

        item0 = data0[0: index0[0]]
        item1 = data1[0: index1[0]]
        if len(item0) > minCount and len(item0) > minCount:
            index00, index11 = best_similar(item0, item1)

        item0 = data0[index0[0]: index0[1]]
        item1 = data1[index1[0]: index1[1]]

        print(index0[0], item0)
        print(index1[0], item1)

        item0 = data0[index0[1]: len(data0)]
        item1 = data1[index1[1]: len(data1)]
        if len(item0) > minCount and len(item0) > minCount:
            index00, index11 = best_similar(item0, item1)

        # if index0[1] == len(item0) or index1[1] == len(item1):
        #     break
        # elif len(item0) > minCount and len(item1) > minCount:
        #     data0 = item0
        #     data1 = item1

        # result0.append((index0[0], index0[1]))
        # result1.append((index1[0], index1[1]))
    #
    # else:
    #     break

    return result0, result1


if __name__ == '__main__':
    srtTextsFile = '../1_srt.txt'
    textsFile = '../1.txt'

    srtLines = read_lines(srtTextsFile)
    txtLines = read_lines(textsFile)

    srtPinyins = texts_to_pinyins(srtLines)
    txtPinyins = texts_to_pinyins(txtLines)

    print(len(srtLines), len(txtLines), len(srtPinyins), len(txtPinyins))

    offset0 = 0
    offset1 = 0

    list0 = srtPinyins
    list1 = txtPinyins
    result0, result1 = split_list(list0, list1)
    print(result0, result1)

    # while True:
    # if len(result0) >= 3:
    #     list0 = srtPinyins[result0[0][0]:result0[0][1]]
    #     list1 = txtPinyins[result1[0][0]:result1[0][1]]
    #
    #     print("0", list0)
    #     print("0", list1)
    #
    #     offset0 += len(list0)
    #     offset1 += len(list1)
    #
    #     list0 = srtPinyins[result0[1][0]:result0[1][1]]
    #     list1 = txtPinyins[result1[1][0]:result1[1][1]]
    #
    #     print("1", list0)
    #     print("1", list1)
    #
    #     offset0 += len(list0)
    #     offset1 += len(list1)
    #
    #     list0 = srtPinyins[result0[2][0]:result0[2][1]]
    #     list1 = txtPinyins[result1[2][0]:result1[2][1]]
    #
    #     print("2", list0)
    #     print("2", list1)
    #
    #     offset0 += len(list0)
    #     offset1 += len(list1)
