import os
import sys
basedir = os.path.dirname(os.path.abspath(__name__))
sys.path.append(basedir)
from db import hd_mysql2
import time
from loginer import QQCookies
from selenium import webdriver
import datetime

class updater():

    def __init__(self):
        self.mysql_ins = hd_mysql2
        self.w = webdriver.Chrome(executable_path='chromedriver.exe')
        self.loginer = QQCookies(self.w)
        self.user_key = 'login_name'
        self.pwd_key = 'password'


    def main(self):
        try:
            users = hd_mysql2.get_all_ccount(1)
            for user in users:
                time.sleep(10)
                u = user[self.user_key]
                p = user[self.pwd_key]
                print(u)
                print(p)
                status = self.loginer.main(u, p)
                # u = int(u)
                if status == 1:
                    hd_mysql2.hande_error(status, u)
                    print("处理密码错误")
                    continue

                elif status == 3:
                    hd_mysql2.hande_error(status, u)
                    print("处理扫码")
                    time.sleep(10)
                    continue
                hd_mysql2.update_cookies(status, u)
                time.sleep(10)
            self.w.quit()
        except Exception as  e:
            print(e)
            print("updater init fade")


if __name__ == '__main__':
    while True:

        time.sleep(3600)
        up = updater()
        up.main()
        print(datetime.datetime.now())
