import hashlib
import json
import re
import requests
import time
from lxml import etree
import sys
import os
sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.abspath(__name__))))))
from wl_spider_video.db.mysql import Video, session


def sign(t):
    src = "100-DDwODVkv&6c4aa6af6560efff5df3c16c704b49f1&{}".format(t)
    m = hashlib.md5()
    m.update(src.encode())
    return m.hexdigest()

# 访问频率过快会可能导致拿不到评论数据


if __name__ == '__main__':
    videos = session.query(Video).filter(Video.pid == 15).all()
    for video in videos:
        resp = requests.get(video.source_url)
        tree = etree.HTML(resp.text)
        try:
            hit = tree.xpath("//div[@id='listitem_page1']/div[@class='item item-cover current']//div[@class='status']/span/text()")[0].replace("热度 ", "")
        except IndexError:
            print(video.source_url + "页面解析失败")
            continue
        vid = re.search(r"videoId: '(\d+)',", resp.text).group(1)
        t = str(int(time.time()))
        url = "https://p.comments.youku.com/ycp/comment/pc/commentList?" \
              "jsoncallback=n_commentList&app=100-DDwODVkv&objectId={}" \
              "&objectType=1&listType=0&currentPage=1&pageSize=30&sign={}&time={}".format(vid, sign(t), t)
        comment_resp = requests.get(url)
        comment_json = json.loads(comment_resp.text.replace("n_commentList(", "")[:-1])
        comment_total = comment_json["data"]["totalSize"]
        video.comment_num = comment_total
        video.hit = hit
        print(comment_total, hit, video.source_url)
        session.commit()





