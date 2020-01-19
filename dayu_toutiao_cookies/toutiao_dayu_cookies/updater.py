# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     updater
   Description :
   Author :       maodun
   date：          2019-06-11
-------------------------------------------------
   Change Activity:
                   2019-06-11:
-------------------------------------------------
"""
__author__ = 'maodun'

import os
import sys
import time
basedir = os.path.dirname(os.path.abspath(__name__))
sys.path.append(basedir)

from utils.db_tools import hd_mysql
from utils.loginer_tools import CHROME_OPTION_toutiao
from toutiao_dayu_cookies.loginer_toutiao import toutiao_cookies
from toutiao_dayu_cookies.loginer_dayu import dayu_cookies
from selenium import webdriver


class updater():
    def __init__(self, w):
        self.mysql_ins = hd_mysql
        self.user_key = 'login_name'
        self.pwd_key = 'password'
        self.w = w
        self.ttloginer = toutiao_cookies(self.w)
        self.dayuloginer = dayu_cookies(self.w)


    def toutiao(self):
        try:
            users = hd_mysql.get_all_count(3)
            for user in users:
                u = user[self.user_key]
                p = user[self.pwd_key]
                print(u)
                print(p)
                status = self.ttloginer.main(u, p)
                if status == 1:
                    hd_mysql.hande_error(status, u)
                    print("处理密码错误")

                    self.w.delete_all_cookies()
                    continue
                elif status == 3:
                    hd_mysql.hande_error(status, u)
                    print("处理手机验证码")
                    self.w.delete_all_cookies()
                    continue
                hd_mysql.update_cookies(status, u)
                self.w.delete_all_cookies()
                time.sleep(20)
        except Exception as e:
            print(e)
            print("updater init fade")

    def dayu(self):
        try:
            users = hd_mysql.get_all_count(4)
            for user in users:
                time.sleep(10)
                u = user[self.user_key]
                p = user[self.pwd_key]
                print(u)
                print(p)
                status = self.dayuloginer.main(u, p)
                if status == 1:
                    hd_mysql.hande_error(status, u)
                    print("处理密码错误")
                    self.w.delete_all_cookies()
                    time.sleep(10)
                    continue

                elif status == 3:
                    hd_mysql.hande_error(status, u)
                    print("处理手机验证码")
                    self.w.delete_all_cookies()
                    time.sleep(10)
                    continue
                hd_mysql.update_cookies(status, u)
                self.w.delete_all_cookies()
            self.w.quit()

        except Exception as e:
            print(e)
            print("updater init fade")


if __name__ == '__main__':
    while True:
        time.sleep(21600)
        w = webdriver.Chrome(executable_path=r'../driver_toutiao/chromedriver', options=CHROME_OPTION_toutiao)
        # w = webdriver.Chrome(executable_path=r'../driver_toutiao/chromedriver')
        up = updater(w)
        up.toutiao()
        up.dayu()
    # print("111")

