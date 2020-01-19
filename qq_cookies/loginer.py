import cv2
import numpy as np
from time import sleep
import requests
import base64

#selenium配置
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import  By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import random

def sigmoid(x):
    s = 1 / (1 + 30 * np.exp(-x))
    return s

class QQCookies():
    def __init__(self, w):
        self.browser = w
        self.url = 'https://graph.qq.com/oauth2.0/authorize?client_id=101490602&response_type=code&redirect_uri=https%3A%2F%2Fom.qq.com%2FUser%2FQHLCallBack%3Furl%3Dhttps%253A%252F%252Fom.qq.com%252FuserAuth%252FsignInViaQQ%26target%3Dtop&state=STATE&scope=get_user_info&display=PC'
        self.wait = WebDriverWait(self.browser, 10)

    def open(self, user, pwd):
        self.browser.delete_all_cookies()
        self.browser.get(self.url)
        self.browser.switch_to.frame(self.browser.find_element_by_name('ptlogin_iframe'))
        user_pwd_btn = self.browser.find_element_by_id('switcher_plogin')
        user_pwd_btn.click()
        user_text = self.wait.until(EC.presence_of_all_elements_located((By.NAME, 'u')))
        user_text = self.browser.find_element_by_id('u')
        pwd_text =self.browser.find_element_by_id('p')
        submit_btn = self.browser.find_element_by_id('login_button')
        user_text.clear()
        user_text.send_keys(user)
        print(pwd)
        pwd_text.send_keys(pwd)
        submit_btn.click()

    def password_error(self):
        """
        判断用户名密码是否错误
        :return:
        """
        try:
            return WebDriverWait(self.browser, 1).until((EC.text_to_be_present_in_element((By.ID, 'err_m'), '密码')))
        except TimeoutException:
            return False

    @staticmethod
    def action_list(num):
        list_len = 6
        factor = num // list_len
        action_list = [factor for _ in range(list_len)]
        for index, action in enumerate(action_list[:list_len // 2]):
            rand = random.randrange(factor - 10, factor)
            action_list[index] = action_list[index] - rand
            action_list[-(index + 1)] = action_list[-(index + 1)] + rand
            factor -= 10
        return action_list

    def Need_qrcode(self):
        """
        判断是否需要扫码

        :return:
        """
        try:
            return WebDriverWait(self.browser, 1).until(EC.text_to_be_present_in_element((By.ID, 'err_m'), '手机'))
        except TimeoutException:
            return False

    #判断是否登录成功
    def login_seccessfully(self):


        sleep(1)
        try:
            if "腾讯内容" in self.browser.title:
                 return True
            return WebDriverWait(self.browser, 2).until(EC.visibility_of_element_located((By.XPATH, "//*[@class='link-logout']")))

        except TimeoutException:
            return False

    def still_gk(self):
        """
        判断是否继续滑块
        :return:

        """
        try:
            return WebDriverWait(self.browser,2).until(EC.text_to_be_present_in_element((By.ID, 'e_showFB'), '反馈'))
        except TimeoutException:
            print("无需继续滑动")
            return False

    def get_cookies(self):

        """
        获得当前cookies
        :return:
        """
        cookies_temp = self.browser.get_cookies()
        cookies = ""
        for cookie in cookies_temp:
            name = cookie['name']
            values = cookie['value']
            cookie = name + "=" + values + "; "
            cookies = cookies + cookie

        cookies = cookies[:-2]
        return cookies

    def save_image(self, url, name, img_type):
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0'
        res = requests.get(url, headers={'User-Agent': ua})
        # print(res.headers)
        if img_type == 1:
            image_name = "block"
        else:
            image_name = "bg"
        if res.headers['content-type'].find('png') != -1:
            img_file_path = name + "-" + image_name + ".png"
        elif res.headers['content-type'].find('jpeg') != -1:
            img_file_path = name + "-" + image_name + ".jpg"
        else:
            img_file_path = name + "-" + image_name + ".png"
        f = open(img_file_path, 'wb')
        f.write(res.content)
        f.close()
        return img_file_path

    def get_image_position(self):
        try:
            background = self.browser.find_element_by_id('slideBg').get_attribute('src')
            block = self.browser.find_element_by_id('slideBlock').get_attribute('src')
            if background is None or block is None:
                return
            bg_path = self.save_image(background, "dao", 2)
            print(bg_path)
            blk_path = self.save_image(block, "dao", 1)
            print(blk_path)
            block = cv2.imread(blk_path, 0)
            template = cv2.imread(bg_path, 0)
            cv2.imwrite('template.jpg', template)
            cv2.imwrite('block.jpg', block)
            block = cv2.imread('block.jpg')
            block = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)
            block = abs(255 - block)
            cv2.imwrite('block.jpg', block)
            block = cv2.imread('block.jpg')
            template = cv2.imread('template.jpg')
            result = cv2.matchTemplate(block, template, cv2.TM_CCOEFF_NORMED)
            x, y = np.unravel_index(result.argmax(), result.shape)
            element = self.browser.find_element_by_id('tcaptcha_drag_thumb')
            ActionChains(self.browser).click_and_hold(on_element=element).perform()
            ActionChains(self.browser).move_to_element_with_offset(to_element=element, xoffset=int(y * 0.4 + 18), yoffset=0).perform()
            sleep(1)
            ActionChains(self.browser).release(on_element=element).perform()
            # sleep(3)
        except Exception as e:
            print(e)
            print("hk shiwu")

    def start_handle(self):
        try:
            print("等待托块")
            sleep(3)
            self.get_image_position()
        except NoSuchElementException as msg:
            print("未找到拖动图片块")
            return False

    def Need_hk(self):
        try:
            return WebDriverWait(self.browser, 2).until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'tcaptcha_iframe')))
        except TimeoutException:
            return False



    def main(self, user, pwd):
        pwd = base64.b64decode(pwd)
        pwd = pwd.decode(encoding='utf8')
        for _ in range(4):
            self.open(user, pwd)
            if self.password_error():
                return 1
            if self.Need_qrcode():
                print("要扫码 %s" %user)
                return 3
            if self.Need_hk():
                self.start_handle()
                sleep(3)
                while True:
                    if self.still_gk():
                        self.start_handle()
                        print("还需要滑动")
                        sleep(2)
                    else:
                        break
            if not self.Need_hk() and not self.login_seccessfully() and not self.Need_qrcode():
                return 1
            if self.login_seccessfully():
                cookies = self.get_cookies()
                return cookies








if __name__ == '__main__':
    w  = webdriver.Chrome()
    loginer = QQCookies(w)
    loginer.main('11312239', 'bTk2OTc2MTk=')
