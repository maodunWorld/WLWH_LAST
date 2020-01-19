import os
import random
import time
import win32gui

import cv2
import numpy as np
import requests
import win32con
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"
}

title = "丰盛的范德萨范德萨"


def sigmoid(x):
    s = 1 / (1 + 30 * np.exp(-x))
    return s


def save_img(path, content):
    with open(path, "wb") as f:
        f.write(content)


def get_location(image_path, block_path):
    # bgimg = cv2.imread(image_path)
    # template = cv2.imread(block_path, 0)
    # bgimg_gray = cv2.cvtColor(bgimg, cv2.COLOR_BGR2GRAY)
    # res = cv2.matchTemplate(bgimg_gray, template, cv2.TM_CCOEFF_NORMED)
    # index = cv2.minMaxLoc(result)
    # return index
    block = cv2.imread(block_path)
    block = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)
    block = abs(255 - block)
    cv2.imwrite(block_path, block)
    block = cv2.imread(block_path)
    template = cv2.imread(image_path)
    result = cv2.matchTemplate(block, template, cv2.TM_CCOEFF_NORMED)
    value = cv2.minMaxLoc(result)
    return value[2][0]


def upload(path):
    dialog = win32gui.FindWindow(None, '打开')  # 对话框
    ComboBoxEx32 = win32gui.FindWindowEx(dialog, 0, 'ComboBoxEx32', None)
    ComboBox = win32gui.FindWindowEx(ComboBoxEx32, 0, 'ComboBox', None)
    # 获取文件路径输入框对象的句柄
    Edit = win32gui.FindWindowEx(ComboBox, 0, 'Edit', None)
    # 获取 打开button按钮对象
    button = win32gui.FindWindowEx(dialog, 0, 'Button', '打开(&O)')
    # 输入框输入绝对路径
    win32gui.SendMessage(Edit, win32con.WM_SETTEXT, 0, path)
    # 点击 打开
    win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, button)


def build_tag(tags):
    for tag in tags:
        Browser.find_element_by_xpath("//div[@class='content-tag']//input").send_keys(tag)
        Browser.find_element_by_xpath("//div[@class='content-tag']//input").send_keys(Keys.ENTER)
        time.sleep(0.5)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__name__)))

option = webdriver.ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])

Browser = webdriver.Chrome(chrome_options=option)

Browser.get("https://mp.qutoutiao.net/login")
# 登录开始
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//i[@class='login-icon']/following-sibling::input[1]"))).send_keys("15574819298")
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//i[@class='pwd-icon']/following-sibling::input[1]"))).send_keys("yao147258")
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//button[@id='submit-login']"))).click()
# 登录结束

# 跳转发布开始
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//span[contains(string(), '发布内容')]"))).click()
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//p[contains(string(), '发布视频')]"))).click()
# *** 处理发文规范弹窗 ***
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//i[@class='el-message-box__close el-icon-close']"))).click()
time.sleep(1)
# 跳转发布结束

# 开始发视频
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//input[@id='inp-video-file']"))).click()
time.sleep(1)   # 等待上传框体加载
upload(r"d:\a1bad153a548f92f3078e89361dbce41.mp4")
WebDriverWait(Browser, 100).until(
    EC.presence_of_element_located((By.XPATH, "//span[contains(string(), '上传成功')]")))
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//form[@class='el-form el-form--label-left']/div[1]//input"))).send_keys([Keys.BACKSPACE for i in range(1, 100)] + [i for i in title])     # 发送标题
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//textarea[@class='el-textarea__inner']"))).send_keys("简介简介")     # 发送标题
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='请选择分类']"))).click()
time.sleep(1)   # 等待分类加载
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//dd[contains(string(), '自驾游')]"))).click()
time.sleep(1)
build_tag(["高分段", "范德萨", "热舞"])
time.sleep(0.5)
# --  选择封面开始
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//div[@class='el-upload']"))).click()
time.sleep(1)   # 等待封面框体加载
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//p[contains(string(), '自定义封面')]"))).click()
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//span[contains(string(), '选择图片')]"))).click()
time.sleep(1)  # 等待上传框体加载
upload(r"d:\0.png")
time.sleep(3)    # 等待图片上传完成  # TODO 待处理
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//div[@class='el-dialog__wrapper dialog-img-cropper']//span[contains(string(), '确 定')]"))).click()
# 封面选择结束
# 视频信息构造结束
time.sleep(3)
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//button[@class='el-button el-button--primary']//span[contains(string(), '发布')]"))).click()
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//button[@class='el-button el-button--primary el-button--medium']//span[contains(string(), '确认发布')]")))
time.sleep(1)
Browser.find_element_by_xpath("//button[@class='el-button el-button--primary el-button--medium']//span[contains(string(), '确认发布')]").click()
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//span[contains(string(), '内容已提交成功，请耐心等待审核')]")))







