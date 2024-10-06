from paddlex import create_pipeline
from utils.file_utils import write_to_file
import os


# 文档场景信息抽取v3	PP-ChatOCRv3-doc	文档场景信息抽取v3产线Python脚本使用说明
# 通用OCR	OCR	通用OCR产线Python脚本使用说明
# 通用表格识别	table_recognition	通用表格识别产线Python脚本使用说明
# 印章识别	coming soon	coming soon
# 公式识别	coming soon	coming soon


def predict_files(images, pipeline="OCR"):
    pipeline = create_pipeline(pipeline=pipeline)
    return pipeline.predict(images)


def parser_texts(predict, writeToFile=False):
    buffer = ""
    for res in predict:

        text = ""
        resultTexts = res["rec_text"]
        if len(resultTexts) > 0:
            for txt in resultTexts:
                text += txt
                text += "\n"

        buffer += "\n"
        buffer += text

        if writeToFile:
            imagePath = res["input_path"]
            name = os.path.basename(imagePath)
            imageRoot = os.path.dirname(imagePath)
            txtPath = os.path.join(imageRoot, "{}.txt".format(name.split(".")[0]))
            write_to_file(txtPath, text)

    return buffer


if __name__ == '__main__':
    image0 = "C:\\Users\\Administrator\\Documents\\05.jpg"
    image1 = "C:\\Users\\Administrator\\Documents\\06.jpg"

    output = predict_files([image0, image1])

    text = parser_texts(output, writeToFile=True)
    print(text)

    # for res in output:
    #     res.print()
    #     texts = res["rec_text"]
    #     print(texts)
    # res.save_to_img("../output/")
    # res.save_to_json("../output/")
