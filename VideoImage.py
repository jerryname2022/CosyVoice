from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

videoPath = "E:\\youtube\\hlm\\1\\1-2_mask.mp4"
coverPath = "E:\\youtube\\hlm\\1\\1-2.png"
outPath = "E:\\youtube\\hlm\\1\\1-2_cover.mp4"
# 加载视频文件
video = VideoFileClip(videoPath)
# 加载替换用的图片
cover = ImageClip(coverPath)

# 设置替换图片的持续时间、位置和大小
cover = cover.set_duration(1 / video.fps).resize(video.size).set_position("center")

# 创建一个包含替换图片的短视频片段
cover = cover.set_start(0)

# 将视频的其余部分（从第二帧开始）提取出来
subVideo = video.subclip(1 / video.fps)

# 合成替换图片和剩余视频
finalClip = CompositeVideoClip([cover, subVideo.set_start(1 / video.fps)])

# 输出结果
finalClip.write_videofile(outPath, codec="libx264")
