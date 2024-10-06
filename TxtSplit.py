import os
from utils.file_utils import read_lines, write_to_file


# os.environ["http_proxy"] = "http://172.29.0.1:1081"
# os.environ["https_proxy"] = "http://172.29.0.1:1081"


def splitFile(filepath, count=3):
    folder = os.path.dirname(filepath)
    basename = os.path.basename(filepath).split(".")[0]
    formate = os.path.basename(filepath).split(".")[1]

    print(folder, basename, formate)

    lines = read_lines(filepath)

    txtCount = 0
    for line in lines:
        line = line.strip()
        txtCount += len(line)

    splitCount = txtCount // count

    if (splitCount * count) != txtCount:
        splitCount += count  # 6860 2286

    fileIndex = 0
    itemCount = 0
    buffer = ""

    for line in lines:
        if itemCount > splitCount:
            fileout = os.path.join(folder, "{}-{}.{}".format(basename, fileIndex, formate))
            write_to_file(fileout, buffer)
            buffer = ""
            itemCount = 0
            fileIndex += 1

        line = line.strip()
        buffer += line
        buffer += '\r'
        itemCount += len(line)

    fileout = os.path.join(folder, "{}-{}.{}".format(basename, fileIndex, formate))
    write_to_file(fileout, buffer)

    print(txtCount, splitCount)


number = 120
filepath = f"E:\\youtube\hlm\\{number}/{number}.txt"
splitFile(filepath, count=3)
