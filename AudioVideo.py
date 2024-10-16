import os

from moviepy.editor import *
import numpy as np
import cupy as cp
import cv2, math, random
from utils.file_utils import read_lines
from utils.srt_utils import parse_srt_time, srt_texts_times
from utils.txt_utils import is_text
from PIL import Image, ImageDraw, ImageFont
from moviepy.video.fx.resize import resize
from itertools import combinations


class BaseClip(VideoClip):
    def __init__(self, duration, size=(1920, 1080), fps=30):
        super().__init__()
        self.duration = duration
        self.fps = fps
        self.size = size

    def to_array(self, frame):
        frame = cp.array(frame, dtype=cp.uint8)
        return frame

    def create_frame(self, width, height, color):
        # Create a mask frame with the specified color and opacity
        newFrame = cp.zeros((height, width, 3), dtype=cp.uint8)
        # newFrame = torch.zeros((height, width, 3), device=self.device, dtype=torch.uint8)
        # newFrame = np.zeros((height, width, 3), dtype=np.uint8)
        # newFrame[:, :, :3] = color  # Set RGB color
        newFrame[:, :, 0] = color[0]
        newFrame[:, :, 1] = color[1]
        newFrame[:, :, 2] = color[2]
        return newFrame

    def location(self, background, frame, x, y, endY=True, endX=True, opacity=1):

        w, h = background.shape[1], background.shape[0]
        fw, fh = frame.shape[1], frame.shape[0]

        toX, toY = x + fw, y + fh

        boxW = min(toX, w) - max(0, x)
        boxH = min(toY, h) - max(0, y)

        bx, by = max(0, x), max(0, y)
        fx, fy = fw - boxW, fh - boxH

        if not endX:
            fx = 0

        if not endY:
            fy = 0

        if boxW > 0 and boxH > 0:
            alpha = opacity

            background[by:by + boxH, bx:bx + boxW] = alpha * frame[fy:fy + boxH, fx:fx + boxW] + (
                    1 - alpha) * background[by:by + boxH, bx:bx + boxW]

    def alpha_in(self, background, frame, ctime, duration=0.8):

        w, h = background.shape[1], background.shape[0]
        fw, fh = frame.shape[1], frame.shape[0]

        diffW = w - fw
        diffH = h - fh

        x = diffW // 2
        y = diffH // 2

        alpha = min(ctime, duration) / duration
        self.location(background, frame, x, y, opacity=alpha)

    def left_in(self, background, frame, toX, toY, ctime, duration=0.8, move=True):
        step = 0.000000001
        count = 1 / step

        w, h = background.shape[1], background.shape[0]
        fw, fh = frame.shape[1], frame.shape[0]

        ftime = count - (count * ctime / duration)

        quart = self.ease_quart(ftime)
        total = self.ease_quart(count)

        progress = (1 - quart / total)
        distance = int((toX + fw) * progress)

        x = distance - fw
        y = toY

        if not move:
            distance = int(fw * progress)
            frame = frame[:, :distance]
            x = toX
            y = toY

        self.location(background, frame, x, y)

    def right_in(self, background, frame, toX, toY, ctime, duration=0.8, move=True):
        step = 0.000000001
        count = 1 / step

        w, h = background.shape[1], background.shape[0]
        fw, fh = frame.shape[1], frame.shape[0]

        ftime = count - (count * ctime / duration)

        quart = self.ease_quart(ftime)
        total = self.ease_quart(count)

        progress = (1 - quart / total)
        distance = int((w - toX) * progress)

        x = w - distance
        y = toY

        if not move:
            distance = int(fw * progress)
            frame = frame[:, fw - distance:]
            x = toX + fw - distance
            y = toY

        self.location(background, frame, x, y, endX=False)

    def top_in(self, background, frame, toX, toY, ctime, duration=0.8, move=True):
        step = 0.000000001
        count = 1 / step

        w, h = background.shape[1], background.shape[0]
        fw, fh = frame.shape[1], frame.shape[0]

        ftime = count - (count * ctime / duration)

        quart = self.ease_quart(ftime)
        total = self.ease_quart(count)

        progress = (1 - quart / total)
        distance = int((toY + fh) * progress)

        x = toX
        y = distance - fh

        if not move:
            distance = int(fh * progress)
            frame = frame[:distance, :]
            x = toX
            y = toY

        self.location(background, frame, x, y)

    def bottom_in(self, background, frame, toX, toY, ctime, duration=0.8, move=True):
        step = 0.000000001
        count = 1 / step

        w, h = background.shape[1], background.shape[0]
        fw, fh = frame.shape[1], frame.shape[0]

        ftime = count - (count * ctime / duration)

        quart = self.ease_quart(ftime)
        total = self.ease_quart(count)

        progress = (1 - quart / total)
        distance = int((h - toY) * progress)

        x = toX
        y = h - distance

        if not move:
            distance = int(fh * progress)
            frame = frame[fh - distance:, :]
            x = toX
            y = toY + fh - distance

        self.location(background, frame, x, y, endY=False)

    def right_out(self, background, frame, fromX, fromY, ctime, duration=0.8):
        step = 0.000000001
        count = 1 / step

        w, h = background.shape[1], background.shape[0]
        fw, fh = frame.shape[1], frame.shape[0]

        ftime = count - (count * ctime / duration)

        quart = self.ease_quart(ftime)
        total = self.ease_quart(count)

        progress = (1 - quart / total)
        # distance = int((w + fw - fromX) * progress)
        distance = int((w - fromX) * progress)

        x = fromX + distance
        y = fromY

        self.location(background, frame, x, y, endX=False)

    def left_out(self, background, frame, fromX, fromY, ctime, duration=0.8):
        step = 0.000000001
        count = 1 / step

        w, h = background.shape[1], background.shape[0]
        fw, fh = frame.shape[1], frame.shape[0]

        ftime = count - (count * ctime / duration)

        quart = self.ease_quart(ftime)
        total = self.ease_quart(count)

        progress = (1 - quart / total)
        distance = int((fw + fromX) * progress)

        x = fromX - distance
        y = fromY

        self.location(background, frame, x, y)

    def top_out(self, background, frame, fromX, fromY, ctime, duration=0.8):
        step = 0.000000001
        count = 1 / step

        w, h = background.shape[1], background.shape[0]
        fw, fh = frame.shape[1], frame.shape[0]

        ftime = count - (count * ctime / duration)

        quart = self.ease_quart(ftime)
        total = self.ease_quart(count)

        progress = (1 - quart / total)
        distance = int((fh + fromY) * progress)

        x = fromX
        y = fromY - distance

        self.location(background, frame, x, y)

    def bottom_out(self, background, frame, fromX, fromY, ctime, duration=0.8):
        step = 0.000000001
        count = 1 / step

        w, h = background.shape[1], background.shape[0]
        fw, fh = frame.shape[1], frame.shape[0]

        ftime = count - (count * ctime / duration)

        quart = self.ease_quart(ftime)
        total = self.ease_quart(count)

        progress = (1 - quart / total)
        # distance = int((fh + h - fromY) * progress)
        distance = int((h - fromY) * progress)

        x = fromX
        y = fromY + distance

        self.location(background, frame, x, y, endY=False)

    def is_image(self, name):
        images = (
            '.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff', '.jfif', '.webp',
            '.image', '.jpg_large')
        return name.lower().endswith(images)

    def is_text(self, name):
        images = ('.txt', '.text')
        return name.lower().endswith(images)

    def is_book(self, name):
        images = ('.book',)
        return name.lower().endswith(images)

    def ease_quart(self, x):
        return 1 - math.pow(1 - x, 5)


