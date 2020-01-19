import os
import random
import sys
import time
import win32gui
import cv2
import requests
import numpy as np
import win32con
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait


title = "反攻倒算噶法规的"
content = "发生大幅第三方士大夫"
video_type = "动物"

def sigmoid(x):
    s = 1 / (1 + 30 * np.exp(-x))
    return s


def save_img(path, content):
    with open(path, "wb") as f:
        f.write(content)


def get_location(image_path, block_path):
    block = cv2.imread(block_path)
    block = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)
    block = abs(255 - block)
    cv2.imwrite(block_path, block)
    block = cv2.imread(block_path)
    template = cv2.imread(image_path)
    result = cv2.matchTemplate(block, template, cv2.TM_CCOEFF_NORMED)
    value = cv2.minMaxLoc(result)
    return value[2][0]


def handler_slider_verify():
    time.sleep(2)
    image = Browser.find_element_by_xpath("//img[@id='validate-big']").get_attribute("src")
    block = Browser.find_element_by_xpath("//img[@class='validate-block']").get_attribute("src")
    # 下载图片并保存
    image_resp = requests.get(image, headers=headers)
    image_path = BASE_DIR + r"\\cache\\" + str(int(time.time())) + str(random.randrange(10000, 99999)) + '0.jpg'
    save_img(image_path, image_resp.content)
    block_resp = requests.get(block, headers=headers)
    block_path = BASE_DIR + r"\\cache\\" + str(int(time.time())) + str(random.randrange(10000, 99999)) + "1.jpg"
    save_img(block_path, block_resp.content)
    # 过滑块
    time.sleep(2)
    location = get_location(image_path, block_path)

    start = Browser.find_element_by_xpath("//img[@class='drag-button']")

    action_chain = action_list(location)
    ActionChains(Browser).click_and_hold(start).perform()
    for action in action_chain:
        time.sleep(0.05)
        ActionChains(Browser).move_by_offset(xoffset=action, yoffset=0).perform()
    ActionChains(Browser).release().perform()
    try:
        if WebDriverWait(Browser, 1).until(EC.presence_of_element_located((By.XPATH, "//div[@class='validate-msg validate-fail']"))):
            return handler_slider_verify()
    except TimeoutException:
        pass


def action_list(num):
    remain = num
    act_list = list()
    randlist = list(map(sigmoid, range(10)))
    for i, rand in enumerate(randlist):
        if i == 9:
            randlist.pop()
            break
        randlist[i] = randlist[i+1] - randlist[i]
    factor = num / sum(randlist)
    for rand in randlist:
        randnumber = int(factor * rand) + 1
        act_list.append(randnumber)
        remain -= randnumber
    act_list.append(remain)
    return act_list


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


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__name__)))

option = webdriver.ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])

Browser = webdriver.Chrome(chrome_options=option)

