from utils.ocr_utils import predict_files, parser_texts
from utils.file_utils import read_lines, write_to_file
import os

if __name__ == '__main__':
    imageRoot = "C:\\Users\\Administrator\\Documents\\zuishiwenren"
    txtPath = "C:\\Users\\Administrator\\Documents\\zuishiwenren.txt"

    names = [f for f in os.listdir(imageRoot) if f.endswith('.txt')]

    buffer = ""
    images = []
    for name in names:
        imagePath = os.path.join(imageRoot, name)
        texts = read_lines(imagePath)

        for txt in texts:
            buffer += txt.strip()
            buffer += "\n"

        buffer += "\n"
        buffer += "\n"
        buffer += "\n"
        buffer += "\n"
        print(imagePath, texts)
        images.append(imagePath)
        # print(imagePath)

    write_to_file(txtPath, buffer)
    # outputs = predict_files(images)
    # text = parser_texts(outputs, writeToFile=True)
    # print(text)
