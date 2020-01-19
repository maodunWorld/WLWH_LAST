import requests
import json
from requests.cookies import RequestsCookieJar
s = requests.session()
s.verify = False
def login():

    s.headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"
    }


    #这里我们使用cookie对象进行处理
    jar = RequestsCookieJar()
    with open("cookies.txt", "r") as fp:
        cookies = json.load(fp)
        for cookie in cookies:
            jar.set(cookie['name'], cookie['value'])

    #百度个人中心
    #r = s.get("https://www.baidu.com/p/setting/profile/basic", cookies=jar)

    # 也可以使用字典设置
    cookies_dict = dict()
    with open("cookies.txt", "r") as fp:
        cookies = json.load(fp)
        for cookie in cookies:
            cookies_dict[cookie['name']] = cookie['value']
    r = s.get("https://om.qq.com/omIndex/getIndexChangeDetail?relogin=1", cookies=cookies_dict)

    r.encoding = "utf-8"
    print(r.text)

if __name__ == '__main__':
    login()