#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# Copyright FunASR (https://github.com/alibaba-damo-academy/FunClip). All Rights Reserved.
#  MIT License  (https://opensource.org/licenses/MIT)

import time


def format_fime(timestamp, format="%Y%m%d %H:%M:%S") -> str:
    t = time.localtime(timestamp)
    return time.strftime(format, t)


def log_time(tag=""):
    print(tag, format_fime(time.time()))


if __name__ == '__main__':
    pass