class MediaScaleClip(BaseClip):
    def __init__(self, mediaClip, scaleFrom, scaleTo, size=(1920, 1080), fps=30):
        super().__init__(mediaClip.duration, size=size, fps=fps)
        self.mediaClip = mediaClip
        self.scaleFrom = scaleFrom
        self.scaleTo = scaleTo

    def make_frame(self, t):

        # (scale - scaleFrom)  / (scaleTo - scaleFrom) = t /  duration
        scale = t * (self.scaleTo - self.scaleFrom) / self.duration + self.scaleFrom

        color = (0xf2, 0xf4, 0xf5)
        width, height = self.size[0], self.size[1]
        background = self.create_frame(width, height, color)

        fh = int(scale * self.mediaClip.size[1])
        fw = int(scale * self.mediaClip.size[0])

        if fw % 2 != 0:
            fw += 1

        if fh % 2 != 0:
            fh += 1

        frame = self.to_array(resize(self.mediaClip, newsize=(fw, fh)).get_frame(t))

        offsetX = width - frame.shape[1]
        offsetY = height - frame.shape[0]

        x = offsetX // 2
        y = offsetY // 2

        self.location(background, frame, x, y)
        return background


class TxtClip(BaseClip):
    def __init__(self, mediaClip, text, fontColor=(0, 0, 0, 0xFF), fontPath=f"D:\\CosyVoice\\asset\\TW-Kai-98_1.ttf",
                 direction="ltr",  # 它可以是'rtl'（从右到左），'ltr'（从左到右）或'ttb'（从上到下）。需要libraqm。
                 size=(1920, 1080), fps=30):
        super().__init__(mediaClip.duration, size=size, fps=fps)

        self.mediaClip = mediaClip
        self.text = text
        self.fontColor = fontColor
        self.fontPath = fontPath
        self.direction = direction

        self.setup_media()

    def font_Size(self, image, imageDraw, textCount, fontPath, rate=0.8):
        width, height = image.size
        maxWidth = int(rate * width)
        maxHeight = int(rate * height)

        calculateTexts = ""
        for index in range(textCount + 1):
            calculateTexts += "趣"

        calculateSize = 10

        while True:
            # left, top, right, bottom = imageDraw.textbbox((0, 0), calculateTexts,
            #                                               font=ImageFont.truetype(fontPath, size=calculateSize))
            # textWidth = right - left
            # textHeight = bottom - top
            textWidth, textHeight = imageDraw.textsize(calculateTexts,
                                                       font=ImageFont.truetype(fontPath, size=calculateSize),
                                                       direction=self.direction)
            calculateSize += 2

            if (textWidth > maxWidth or textHeight > maxHeight):
                break

        return calculateSize

    def setup_media(self):

        height = int(self.size[1] * 0.15)

        imageClip = self.mediaClip

        frame = imageClip.get_frame(0)
        image = Image.fromarray(np.array(frame))

        imageDraw = ImageDraw.Draw(image)
        fontSize = self.font_Size(image, imageDraw, len(self.text), self.fontPath, rate=0.8)

        text = self.text
        textWidth, textHeight = imageDraw.textsize(text,
                                                   font=ImageFont.truetype(self.fontPath, size=fontSize),
                                                   direction=self.direction)

        # image = Image.new('RGBA', (textWidth + 2 * margin, textHeight + 2 * margin), color=color)
        imageDraw = ImageDraw.Draw(image)
        x = (image.size[0] - textWidth) // 2
        y = (image.size[1] - textHeight) // 2

        imageDraw.text((x, y), text, self.fontColor, font=ImageFont.truetype(self.fontPath, size=fontSize),
                       direction=self.direction)
        textClip = ImageClip(np.array(image))

        width, height = textClip.size[0], textClip.size[1]

        scaleW = self.size[0] / width
        scaleH = self.size[1] / height

        scale = min(scaleW, scaleH)
        targetSize = (int(width * scale), int(height * scale))

        textClip = resize(textClip, newsize=targetSize)

        self.textClip = textClip

    def txt_frame(self, t):
        textClip = self.textClip
        frame = self.to_array(textClip.get_frame(0))
        return frame

    def make_frame(self, t):

        color = (0xf2, 0xf4, 0xf5)
        width, height = self.size[0], self.size[1]
        background = self.create_frame(width, height, color)

        frame = self.txt_frame(t)

        offsetX = width - frame.shape[1]
        offsetY = height - frame.shape[0]

        x = offsetX // 2
        y = offsetY // 2

        self.location(background, frame, x, y)
        return background


