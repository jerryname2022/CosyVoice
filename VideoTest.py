from moviepy.editor import *
import chardet, math
import numpy as np
from PIL import Image
import cv2, math
from pypinyin import pinyin, lazy_pinyin, Style
from moviepy.video.fx.resize import resize


class MediaScaleClip(VideoClip):
    def __init__(self, mediaClip, scaleFrom, scaleTo, size=(1920, 1080), fps=30):
        super().__init__()
        self.mediaClip = mediaClip
        self.duration = self.mediaClip.duration
        self.fps = fps
        self.size = size
        self.scaleFrom = scaleFrom
        self.scaleTo = scaleTo

    def create_frame(self, width, height, color):
        # Create a mask frame with the specified color and opacity
        newFrame = np.zeros((height, width, 3), dtype=np.uint8)
        # newFrame = torch.zeros((height, width, 3), device=self.device, dtype=torch.uint8)
        # newFrame = np.zeros((height, width, 3), dtype=np.uint8)
        # newFrame[:, :, :3] = color  # Set RGB color
        newFrame[:, :, 0] = color[0]
        newFrame[:, :, 1] = color[1]
        newFrame[:, :, 2] = color[2]
        return newFrame

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

            background[by:by + boxH, bx:bx + boxW] = alpha * frame[fy:fy + boxH, fx:fx + boxW] + (
                    1 - alpha) * background[by:by + boxH, bx:bx + boxW]

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

        frame = np.array(resize(self.mediaClip, newsize=(fw, fh)).get_frame(t))

        offsetX = width - frame.shape[1]
        offsetY = height - frame.shape[0]

        x = offsetX // 2
        y = offsetY // 2

        self.location(background, frame, x, y)
        return background


duration = 10
fps = 30

mediaPath = "E:\\youtube\\test\\image.png"
outputPath = "E:\\youtube\\test\\gif_out.mp4"

image = Image.open(mediaPath).convert('RGB')
mediaClip = ImageClip(np.array(image)).set_duration(duration).set_fps(fps)
scaleTo = 1.1
scaleFrom = 0.8

# scaleClip = mediaClip.resize(func_resize).set_position(('center', 'center'))
# scaleClip.write_videofile(outputPath, codec='libx264', audio_codec='aac')

# mediaClip = VideoFileClip(mediaPath, has_mask=True)

scaleClip = MediaScaleClip(mediaClip, scaleTo, scaleFrom, size=(mediaClip.size[0], mediaClip.size[1]))
scaleClip.write_videofile(outputPath, codec='libx264', audio_codec='aac')
