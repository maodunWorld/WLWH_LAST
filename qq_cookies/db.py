from lazyspider.lazystore import LazyMysql
import base64
from config import *
import base64

class handle_mysql():

    def __init__(self):
        self.db_info = MY_INFO
        self.handle_db = MYDB_INFO
        self.user = 'login_name'
        self.pwd = 'password'
        self.cookieCloumn = 'cookies'
        self.mysql_ins = LazyMysql(self.db_info)
        self.status_key = 'error_status'
        self.pid = 'pid'

    def hande_error(self, status, user_name):
        if status == 1:
            pwd_sql = "update {} set {}={} where login_name= '{}'".format(self.handle_db, self.status_key, status, user_name)
            print("handle pwd error %s" %user_name)
            return self.mysql_ins.query(pwd_sql)

        elif status == 3:
            #QRError
            QR_sql = "update {} set {}={} where login_name='{}'".format(self.handle_db, self.status_key, status, user_name)
            return self.mysql_ins.query(QR_sql)




    def update_cookies(self, cookie, user_name):
        cookies_sql = "update {} set {}= '{}' where login_name='{}'".format(self.handle_db,  self.cookieCloumn, cookie,  user_name)
        print(cookies_sql)
        self.refresh_status(user_name)
        print("update cookies %s" %user_name)
        return self.mysql_ins.query(cookies_sql)

    def get_allAccount(self):
        all_sql = "select {}, {} from {} where ({}=0 or {}=3) and {}=1".format(self.user, self.pwd, self.handle_db, self.status_key, self.status_key, self.pid)
        return self.mysql_ins.query(all_sql)

    def refresh_status(self, user_name):
        refresh_sql = "update {} set {}={} where login_name='{}'".format(self.handle_db, self.status_key, 0, user_name)
        print("refresh status %s" %user_name)
        return self.mysql_ins.query(refresh_sql)

    def refresh_allStatus(self):
        refresh_sql = "update {} set {}=0".format(self.handle_db, self.status_key)
        return self.mysql_ins.query(refresh_sql)

    def get_all_ccount(self, pid_name):
        get_sql = "select {}, {} from {} where {}={}".format(self.user, self.pwd, self.handle_db, self.pid, pid_name)
        return self.mysql_ins.query(get_sql)


hd_mysql2 = handle_mysql()

if __name__ == '__main__':
    hd = handle_mysql()
    print(hd.refresh_allStatus())
    # users = hd.get_all_ccount(1)
    # for _ in users:
    #
    #     user = _['login_name']
    #     pwd = base64.b64decode(_['password']).decode('utf8')
    #     print(user, pwd)






