from moviepy.editor import *
# import numpy as np
# import cupy as cp
import torch
import cv2, math, random
from utils.file_utils import read_lines
from utils.srt_utils import parse_srt_time, srt_texts_times
from utils.txt_utils import is_text
from PIL import Image, ImageDraw, ImageFont
from moviepy.video.fx.resize import resize
from itertools import combinations


class FrameClip(VideoClip):
    def __init__(self, audioFile, srtFile, size=(1920, 1080), fps=30):
        super().__init__()

        texts, times = srt_texts_times(srtFile)

        self.audioFile = audioFile
        self.audio = AudioFileClip(audioFile)
        self.duration = self.audio.duration
        self.fps = fps
        self.size = size
        self.srtFile = srtFile
        self.texts = texts
        self.times = times
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        print("texts times ... ", len(texts), len(times))

    def create_frame(self, width, height, color, opacity):
        # Create a mask frame with the specified color and opacity
        mask_frame = torch.zeros((height, width, 3), dtype=torch.uint8, device=self.device)
        # mask_frame[:, :, :3] = color  # Set RGB color
        mask_frame[:, :, 0] = color[0]
        mask_frame[:, :, 1] = color[1]
        mask_frame[:, :, 2] = color[2]
        # mask_frame[:, :, 3] = int(opacity * 255)  # Set alpha channel
        return mask_frame

    def location(self, background, frame, x, y, endY=True, endX=True, opacity=1):

        width, height = background.shape[1], background.shape[0]
        fWidth, fHeight = frame.shape[1], frame.shape[0]

        toX, toY = x + fWidth, y + fHeight

        boxW = min(toX, width) - max(0, x)
        boxH = min(toY, height) - max(0, y)

        bx, by = max(0, x), max(0, y)
        fx, fy = fWidth - boxW, fHeight - boxH

        if not endX:
            fx = 0

        if not endY:
            fy = 0

        if boxW > 0 and boxH > 0:
            alpha = opacity

            # background[bx:bx + boxW, by:by + boxH] = alpha * frame[fx:fx + boxW, fy:fy + boxH] + (
            #         1 - alpha) * background[bx:bx + boxW, by:by + boxH]

            background[by:by + boxH, bx:bx + boxW] = alpha * frame[fy:fy + boxH, fx:fx + boxW] + (
                    1 - alpha) * background[by:by + boxH, bx:bx + boxW]

    def alpha_in(self, background, frame, ctime, duration=0.8):

        width, height = background.shape[0], background.shape[1]
        fWidth, fHeight = frame.shape[0], frame.shape[1]

        diffW = width - fWidth
        diffH = height - fHeight

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
        images = ('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff')
        return name.lower().endswith(images)

    def text_index(self, t):
        index = 0
        for item in self.times:
            ftime = float(item)
            if ftime > t:
                return index
            if index < (len(self.times) - 1):
                index += 1
        return index

    def ease_quart(self, x):
        return 1 - math.pow(1 - x, 5)


