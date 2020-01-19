import json
import re
import time
import win32gui

import requests
import win32con
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

account = "2313858295@qq.com"
password = "chf880302"
video_type = "时尚"
video_path = r"d:\a1bad153a548f92f3078e89361dbce41.mp4"
image_path = r"d:\0.png"


def upload(path):
    dialog = win32gui.FindWindow(None, '打开')  # 对话框
    ComboBoxEx32 = win32gui.FindWindowEx(dialog, 0, 'ComboBoxEx32', None)
    ComboBox = win32gui.FindWindowEx(ComboBoxEx32, 0, 'ComboBox', None)
    # 获取文件路径输入框对象的句柄
    Edit = win32gui.FindWindowEx(ComboBox, 0, 'Edit', None)
    # 获取 打开button按钮对象
    button = win32gui.FindWindowEx(dialog, 0, 'Button', '打开(&O)')
    # 输入框输入绝对路径
    win32gui.SendMessage(Edit, win32con.WM_SETTEXT, 0, path)
    # 点击 打开
    win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, button)


def click(element_xpath, count=0):

    assert count < 10, "点击事件失败  element:".format(element_xpath)
    try:
        Browser.find_element_by_xpath(element_xpath).click()
    except WebDriverException as e:
        print("fail--", e)
        count += 1
        time.sleep(5)
        return click(element_xpath, count=count)


option = webdriver.ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])
Browser = webdriver.Chrome(chrome_options=option)

Browser.get("https://mp.dayu.com/")
time.sleep(3)
iframe = Browser.find_element_by_tag_name("iframe")
Browser.switch_to.frame(iframe)
Browser.find_element_by_xpath("//input[@id='login_name']").send_keys(account)
Browser.find_element_by_xpath("//input[@id='password']").send_keys(password)
slide = Browser.find_element_by_xpath("//span[@id='nc_1_n1z']")


# 过验证   TODO 轨迹待调整
action_chain = [30, 25, 45, 55, 40, 80]
ActionChains(Browser).click_and_hold(slide).perform()
for action in action_chain:
            time.sleep(0.1)
            ActionChains(Browser).move_by_offset(xoffset=action, yoffset=0).perform()
ActionChains(Browser).release().perform()
time.sleep(0.5)

# 切换视频上传页面
Browser.find_element_by_xpath("//input[@id='submit_btn']").click()
time.sleep(2)
Browser.find_element_by_xpath("//a[@id='w-menu-']").click()
time.sleep(1)
Browser.find_element_by_xpath("//a[@data-path='/dashboard/video/write']").click()
time.sleep(1)
# ----- end -----

# 视频上传开始
Browser.find_element_by_xpath("//div[@class='article-write_video-container-upload-from localVideoUpload']").click()
time.sleep(1)
upload(video_path)
# ---- end -----
WebDriverWait(Browser, 600).until(EC.presence_of_element_located((By.XPATH, "//div[@class='w-form-field-content']/input")))
time.sleep(2)
# 视频参数
Browser.find_element_by_xpath("//div[@class='w-form-field-content']/input").click()
time.sleep(0.05)
Browser.find_element_by_xpath("//div[@class='w-form-field-content']/input").clear()
Browser.find_element_by_xpath("//div[@class='w-form-field-content']/input").send_keys("标题标个题")
time.sleep(0.1)
Browser.find_element_by_xpath("//div[@class='w-form-field-content']/textarea").click()
time.sleep(0.05)
Browser.find_element_by_xpath("//div[@class='w-form-field-content']/textarea").clear()
Browser.find_element_by_xpath("//div[@class='w-form-field-content']/textarea").send_keys("简介简介")
Browser.find_element_by_xpath("//div[@class='widgets-selects_container']").click()
time.sleep(0.5)

WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located(
        (By.XPATH, "//div[@class='article-write_video-tags form-control']"))).click()
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located(
        (By.XPATH, "//div[@class='article-write_video-tags form-control']//input[1]"))).send_keys("过水电费干点啥风哥")
Browser.find_element_by_xpath("//div[@class='article-write_video-tags form-control']//input[1]").send_keys(Keys.ENTER)
time.sleep(1)
print(Browser.find_element_by_xpath("//div[@class='article-write_video-tags form-control']").get_attribute("innerHTML"))
WebDriverWait(Browser, 10).until(
    EC.presence_of_element_located(
        (By.XPATH, "//div[@class='article-write_video-tags form-control']/div[2]/input"))).send_keys("fasdf")
Browser.find_element_by_xpath("//div[@class='article-write_video-tags form-control']/div[2]/input").send_keys(Keys.ENTER)



Browser.find_element_by_xpath("//div[@class='widgets-selects_select_container']/a[contains(string(), '{}')]".format(video_type)).click()
image_div = Browser.find_element_by_xpath("//div[@class='article-write_box-form-coverImg']")
Browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
ActionChains(Browser).move_to_element(image_div).perform()
time.sleep(0.1)

image_div.find_element_by_xpath("//button[contains(string(), '从本地选择')]").click()
time.sleep(0.5)
upload(image_path)
time.sleep(2)

image_submit = Browser.find_element_by_xpath("//button[@class='w-btn w-btn_primary']")
ActionChains(Browser).move_to_element(image_submit).perform()
click("//div[@class='widgets-pop_container']//div[@class='w-btn-toolbar']/button[@class='w-btn w-btn_primary']")
# click("//div[@class='widgets-pop_container']//[contains(string(), '保存')]")

time.sleep(0.5)
click("//div[@class='article-write_radio']/div[@class='w-radio w-radio_checked iconfont wm-icon-yes']")
click("//button[contains(string(), '发表')]")
time.sleep(1)
# ---- end ----
# 确认发布
click("//button[contains(string(), '确认发表')]")

time.sleep(2)



# 获取aid
time.sleep(2)
click("//ul[@class='w-list']/li[1]//div[@class='w-list-item-content-detail']/h3/a")
time.sleep(4)
ahref = Browser.find_element_by_xpath("//div[@class='contents-publish-article-preview']/iframe").get_attribute("src")
time.sleep(1)
info_frame = Browser.find_element_by_xpath("//div[@class='contents-publish-article-preview']/iframe")
Browser.switch_to.frame(info_frame)
vhref = Browser.find_element_by_xpath("//p[@class='videobox']/iframe").get_attribute("src")
# https://mobile.dayu.com/preview.html?type=2&wm_cid=292528909420597248&ts=1559532453266&acl=7c06f9b244349a2d4dd0eb8ba7a94971&uc_biz_str=S:custom%7CC:iflow_wm2&uc_param_str=frdnsnpfvecpntnwprdssskt&wm_id=63acb030c4b74528bcf6fe7110247eea


def get_aid(href):
    url = "https://mobile.dayu.com/api/preview?wm_cid={}&type=2&ts={}&acl={}&type=2&biz_id=1002"
    wm_cid = re.search(r"wm_cid=(\d+?)&", href).group(1)
    acl = re.search("acl=(.*?)&", href).group(1)
    resp = requests.get(url.format(wm_cid, int(time.time()), acl))
    print(resp.text)
    j_resp = json.loads(resp.text)
    aid = j_resp["data"]["origin_id"]
    return aid


def get_vid(href):
    vid = re.search("video_id=(.*?)&", href)
    return vid


aid = get_aid(ahref)
vid = get_vid(vhref)
print(aid, vid)



