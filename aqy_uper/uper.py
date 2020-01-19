import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import logger


class aqy_uper():
    def __init__(self, id, user, pwd, video_path, image_path, title, short_title, channel, typeName, classify, area, vedioAddr, accountType):
        self.driver = webdriver.Chrome(executable_path='chromedriver')
        self.pub_id = id
        self.user = user
        self.pwd = pwd
        # self.video_path = video_path
        # self.image_path = image_path
        self.video_path = '\\\\192.168.200.249' + video_path[2:]
        self.image_path = '\\\\192.168.200.249' + image_path[2:]
        self.title = title
        self.short_title = short_title
        self.status = False
        self.msg = "发布成功"
        self.channel = channel
        self.type_name = typeName
        self.classify = classify
        self.area = area
        self.accountType = accountType
        #肖磊写错了应该是videoAddr
        self.videoAddr = vedioAddr
        self.cookies = ""
        #　TODO　需要查看aid和vid
        self.vid = None
        self.aid = None

    def get_cookies(self):
        cookies_temp = self.driver.get_cookies()
        cookies = ""
        for cookie in cookies_temp:
            name = cookie['name']
            values = cookie['value']
            cookie = name + "=" + values + "; "
            cookies = cookies + cookie
        cookies = cookies[:-2]
        return cookies

    @staticmethod
    def webdriverwait_send_keys(dri, element, value):
        """
        显示等待输入
        :param dri: driver
        :param element:
        :param value:
        :return:
        """
        WebDriverWait(dri, 10, 5).until(lambda dr: element).send_keys(value)

    @staticmethod
    def webdriverwait_click(dri, element):
        """
        显示等待 click
        :param dri: driver
        :param element:
        :return:
        """
        WebDriverWait(dri, 10, 5).until(lambda dr: element).click()

    def login(self):
        try:
            self.driver.delete_all_cookies()
            self.driver.maximize_window()
            self.driver.get("https://mp.iqiyi.com/")
            self.driver.find_element_by_xpath(
                u"(.//*[normalize-space(text()) and normalize-space(.)='注册'])[1]/following::a[1]").click()
            time.sleep(2)
            #选择账号密码登录
            self.driver.switch_to.frame(self.driver.find_element_by_id('login_frame'))
            self.driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div/div[4]/div[2]/p/span/a[1]").click()
            self.driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/input").clear()
            time.sleep(1)
            self.driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/input").send_keys(self.user)
            self.driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div/div[1]/div[1]/div/div[2]/div/input[1]").send_keys(self.pwd)
            self.driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div/div[1]/div[1]/div/a[2]").click()
            time.sleep(5)
        except Exception as e:
            logger.info(e)
            raise Exception("登录失败")

    def need_verify(self):
        try:
            return WebDriverWait(self.driver, 5).until(EC.text_to_be_present_in_element((By.XPATH, "//p[@class='default-text']"), '向右'))
        except Exception:
            return False
            logger.info("未检测到滑动验证码")
            pass



    #选择创作并上传视频
    def go_video(self):
        try:
            self.driver.implicitly_wait(20)
            self.cookies = self.get_cookies()
            self.driver.find_element_by_xpath('//*[@id="appEntry"]/div[2]/aside/div[2]/ul/li[1]/ul/li[2]/a/span').click()
            self.driver.implicitly_wait(10)
            try:
                pub_btn = self.driver.find_element_by_xpath('//*[@id="appEntry"]/div[2]/div/div[1]/div[2]/div[1]/div/div[1]/div/b')
                self.webdriverwait_click(self.driver, pub_btn)
            except Exception:
                pass
            # self.driver.find_element_by_xpath('//*[@id="appEntry"]/div[2]/div/div[1]/div[2]/div[1]/div/div[1]/div/b').click()
            time.sleep(2)
            os.system('up.exe ' + self.video_path)
            time.sleep(2)
            WebDriverWait(self.driver, 720).until(EC.presence_of_element_located((By.XPATH, "//span[contains(string(), '视频上传成功')]")))
            print("视频上传成了")
        except Exception as e:
            logger.info(e)
            raise Exception("上传视频失败")

    def is_rep(self):
        try:
            return WebDriverWait(self.driver, 40).until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="appEntry"]/div[2]/div/section/div/div[2]/div[1]/div[2]/div[2]/div[2]/div/span'), '重复'))
        except Exception:
            return  False

    def go_image(self):
        try:
            self.driver.implicitly_wait(20)
            self.driver.find_element_by_xpath('//*[@id="appEntry"]/div[2]/div/section/div/div[2]/div[2]/form/ul[1]/li[1]/div/div/div/div[1]/div[2]/div/div[1]/div').click()
            self.driver.implicitly_wait(20)
            self.driver.find_element_by_xpath('/html/body/div[5]/div[1]/div/div/div[2]/dl/dd/button').click()
            time.sleep(2)
            os.system('up.exe ' + self.image_path)
            time.sleep(2)
            self.driver.find_element_by_xpath('/html/body/div[5]/div[3]/button').click()
            WebDriverWait(self.driver, 160).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="appEntry"]/div[2]/div/section/div/div[2]/div[2]/form/ul[1]/li[1]/div/div/div/div[2]/span/i')))
            print("视频封面上传成功")
        except Exception as e:
            logger.info(e)
            raise Exception("上传封面失败")

    def go_twoTitle(self):
        try:
            self.driver.implicitly_wait(20)
            self.driver.find_element_by_xpath('//*[@id="appEntry"]/div[2]/div/section/div/div[2]/div[2]/form/ul[1]/li[2]/div/div/div[1]/input').clear()
            self.driver.find_element_by_xpath('//*[@id="appEntry"]/div[2]/div/section/div/div[2]/div[2]/form/ul[1]/li[2]/div/div/div[1]/input').send_keys(self.title)
            self.driver.implicitly_wait(20)
            self.driver.find_element_by_xpath('//*[@id="appEntry"]/div[2]/div/section/div/div[2]/div[2]/form/ul[1]/li[3]/div/div/div[1]/input').clear()
            self.driver.find_element_by_xpath('//*[@id="appEntry"]/div[2]/div/section/div/div[2]/div[2]/form/ul[1]/li[3]/div/div/div[1]/input').send_keys(self.short_title)
            print("打完标题了")
        except Exception as e:
            logger.info(e)
            raise Exception("打title失败")

    def go_channel(self):
        try:
            self.driver.implicitly_wait(20)
            #选择频道,按下弹出选择框
            if self.accountType == 1:
                self.driver.execute_script("var q=document.documentElement.scrollTop=100000")
                self.driver.find_element_by_xpath('//*[@id="appEntry"]/div[2]/div/section/div/div[2]/div[2]/form/ul[1]/li[7]/div/div/div/div[1]/span/span/i').click()
                time.sleep(10)
                self.driver.find_element_by_xpath("//li[contains(string(), '{}')]".format(self.channel)).click()
                time.sleep(4)
                #在选择框中选择 片花 片花是7
            if self.accountType == 2:
                self.driver.find_element_by_xpath('//*[@id="appEntry"]/div[2]/div/section/div/div[2]/div[2]/div[1]/ul/li[2]/a').click()
                time.sleep(4)
                self.driver.find_element_by_xpath('//*[@id="appEntry"]/div[2]/div/section/div/div[2]/div[2]/form/ul[2]/li[1]/div/div/div/div/div/span/span/i').click()
                time.sleep(4)
                try:
                    self.driver.find_element_by_xpath("//li[contains(string(), '{}')]".format(self.channel)).click()
                except Exception:
                    logger.info("无法通过字符串选择分类")
                time.sleep(4)
                self.driver.find_element_by_xpath('//*[@id="appEntry"]/div[2]/div/section/div/div[2]/div[2]/div[1]/ul/li[1]').click()
                time.sleep(2)
                self.driver.execute_script("var q=document.documentElement.scrollTop=1000")

            if self.channel == '片花':
                self.driver.find_element_by_xpath("//span[contains(string(), '{}')]".format(self.type_name)).click()
                time.sleep(5)
                self.driver.find_element_by_xpath("//span[contains(string(), '{}')]".format(self.classify)).click()
                time.sleep(5)
                if self.classify == '电影':
                    self.driver.find_element_by_xpath('//*[@id="appEntry"]/div[2]/div/section/div/div[2]/div[2]/form/ul[1]/ul/li[3]/div/div/div/input').send_keys(self.videoAddr)
                time.sleep(5)
                self.driver.find_element_by_xpath("//span[contains(string(), '{}')]".format(self.area)).click()
                #选择发布时间
                time.sleep(4)
                # self.driver.find_element_by_xpath("//i[@class='pf-icon icon-calendar']").click()
                # time.sleep(2)
                # #默认上传当天发布
                # # self.driver.find_element_by_xpath("//span[@class='flatpickr-day today selected']").click()
                # # self.driver.find_element_by_xpath("/html/body/div[19]/div[2]/div/div[2]/div/span[26]").click()
                print('选完频道了')
                self.driver.execute_script("var q=document.documentElement.scrollTop=100000")

        except Exception as e:
            logger.info(e)
            raise Exception("选频道失败")

    def orignal_publish(self):
        try:
            self.driver.implicitly_wait(20)
            #选择原创并发布
            self.driver.find_element_by_xpath("//*[@class='mp-svgicon svg-originalBtn mp-button--left']").click()
            time.sleep(2)
            # 发布
            self.driver.find_element_by_xpath("//*[@class='mp-button mp-button--success is-animate']").click()
            # #测试,选择发布为草稿
            # self.driver.find_element_by_xpath("//*[@rseat='fb_bmyccgan']").click()
            print("发布啦")
            time.sleep(5)
            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[20]/div/div[2]/div/a')))
                self.msg = "爱奇艺系统异常"
                return
            except Exception:
                print("没有系统异常")
            self.status = True
            time.sleep(5)
        except Exception as e:
            logger.info(e)
            raise Exception("发布失败")

    def main(self):
        try:
            self.login()
            if self.need_verify():
                raise  Exception("需要滑动码")
            self.go_video()
            if self.is_rep():
                raise  Exception("视频重复")
            self.go_image()
            self.go_twoTitle()
            self.go_channel()
            self.orignal_publish()
        except Exception as e:
            logger.info(e)
            self.msg = str(self.msg) + e.__str__()
            raise e
        finally:
            self.driver.quit()
            return self.status, self.msg, self.cookies


if __name__ == '__main__':
    # id, user, pwd, video_path, image_path, title, short_title, channel, type_name, classify, area, videoAddr, accountType)
    # aqy = aqy_uper(231, '15616210962@sohu.com','lp111628', 'D:\\aqy\\1\\1.mp4', 'D:\\aqy\\1\\1.png', '金喜宝和杨凯楠假洞房，被家人将房门钉死了，这下要假戏真做了！', '金喜宝和杨凯楠假洞房', '片花', '片花', '电影', '华语', 'https:www.baidu.com', 1)
    aqy = aqy_uper(231, 'AA56789aa@2980.com','A525186075i', 'D:\\aqy\\1\\6.mp4', 'D:\\aqy\\1\\1.png', '金喜宝和杨凯楠假洞房，被家人将房门钉死了，这下要假戏真做了！', '金喜宝和杨凯楠假洞房', '片花', '片花', '电影', '华语', 'https:www.baidu.com', 2)
    aqy.main()
    print(1)
