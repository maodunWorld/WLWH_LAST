import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from util import logger, Utils
from settings import IS_OLINE


class QutoutiaoUpload(object):

    driver_path = "./driver/chromedriver.exe"

    def __init__(self, account, password, video_type, video_path, image_path, title, content, tags, id):
        self.id = id
        self.tags = tags
        self.account = account
        self.password = password
        self.video_type = video_type
        if IS_OLINE:
            self.video_path = video_path
            self.image_path = image_path
        else:
            self.video_path = '\\\\192.168.200.249' + video_path[2:]
            self.image_path = '\\\\192.168.200.249' + image_path[2:]
        self.title = title
        self.content = content
        self.msg = ''
        self.status = False
        self.aid = ''
        self.vid = ''
        self.browser = self.init_browser()

    def init_browser(self):
        option = webdriver.ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        browser = webdriver.Chrome(executable_path=self.driver_path, chrome_options=option)
        return browser

    def build_tag(self, tags):
        for tag in tags:
            self.browser.find_element_by_xpath("//div[@class='content-tag']//input").send_keys(tag)
            self.browser.find_element_by_xpath("//div[@class='content-tag']//input").send_keys(Keys.ENTER)
            time.sleep(0.5)

    def run(self):
        try:
            self.go()
        except Exception as e:
            logger.error("头条上传失败 任务id:{} error=>{}".format(self.id, e))
            self.msg = "上传未知失败  请检查上传日志 error:{}".format(e)
        self.browser.close()
        return self.status, self.aid, self.vid, self.msg

    def go(self):
        self.browser.get("https://mp.qutoutiao.net/login")
        # 登录开始
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//i[@class='login-icon']/following-sibling::input[1]"))).send_keys(self.account)
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//i[@class='pwd-icon']/following-sibling::input[1]"))).send_keys(
            self.password)
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@id='submit-login']"))).click()
        # 登录结束
        time.sleep(2)
        self.browser.maximize_window()

        # 跳转发布开始
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(string(), '发布内容')]"))).click()
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(string(), '发布视频')]"))).click()
        #手机验证码
        try:
            WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div[2]/div/div[2]/div/div[2]/div/div[3]/div/div[3]/span/button[1]/span'))
            )
            self.msg = '需要手机验证码，请延时提交'
            return
        except Exception:
            pass
        # *** 处理发文规范弹窗 ***
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//i[@class='el-message-box__close el-icon-close']"))).click()
        time.sleep(1)
        # 跳转发布结束

        # 开始发视频
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='inp-video-file']"))).click()
        time.sleep(1)  # 等待上传框体加载
        Utils.upload(self.video_path)
        WebDriverWait(self.browser, 100).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(string(), '上传成功')]")))
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//form[@class='el-form el-form--label-left']/div[1]//input"))).send_keys(
            [Keys.BACKSPACE for i in range(1, 100)] + [i for i in self.title])  # 发送标题
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@class='el-textarea__inner']"))).send_keys(
            self.content)  # 发送描述
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='请选择分类']"))).click()
        time.sleep(1)  # 等待分类加载
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//dd[contains(string(), '{}')]".format(self.video_type)))).click()
        time.sleep(1)
        self.build_tag(self.tags)
        time.sleep(0.5)
        # --  选择封面开始
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='el-upload']"))).click()
        time.sleep(1)  # 等待封面框体加载
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(string(), '自定义封面')]"))).click()
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(string(), '选择图片')]"))).click()
        time.sleep(1)  # 等待上传框体加载
        Utils.upload(self.image_path)
        time.sleep(3)  # 等待图片上传完成  # TODO 待处理
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            "//div[@class='el-dialog__wrapper dialog-img-cropper']//span[contains(string(), '确 定')]")))
        time.sleep(1)
        self.browser.find_element_by_xpath("//div[@class='el-dialog__wrapper dialog-img-cropper']//span[contains(string(), '确 定')]").click()
        # 封面选择结束
        # 视频信息构造结束
        time.sleep(3)
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[@class='el-button el-button--primary']//span[contains(string(), '发布')]"))).click()
        try:
            WebDriverWait(self.browser, 3).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='el-message-box__message']")))
            time.sleep(2)
            self.msg = self.browser.find_element_by_xpath("//div[@class='el-message-box__message']").text
            if self.msg:
                return
        except TimeoutException:
            pass
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@class='el-button el-button--primary el-button--medium']//span[contains(string(), '确认发布')]")))   # TODO
        time.sleep(1)
        self.browser.find_element_by_xpath("//button[@class='el-button el-button--primary el-button--medium']//span[contains(string(), '确认发布')]").click()
        time.sleep(2)
        self.status = True
        #    TODO 确认发布
