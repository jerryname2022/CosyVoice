# from skimage.measure import compare_ssim
from skimage.metrics import structural_similarity
# ~ import skimage  as ssim
import argparse
import imutils
import cv2
import aircv as ac
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt


def test1():
    srcImage = "F:\\yolov3\\boxTest/video1-00613.jpeg"
    objImage = "F:\\yolov3\\outs\\5_3.jpg"

    imageA = cv2.imread(srcImage)
    imageB = cv2.imread(objImage)

    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    (score, diff) = structural_similarity(grayA, grayB, full=True)
    diff = (diff * 255).astype("uint8")
    print("SSIM:{}".format(score))

    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]

    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(imageA, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.rectangle(imageB, (x, y), (x + w, y + h), (0, 0, 255), 2)

    cv2.imshow("Modified", imageB)
    cv2.imwrite("F:\\yolov3\\boxTest/haha2.jpeg", imageB)
    cv2.waitKey(0)


def test2():
    imageA = cv2.imread("F:\\yolov3\\boxTest/video1-00613.jpeg", cv2.IMREAD_GRAYSCALE)
    imageB = cv2.imread("F:\\yolov3\\boxTest/video1-00691.jpeg", cv2.IMREAD_GRAYSCALE)

    # 初始化ORB检测器
    orb = cv2.ORB_create()

    # 检测关键点和描述符
    ref_kp, ref_des = orb.detectAndCompute(imageA, None)
    search_kp, search_des = orb.detectAndCompute(imageB, None)

    # 初始化BFMatcher
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # 匹配描述符
    matches = bf.match(ref_des, search_des)

    # 对匹配结果进行排序
    matches = sorted(matches, key=lambda x: x.distance)

    # 绘制前N个匹配项
    img_matches = cv2.drawMatches(imageA, ref_kp, imageB, search_kp, matches[:50], None, flags=2)

    # 显示匹配结果
    cv2.imshow('Matches', img_matches)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 可以通过confidencevalue来调节相似程度的阈值，小于阈值不相似


def matchImg(imgsrc, imgobj, phone_x, phone_y, confidencevalue=0):  # imgsrc=原始图像，imgobj=待查找的图片
    imsrc = ac.imread(imgsrc)
    imobj = ac.imread(imgobj)
    match_result = ac.find_template(imsrc, imobj, confidencevalue)
    print(match_result)
    if match_result is not None:
        match_result['shape'] = (imsrc.shape[1], imsrc.shape[0])  # 0为高，1为宽
        x, y = match_result['result']  # 标准图中小图位置x,y
        shape_x, shape_y = tuple(map(int, match_result['shape']))  # 标准图中x,y
        position_x, position_y = int(phone_x * (x / shape_x)), int(phone_y * (y / shape_y))
    else:
        return None, None, None, None
    # print(match_result)
    # return match_result
    return position_x, position_y, str(match_result['confidence'])[:4], match_result


def fixed_size(width, height, infile, outfile):
    """按照固定尺寸处理图片"""
    im = Image.open(infile)
    out = im.resize((width, height), Image.ANTIALIAS)
    out.save(outfile)


def get_picture_size(imgsrc):
    '''获取图片长，宽'''
    imsrc = ac.imread(imgsrc)
    y, x, z = imsrc.shape
    return x, y


def test3():
    srcImage = "F:\\yolov3\\boxTest/video1-00613.jpeg"
    objImage = "F:\\yolov3\\outs\\5_3.jpg"

    result = matchImg(srcImage, objImage, 0, 0)

    zuobiao = result[3]["rectangle"]
    xmin = zuobiao[0][0]
    ymin = zuobiao[0][1]
    xmax = zuobiao[2][0]
    ymax = zuobiao[3][1]

    image = cv2.imread(srcImage)
    cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
    cv2.imwrite('F:\\yolov3\\boxTest\\2.jpg', image)


def test4():
    srcImage = "F:\\yolov3\\boxTest/video1-00613.jpeg"
    objImage = "F:\\yolov3\\outs\\5_3.jpg"

    image = cv2.imread(srcImage)
    template = cv2.imread(objImage)

    width, height = template.shape[:2]

    print(width, height)
    result = cv2.matchTemplate(image, template, cv2.TM_CCORR_NORMED)

    threshold = 0.8
    locations = np.where(result >= threshold)

    for loc in zip(*locations[::-1]):
        cv2.rectangle(image, loc, (loc[0] + width, loc[1] + height), (0, 255, 0), 2)

    # 显示匹配结果
    cv2.imshow('Matches', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def test5():
    srcImage = "F:\\yolov3\\boxTest/video1-00613.jpeg"
    objImage = "F:\\yolov3\\outs\\0_14.jpg"

    image = cv2.imread(srcImage, cv2.IMREAD_GRAYSCALE)
    template = cv2.imread(objImage, cv2.IMREAD_GRAYSCALE)

    width, height = template.shape[:2]
    print(width, height)

    results = cv2.matchTemplate(image, template, cv2.TM_SQDIFF_NORMED)
    cv2.normalize(results, results, 0, 1, cv2.NORM_MINMAX, -1)

    minValue, maxValue, minLoc, maxLoc = cv2.minMaxLoc(results)

    print("minValue", minValue)

    resultPoint1 = minLoc
    resultPoint2 = (resultPoint1[0] + width, resultPoint1[1] + height)

    cv2.rectangle(image, resultPoint1, resultPoint2, (0, 0, 255), 2)

    # 显示匹配结果
    # cv2.imshow('template', template)
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def test6():
    srcImage = "F:\\yolov3\\boxTest/video9-000001.jpg"
    objImage = "F:\\yolov3\\outs\\0_14.jpg"

    MIN_MATCH_COUNT = 10  # 设置最低特征点匹配数量为10
    template = cv2.imread(objImage, 0)  # queryImage
    target = cv2.imread(srcImage, 0)  # trainImage
    # Initiate SIFT detector创建sift检测器
    sift = cv2.xfeatures2d.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(template, None)
    kp2, des2 = sift.detectAndCompute(target, None)
    # 创建设置FLANN匹配
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    # 舍弃大于0.7的匹配
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)

    if len(good) > MIN_MATCH_COUNT:
        # 获取关键点的坐标
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        # 计算变换矩阵和MASK
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()
        h, w = template.shape
        # 使用得到的变换矩阵对原图像的四个角进行变换，获得在目标图像上对应的坐标
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        cv2.polylines(target, [np.int32(dst)], True, 0, 2, cv2.LINE_AA)
    else:
        print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
        matchesMask = None
    draw_params = dict(matchColor=(0, 255, 0),
                       singlePointColor=None,
                       matchesMask=matchesMask,
                       flags=2)
    result = cv2.drawMatches(template, kp1, target, kp2, good, None, **draw_params)

    cv2.imshow('image', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # plt.imshow(result, 'gray')
    # plt.show()


def test7():
    print(cv2.__version__)
    tracker = cv2.TrackerCSRT_create()


test7()
