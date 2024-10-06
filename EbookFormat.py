import os, chardet, math
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from utils.txt_utils import is_text
from utils.file_utils import read_lines, write_to_file

fontPath = "D:\\CosyVoice\\asset\\TW-Kai-98_1.ttf"
fontColor = (0, 0, 0, 0xFF)
lineColor = (0x46, 0x4C, 0x4E, 0x20)
lineCount = 14
textCount = 28
widthRate = 0.88
heightRate = 0.96


def calculateFontSize(image, imageDraw):
    width, height = image.size
    maxWidth = int(widthRate * width)
    maxHeight = int(heightRate * height)

    calculateTexts = ""
    for index in range(textCount + 1):
        calculateTexts += "趣"

    calculateSize = 10

    while True:
        left, top, right, bottom = imageDraw.textbbox((0, 0), calculateTexts,
                                                      font=ImageFont.truetype(fontPath, size=calculateSize))
        textWidth = right - left
        textHeight = bottom - top
        # textWidth, textHeight = imageDraw.textsize(calculateTexts,
        #                                            font=ImageFont.truetype(fontPath, size=calculateSize))
        calculateSize += 2

        if (textWidth > maxWidth or (textHeight * lineCount) > maxHeight):
            break

    return calculateSize


def splitTexts(text, length):
    return [text[i:i + length] for i in range(0, len(text), length)]


def newPage(imagePath):
    image = Image.open(imagePath)
    imageDraw = ImageDraw.Draw(image)

    width, height = image.size
    textMaxWidth = int(widthRate * width)
    textMaxHeight = int(heightRate * height)

    marginX = int((width - textMaxWidth) / 2)
    marginY = int((height - textMaxHeight) / 2)

    textHeight = int(textMaxHeight / lineCount)
    textWidth = int(textMaxWidth / textCount)

    fontSize = calculateFontSize(image, imageDraw)

    lineHeight = marginY

    while True:
        imageDraw.line([(marginX, lineHeight), (width - marginX, lineHeight)], fill=lineColor, width=1)
        lineHeight += textHeight
        if lineHeight > (height - marginY):
            break
    return image, imageDraw, fontSize, marginX, marginY, textHeight, textWidth


def drawImages(count, step):
    textfile = f"E:\\youtube\hlm\\{count}\\{count}-{step}.txt"
    imagefile = 'E:\\book1920.png'

    filename = os.path.basename(textfile)
    folder = os.path.dirname(textfile)
    basename = str(filename).split(".")[0]

    imageRoot = os.path.join(folder, "{}_images".format(basename))
    os.makedirs(imageRoot, exist_ok=True)

    lines = read_lines(textfile)

    drawFlag = 0
    pageFlag = 0
    image, imageDraw, fontSize, marginX, marginY, textHeight, textWidth = newPage(imagefile)

    width, height = image.size
    maxWidth = int(widthRate * width)
    maxHeight = int(heightRate * height)

    # imageSave = 'E:\\book_bg_red.png'
    # size = (width - (marginX * 2), textHeight)
    # color = (0xDF, 0x30, 0x00, 0x50)  # RGBA

    # createImage(color, size, imageSave)

    locations = ""

    allClears = ""
    charImages = ""

    for line in lines:
        texts = splitTexts("，，" + line, textCount)
        newline = True
        for text in texts:
            if drawFlag >= lineCount:
                image.save(os.path.join(imageRoot, "{}.png".format(pageFlag)))
                pageFlag += 1
                drawFlag = 0
                image, imageDraw, fontSize, marginX, marginY, textHeight, textWidth = newPage(imagefile)

            fromX = marginX
            fromY = marginY + drawFlag * textHeight
            if newline:
                fromX += (2 * textWidth)
                text = text[2:len(text)]

            clears = ""
            for char in text:
                if is_text(char):
                    clears += char
                    charImage = os.path.join(imageRoot, "{}.png".format(pageFlag))
                    charImages += f'{charImage}\r'

            allClears += clears

            charFlow = ""
            for char in text:
                if is_text(char):
                    left, top, right, bottom = imageDraw.textbbox((fromX, fromY), charFlow,
                                                                  font=ImageFont.truetype(fontPath, size=fontSize))
                    flowWidth = right - left
                    flowHeight = bottom - top

                    left, top, right, bottom = imageDraw.textbbox((fromX, fromY), char,
                                                                  font=ImageFont.truetype(fontPath, size=fontSize))
                    charWidth = right - left
                    locations += f'{int(fromX)}:{int(fromY)}:{int(flowWidth)}:{int(charWidth)}:{int(textHeight)}\r'

                charFlow += char

            imageDraw.text((fromX, fromY), text, fontColor, font=ImageFont.truetype(fontPath, size=fontSize))
            print(text)
            drawFlag += 1
            newline = False

    image.save(os.path.join(imageRoot, "{}.png".format(pageFlag)))
    write_to_file(os.path.join(imageRoot, "{}.locations".format(basename)), locations)
    write_to_file(os.path.join(imageRoot, "{}.clears".format(basename)), allClears)
    write_to_file(os.path.join(imageRoot, "{}.images".format(basename)), charImages)


