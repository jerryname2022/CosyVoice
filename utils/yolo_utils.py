#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# Copyright FunASR (https://github.com/alibaba-damo-academy/FunClip). All Rights Reserved.
#  MIT License  (https://opensource.org/licenses/MIT)

from PIL import Image
from utils.file_utils import read_lines
import os


def parser_labels(labelFile, imageFile):
    labels = read_lines(labelFile)
    image = Image.open(imageFile)
    width, height = image.size[0], image.size[1]
    print(width, height)

    results = []
    for label in labels:
        splits = label.strip().split(" ")
        if len(splits) >= 5:
            index = splits[0]
            cx = int(float(splits[1]) * width)
            cy = int(float(splits[2]) * height)
            bw = int(float(splits[3]) * width)
            bh = int(float(splits[4]) * height)

            left = cx - (bw // 2)
            right = cx + (bw // 2)
            top = cy - (bh // 2)
            bottom = cy + (bh // 2)
            results.append((index, left, right, top, bottom))
        # print(label, splits)

    return results


if __name__ == '__main__':
    labelFile = "F:\\yolov3\\video9\\video9-000001.txt"
    imageFile = "F:\\yolov3\\video9\\video9-000001.jpg"
    outPath = "F:\\yolov3\\outs"

    labels = parser_labels(labelFile, imageFile)

    image = Image.open(imageFile)

    index = 0
    for label in labels:
        name = label[0]
        left = label[1]
        right = label[2]
        top = label[3]
        bottom = label[4]
        bbox = (left, top, right, bottom)

        bboxImage = image.crop(bbox)
        bboxImage.save(os.path.join(outPath, "{}_{}.jpg".format(name, index)))
        index += 1

    # print(labels)
