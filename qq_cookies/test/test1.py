from selenium import webdriver
import json

if __name__ == '__main__':
    driver = webdriver.Chrome('../chromedriver.exe')
    input(">>")
    cookies = driver.get_cookies()
    with open("cookies.txt", "w") as fp:
        json.dump(cookies, fp)