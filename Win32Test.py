from win32gui import *  # 操作windows窗口
from PIL import ImageGrab  # 操作图像
import win32con  # 系统操作

names = set()


def get_window_title(window, nouse):
    '''
    获取窗口标题函数
    :param window: 窗口对象
    :param nouse:
    :return:
    '''

    if IsWindow(window) and IsWindowEnabled(window) and IsWindowVisible(window):
        names.add(GetWindowText(window))


EnumWindows(get_window_title, 0)
list_ = [name for name in names if name]

for n in list_:
    print('活动窗口: ', n)

name = "Android Emulator - Pixel_3a_XL_API_30:5554"
window = FindWindow(0, name)  # 根据窗口名称获取窗口对象
# ShowWindow(window, win32con.SW_MAXIMIZE)  # 将该窗口最大化

startX, startY, endX, endY = GetWindowRect(window)
print(startX, startY, endX, endY)

box = (startX, startY, endX, endY)
image = ImageGrab.grab(box)
image.show()
# image.save('target.png')
