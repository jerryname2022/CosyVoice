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


def alignment_score(A, B):
    lenA = len(A)
    lenB = len(B)
    if lenA == lenB:
        score = 0
        for index in range(lenA):
            charA = A[index]
            charB = B[index]
            if charA == "*" or charB == "*":
                continue
            if charA == charB:
                score += 1
        return score / lenA

    return 0


# 示例 1: 从字符串中选择组合
A = list('ABCDEEF')
B = list('ABF')
D = [None] * len(A)

outSize = len(A) - len(B)
# print(A)
positionsRange = range(len(B) + outSize)  # range(0, 8)

result = combinations(positionsRange, outSize)

print(list(result))

# for itemPositions in combinations(positionsRange, outSize):
#     # print(itemPositions, 5 in itemPositions)
#     flag = 0
#     for index in range(len(D)):
#         if index in itemPositions:
#             D[index] = '*'
#         else:
#             D[index] = B[flag]
#             flag += 1
#
#     print(D, alignment_score(A, D))


    # result = []
    # last_pos = 0
    # for pos in zero_positions:
    #     # 将字符串 s 中的字符添加到当前插入位置
    #     result.append(s[last_pos:pos])
    #     # 插入零
    #     result.append('*')
    #     last_pos = pos
    #
    # result.append(s[last_pos:])
    # print(result)
    # for pos in zero_positions:
    #     # 打印结果
    #     print(pos, zero_positions)



