import logging
import os
import win32gui
import coloredlogs
import numpy as np
import win32con

logger = logging.getLogger("Dayu")
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
logging.getLogger("chardet.charsetprober").setLevel(logging.ERROR)
coloredlogs.install(level='DEBUG', logger=logger)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
logging.basicConfig(filename=BASE_DIR + "/log.txt", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def sigmoid(x):
    """
    滑动验证码基础方程
    """
    s = 1 / (1 + 30 * np.exp(-x))
    return s


class Utils:

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"
    }

    @staticmethod
    def upload(path):
        """
        窗体文件上传
        :param path: 文件路径
        :return:
        """
        dialog = win32gui.FindWindow(None, '打开')  # 对话框
        ComboBoxEx32 = win32gui.FindWindowEx(dialog, 0, 'ComboBoxEx32', None)
        ComboBox = win32gui.FindWindowEx(ComboBoxEx32, 0, 'ComboBox', None)
        # 获取文件路径输入框对象的句柄
        Edit = win32gui.FindWindowEx(ComboBox, 0, 'Edit', None)
        # 获取 打开button按钮对象
        button = win32gui.FindWindowEx(dialog, 0, 'Button', '打开(&O)')
        # 输入框输入绝对路径
        try:
            win32gui.SendMessage(Edit, win32con.WM_SETTEXT, None, path)
        except Exception as e:
            print(e)
            print("第一次打地址")

        try:
            win32gui.SendMessage(Edit, win32con.WM_SETTEXT, None, path)
        except Exception as e:
            print(e)
            print("第2次打地址")

        import time
        time.sleep(4)
        # win32gui.SendMessage(Edit, win32con.WM_SETTEXT, 0, path)
        # 点击 打开
        win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, button)

    @staticmethod
    def action_list(num):
        """
        滑动拼图验证码轨迹
        :param num: 移动距离
        :return:
        """
        remain = num
        act_list = list()
        randlist = list(map(sigmoid, range(10)))
        for i, rand in enumerate(randlist):
            if i == 9:
                randlist.pop()
                break
            randlist[i] = randlist[i + 1] - randlist[i]
        factor = num / sum(randlist)
        for rand in randlist:
            randnumber = int(factor * rand) + 1
            act_list.append(randnumber)
            remain -= randnumber
        act_list.append(remain)
        return act_list