class SrtClip(BaseClip):
    def __init__(self, audioFile, srtFile, size=(1920, 1080), fps=30, coverPath=None, musicPath=None,
                 fontColor=(0, 0, 0, 0xFF),
                 fontPath=f"D:\\CosyVoice\\asset\\TW-Kai-98_1.ttf"):

        audio = AudioFileClip(audioFile)
        if os.path.exists(musicPath):
            music = AudioFileClip(musicPath)
            music = music.fx(afx.audio_loop, duration=audio.duration)
            audio = CompositeAudioClip([audio.volumex(1.2), music.volumex(0.1)])

        super().__init__(audio.duration, size=size, fps=fps)

        self.backgroundColor = (0xf2, 0xf4, 0xf5)
        texts, times, srtTexts, srtTimes, maxCount = srt_texts_times(srtFile)
        self.audioFile = audioFile

        if os.path.exists(coverPath):
            image = Image.open(coverPath).convert('RGB')
            self.coverClip = ImageClip(np.array(image))

        self.audio = audio
        self.srtFile = srtFile
        self.texts = texts
        self.times = times
        self.srtTexts = srtTexts
        self.srtTimes = srtTimes
        self.maxCount = maxCount
        self.fontColor = fontColor
        self.fontPath = fontPath

        self.setup_srt()

        print("texts times ... ", len(texts), len(times))

    def font_Size(self, image, imageDraw, textCount, fontPath, rate=0.8):
        width, height = image.size
        maxWidth = int(rate * width)
        maxHeight = int(rate * height)

        calculateTexts = ""
        for index in range(textCount + 1):
            calculateTexts += "趣"

        calculateSize = 10

        while True:
            # left, top, right, bottom = imageDraw.textbbox((0, 0), calculateTexts,
            #                                               font=ImageFont.truetype(fontPath, size=calculateSize))
            # textWidth = right - left
            # textHeight = bottom - top
            textWidth, textHeight = imageDraw.textsize(calculateTexts,
                                                       font=ImageFont.truetype(fontPath, size=calculateSize))
            calculateSize += 2

            if (textWidth > maxWidth or textHeight > maxHeight):
                break

        return calculateSize

    def setup_srt(self):
        width = self.size[0]
        height = int(self.size[1] * 0.15)

        margin = int(height * 0.1)

        color = (self.backgroundColor[0], self.backgroundColor[1],
                 self.backgroundColor[2], 0x00)

        image = Image.new('RGBA', (width, height), color=color)
        imageDraw = ImageDraw.Draw(image)
        fontSize = self.font_Size(image, imageDraw, self.maxCount, self.fontPath, rate=0.8)

        colorOffset = 15
        fillColor = (self.backgroundColor[0] - colorOffset, self.backgroundColor[1] - colorOffset,
                     self.backgroundColor[2] - colorOffset)

        srtTextClips = []
        for text in self.srtTexts:
            textWidth, textHeight = imageDraw.textsize(text,
                                                       font=ImageFont.truetype(self.fontPath, size=fontSize))

            image = Image.new('RGBA', (textWidth + 2 * margin, textHeight + 2 * margin), color=color)
            imageDraw = ImageDraw.Draw(image)
            x = (image.size[0] - textWidth) // 2
            y = (image.size[1] - textHeight) // 2

            imageDraw.rectangle([x - margin, y - margin, x + textWidth + margin, y + textHeight + margin],
                                fill=fillColor)

            imageDraw.text((x, y), text, self.fontColor, font=ImageFont.truetype(self.fontPath, size=fontSize))
            textClip = ImageClip(np.array(image))

            srtTextClips.append(textClip)

            image = Image.new('RGBA', (width, height), color=color)
            imageDraw = ImageDraw.Draw(image)

        self.srtTextClips = srtTextClips

    def text_index(self, t):
        index = 0
        for item in self.times:
            ftime = float(item)
            if ftime > t:
                return index
            if index < (len(self.times) - 1):
                index += 1
        return index

    def srt_index(self, t):
        index = -1
        for item in self.srtTimes:
            ft, tt = float(item.split(":")[0]), float(item.split(":")[1])
            if ft >= t and t <= tt:
                return index
            if index < (len(self.srtTimes) - 1):
                index += 1

        return index

    def srt_frame(self, t):
        srtIndex = self.srt_index(t)
        if srtIndex >= 0:
            textClip = self.srtTextClips[srtIndex]

            frame = self.to_array(textClip.get_frame(0))
            return frame
        return None


