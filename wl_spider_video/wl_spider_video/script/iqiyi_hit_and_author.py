"""
 爱奇艺热度更新
"""

import json
import requests
from lxml import etree
import sys
import os
import re
from sqlalchemy import and_
sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.abspath(__name__))))))
from wl_spider_video.db.mysql import Video, session


if __name__ == '__main__':
    # 加载视频作者和更新视频热度信息
    iqiyi_list = session.query(Video).filter(and_(Video.pid == 12)).all()
    for item in iqiyi_list:
        url = item.source_url
        print(url)
        try:
            resp = requests.get(url)
        except Exception as e:
            print("请求 {} 失败 错误:{}".format(url, e))
            continue
        tree = etree.HTML(resp.text)
        try:
            tvid = re.search(r'param\[\'tvid\'\] = "(\d+)"', resp.text).group(1)
            count_resp = requests.get("https://sns-comment.iqiyi.com/v3/comment/get_comments.action?agent_type=118"
                         "&agent_version=9.11.5&authcookie=null&business_type=17&content_id={}&"
                         "hot_size=0&last_id=204204282121&page=&page_size=20&types=time&"
                         "callback=jsonp_1558924151199_60824".format(tvid))
            total_count = re.search(r'"totalCount":(\d+),', count_resp.text).group(1)
            item.comment_num = total_count
        except Exception as e:
            print(e)
            continue
        try:
            ret = re.search("page-info='(.*?)'", resp.text, re.S)
            page_info = ret.group(1)
            info = json.loads(page_info)
            author = info["user"]["name"] if "user" in info and "name" in info["user"] else None
            tvid = info["tvId"]
            hot_response = requests.get("https://pcw-api.iqiyi.com/video/video/hotplaytimes/{}".format(tvid))
            hot = json.loads(hot_response.text)["data"][0]["hot"]
            item.hit = hot
            item.publish_name = author
            print(hot, author, item.cvedio_id, total_count)
            session.commit()
        except AttributeError as e:                        # 视频被删
            print(e)
            print("页面解析失败   url: {}".format(item.source_url))


