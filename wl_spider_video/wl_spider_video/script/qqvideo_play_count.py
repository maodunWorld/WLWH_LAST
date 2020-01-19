import json
import re
import requests
from sqlalchemy import and_
from lxml import etree
import sys
import os
sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.abspath(__name__))))))
from wl_spider_video.db.mysql import Video, session

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"
}


def get_comment_id(vid):
    callback = "jQuery19106928096080068464_1559015878967"
    url = "https://ncgi.video.qq.com/fcgi-bin/video_comment_id?otype=json&callback={}&op=3&vid={}".format(callback, vid)
    resp = requests.get(url)
    comment_id_json = json.loads(resp.text.replace("jQuery19106928096080068464_1559015878967(", "")[:-1])
    return comment_id_json["comment_id"]


if __name__ == '__main__':
    videos = session.query(Video).filter(and_(Video.pid == 14))
    for video in videos:
        url = video.source_url
        resp = requests.get(url, headers=headers)
        tree = etree.HTML(resp.text)
        try:
            hit = tree.xpath("//em[@id='mod_cover_playnum']/text()")[0]
            vid = re.search("page/(.*).html", url).group(1)
            common_id = get_comment_id(vid)
            if common_id:
                print(common_id, "==============================")
                common_resp = requests.get("https://video.coral.qq.com/varticle/{}/comment/v2?callback=_varticle{}"
                             "commentv2&orinum=10&oriorder=o&pageflag=0&cursor=6389071156922256034&"
                             "scorecursor=0&orirepnum=2&reporder=o&reppageflag=1&source=132&".format(common_id, common_id), headers=headers)
                total_commont = re.search(r'"oritotal":(\d+),', common_resp.text).group(1)
                video.comment_num = total_commont
            else:
                video.comment_num = 0
        except IndexError:
            print("页面解析失败 {}".format(video.source_url))
            continue
        if not hit.isdigit():
            hit = int(float(re.search(r"\d+", hit).group())) * 10000
        video.hit = int(hit)
        print(video.title, video.hit, video.source_url, video.comment_num)
        session.commit()