class FileClip(FrameClip):
    def __init__(self, textsFile, filesPath, audioFile, srtFile, size=(1920, 1080), fps=30):
        super().__init__(audioFile=audioFile, srtFile=srtFile, size=size, fps=fps)

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
            row = 2
            col = size // 2
            if (row * col) < size:
                col += 1
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
                if len(endTags) > 1:
                    tag = endTags[1].strip()

                    if len(tag) > 0 and tag == lastTag:
                        flag += 1
                        lineTags[list(lineTags.keys())[-1]] = flag
                    else:
                        lineTags[i] = flag
                        flag = 1

                    lastTag = tag

        if len(lineTags) > 0:
            lineTags[list(lineTags.keys())[-1]] = flag

        count = 1
        for i in range(len(lines)):
            exist = i in lineTags.keys()
            if not exist:
                lineTags[i] = count
            else:
                count = lineTags[i]

        print(len(lineTags), lineTags)

        medias = []
        scenes = []

        scene = random.randint(1, 4)
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

                if count >= scene:
                    scene = random.randint(1, 4)
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
                    imageClip = ImageClip(videoPath, transparent=True)
                    width, height = imageClip.size[0], imageClip.size[1]
                    scaleW = sceneWidth / width
                    scaleH = sceneHeight / height

                    scale = min(scaleW, scaleH)
                    targetSize = (int(width * scale), int(height * scale))

                    videoClip = resize(imageClip, newsize=targetSize)
                    # videoClip = resize(ImageClip(videoPath), newsize=self.size)
                else:
                    videoClip = VideoFileClip(videoPath, has_mask=True).subclip(start, end)
                    width, height = videoClip.size[0], videoClip.size[1]
                    scaleW = sceneWidth / width
                    scaleH = sceneHeight / height

                    scale = min(scaleW, scaleH)
                    targetSize = (int(width * scale), int(height * scale))

                    videoClip = videoClip.resize(newsize=targetSize)
                    # videoClip = VideoFileClip(videoPath).subclip(start, end).resize(newsize=self.size)

                medias.append((videoClip, start, end, isImage, mediaIn, mediaOut, location))
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

            videoClip, videoStart, videoEnd, isImage, mediaIn, mediaOut, location = self.medias[line]

            t = min(max(t, audioStart), audioEnd)
            fileDuration = videoEnd - videoStart
            audioDuration = audioEnd - audioStart
            ft = (t - audioStart) * fileDuration / audioDuration

            frame = torch.tensor(videoClip.get_frame(ft), device=self.device, dtype=torch.uint8)

            return frame, (t - audioStart), audioDuration, mediaIn, mediaOut, location

        return None

    def make_frame(self, t):
        textIndex = self.text_index(t)
        lineIndex = int(self.textLines[textIndex])

        width, height = self.size[0], self.size[1]
        color = (0xf2, 0xf4, 0xf5)
        opacity = 1
        background0 = self.create_frame(width, height, color, opacity)
        background = self.create_frame(width, height, color, opacity)

        mediaIndex, mediaCount = self.scenes[lineIndex][0], self.scenes[lineIndex][1]
        count = mediaIndex + 1
        fromIndex = lineIndex - count

        w, h = background.shape[1], background.shape[0]

        for i in range(count):
            textLine = fromIndex + 1 + i
            frame, ft, fd, mediaIn, mediaOut, location = self.file_frame(textLine, t)
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
            elif i == (mediaCount - 1) and ft > (fd - outTime):
                # self.right_out(background, frame, x, y, ft - (fd - outTime), duration=outTime)
                # self.left_out(background, frame, x, y, ft - (fd - outTime), duration=outTime)
                # self.top_out(background, frame, x, y, ft - (fd - outTime), duration=outTime)
                # self.bottom_out(background, frame, x, y, ft - (fd - outTime), duration=outTime)

                self.location(background, frame, x, y)
                frame = background
                background = background0
                x = 0
                y = 0

                if mediaIn == 1:
                    self.bottom_out(background, frame, x, y, ft - (fd - outTime), duration=outTime)
                elif mediaIn == 2:
                    self.top_out(background, frame, x, y, ft - (fd - outTime), duration=outTime)
                elif mediaIn == 3:
                    self.right_out(background, frame, x, y, ft - (fd - outTime), duration=outTime)
                else:
                    self.left_out(background, frame, x, y, ft - (fd - outTime), duration=outTime)

            else:
                self.location(background, frame, x, y)

        return background.cpu().numpy()


audioPath = "E:\\douyin\\videos\\车床介绍2.wav"
filesPath = "E:\\douyin\\videos\\车床介绍2.files"
srtPath = "E:\\douyin\\videos\\车床介绍2.srt"
textPath = "E:\\douyin\\videos\\车床介绍2.txt"

outputPath = "E:\\douyin\\videos\\车床介绍2.mp4"

videoClip = FileClip(textPath, filesPath, audioPath, srtPath)
# videoClip.write_videofile(outputPath, codec='libx264', audio_codec='aac', preset="fast", threads=8,
#                           ffmpeg_params=["-gpu", "cuda"])
