import os

from moviepy.editor import *
import chardet
import numpy as np
from PIL import Image
from moviepy.video.fx.resize import resize
from utils.file_utils import read_lines


class MaskClip(VideoClip):
    def __init__(self, coverPath, audioPath, locations, times, images, size=(1920, 1080), fps=30, opacity=0.30,
                 **kwargs):
        super().__init__(**kwargs)
        self.coverPath = coverPath
        self.audio = AudioFileClip(audioPath)
        self.locations = locations
        self.times = times
        self.images = images
        self.duration = self.audio.duration
        self.fps = fps
        self.size = size
        self.opacity = opacity  # Set opacity level

        self.setup()

    def setup(self):
        medias = {}

        key = os.path.basename(self.coverPath.strip())
        present: bool = key in medias.keys()
        if not present:
            medias[key] = resize(ImageClip(coverPath), newsize=self.size)

        for image in self.images:
            key = os.path.basename(image.strip())
            present: bool = key in medias.keys()
            if not present:
                medias[key] = resize(ImageClip(image.strip()), newsize=self.size)

        self.medias = medias

    def time_index(self, t):
        index = 0
        for item in self.times:
            ftime = float(item.strip())
            if ftime > t:
                return index
            if index < (len(self.times) - 1):
                index += 1
        return index

    def mask_frame(self, width, height, color, opacity):
        # Create a mask frame with the specified color and opacity
        mask_frame = np.zeros((height, width, 4), dtype=np.uint8)
        mask_frame[:, :, :3] = color  # Set RGB color
        mask_frame[:, :, 3] = int(opacity * 255)  # Set alpha channel
        return mask_frame

    def image_clip(self, t):
        if t <= 0.5:
            # image = ImageClip(self.coverPath.strip())
            key = os.path.basename(self.coverPath.strip())
            image = self.medias[key]
        else:
            index = int(self.time_index(t))
            key = os.path.basename(self.images[index].strip())
            # image = ImageClip(self.images[index].strip())
            image = self.medias[key]

        return image

    def make_frame(self, t):
        imageClip = self.image_clip(t)
        imageWidth, imageHeight = imageClip.size
        imageFrame = np.array(imageClip.get_frame(t))
        index = int(self.time_index(t))
        if 0 <= index < len(self.locations):
            location = self.locations[index].strip()
            infos = location.split(":")
            fromX, fromY, flowWidth, charWidth, charHeight = int(infos[0]), int(infos[1]), int(infos[2]), \
                int(infos[3]), int(infos[4])

            # fromX / imageWidth = x / size[0]
            fromX = int(self.size[0] * fromX / imageWidth)
            fromY = int(self.size[1] * fromY / imageHeight)
            flowWidth = int(self.size[0] * flowWidth / imageWidth)
            charWidth = int(self.size[0] * charWidth / imageWidth)
            charHeight = int(self.size[1] * charHeight / imageHeight)

            fromTime = 0
            if index - 1 >= 0:
                fromTime = float(self.times[index - 1])
            toTime = float(self.times[index])

            if fromTime < toTime:
                rate = float((t - fromTime) / (toTime - fromTime))
            else:
                rate = 0

            maskHeight = charHeight
            maskWidth = max(0, int(flowWidth + charWidth * (0.4 + rate)))

            # Create the mask frame with the specified color and opacity
            maskColor = (0xDF, 0x30, 0x00)  # RGB color
            maskFrame = self.mask_frame(maskWidth, maskHeight, maskColor, self.opacity)

            videoFrame = imageFrame  # Convert video_frame to numpy array
            maskedFrame = videoFrame.copy()

            if maskWidth <= videoFrame.shape[1] and maskHeight <= videoFrame.shape[0]:
                startX = int(fromX)
                startY = int(fromY)
                endX = min(startX + maskWidth, videoFrame.shape[1])
                endY = min(startY + maskHeight, videoFrame.shape[0])

                # Ensure mask is within video bounds
                maskRegion = maskFrame[:endY - startY, :endX - startX]
                alpha = maskRegion[:, :, 3] / 255.0
                for c in range(3):  # For each RGB channel
                    maskedFrame[startY:endY, startX:endX, c] = (1 - alpha) * videoFrame[startY:endY, startX:endX,
                                                                             c] + alpha * maskRegion[:, :, c]

            return maskedFrame
        else:
            return imageFrame


count = 1
rootPath = f"E:\\youtube\\hlm\\{count}"

for index in range(3):
    coverPath = os.path.join(rootPath, "{}-{}.png".format(count, index))
    audioPath = os.path.join(rootPath, "{}-{}.wav".format(count, index))
    timesPath = os.path.join(rootPath, "{}-{}.times".format(count, index))
    imagesPath = os.path.join(rootPath, "{}-{}.images".format(count, index))
    locationsPath = os.path.join(rootPath, "{}-{}.locations".format(count, index))
    outputPath = os.path.join(rootPath, "{}-{}_out.mp4".format(count, index))

    times = read_lines(timesPath)
    locations = read_lines(locationsPath)
    images = read_lines(imagesPath)

    videoClip = MaskClip(coverPath, audioPath, locations, times, images)
    videoClip.write_videofile(outputPath, codec='libx264', audio_codec='aac', preset="fast", threads=8,
                              ffmpeg_params=["-gpu", "cuda"])

    print("Video processing completed.")
