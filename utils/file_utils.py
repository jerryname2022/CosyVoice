#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# Copyright FunASR (https://github.com/alibaba-damo-academy/FunClip). All Rights Reserved.
#  MIT License  (https://opensource.org/licenses/MIT)

import os, chardet


def write_to_file(path, data, mode="w"):
    with open(path, mode, encoding="utf8") as f:
        f.write(data)
        f.close()


def read_lines(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
        encoding = chardet.detect(data)['encoding']

    if os.path.isfile(filepath):
        # texts = open(filepath, encoding="gbk").readlines()
        with open(filepath, 'r', encoding=encoding) as f:
            texts = f.readlines()
        return texts

    return None


if __name__ == '__main__':
    pass
