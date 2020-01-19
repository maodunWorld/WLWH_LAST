# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     loginer
   Description :
   Author :       maodun
   date：          2019-06-11
-------------------------------------------------
   Change Activity:
                   2019-06-11:
-------------------------------------------------
"""
__author__ = 'maodun'
from time import sleep
import base64
import random

#selenium配置
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import  By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import cv2
import numpy as np
import requests

from  utils.loginer_tools import action_list, CHROME_OPTION_toutiao



class toutiao_cookies():
    def __init__(self, w):
        self.browser = w
        self.url = 'https://sso.toutiao.com/login/?service=https://mp.toutiao.com/sso_confirm/?redirect_url=/'
        self.wait = WebDriverWait(self.browser, 10)

    def open(self, user, pwd):
        self.browser.delete_all_cookies()
        self.browser.get(self.url)
        self.browser.find_element_by_xpath('//*[@id="login-type-account"]/img').click()
        user_text = self.browser.find_element_by_id('user-name').send_keys(user)
        pwd_text =self.browser.find_element_by_id('password').send_keys(pwd)
        submit_btn = self.browser.find_element_by_id('bytedance-login-submit').click()

    def close_click(self):
        try:
            self.browser.execute_script('document.getElementById("verify-container").setAttribute("style", "display:none")')
            submit_btn = self.browser.find_element_by_id('bytedance-login-submit')
            submit_btn.click()
        except Exception:
            print("close and click is done")

    #用户名密码错误判断
    def password_error(self):
        try:
            return WebDriverWait(self.browser, 1).until((EC.text_to_be_present_in_element((By.ID, 'login-msg'), '密码')))
        except TimeoutException:
            return False

    #判断是否登录成功
    def login_seccessfully(self):
        sleep(1)
        try:
            if "头条号" in self.browser.title:
                 return True
            return WebDriverWait(self.browser, 2).until(EC.visibility_of_element_located((By.XPATH, '="index"]/div/div/div[2]/div[2]/a')))
        except TimeoutException:
            return False


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

    def save_image(self, url, name, img_type):
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0'
        res = requests.get(url, headers={'User-Agent': ua})
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

    def need_phone(self):
        try:
            if self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="login-msg"]'))):
                return True
        except TimeoutException:
            return False

    def get_image_position(self):
        background = self.browser.find_element_by_xpath('//*[@id="validate-big"]').get_attribute('src')
        block = self.browser.find_element_by_xpath('//*[@id="verify-bar-box"]/div[2]/img[2]').get_attribute('src')
        if background is None or block is None:
            return
        bg_path = self.save_image(background, "dao", 2)
        blk_path = self.save_image(block, "dao", 1)
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
        value = cv2.minMaxLoc(result)
        element = self.browser.find_element_by_xpath('//*[@id="validate-drag-wrapper"]/div[2]/img')
        ActionChains(self.browser).click_and_hold(on_element=element).perform()
        trunk = action_list(value[2][0])
        for i in trunk:
            ActionChains(self.browser).move_by_offset(xoffset=i, yoffset=0).perform()
            sleep(0.1)
        ActionChains(self.browser).release(on_element=element).perform()
        sleep(1)

    def start_handle(self):
        try:
            print("等待托块")
            self.get_image_position()
        except NoSuchElementException as msg:
            print("未找到拖动图片块")
            return False


    def agree(self):
        try:
            WebDriverWait(self.browser, 3).until(EC.element_to_be_clickable((By.XPATH('/html/body/div[2]/div/div[2]/div/div/button[1]'))))
        except TimeoutException:
            print("不需要同意")

        pass


    def still_hk(self):
        #判断是否还要滑动
        try:
            return WebDriverWait(self.browser, 2).until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="validate-refresh-box"]/span'), '刷新'))
        except TimeoutException:
            print("无需再滑动")
            return False


    def main(self, user, pwd):
        pwd = base64.b64decode(pwd)
        pwd = pwd.decode(encoding='utf8')
        for _ in range(4):
            self.open(user, pwd)
            if self.login_seccessfully():
                cookies = self.get_cookies()
                return cookies
            self.start_handle()
            if self.still_hk():
                self.close_click()
            if self.password_error():
                return 1
            if self.need_phone():
                return 3
            if self.login_seccessfully():
                cookies = self.get_cookies()
                return cookies
            sleep(20)


if __name__ == '__main__':

    w  = webdriver.Chrome(chrome_options=CHROME_OPTION_toutiao)
    loginer = toutiao_cookies(w)
    sleep(2)
    while True:
        t = loginer.main('212416231@qq.com', 'YXFzeGNjNjI=')

        t2 = loginer.main('2587105446@qq.com','YWZyMTQ1NTk=')
        t3 = loginer.main('2587105446@qq.com', 'cmI2ODcxNjE=')
        print(t)
        print(t2)
        print(t3)
