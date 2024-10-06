from moviepy.editor import *
import string, chardet, time, math, sys
from pypinyin import pinyin, lazy_pinyin, Style
from utils.log_utils import log_time
from utils.txt_utils import is_text, texts_to_pinyins
from utils.file_utils import write_to_file, read_lines
from utils.srt_utils import parse_srt_file, parse_srt_time

# sys.setrecursionlimit(2000)

fontPath = "D:\\east-capcha\\assets\\jyt.ttf"
fontColor = (0, 0, 0, 0xFF)
lineColor = (0x46, 0x4C, 0x4E, 0x20)
lineCount = 24
textCount = 40
widthRate = 0.88
heightRate = 0.88


def srt_to_texts(srtFile, textsFile):
    subtitles = parse_srt_file(srtFile)

    texts = ""
    for subtitle in subtitles:
        text = subtitle['text']

        start = float(parse_srt_time(subtitle['start']))
        end = float(parse_srt_time(subtitle['end']))

        if len(text) > 0:
            clear = ""
            for char in text:
                if is_text(char):
                    clear += char

            texts += f'{clear}\r'

    write_to_file(textsFile, texts.strip())


def clear_texts(textsFile, outFile):
    lines = read_lines(textsFile)

    texts = ""
    for line in lines:
        if len(line) > 0:
            loss = ""
            clear = ""
            for char in line:
                if is_text(char):
                    clear += char
                else:
                    if len(clear) > 0:
                        texts += f'{clear}\r'
                        clear = ""

                loss += char

            if len(clear) > 0:
                texts += f'{clear}\r'

    write_to_file(outFile, texts.strip())


def srt_to_times(srtFile, timesFile=None):
    subtitles = parse_srt_file(srtFile)

    # clearSubtitleTexts = ""
    textTimes = ""
    results = []

    for subtitle in subtitles:
        text = subtitle['text']
        start = float(parse_srt_time(subtitle['start']))
        end = float(parse_srt_time(subtitle['end']))
        duration = end - start

        clear = ""
        for char in text:
            if is_text(char):
                clear += char

        if len(clear) > 0:
            charDuration = duration / len(clear)
            durationFlag = start + charDuration
            for char in clear:
                results.append(durationFlag)
                textTimes += f'{durationFlag}\r'
                durationFlag += charDuration

        # clearSubtitleTexts += clear
        print(f"开始时间：{start} 秒")
        print(f"结束时间：{end} 秒")
        print(f"内容：{text}")

    # print(len(clearSubtitleTexts), clearSubtitleTexts)
    if timesFile is not None:
        write_to_file(timesFile, textTimes.strip())

    return results


def texts_to_lines(textsFile, outFile):
    lines = read_lines(textsFile)

    buffers = ""
    for index in range(len(lines)):
        text = lines[index].strip()
        for char in text:
            if is_text(char):
                buffers += f'{index}\r'

    write_to_file(outFile, buffers.strip())


def files_to_offsets(textsFile, timesFile, outFile):
    lines = read_lines(textsFile)
    times = read_lines(timesFile)

    buffers = ""
    count = 0
    for index in range(len(lines)):
        text = lines[index].strip()
        start = times[count].strip()

        if count == 0:
            start = 0

        for char in text:
            if is_text(char):
                count += 1

        if count >= len(times):
            count -= 1

        end = times[count].strip()

        buffers += f'{start}:{end}\r'
        print(text)

    write_to_file(outFile, buffers.strip())


count = 64
item = 2
srtFile = f"E:\\youtube\hlm\\{count}\\{count}-{item}.srt"
timesFile = f"E:\\youtube\hlm\\{count}\\{count}-{item}.times"
textFile = f"E:\\youtube\hlm\\{count}\\{count}-{item}.txt"

# srt_to_texts(srtFile, srtTextsFile)
# clear_texts(textFile, textsFile)
# srt_to_times(srtFile, timesFile)

srtFile = f"E:\\douyin\\videos\\车床介绍.srt"
txtFile = f"E:\\douyin\\videos\\车床介绍.txt"
lineFile = f"E:\\douyin\\videos\\车床介绍.lines"
timesFile = f"E:\\douyin\\videos\\车床介绍.times"
videosFile = f"E:\\douyin\\videos\\车床介绍.files"
offsetsFile = f"E:\\douyin\\videos\\车床介绍.offsets"

# srt_to_times(srtFile, timesFile)
files_to_offsets(txtFile, timesFile, offsetsFile)
# texts_to_lines(txtFile, lineFile)

# srtFile = './1.srt'
# timesFile = './1.times'
# textFile = './1.txt'
# srtTextsFile = './1_srt.txt'
# textsFile = './1.txt'

# srtLines = readLines(srtTextsFile)
# textLines = readLines(textsFile)
#
# resetRightSrt(srtLines, textLines)
