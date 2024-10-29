from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
# from moviepy.video.tools.subtitles import SubtitlesClip, TextClip
# from moviepy.editor import VideoFileClip, concatenate_videoclips
# from moviepy.video.compositing import CompositeVideoClip
from moviepy.config import change_settings
from itertools import combinations, permutations, combinations_with_replacement


# asset = "D:\\CosyVoice\\asset"
# fontPath = "{}\\STHeitiMedium.ttc".format(asset)
#
# change_settings({"IMAGEMAGICK_BINARY": f"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})
#
# # fontPath = "D:\\CosyVoice\\asset\\STHeitiMedium.ttc"
# generator = lambda txt: TextClip(txt, font=fontPath, fontsize=48, color='white')
# subs = [((0, 2), 'sub1中文字幕'),
#         ((2, 4), 'subs2'),
#         ((4, 6), 'subs3'),
#         ((6, 8), 'subs4')]
#
# subtitles = SubtitlesClip(subs, generator)
#
# video = VideoFileClip("E:\\youtube\\test/video_out.mp4")
# video = video.subclip(0, 8)
# video = CompositeVideoClip([video, subtitles.set_pos(('center', 'bottom'))])
#
# video.write_videofile("test_output.mp4")

def same_text2(text0, text1):
    result = []
    flag = -1

    for i in range(len(text0)):
        char0 = text0[i]

        for j in range(len(text1)):
            char1 = text1[j]

            if j > flag and char0 == char1:
                flag = j
                result.append((i, j))
                break

    return result


def itemIn(item, filters):
    index = -1
    for i in range(len(filters)):
        target = filters[i]
        find = item[0] == target[0]
        if find:
            index = i
            break

    return index


def max_index(text0, text1, filters):
    maxCount = 0
    index0, index1, size = 0, 0, 0
    flag = -1
    for i in range(len(text0)):
        char0 = text0[i]
        check = itemIn((i, i), filters)
        if check >= 0:
            flag = filters[check][0] + filters[check][2]
            continue

        if i < flag:
            continue

        for j in range(len(text1)):
            count = 0
            char1 = text1[j]
            while char0 == char1:
                count += 1
                if (j + count) >= len(text1) or (i + count) >= len(text0):
                    break
                char0 = text0[i + count]
                char1 = text1[j + count]

            maxCount = max(count, maxCount)
            if maxCount == count:
                index0 = i
                index1 = j
                size = maxCount

    return index0, index1, size


def same_text(text0, text1):
    filters = []
    while True:
        index0, index1, maxCount = max_index(text0, text1, filters)
        # print("same_text", index0, index1, maxCount)
        if maxCount > 2:
            filters.append((index0, index1, maxCount))
        else:
            break

    def sort_text0(element):
        return int(element[0])

    # print(filters)
    filters.sort(key=sort_text0)
    print(filters)

    result = []

    from0, from1 = 0, 0
    for item in filters:
        to0, to1, count = item[0], item[1], item[2]

        sub0 = text0[from0:to0]
        sub1 = text1[from1:to1]

        same1 = same_text2(sub0, sub1)

        sub2 = text0[to0:to0 + count]
        sub3 = text1[to1:to1 + count]

        same2 = same_text2(sub2, sub3)

        # print("same1", same1)
        # print("same2", same2)
        #
        # print(sub0)
        # print(sub1)
        # print(sub2)
        # print(sub3)

        for s in same1:
            result.append((from0 + s[0], from1 + s[1]))

        for s in same2:
            result.append((to0 + s[0], to1 + s[1]))

        from0, from1 = to0 + count, to1 + count

    return result


def align_texts(text0, text1, marker="*"):
    same0 = same_text(text0, text1)

    count = len(same0) + (len(text0) - len(same0)) + (len(text1) - len(same0))
    print(count, len(same0), same0)

    result0, result1 = [], []

    index2 = 0
    index0, index1 = 0, 0
    to0, to1 = 0, 0

    for i in range(count):
        char0 = marker
        char1 = marker

        if index2 < len(same0):
            to0, to1 = same0[index2]
        else:
            to0, to1 = len(text0), len(text1)

        if index0 == to0 and index1 == to1:
            if index0 < len(text0):
                char0 = text0[index0]
                index0 += 1

            if index1 < len(text1):
                char1 = text1[index1]
                index1 += 1

            index2 += 1
        else:

            if index0 < to0:
                char0 = text0[index0]
                index0 += 1

            if index1 < to1:
                char1 = text1[index1]
                index1 += 1

        result0.append(char0)
        result1.append(char1)
        if index0 == len(text0) and index1 == len(text1):
            break

    # print(result0)
    # print(result1)
    return ''.join(result0), ''.join(result1)


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


def align_texts22(text0, text1, marker="*"):
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

    return ''.join(result0), ''.join(result1)


# 示例使用
text1 = "以后基本在任何地方都不可能在一到两年两到三年的时间里白手起家赚二十1套房子成为上虞代言人以后"
text2 = "基本在任何一个地方都不可能的在一到两年两到三年时间里白手起家赚20套房子成为上虞代言人以后"

result0, result1 = align_texts22(text1, text2)

print("result0:", len(result0), result0)
print("result1:", len(result1), result1)

# 错误的文本和正确的文本
# correct = "以后基本在任何地方都不可能在一到两年两到三年的时间里白手起家赚二十1套房子成为上虞代言人以后"
# erroneous = "基本在任何一个地方都不可能的在一到两年两到三年时间里白手起家赚20套房子成为上虞代言人以后"
#
# # 错误的文本和正确的文本
# # correct = "基本在任何地方"
# # erroneous = "基本在任何一个地方"
# # correct = "ABCDEFG"
# # erroneous = "GCDEFAB"
#
# result0, result1 = align_texts(correct, erroneous)
# # result0, result1 = reverse_text(correct), reverse_text(erroneous)
#
# print("result0:", result0)
# print("result1:", result1)
