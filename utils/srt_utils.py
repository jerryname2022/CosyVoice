#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# Copyright FunASR (https://github.com/alibaba-damo-academy/FunClip). All Rights Reserved.
#  MIT License  (https://opensource.org/licenses/MIT)

from utils.file_utils import read_lines, write_to_file
from utils.txt_utils import reset_texts, is_text


def parse_srt_texts(texts):
    """解析字幕数据 (srt 格式)
Args:
    filename: 字幕文件的路径
Returns:
    一个列表，每个元素是一个字典，包含字幕信息：
        {
            "start": 开始时间戳（秒），
            "end": 结束时间戳（秒），
            "text": 字幕内容
        }
    """

    subtitles = []
    status = 0

    for line in texts:
        line = line.strip()
        # print(line)
        if len(line) == 0:
            status = 0
        elif status == 0:  # 每一行字幕的编号
            # startIndex = int(line)
            subtitles.append({"start": None, "end": None, "text": "", "header": line})
            status = 1
        elif status == 1:  # 时间戳信息
            parts = line.split(" --> ")
            # startTime = parse_srt_time(parts[0])
            # endTime = parse_srt_time(parts[1])
            subtitles[-1]["start"] = parts[0]
            subtitles[-1]["end"] = parts[1]
            status = 2
        elif status == 2:  # 字幕内容
            subtitles[-1]["text"] += line + "\n"
            status = 0

    return subtitles


def parse_srt_file(filename):
    """解析字幕文件 (srt 格式)
    Args:
        filename: 字幕文件的路径
    Returns:
        一个列表，每个元素是一个字典，包含字幕信息：
            {
                "start": 开始时间戳（秒），
                "end": 结束时间戳（秒），
                "text": 字幕内容
            }
    """
    lines = read_lines(filename)
    return parse_srt_texts(lines)


def srt_texts_times(srtFile):
    subtitles = parse_srt_file(srtFile)

    times = []
    texts = []

    srtTimes = []
    srtTexts = []
    maxCount = 0

    for subtitle in subtitles:
        text = subtitle['text']
        start = float(parse_srt_time(subtitle['start']))
        end = float(parse_srt_time(subtitle['end']))
        duration = end - start

        srtTimes.append("{}:{}".format(start, end))
        srtTexts.append(text.strip())

        maxCount = max(maxCount, len(text.strip()))

        clear = ""
        for char in text:
            if is_text(char):
                clear += char

        if len(clear) > 0:
            charDuration = duration / len(clear)
            durationFlag = start + charDuration
            for char in clear:
                times.append(durationFlag)
                texts.append(char)
                durationFlag += charDuration

    return texts, times, srtTexts, srtTimes, maxCount


def srt_texts(subtitles):
    buffers = ""
    index = 1
    for subtitle in subtitles:
        text = subtitle['text']
        start = subtitle['start']
        end = subtitle['end']

        line0 = f'{index}\n'
        line1 = f'{start} --> {end}\n'
        line2 = f'{text}\n'
        line3 = f'\n'

        buffers += line0
        buffers += line1
        buffers += line2
        buffers += line3

        index += 1

    return buffers


def write_srt_file(subtitles, output):
    buffers = srt_texts(subtitles)
    write_to_file(output, buffers)


def parse_srt_time(formatTime):
    """解析时间戳字符串
    Args:
        formatTime: 时间戳字符串 (例如 "00:00:05,123")

    Returns:
        浮点数，表示秒数
    """
    hours, minutes, seconds = formatTime.split(':')
    seconds, milliseconds = seconds.split(',')
    seconds = float(seconds) + int(milliseconds) / 1000
    return int(hours) * 3600 + int(minutes) * 60 + seconds


def reset_srt(srtTxts, rightTxts):
    lines = []
    subtitles = parse_srt_texts(srtTxts)

    for i in range(len(subtitles)):
        subtitle = subtitles[i]
        text = subtitle['text'].strip()
        if len(text) > 0:
            lines.append(text)

    targets = reset_texts(lines, rightTxts)
    targetSubtitles = []

    index = 1
    for i in range(len(subtitles)):
        subtitle = subtitles[i]
        start = subtitle['start']
        end = subtitle['end']

        present: bool = str(i) in targets.keys()
        if present:
            text = targets[str(i)]
            targetSubtitles.append({"start": start, "end": end, "text": text})
            index += 1

    return targetSubtitles


if __name__ == '__main__':
    srtFile = f"../82.srt"
    txtFile = f"../82.txt"
    outFile = '../82_out.srt'
    srtTexts = read_lines(srtFile)
    txtTexts = read_lines(txtFile)

    subtitles = reset_srt(srtTexts, txtTexts)
    write_srt_file(subtitles, outFile)

    # subtitles = parse_srt_file(file)

    # for subtitle in subtitles:
    #     header = subtitle["header"].strip()
    #     text = subtitle['text'].strip()
    #
    #     start = subtitle['start']
    #     end = subtitle['end']
    #
    #     # duration = end - start
    #     print(header)
    #     print("{} --> {}".format(start, end))
    #     print(text)

    # print(len(subtitles))
