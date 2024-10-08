from moviepy.editor import *
import chardet, math
import numpy as np
from PIL import Image
import cv2, math
from pypinyin import pinyin, lazy_pinyin, Style


class VideoFrameClip(VideoClip):
    def __init__(self, coverPath, audioPath, size=(1920, 1080), fps=30, **kwargs):
        super().__init__(**kwargs)
        self.coverPath = coverPath
        self.audio = AudioFileClip(audioPath)
        self.duration = self.audio.duration
        self.fps = fps
        self.size = size

    def mask_frame(self, width, height, color, opacity):
        # Create a mask frame with the specified color and opacity
        mask_frame = np.zeros((height, width, 4), dtype=np.uint8)
        mask_frame[:, :, :3] = color  # Set RGB color
        mask_frame[:, :, 3] = int(opacity * 255)  # Set alpha channel
        return mask_frame

    def image_clip(self, t):
        image = ImageClip(self.coverPath.strip())
        return image

    def easeOutQuart(self, x):
        return 1 - math.pow(1 - x, 5)

    def make_frame(self, t):
        imageClip = self.image_clip(t)
        imageWidth, imageHeight = imageClip.size

        step = 0.000000001
        count = 1 / step

        start = 0
        end = self.duration
        atime = end - start

        mtime = min(max(0, t - start), atime)
        ftime = count - (count * mtime / atime)

        quart = self.easeOutQuart(ftime)
        total = self.easeOutQuart(count)

        scaleX = 1.1

        # scaleX = 1 + 0.5 * (1 - quart / total)
        # scaleX = 1 + 0.5 * (quart / total)

        targetWidth = int(scaleX * self.size[0])
        targetHeight = int(scaleX * self.size[1])

        if targetWidth % 2 != 0:
            targetWidth += 1

        if targetHeight % 2 != 0:
            targetHeight += 1

        targetFrame = np.array(imageClip.resize(newsize=(targetWidth, targetHeight)).get_frame(t))

        distanceX = targetWidth - self.size[0]
        distanceY = targetHeight - self.size[1]

        fromX = int(distanceX * quart / total)  # int(t * distanceX / self.duration)
        # fromX = int(distanceX * (1 - quart / total))  # int(t * distanceX / self.duration)
        fromY = (targetHeight - self.size[1]) // 2

        # fromX = (targetWidth - self.size[0]) // 2  # int(t * distanceX / self.duration)
        # fromY = (targetHeight - self.size[1]) // 2

        toX = fromX + self.size[0]
        toY = fromY + self.size[1]

        return targetFrame[fromY:toY, fromX:toX]


def readLines(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
        encoding = chardet.detect(data)['encoding']

    if os.path.isfile(filepath):
        texts = open(filepath, encoding=encoding).readlines()
        return texts

    return None


coverPath = "E:\\youtube\\test\\image.png"
audioPath = "E:\\youtube\\test\\audio.wav"
outputPath = "E:\\youtube\\test\\gif_out.mp4"
gif1 = "C:\\Users\\Administrator\\Pictures\\gif1.gif"


# watermark = VideoFileClip(gif1, has_mask=True)  # loop gif
# print(watermark.duration)
# watermark.write_videofile(outputPath, codec='libx264', audio_codec='aac')

# videoClip = VideoFrameClip(coverPath, audioPath, size=(512, 512))
# videoClip.write_videofile(outputPath, codec='libx264', audio_codec='aac')


def alignmentScore(listA, listB, alignment='*'):
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


def bestAlignment(list0, list1, alignment='*'):
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
    print("reverse", reverse0Sames, reverse1Sames)
    print("order", order0Sames, order1Sames)

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
    print(len(list0), len(list1))

    result0, result1 = [], []

    count = minCount
    j = 0
    jump = 0
    for i in range(len(list0)):
        # char0 = list0[i]
        if i < jump:
            continue

        sub0 = list0[i: min(len(list0), i + count)]

        for z in range(len(list1)):
            if z < j:
                continue

            sub1 = list1[z: min(len(list1), z + count)]
            score = alignmentScore(sub0, sub1)

            if score > 0.99:
                while score > 0.99:
                    count += 1
                    sub0 = list0[i: min(len(list0), i + count)]
                    sub1 = list1[z: min(len(list1), z + count)]
                    score = alignmentScore(sub0, sub1)

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


def isText(char):
    """判断字符是否为字母或数字。"""
    return char.isalpha() or char.isdigit()


def textsToPinyins(texts):
    pinyins = []
    for text in texts:
        # clear = ""
        for char in text:
            if isText(char):
                charPinyin = lazy_pinyin(char.strip())  # []
                pinyins.extend(charPinyin)
                # clear += char.strip()
        # clearTexts += clear
        # print(text)
        # print(clear)
    return pinyins


# srtTextsFile = './1_srt.txt'
# textsFile = './1_text.txt'
#
# # 示例
# A = ['bian', 'ming']
# B = ['er', 'bian', 'jiao']
# print(A)
# print(B)
#
# # bestAlignment(A, B)
# result0, result1 = bestAlignment(A, B)
# print(result0)
# print(result1)

# for i in range(1):
#     print(i)
# parts = "4.png".split(" --> ")
#
# print(parts)


# import cupy as cp
import numpy as np
from scipy.ndimage import zoom

# videoPath = "E:\\douyin\\章太炎\\周树人.jfif"
# image = Image.open(videoPath).convert('RGB')
# print("image", image.size)
#
# imageClip = ImageClip(np.array(image))
# frame = np.array(imageClip.get_frame(0), dtype=np.uint8)
# print("frame0", frame.shape)
#
# frame = np.array(imageClip.get_frame(0), dtype=np.uint8)
# print("frame1", frame.shape)
#
# scale = 1.2
# newW, newH = int(scale * frame.shape[1]), int(scale * frame.shape[0])
# newSize = (newH, newW)
#
# # zoomFrame = np.resize(frame, newSize)  # (H, W, C)
#
# factors = (newH / frame.shape[0], newW / frame.shape[1], 1)  # (H, W, C)
# zoomFrame = np.array(zoom(frame, factors, order=3))  # 使用三次插值
#
# print("zoomFrame", zoomFrame.shape)
#
# imageSave = Image.fromarray(zoomFrame)
# imageSave.save('3.jpg')
from moviepy.config import change_settings

change_settings({"IMAGEMAGICK_BINARY": f"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})

text = "他的条件是：将来中国派使到伦敦去的时候".strip()
text2 = "  中西的关系是特别的。在鸦片战净以前，我们不肯给外国平等待遇".strip()

fontPath = "D:\\CosyVoice\\asset\\TW-Kai-98_1.ttf"
textClip = TextClip(text, font=fontPath, fontsize=48, color='white')
textClip2 = TextClip(text2, font=fontPath, fontsize=48, color='white')

print(textClip.size, textClip2.size)
# (685, 56) (1072, 56)