def createImage(color, size, savePath):
    image = Image.new('RGBA', size, color)
    draw = ImageDraw.Draw(image)

    image.save(savePath)


def testImage():
    file0 = 'E:\\youtube\\test\\book1920grya.png'
    file1 = "E:\\youtube\\test\\1.png"

    fileout0 = 'E:\\youtube\\test\\image_out0.png'
    fileout1 = 'E:\\youtube\\test\\image_out1.png'

    image0 = np.array(Image.open(file0))
    image1 = np.array(Image.open(file1))

    print(image0.shape, image1.shape)  # (1080, 1920, 4) (512, 512, 3)
    width0, height0 = image0.shape[0], image0.shape[1]
    width1, height1 = image1.shape[0], image1.shape[1]

    offsetX = (width0 - width1) // 2
    offsetY = (height0 - height1) // 2

    print(width0, height0, offsetX, offsetY)

    startX = offsetX
    startY = offsetY
    endX = startX + width1
    endY = startY + height1

    print(startX, endX, startY, endY)

    masked = image0.copy()

    filter = masked[startX:endX, startY:endY] * 1.16
    minColor = filter[0, 0] - image1[0, 0]
    maxColor = minColor

    for x in range(width1):
        for y in range(height1):
            c0 = masked[startX + x, startY + y]
            c1 = image1[x, y]
            # print(c0, c1)
            minColor = min(minColor, int(c0 - c1))
            maxColor = max(maxColor, int(c0 - c1))

    print(minColor, maxColor)
    # masked[startX:endX, startY:endY] = (masked[startX:endX, startY:endY] * 1.16 + image1[:, :])

    # for a in range(3):
    #     # masked[startX:endX, startY:endY, alpha] = image0[startX:endX, startY:endY, alpha] + image1[:, :, alpha]
    #     # masked[startX:endX, startY:endY, a] = image1[:, :, a]
    #     masked[startX:endX, startY:endY, a] = (masked[startX:endX, startY:endY, a] + image1[:, :, a]) // 2

    # out = Image.fromarray(masked)
    # out.save(fileout0)


def apply_color_range(filein, fileout, white, back):
    # 读取图片并转换为 RGB 模式
    with Image.open(filein) as image:
        rgb = image.convert('RGBA')
        gray = image.convert('L')

        rgbArray = np.array(rgb)
        grayArray = np.array(gray)

        print(rgbArray.shape, grayArray.shape)

        copy = np.copy(rgbArray)

        for alpha in range(3):
            a = white[alpha]
            b = back[alpha]
            distance = a - b  # math.fabs(a - b)
            copy[:, :, alpha] = (a + distance * grayArray / 255)

        # a = 0
        # b = 255
        # copy[:, :, 3] = (a + distance * grayArray / 255)
        imageOut = Image.fromarray(grayArray)
        imageOut.save(fileout)


# 示例使用
# filein = 'E:\\youtube\\test\\book1920.png'
# fileout = 'E:\\youtube\\test\\book1920grya.png'
# colorFrom = (251, 248, 214)  # (R, G, B)
# colorTo = (231, 221, 185)
#
# # colorFrom = (0, 0, 0)  # (R, G, B)
# # colorTo = (251, 251, 251)
# apply_color_range(filein, fileout, colorFrom, colorTo)

# testImage()

count = 120
for step in range(3):
    drawImages(count, step)