# 登录
Browser.get("https://sso.toutiao.com/login/?service=https://mp.toutiao.com/sso_confirm/?redirect_url=JTJG")
Browser.implicitly_wait(30)
Browser.find_element_by_xpath("//div[@id='login-type-account']").click()
time.sleep(2)
Browser.find_element_by_xpath("//input[@id='user-name']").send_keys("212416231@qq.com")
Browser.find_element_by_xpath("//input[@id='password']").send_keys("aqsxcc62")
time.sleep(0.1)
Browser.find_element_by_xpath("//button[@id='bytedance-login-submit']").click()
handler_slider_verify()   # 处理滑块
print("=====")
# --- 登录结束 ----
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//span[contains(string(), '西瓜视频')]"))).click()
Browser.implicitly_wait(20)
# 跳转视屏上传页面
Browser.get("https://mp.toutiao.com/profile_v3/xigua/upload-video")
# 视屏上传开始
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//div[@class='undefined upload-handler ']"))).click()
time.sleep(1)      # 等待上传框体加载
upload(r"D:\剪辑片单\军旅\雪豹\雪豹：她被日军侮辱不敢面对水生！.mp4")
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//span[contains(string(), '上传成功')]"))) # 等待视频上传完成
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//div[@class='article-title-wrap-new']/input"))).clear()
Browser.find_element_by_xpath("//div[@class='article-title-wrap-new']/input").send_keys(title)
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//span[@class='tui-input-wrapper']/textarea"))).clear()
Browser.find_element_by_xpath("//span[@class='tui-input-wrapper']/textarea").send_keys(content)
is_origin = True
if is_origin:    # 是否原创
    # WebDriverWait(Browser, 10).until(
    #     EC.presence_of_element_located((By.XPATH, "//div[@class='edit-cell-new add-origin']//div[@class='tui2-radio']/input"))).click()
    WebDriverWait(Browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='tui2-radio-text' and contains(string(), '声明原创')]/..//input"))).click()
    WebDriverWait(Browser, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(string(.), '确 定')]"))).click()
    WebDriverWait(Browser, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[@class='tui2-radio-text' and contains(string(), '非独家')]/..//input"))).click()
    is_first = False
    if is_first:       # 是否首发
        WebDriverWait(Browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='tui2-radio-text' and contains(string(), '非首发')]/..//input"))).click()
        WebDriverWait(Browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='m-video-first']/div[@class='edit-cell-new'][1]//input"))).send_keys("http://www.baidu.com")
        WebDriverWait(Browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='m-video-first']/div[@class='edit-cell-new'][2]//input"))).send_keys("企鹅")
        WebDriverWait(Browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='m-video-first']/div[@class='edit-cell-new'][3]//input"))).send_keys("过水电费干点啥风哥")
    else:
        WebDriverWait(Browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[@class='tui2-radio-text' and contains(string(), '首发')]/..//input"))).click()
time.sleep(5)
# 原创结束
Browser.find_element_by_xpath("//div[@class='edit-cell-new video-tag show-short']//input").send_keys("gsdfg")
Browser.find_element_by_xpath("//div[@class='edit-cell-new video-tag show-short']//input").send_keys(Keys.ENTER)

WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//div[@class='Select tui-select Select--single']/div[@class='Select-control']"))).click()
time.sleep(0.1)
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//div[@aria-label='{}']".format(video_type)))).click()
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//div[@class='submit btn ']".format(video_type)))).click()


# # 切换发视频页面
# Browser.get("https://mp.toutiao.com/profile_v3/smallvideo/publish")
# # end
# WebDriverWait(Browser, 10).until(
#     EC.presence_of_element_located((By.XPATH, "//button[@class='tui2-btn tui2-btn-size-default tui2-btn-primary src-pages-publish-components-empty-file-index-button']"))).click()
# # --- end ---
# time.sleep(2)  # 等待上传框体加载
# upload(r"d:\a1bad153a548f92f3078e89361dbce41.mp4")
# # 构建上传信息
# WebDriverWait(Browser, 10).until(
#     EC.presence_of_element_located((By.XPATH, "//div[@class='src-pages-publish-index-publish-form']//textarea[@class='tui2-input']"))).send_keys("测试标题标题")
# -- 上传封面
# WebDriverWait(Browser, 10).until(
#     EC.presence_of_element_located((By.XPATH, "//img[@alt='设置封面']"))).click()
# time.sleep(3)
# WebDriverWait(Browser, 10).until(
#     EC.presence_of_element_located((By.XPATH, "//div[@class=' upload-handler']"))).click()
# time.sleep(1)  # 等待上传框加载
# upload(r"d:\0.png")
# time.sleep(5)
# WebDriverWait(Browser, 10).until(
#     EC.presence_of_element_located((By.XPATH, "//button[@class='tui2-btn tui2-btn-size-default tui2-btn-primary pgc-button']"))).click()   # 确定选择
# -- 封面上传end
# 上传信息构建结束
# WebDriverWait(Browser, 10).until(
#     EC.presence_of_element_located((By.XPATH, "//button[@class='tui2-btn tui2-btn-size-default tui2-btn-primary']"))).click()   # 确认发布




# bui-left upload-cover upload-cover-add
# element.find_element_by_xpath(".//a").get_attribute("href")
