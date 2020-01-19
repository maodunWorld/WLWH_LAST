from selenium import  webdriver
import json

if __name__ == '__main__':

    driver = webdriver.Chrome('../chromedriver.exe')
    # 设置cookies前必须访问一次百度的页面
    driver.get("https://om.qq.com/userAuth/index")
    with open("cookies.txt", "r") as fp:
        cookies = json.load(fp)
        for cookie in cookies:
            cookie.pop('domain')  # 如果报domain无效的错误
            driver.add_cookie(cookie)

    driver.get("https://om.qq.com/userAuth/index")
    input(">>")
