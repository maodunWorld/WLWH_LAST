import json
import random
import re
import time
import numpy as np
import requests
import traceback

from selenium.webdriver.common.keys import Keys

from util import Utils, logger
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def sigmoid(x):
    s = 1 / (1 + 30 * np.exp(-x))
    return s


class DayuUpload(object):

    driver_path = "./driver/chromedriver.exe"

    def __init__(self, account, password, video_type, video_path, image_path, title, content, id, tags):
        self.id = id
        self.tags = tags
        self.account = account
        self.password = password
        self.video_type = video_type
        self.video_path = video_path
        self.image_path = image_path
        self.title = title
        self.content = content
        self.msg = ''
        self.up_num = 15
        self.status = False
        self.aid = ''
        self.vid = ''
        self.browser = self.init_browser()

    def init_browser(self):
        option = webdriver.ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        browser = webdriver.Chrome(executable_path=self.driver_path, chrome_options=option)
        return browser

    def returned_status(self):
        self.status = False
        return self.status, self.aid, self.vid, self.msg


    def get_aid(self, href):
        url = "https://mobile.dayu.com/api/preview?wm_cid={}&type=2&ts={}&acl={}&type=2&biz_id=1002"
        wm_cid = re.search(r"wm_cid=(\d+?)&", href).group(1)
        acl = re.search("acl=(.*?)&", href).group(1)
        resp = requests.get(url.format(wm_cid, int(time.time()), acl))
        j_resp = json.loads(resp.text)
        aid = j_resp["data"]["origin_id"]
        return aid

    def get_vid(self, href):
        vid = re.search("video_id=(.*?)&", href).group(1)
        return vid

    @staticmethod
    def action_list(num):
        """
        :param num: y 轴移动总距离
        """
        list_len = 6
        factor = num // list_len
        action_list = [factor for _ in range(list_len)]
        for index, action in enumerate(action_list[:list_len // 2]):
            rand = random.randrange(factor - 10, factor)
            action_list[index] = action_list[index] - rand
            action_list[-(index + 1)] = action_list[-(index + 1)] + rand
            factor -= 10
        return action_list

    def build_tags(self, tags):
        time.sleep(0.5)
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='article-write_video-tags form-control']"))).click()
        for i, tag in enumerate(tags, start=1):
            time.sleep(0.2)
            xpath = "//div[@class='article-write_video-tags form-control']/div[{}]/input".format(i)
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, xpath))).send_keys(tag)
            self.browser.find_element_by_xpath(xpath).send_keys(Keys.ENTER)



    def login(self):
        try:
            user_type = self.account.split('@')
            if len(user_type) > 1:
                self.browser.get("https://mp.dayu.com/")
                time.sleep(3)
                iframe = self.browser.find_element_by_tag_name("iframe")
                self.browser.switch_to.frame(iframe)
                self.browser.find_element_by_xpath("//input[@id='login_name']").send_keys(self.account)
                self.browser.find_element_by_xpath("//input[@id='password']").send_keys(self.password)
                slide = self.browser.find_element_by_xpath("//span[@id='nc_1_n1z']")

                action_chain = self.action_list(300)
                ActionChains(self.browser).click_and_hold(slide).perform()
                for action in action_chain:
                    time.sleep(0.1)
                    ActionChains(self.browser).move_by_offset(xoffset=action, yoffset=0).perform()
                ActionChains(self.browser).release().perform()
                WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//b[contains(string(), '验证通过')]")))
                self.browser.find_element_by_xpath("//input[@id='submit_btn']").click()
            else:
                self.browser.get('https://account.youku.com/partnerLogin.htm?pid=20170512PLF000867&callback=https%3A%2F%2Fmp.dayu.com%2Fyt-login-callback%3Fredirect_url%3D')
                time.sleep(3)
                self.browser.find_element_by_xpath('//*[@id="YT-ytaccount"]').send_keys(self.account)
                self.browser.find_element_by_xpath('//*[@id="YT-ytpassword"]').send_keys(self.password)
                self.browser.find_element_by_xpath('//*[@id="YT-nloginSubmit"]').click()
                time.sleep(3)

        except Exception as e:
            logger.error("大鱼号任务登录失败 任务ID{} ，失败信息{}".format(self.id, e))
            self.msg = "登录出现失败,  请通知技术人员, 并重新提交"
            return True
        try:
            self.browser.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/div/button[1]').click()
            time.sleep(2)
        except Exception:
            pass

        self.browser.maximize_window()

    def goto_create(self):
        try:
            # 切换视频上传页面
            time.sleep(1)
            self.browser.implicitly_wait(10)
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[@id='w-menu-']"))).click()
            time.sleep(2)
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[@data-path='/dashboard/video/write']"))).click()
            time.sleep(1)
            return True
            # ----- end -----
        except Exception as e:
            self.msg =  '跳转创作短视频失败，请重新提交'
            return True

    def upload_video(self):

        try:
            # 视频上传开始
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='article-write_video-container-upload-local']"))).click()
            time.sleep(1)
            Utils.upload(self.video_path)
            time.sleep(2)
            # try:
            #     Utils.upload(self.video_path)
            # except Exception as e:
            #     print(e)
            #     print("第二次打视频地址")
            # ---- end -----
            WebDriverWait(self.browser, 180).until(
                EC.presence_of_element_located((By.XPATH, "//p[contains(string(), '视频上传成功，处理中')]")))
            time.sleep(2)
            up_number = int(self.browser.find_element_by_xpath('/html/body/div[1]/div[4]/div/div[2]/div/div/div[2]/div/div[2]/span').text())
            if up_number == 0:
                self.msg = "上传数量不足"
                return True
                # self.up_num = up_number
        except Exception as e:
            self.msg = str(e) + "视频打开上传失败，请通知技术人员,并重新上传"
            self.returned_status()
            return True

    def make_title(self):
        try:
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='w-form-field-content']/input"))).clear()
            self.browser.find_element_by_xpath("//div[@class='w-form-field-content']/input").clear()
            time.sleep(0.1)
            self.browser.find_element_by_xpath("//div[@class='w-form-field-content']/input").send_keys([Keys.BACKSPACE for i in range(1, 100)] + [i for i in self.title])
            time.sleep(0.1)
        except Exception as e:
            logger.error("写标题，视频简介失败， 具体内容为{}".format(e))
            self.msg("系统故障，请重新上传")
            return True

    def make_tag_type(self):
        try:
            js = "var q=document.documentElement.scrollTop=100000"
            self.browser.execute_script(js)
            self.browser.find_element_by_xpath("//div[@class='w-form-field-content']/textarea").clear()
            time.sleep(0.1)
            self.browser.find_element_by_xpath("//div[@class='w-form-field-content']/textarea").send_keys(
                [Keys.BACKSPACE for i in range(1, 100)] + [i for i in self.title])
            time.sleep(0.1)
            self.build_tags(self.tags)
            self.browser.find_element_by_xpath("//div[@class='widgets-selects_container']").click()
            print("选择分类失败")
        except Exception as e:
            logger.error("选tag， 选分类失败{}".format(e))
            self.msg = "系统故障，请重新提交"
            return  True

    def upload_img(self):
        try:
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='widgets-selects_select_container']/a[contains(string(), '{}')]".format(self.video_type)))).click()
            image_div = self.browser.find_element_by_xpath("//div[@class='article-write_box-form-coverImg']")
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            ActionChains(self.browser).move_to_element(image_div).perform()
            ActionChains(self.browser).move_to_element(image_div).perform()
            ActionChains(self.browser).move_to_element(image_div).perform()
            ActionChains(self.browser).move_to_element(image_div).perform()
            time.sleep(0.1)
            image_div.find_element_by_xpath("//button[contains(string(), '从本地选择')]").click()
            time.sleep(0.5)
            print(self.image_path)
            Utils.upload(self.image_path)
            print("打图片地址上去")
            # Utils.upload(self.image_path)
            # print("丢图片地址异常")
            # time.sleep(2)

            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='article-material-image-dialog_btn']//button[contains(string(), '保存') and not(@disabled)]"))).click()
            time.sleep(2)
        except Exception as e:
            logger.error("上传封面失败，失败信息{}".format(e))
            self.msg = "上传失败，重新提交"
            return True

    def send(self):
        try:
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(string(), '发表')]"))).click()
            time.sleep(1)

            # # 判断是否标题党
            # try:
            #     WebDriverWait(self.browser, 3).until(
            #         EC.text_to_be_present_in_element((By.XPATH, "/html/body/div[4]/div/div[2]/div/div[1]"), '平台')
            #     )
            #     self.msg = "标题党嫌疑，请再改改"
            # except Exception as e:
            #     print("暂无标题党嫌疑")
            # ---- end ----
            # 确认发布
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(string(), '确认发表')]"))).click()
            # ---- end ----
            # 获取视频信息
            time.sleep(2)
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//ul[@class='w-list']/li[1]//div[@class='w-list-item-content-detail']/h3/a"))).click()
            self.status = True
            time.sleep(2)
            ahref = self.browser.find_element_by_xpath(
                "//div[@class='contents-publish-article-preview']/iframe").get_attribute("src")
            info_frame = self.browser.find_element_by_xpath("//div[@class='contents-publish-article-preview']/iframe")
            self.browser.switch_to.frame(info_frame)
            vhref = self.browser.find_element_by_xpath("//div[@class='article-content simple-ui']//iframe").get_attribute(
                "src")
            self.aid = self.get_aid(ahref)
            self.vid = self.get_vid(vhref)
        except Exception as e:
            logger.error("发表问题 {}".format(e))
            self.msg = "标题党嫌疑，请你重新修改"
            return True

    def go(self):
        if self.login():
            return
        if self.goto_create():
            return
        if self.upload_video():
            return
        if self.make_title():
            return
        if self.make_tag_type():
            return
        if self.upload_img():
            return
        time.sleep(10)
        if self.send():
            return

    def run(self):
        try:
            self.go()
        except Exception as e:
            logger.error("大鱼上传失败 任务id:{} error=>{}".format(self.id, e))
            self.msg = "上传未知失败  请检查上传日志 error:{}".format(e)
        self.browser.close()
        return self.status, self.aid, self.vid, self.msg