class FileClip(SrtClip):
    def __init__(self, textsFile, filesPath, audioFile, srtFile, size=(1920, 1080), fps=30, coverPath=None,
                 musicPath=None):
        super().__init__(audioFile=audioFile, srtFile=srtFile, size=size, fps=fps, coverPath=coverPath,
                         musicPath=musicPath)

        self.setup_texts(textsFile)
        self.setup_medias(filesPath)

    def setup_texts(self, textsFile):
        print("setup texts ... ")

        lines = read_lines(textsFile)
        count = 0
        for index in range(len(lines)):
            count += len(lines[index].strip())

        lineTimes = []
        textLines = []

        count = 0
        for index in range(len(lines)):
            text = lines[index].strip()
            start = self.times[count]

            if count == 0:
                start = 0

            for char in text:
                if is_text(char):
                    count += 1
                    textLines.append(index)

            if count >= len(self.times):
                count -= 1

            end = self.times[count]
            lineTimes.append(f'{start}:{end}')

        self.textLines = textLines
        self.lineTimes = lineTimes

        print("lines lineTimes textLines ... ", len(lines), len(lineTimes), len(textLines))

    def index_location(self, index, row=2, col=2):
        width, height = self.size[0], self.size[1]

        itemWidth = width // row
        itemHeight = height // col

        totalWidth = index * itemWidth
        rowWidth = totalWidth - int(totalWidth / width) * width

        colIndex = int((totalWidth + width) / width) - 1  # 列
        rowIndex = int((rowWidth + itemWidth) / itemWidth) - 1  # 行

        if colIndex < 0:
            colIndex = 0
        if rowIndex < 0:
            rowIndex = 0

        x = rowIndex * itemWidth
        y = colIndex * itemHeight

        return (x, y, itemWidth, itemHeight)

    def row_col(self, size):
        row, col = 1, 1
        if size == 2:
            row = 2
            col = 1
            if self.size[1] > self.size[0]:
                row = 1
                col = 2
        elif size > 2:
            col = 2
            row = size // col
            if (row * col) < size:
                row += 1
            if self.size[1] > self.size[0]:
                tmp = row
                row = col
                col = tmp

        return row, col

    def setup_medias(self, filesPath):
        print("setup medias ... ")
        folder = os.path.dirname(self.audioFile)
        lines = read_lines(filesPath)

        lineTags = {}
        lastTag = ""
        flag = 1

        for i in range(len(lines)):
            line = lines[i]
            parts = line.split(" --> ")
            if len(parts) > 0:
                endTags = parts[1].split(" ")
                tag = ""
                if len(endTags) > 1:
                    tag = endTags[1].strip()

                if len(tag) > 0 and tag == lastTag:
                    flag += 1
                else:
                    if flag > 1:
                        lineTags[i - 1] = flag
                    flag = 1

                lastTag = tag

        if flag > 1:
            lineTags[len(lines) - 1] = flag

        # print(len(lineTags), lineTags)
        keys = list(lineTags.keys())
        for key in keys:
            count = lineTags[key]
            for i in range(count):
                lineTags[key - i] = count

        # print(len(lineTags), lineTags)
        for i in range(len(lines)):
            exist = i in lineTags.keys()
            if not exist:
                lineTags[i] = 1

        # print(len(lineTags), lineTags)

        medias = []
        scenes = []

        scene = lineTags[0]  # random.randint(1, 4)
        locations = list(range(scene))
        row, col = self.row_col(scene)

        randomLocations = list(combinations(locations, scene))
        randomLocations = randomLocations[len(randomLocations) // 2]
        count = 0
        sceneIndex = 0

        sceneWidth = int(self.size[0] * 0.8) // row
        sceneHeight = int(self.size[1] * 0.8) // col

        for i in range(len(lines)):
            line = lines[i]
            parts = line.split(" --> ")
            if len(parts) > 0:
                filename = parts[0].split(" ")[0]
                videoPath = os.path.join(folder, filename)
                isImage = self.is_image(filename)
                isText = self.is_text(filename)
                isBook = self.is_book(filename)

                if count >= scene:
                    scene = lineTags[i]  # random.randint(1, 4)

                    locations = list(range(scene))
                    row, col = self.row_col(scene)

                    sceneWidth = int(self.size[0] * 0.8) // row
                    sceneHeight = int(self.size[1] * 0.8) // col

                    randomLocations = list(combinations(locations, scene))
                    randomLocations = randomLocations[len(randomLocations) // 2]

                    count = 0
                    sceneIndex += 1

                mediaIn = random.randint(1, 8)
                mediaOut = random.randint(1, 4)

                start = parse_srt_time(parts[0].split(" ")[1])
                end = parse_srt_time(parts[1].split(" ")[0])

                locationIndex = randomLocations[count]
                location = self.index_location(locationIndex, row=row, col=col)

                if isImage:
                    image = Image.open(videoPath).convert('RGB')
                    imageClip = ImageClip(np.array(image)).set_duration(2).set_fps(self.fps)
                    # imageClip = ImageClip(cp.asnumpy(image))
                    # imageClip = ImageClip(np.array(image))
                    width, height = imageClip.size[0], imageClip.size[1]
                    scaleW = sceneWidth / width
                    scaleH = sceneHeight / height

                    scale = min(scaleW, scaleH)
                    targetSize = (int(width * scale), int(height * scale))

                    videoClip = resize(imageClip, newsize=targetSize)
                    # videoClip = resize(ImageClip(videoPath), newsize=self.size)
                elif isText or isBook:

                    text = filename.split(".")[0]

                    direction = "ltr"
                    if isText:
                        color = self.backgroundColor
                        newFrame = np.zeros((sceneWidth, sceneHeight, 3), dtype=np.uint8)
                        newFrame[:, :, :3] = color

                        imageClip = ImageClip(newFrame).set_duration(2).set_fps(self.fps)
                    else:
                        direction = "ttb"
                        bookPath = "E:\\douyin\\书面.png"
                        image = Image.open(bookPath).convert('RGB')
                        imageClip = ImageClip(np.array(image)).set_duration(2).set_fps(self.fps)

                    videoClip = TxtClip(imageClip, text, size=(sceneWidth, sceneHeight), direction=direction)

                else:
                    videoClip = VideoFileClip(videoPath, has_mask=True).subclip(start, end)
                    width, height = videoClip.size[0], videoClip.size[1]
                    scaleW = sceneWidth / width
                    scaleH = sceneHeight / height

                    scale = min(scaleW, scaleH)
                    targetSize = (int(width * scale), int(height * scale))

                    videoClip = videoClip.resize(newsize=targetSize)
                    # videoClip = VideoFileClip(videoPath).subclip(start, end).resize(newsize=self.size)

                if scene > 1 and count == 0:  # 对齐
                    sceneWidth = min(sceneWidth, videoClip.size[0])
                    sceneHeight = min(sceneHeight, videoClip.size[1])

                scaleClip = videoClip
                if isImage and scene == 1:
                    scaleFrom = 1
                    scaleTo = 1.2

                    scaleClip = MediaScaleClip(videoClip, scaleFrom, scaleTo,
                                               size=(
                                                   int(videoClip.size[0] * scaleTo), int(videoClip.size[1] * scaleTo)))

                medias.append((videoClip, scaleClip, start, end, isImage, mediaIn, mediaOut, location))
                scenes.append((count, scene))

                count += 1

        self.medias = medias
        self.scenes = scenes

        print("scenes", scenes)

    def file_frame(self, line, t):

        parts = self.lineTimes[line].split(":")
        if len(parts) > 1:
            audioStart = float(parts[0])
            audioEnd = float(parts[1])

            videoClip, scaleClip, videoStart, videoEnd, isImage, mediaIn, mediaOut, location = self.medias[line]

            t = min(max(t, audioStart), audioEnd)
            fileDuration = videoEnd - videoStart
            audioDuration = audioEnd - audioStart
            ft = (t - audioStart) * fileDuration / audioDuration

            frame = self.to_array(videoClip.get_frame(ft))
            # frame = np.array(videoClip.get_frame(ft), dtype=np.uint8)
            # frame = torch.tensor(videoClip.get_frame(ft), device=self.device, dtype=torch.uint8)

            return frame, scaleClip, (t - audioStart), audioDuration, mediaIn, mediaOut, location, isImage

        return None

    def make_frame(self, t):

        width, height = self.size[0], self.size[1]
        color = self.backgroundColor

        background0 = self.create_frame(width, height, color)
        background = self.create_frame(width, height, color)

        if t <= 0.1 and self.coverClip is not None:
            frame = self.to_array(self.coverClip.get_frame(0))
            fw, fh = frame.shape[1], frame.shape[0]
            offsetX = width - fw
            offsetY = height - fh
            x = offsetX // 2
            y = offsetY // 2
            self.location(background, frame, x, y)
        else:
            textIndex = self.text_index(t)
            lineIndex = int(self.textLines[textIndex])

            mediaIndex, mediaCount = self.scenes[lineIndex][0], self.scenes[lineIndex][1]
            count = mediaIndex + 1
            fromIndex = lineIndex - count

            # w, h = background.shape[1], background.shape[0]

            for i in range(count):
                textLine = fromIndex + 1 + i
                frame, scaleClip, ft, fd, mediaIn, mediaOut, location, isImage = self.file_frame(textLine, t)
                fx, fy, itemWidth, itemHeight = location[0], location[1], location[2], location[3]

                fWidth, fHeight = frame.shape[1], frame.shape[0]
                offsetX = itemWidth - fWidth
                offsetY = itemHeight - fHeight
                x = fx + offsetX // 2
                y = fy + offsetY // 2

                inTime = 1.2
                outTime = 1.0

                if i == mediaIndex and ft < inTime:
                    # self.left_in(background, frame, x, y, ft, duration=inTime, move=False)
                    # self.right_in(background, frame, x, y, ft, duration=inTime, move=False)
                    # self.top_in(background, frame, x, y, ft, duration=inTime, move=False)
                    # self.bottom_in(background, frame, x, y, ft, duration=inTime, move=False)

                    if mediaIn == 1:
                        self.bottom_in(background, frame, x, y, ft, duration=inTime)
                    elif mediaIn == 2:
                        self.top_in(background, frame, x, y, ft, duration=inTime)
                    elif mediaIn == 3:
                        self.right_in(background, frame, x, y, ft, duration=inTime)
                    elif mediaIn == 4:
                        self.left_in(background, frame, x, y, ft, duration=inTime)
                    elif mediaIn == 5:
                        self.bottom_in(background, frame, x, y, ft, duration=inTime, move=False)
                    elif mediaIn == 6:
                        self.top_in(background, frame, x, y, ft, duration=inTime, move=False)
                    elif mediaIn == 7:
                        self.right_in(background, frame, x, y, ft, duration=inTime, move=False)
                    else:
                        self.left_in(background, frame, x, y, ft, duration=inTime, move=False)
                elif (textLine + 1) != len(self.medias) and i == (mediaCount - 1) and ft > (fd - outTime):
                    # self.right_out(background, frame, x, y, ft - (fd - outTime), duration=outTime)
                    # self.left_out(background, frame, x, y, ft - (fd - outTime), duration=outTime)
                    # self.top_out(background, frame, x, y, ft - (fd - outTime), duration=outTime)
                    # self.bottom_out(background, frame, x, y, ft - (fd - outTime), duration=outTime)

                    self.location(background, frame, x, y)
                    frame = background
                    background = background0
                    x = 0
                    y = 0

                    ft = ft - (fd - outTime)
                    if mediaIn == 1:
                        self.bottom_out(background, frame, x, y, ft, duration=outTime)
                    elif mediaIn == 2:
                        self.top_out(background, frame, x, y, ft, duration=outTime)
                    elif mediaIn == 3:
                        self.right_out(background, frame, x, y, ft, duration=outTime)
                    else:
                        self.left_out(background, frame, x, y, ft, duration=outTime)
                else:

                    if isImage and mediaCount == 1:
                        ad = fd - (outTime + inTime)
                        ft = ft - inTime
                        # ft / ad = rt / duration
                        rt = scaleClip.duration * ft / ad
                        frame = self.to_array(scaleClip.get_frame(rt))
                        offsetX = width - frame.shape[1]
                        offsetY = height - frame.shape[0]

                        x = offsetX // 2
                        y = offsetY // 2

                    self.location(background, frame, x, y)

            srtFrame = self.srt_frame(t)
            if srtFrame is not None:
                fWidth, fHeight = srtFrame.shape[1], srtFrame.shape[0]
                offsetX = width - fWidth
                x = offsetX // 2
                y = height - int(fHeight * 1.1)
                self.location(background, srtFrame, x, y, opacity=0.75)

        return background
        # return background.cpu().numpy()


musicPath = "E:\\douyin\\music1.mp3"

# audioPath = "E:\\douyin\\videos\\车床介绍.wav"
# filesPath = "E:\\douyin\\videos\\车床介绍.files"
# srtPath = "E:\\douyin\\videos\\车床介绍.srt"
# textPath = "E:\\douyin\\videos\\车床介绍.txt"
#
# outputPath = "E:\\douyin\\videos\\车床介绍.mp4"

coverPath = "E:\\douyin\\7.罗振玉\\罗振玉背景.png"

audioPath = "E:\\douyin\\7.罗振玉\\豹子头林冲-罗振玉.wav"
filesPath = "E:\\douyin\\7.罗振玉\\豹子头林冲-罗振玉.files"
srtPath = "E:\\douyin\\7.罗振玉\\豹子头林冲-罗振玉.srt"
textPath = "E:\\douyin\\7.罗振玉\\豹子头林冲-罗振玉.txt"

outputPath = "E:\\douyin\\7.罗振玉\\豹子头林冲-罗振玉.mp4"

videoClip = FileClip(textPath, filesPath, audioPath, srtPath, musicPath=musicPath, coverPath=coverPath)
videoClip.write_videofile(outputPath, codec='libx264', audio_codec='aac', preset="fast", threads=4,
                          ffmpeg_params=["-gpu", "cuda"])

# duration = 5
# fps = 30
#
# mediaPath = "E:\\douyin\\书面.png"
# outputPath = "E:\\douyin\\书面_out.mp4"
#
# image = Image.open(mediaPath).convert('RGB')
# mediaClip = ImageClip(np.array(image)).set_duration(duration).set_fps(fps)
#
# txt = "殷虚书契考释"
# videoClip = TxtClip(mediaClip, txt, direction="ttb")
# videoClip.write_videofile(outputPath, codec='libx264', audio_codec='aac', preset="fast", threads=4,
#                           ffmpeg_params=["-gpu", "cuda"])
