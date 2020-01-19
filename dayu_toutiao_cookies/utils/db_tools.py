# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     db_tools
   Description :
   Author :       maodun
   date：          2019-06-11
-------------------------------------------------
   Change Activity:
                   2019-06-11:
-------------------------------------------------
"""
__author__ = 'maodun'


from lazyspider.lazystore import LazyMysql
import base64
from secure import *
import base64

class handle_mysql():

    def __init__(self):
        #mysql配置
        self.db_info = MY_INFO
        self.table = TABLE
        self.user = 'login_name'
        self.pwd = 'password'
        self.cookieCloumn = 'cookies'
        self.status_key = 'error_status'
        self.pid = 'pid'

        self.mysql_ins = LazyMysql(self.db_info)

    def hande_error(self, status, user_name):
        if status == 1:
            pwd_sql = "update {} set {}={} where login_name= '{}'".format(self.table, self.status_key, status, user_name)
            print("handle pwd error %s" %user_name)
            return self.mysql_ins.query(pwd_sql)

        elif status == 3:
            #QRError
            QR_sql = "update {} set {}={} where login_name='{}'".format(self.table, self.status_key, status, user_name)
            return self.mysql_ins.query(QR_sql)

    def update_cookies(self, cookie, user_name):
        cookies_sql = "update {} set {}= '{}' where login_name='{}'".format(self.table,  self.cookieCloumn, cookie,  user_name)
        print(cookies_sql)
        self.refresh_status(user_name)
        return self.mysql_ins.query(cookies_sql)

    def refresh_status(self, user_name):
        refresh_sql = "update {} set {}={} where login_name='{}'".format(self.table, self.status_key, 0, user_name)
        return self.mysql_ins.query(refresh_sql)

    def get_all_count(self, pid_name):
        get_sql = "select {}, {} from {} where {}={}".format(self.user, self.pwd, self.table, self.pid, pid_name)
        return self.mysql_ins.query(get_sql)

hd_mysql = handle_mysql()

if __name__ == '__main__':
    hd = handle_mysql()







