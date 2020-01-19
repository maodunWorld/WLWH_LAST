# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     loginer_dayu
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
#架构设置
from utils.loginer_tools import CHROME_OPTION_toutiao
from utils.loginer_tools import action_list



def sigmoid(x):
    s = 1 / (1 + 30 * np.exp(-x))
    return s


class dayu_cookies():
    def __init__(self, w):
        self.browser =  w
        self.url = 'https://mp.dayu.com/?redirect_url=%2Fdashboard%2Findex'
        self.url2 = 'https://account.youku.com/partnerLogin.htm?pid=20170512PLF000867&callback=https%3A%2F%2Fmp.dayu.com%2Fyt-login-callback%3Fredirect_url%3D'

    def open(self, user, pwd, user_type):
        if len(user_type) == 1:
            self.browser.delete_all_cookies()
            self.browser.get(self.url2)
            try:
                self.browser.find_element_by_id('changeAccount').click()
                self.browser.find_element_by_xpath('//*[@id="YT-ytaccount"]').clear()
            except Exception as e:
                print(e)
                print("第一次")
            self.browser.find_element_by_xpath('//*[@id="YT-ytaccount"]').send_keys(user)
            self.browser.find_element_by_xpath('//*[@id="YT-ytpassword"]').send_keys(pwd)
            self.browser.find_element_by_xpath('//*[@id="YT-nloginSubmit"]').click()
            try:
                slide = self.browser.find_element_by_xpath('//*[@id="nc_1_n1z"]')
                action_chain = action_list(300)
                ActionChains(self.browser).click_and_hold(slide).perform()
                for action in action_chain:
                    sleep(0.2)
                    ActionChains(self.browser).move_by_offset(xoffset=action, yoffset=0).perform()
                ActionChains(self.browser).release().perform()
                submit_btn = self.browser.find_element_by_id('submit_btn')
                submit_btn.click()
            except Exception as e:
                print("不需要滑块")
            try:
                slide = self.browser.find_element_by_xpath('//*[@id="nc_1_n1z"]')
                action_chain = action_list(300)
                ActionChains(self.browser).click_and_hold(slide).perform()
                for action in action_chain:
                    sleep(0.2)
                    ActionChains(self.browser).move_by_offset(xoffset=action, yoffset=0).perform()
                ActionChains(self.browser).release().perform()
                submit_btn = self.browser.find_element_by_id('submit_btn')
                submit_btn.click()
            except Exception as e:
                print("不需要滑块")

        else:
            self.browser.delete_all_cookies()
            self.browser.get(self.url)
            self.browser.switch_to_frame(self.browser.find_element_by_xpath('//iframe'))
            user_text = self.browser.find_element_by_id('login_name').send_keys(user)
            pwd_text =self.browser.find_element_by_id('password').send_keys(pwd)

    #判断用户名密码是否错误
    def password_error(self):
        try:
            return WebDriverWait(self.browser, 1).until((EC.text_to_be_present_in_element((By.ID, 'message'), '密码')))
        except TimeoutException:
            return False

    #判断是否登录成功
    def login_seccessfully(self):
        try:
            if "大鱼" in self.browser.title:
                return True
            return WebDriverWait(self.browser, 2).until(EC.visibility_of_element_located((By.XPATH, '="index"]/div/div/div[2]/div[2]/a')))
        except TimeoutException:
            return False

    #获取格式化的cookies
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

    #是否需要手机登录
    def need_phone(self):
        try:
            if self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="login-msg"]'))):
                return True
        except TimeoutException:
            return False

    def hanlde_hk(self):
        slide = self.browser.find_element_by_xpath("//span[@id='nc_1_n1z']")
        action_chain = action_list(300)
        ActionChains(self.browser).click_and_hold(slide).perform()
        for action in action_chain:
            sleep(0.2)
            ActionChains(self.browser).move_by_offset(xoffset=action, yoffset=0).perform()
        ActionChains(self.browser).release().perform()
        submit_btn = self.browser.find_element_by_id('submit_btn')
        submit_btn.click()

    def main(self, user, pwd):
        pwd = base64.b64decode(pwd)
        pwd = pwd.decode(encoding='utf8')
        for _ in range(4):
            user_type = user.split('@')
            self.browser.delete_all_cookies()
            self.open(user, pwd, user_type)
            user_type = (len(user_type) == 1)
            if user_type:
                sleep(2)
                if self.login_seccessfully():
                    try:
                        self.browser.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/div/button[1]').click()
                    except Exception:
                        print("不需要同意")
                    return self.get_cookies()
                else:
                    return 1
            else:
                self.hanlde_hk()
                if self.password_error():
                    return 1
                if self.login_seccessfully():
                    cookies = self.get_cookies()
                    try:
                        self.browser.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/div/button[1]').click()
                    except Exception:
                        print("不需要同意")
                    return cookies
                if self.need_phone():
                    return 3
                if self.login_seccessfully():
                    cookies = self.get_cookies()
                    try:
                        self.browser.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/div/button[1]').click()
                    except Exception:
                        print("不需要同意")
                    return cookies

            return 1

if __name__ == '__main__':
    w  = webdriver.Chrome(executable_path=r'../driver_toutiao/chromedriver', chrome_options=CHROME_OPTION_toutiao)
    loginer = dayu_cookies(w)
    # while True:
    t = loginer.main('18692958083', 'Y2hmODgwMzAy')
    print(t)

