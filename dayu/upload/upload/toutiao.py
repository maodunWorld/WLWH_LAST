import re

import cv2
import random
import time
import requests
import traceback
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from util import logger, BASE_DIR, Utils


class ToutiaoUpload(object):

    driver_path = "./driver/chromedriver.exe"
    url = "https://sso.toutiao.com/login/?service=https://mp.toutiao.com/sso_confirm/?redirect_url=JTJG"

    def __init__(self, account, password, video_path, image_path, title, id, content, video_type, is_origin, is_first, tags, first_info=None):
        self.id = id
        self.tags = tags
        self.video_type = video_type
        self.is_first = is_first
        self.content = content
        self.account = account
        self.password = password
        # self.video_path = '\\\\192.168.200.249' + video_path[2:]
        # self.image_path = '\\\\192.168.200.249' + image_path[2:]
        self.video_path = video_path
        self.image_path = image_path
        self.is_origin = is_origin
        self.title = title
        self.first_url, self.first_platform, self.first_uname = self.parse_first_info(first_info)
        self.msg = ''
        self.status = False
        self.aid = ''
        self.vid = ''
        self.browser = self.init_browser()
        self.cookies = ""

    def get_cookies(self):
        cookies_temp = self.browser.get_cookies()
        cookies = ""
        for cookie in cookies_temp:
            name = cookie['name']
            values = cookie['value']
            cookie = name + "=" + values + "; "
            cookies = cookies + cookie
        cookies = cookies[:-2]
        return cookies

    @staticmethod
    def parse_first_info(first_info):
        if first_info:
            return first_info["first_url"], first_info["first_platform"], first_info["first_uname"]
        else:
            return "", "", ""

    @staticmethod
    def save_img(path, content):
        with open(path, "wb") as f:
            f.write(content)

    def init_browser(self):
        """初始化浏览器"""
        option = webdriver.ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        browser = webdriver.Chrome(executable_path=self.driver_path, chrome_options=option)
        return browser

    def run(self):
        try:
            self.go()
        except Exception as e:
            logger.error("头条上传失败 任务id:{} error=>{}".format(self.id, e))
            self.msg = "上传未知失败  请检查上传日志 error:{}".format(e)
        self.browser.close()
        return self.status, self.aid, self.vid, self.msg, self.cookies

    def build_tags(self, tags):
        for tag in tags:
            time.sleep(0.2)
            self.browser.find_element_by_xpath("//div[@class='edit-cell-new video-tag show-short']//input").send_keys(tag)
            self.browser.find_element_by_xpath("//div[@class='edit-cell-new video-tag show-short']//input").send_keys(Keys.ENTER)

    @staticmethod
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

    def get_aid(self, href):
        aid = re.search(r"pgc_id=(\d+)", href).group(1)
        return aid

    def get_vid(self, href):
        self.browser.get(href)
        vid = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='tt-video-box']"))).get_attribute("tt-videoid")
        return vid

    def handler_slider_verify(self):
        time.sleep(3)
        image = self.browser.find_element_by_xpath("//img[@id='validate-big']").get_attribute("src")
        block = self.browser.find_element_by_xpath("//img[@class='validate-block']").get_attribute("src")
        # 下载图片并保存
        image_resp = requests.get(image, headers=Utils.headers)
        image_path = BASE_DIR + r"\\cache\\" + str(int(time.time())) + str(random.randrange(10000, 99999)) + '0.jpg'
        self.save_img(image_path, image_resp.content)
        block_resp = requests.get(block, headers=Utils.headers)
        block_path = BASE_DIR + r"\\cache\\" + str(int(time.time())) + str(random.randrange(10000, 99999)) + "1.jpg"
        self.save_img(block_path, block_resp.content)
        # 过滑块
        time.sleep(2)
        location = self.get_location(image_path, block_path)

        start = self.browser.find_element_by_xpath("//img[@class='drag-button']")

        action_chain = Utils.action_list(location)
        ActionChains(self.browser).click_and_hold(start).perform()
        for action in action_chain:
            time.sleep(0.05)
            ActionChains(self.browser).move_by_offset(xoffset=action, yoffset=0).perform()
        ActionChains(self.browser).release().perform()
        try:         # TODO
            if WebDriverWait(self.browser, timeout=3).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='validate-msg validate-fail']"))):
                return self.handler_slider_verify()
        except TimeoutException:
            pass

    def go(self):
        # 登录
        self.browser.get("https://sso.toutiao.com/login/?service=https://mp.toutiao.com/sso_confirm/?redirect_url=JTJG")
        self.browser.implicitly_wait(30)
        self.browser.find_element_by_xpath("//div[@id='login-type-account']").click()
        time.sleep(2)
        self.browser.find_element_by_xpath("//input[@id='user-name']").send_keys(self.account)
        self.browser.find_element_by_xpath("//input[@id='password']").send_keys(self.password)
        time.sleep(0.1)
        self.browser.find_element_by_xpath("//button[@id='bytedance-login-submit']").click()
        self.handler_slider_verify()  # 处理滑块
        time.sleep(2)
        self.browser.maximize_window()
        # --- 登录结束 ----
        self.cookies = self.get_cookies()

        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(string(), '西瓜视频')]"))).click()
        self.browser.implicitly_wait(20)
        # 跳转视屏上传页面
        self.browser.get("https://mp.toutiao.com/profile_v3/xigua/upload-video")
        # 视屏上传开始
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='undefined upload-handler ']"))).click()
        time.sleep(1)  # 等待上传框体加载
        Utils.upload(self.video_path)
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(string(), '上传成功')]")))  # 等待视频上传完成
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='article-title-wrap-new']/input"))).clear()
        self.browser.find_element_by_xpath("//div[@class='article-title-wrap-new']/input").send_keys([Keys.BACKSPACE for i in range(1, 100)] + [i for i in self.title])
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='tui-input-wrapper']/textarea"))).clear()
        self.browser.find_element_by_xpath("//span[@class='tui-input-wrapper']/textarea").send_keys([Keys.BACKSPACE for i in range(1, 100)] + [i for i in self.content])

        if self.is_origin:  # 是否原创
            # WebDriverWait(Browser, 10).until(
            #     EC.presence_of_element_located((By.XPATH, "//div[@class='edit-cell-new add-origin']//div[@class='tui2-radio']/input"))).click()
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[@class='tui2-radio-text' and contains(string(), '声明原创')]/..//input"))).click()
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(string(.), '确 定')]"))).click()
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[@class='tui2-radio-text' and contains(string(), '非独家')]/..//input"))).click()
            if self.is_first:  # 是否首发
                WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//span[@class='tui2-radio-text' and contains(string(), '非首发')]/..//input"))).click()
                WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='m-video-first']/div[@class='edit-cell-new'][1]//input"))).send_keys(self.first_url)
                WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='m-video-first']/div[@class='edit-cell-new'][2]//input"))).send_keys(self.first_platform)
                WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='m-video-first']/div[@class='edit-cell-new'][3]//input"))).send_keys(self.first_uname)
            else:
                WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//span[@class='tui2-radio-text' and contains(string(), '首发')]/..//input"))).click()
        else:
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[@class='tui2-radio-text' and contains(string(), '非原创')]/..//input"))).click()
        # 原创结束

        self.build_tags(self.tags)
        # self.browser.find_element_by_xpath("//div[@class='edit-cell-new video-tag show-short']//input").send_keys("gsdfg")
        # self.browser.find_element_by_xpath("//div[@class='edit-cell-new video-tag show-short']//input").send_keys(Keys.ENTER)

        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='Select tui-select Select--single']/div[@class='Select-control']"))).click()
        time.sleep(0.1)
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='{}']".format(self.video_type)))).click()
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='submit btn ']"))).click()
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='m-pgc-video-manage']")))
        self.status = True
        # self.browser.close()
        # 获取信息开始
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='m-articles no-count']")))  # 确认视频列表加载
        href = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='m-articles no-count']/div[1]//a[@class='title-wrap']"))).get_attribute("href")
        self.aid = self.get_aid(href)
        self.vid = self.get_vid(href)

