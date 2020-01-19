# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import random
import subprocess
import time
from datetime import datetime
from wl_spider_video.db.mysql import Video, session
from wl_spider_video.db.redis import redis_cli
from wl_spider_video.setting.const import CRAWL_DAY, DOWNLOAD_TIMEOUT
from wl_spider_video.util import iqiyi_channel_dict, qq_channel_dict, type_dict, youku_channel_dict
from scrapy.exceptions import DropItem

# DownloadPipeline  视屏下载(去重, 日期筛选)      SavePipeline   入库


class IqiyiDownloadVideoPipeline(object):
    # 视频下载
    def process_item(self, item, spider):
        if self.check_exist(item["playUrl"]) or self.check_time(item["time"]):
            spider.logger.info("丢弃重复条目 {}".format(item["name"]))
            raise DropItem
        url = item["playUrl"]
        date = datetime.now().strftime("%Y%m%d")
        channel = iqiyi_channel_dict[item["channelId"]]
        filename = item["name"] + ".mp4"
        item["site"] = "爱奇艺"
        download_path = "D:/采集资源/{}/{}/{}".format(item["site"], date, channel)
        redis_cli.sadd("iqiyi", item["playUrl"])
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        p = subprocess.Popen('you-get -o {} {}'.format(download_path, url),
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # 控制台调用you-get 阻塞式方法 下载视屏 stdout和stderr表示是否在控制台输出信息  不写的话表示在控制台打印消息

        try:
            p.communicate(timeout=DOWNLOAD_TIMEOUT)            # 下载单个视频最长等待时间
        except subprocess.TimeoutExpired:
            p.kill()
            spider.logger.error("下载视屏 {} 超时失败".format(item["playUrl"]))
            raise DropItem
        if p.returncode != 0:                                  # subprocess执行结果
            spider.logger.error("下载视屏 {} you-get失败".format(item["playUrl"]))
            raise DropItem
        item["path"] = download_path + "/" + filename
        return item

    @staticmethod
    def check_exist(url):
        if redis_cli.sismember("iqiyi", url):
            return True
        return False

    @staticmethod
    def check_time(_t):
        t = datetime.strptime(_t, "%Y-%m-%d")
        if (datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d") - t).days > CRAWL_DAY:
            return True
        return False


class IqiyiSavePipeline(object):

    def process_item(self, item, spider):
        did = str(int(time.time() * 1000)) + str(random.randrange(100000, 999999))
        iqiyi = Video()
        iqiyi.title = item["name"]
        iqiyi.type_name = iqiyi_channel_dict[item["channelId"]]
        iqiyi.publish_time = datetime.strptime(item["time"], "%Y-%m-%d")
        iqiyi.imgurl = item['imageUrl']
        iqiyi.create_time = datetime.now()
        iqiyi.intro = item["description"]
        iqiyi.source_url = item["playUrl"]
        iqiyi.path = item["path"]
        iqiyi.plat_name = item["site"]
        iqiyi.pid = 12         # 爱奇艺父级ID
        iqiyi.did = did
        iqiyi.is_index = 1
        iqiyi.type_id = type_dict[iqiyi_channel_dict[item["channelId"]]]
        iqiyi.is_reader = 1
        iqiyi.is_use = 1
        session.add(iqiyi)
        try:
            session.commit()
        except Exception as e:
            spider.logger.error("数据保存失败 from :{} 错误: {}".format(iqiyi.source_url, e))
            session.rollback()
            redis_cli.hdel("iqiyi", iqiyi.source_url)
            raise DropItem
        spider.logger.info("添加iqiyi条目 标题{} playUrl:{}".format(iqiyi.title, iqiyi.source_url))
        return item


class QqDownloadVideoPipeline(object):

    def process_item(self, item, spider):
        if self.check_time(item["publish_time"]) or self.check_exist(item["playUrl"]):
            spider.logger.warning("丢弃条目 {}".format(item))
            raise DropItem
        url = item["playUrl"]
        date = datetime.now().strftime("%Y%m%d")
        channel = qq_channel_dict[item["channel"]]
        item["site"] = "腾讯视频"
        filename = item["name"] + ".mp4"
        download_path = "D:/采集资源/{}/{}/{}".format(item["site"], date, channel)
        redis_cli.sadd("qqvideo", item["playUrl"])
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        p = subprocess.Popen('you-get -o {} {}'.format(download_path, url),
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            p.communicate(timeout=DOWNLOAD_TIMEOUT)  # 下载单个视频最长等待时间
        except subprocess.TimeoutExpired:
            p.kill()
            spider.logger.error("下载视屏 {} 超时失败".format(item["playUrl"]))
            raise DropItem
        if p.returncode != 0:
            spider.logger.error("下载视屏 {} you-get失败".format(item["playUrl"]))
            raise DropItem
        item["path"] = download_path + "/" + filename
        return item

    @staticmethod
    def check_time(_time):
        t = datetime.strptime(_time, "%Y年%m月%d日发布")
        if (datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d") - t).days > CRAWL_DAY:
            return True
        return False

    @staticmethod
    def check_exist(url):
        if redis_cli.sismember("qqvideo", url):
            return True
        return False


class QqSavePipeline(object):

    def process_item(self, item, spider):
        did = str(int(time.time() * 1000)) + str(random.randrange(100000, 999999))
        qqvideo = Video()
        qqvideo.title = item["name"]
        qqvideo.type_name = qq_channel_dict[item["channel"]]
        qqvideo.publish_time = datetime.strptime(item["publish_time"], "%Y年%m月%d日发布")
        qqvideo.publish_name = item['publish_name']
        qqvideo.imgurl = item['imgurl']
        qqvideo.create_time = datetime.now()
        qqvideo.intro = item["intro"]
        qqvideo.source_url = item["playUrl"]
        qqvideo.path = item["path"]
        qqvideo.plat_name = item["site"]
        qqvideo.type_id = type_dict[qq_channel_dict[item["channel"]]]
        qqvideo.is_reader = 1
        qqvideo.is_use = 1
        qqvideo.pid = 14         # 父级ID
        qqvideo.did = did
        qqvideo.is_index = 1
        session.add(qqvideo)
        try:
            session.commit()
        except Exception as e:
            spider.logger.error("数据保存失败 from :{} 错误: {}".format(qqvideo.source_url, e))
            session.rollback()
            redis_cli.hdel("qqvideo", qqvideo.source_url)
            raise DropItem
        spider.logger.info("添加qqvideo条目 标题{} playUrl:{}".format(qqvideo.title, qqvideo.source_url))
        return item


class YoukuDownloadVideoPipeline(object):

    def process_item(self, item, spider):
        if self.check_time(item["publish_time"]) or self.check_exist(item["playUrl"]):
            spider.logger.warning("丢弃条目 {}".format(item))
            raise DropItem
        url = item["playUrl"]
        date = datetime.now().strftime("%Y%m%d")
        channel = youku_channel_dict[item["channel"]]
        item["site"] = "优酷"
        filename = item["name"] + ".mp4"
        download_path = "D:/采集资源/{}/{}/{}".format(item["site"], date, channel)
        redis_cli.sadd("youku", item["playUrl"])
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        p = subprocess.Popen('you-get -o {} {}'.format(download_path, url),
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            p.communicate(timeout=DOWNLOAD_TIMEOUT)  # 下载单个视频最长等待时间
        except subprocess.TimeoutExpired:
            p.kill()
            spider.logger.error("下载视屏 {} 超时失败".format(item["playUrl"]))
            raise DropItem
        if p.returncode != 0:
            spider.logger.error("下载视屏 {} you-get失败".format(item["playUrl"]))
            raise DropItem
        item["path"] = download_path + "/" + filename
        return item

    @staticmethod
    def check_time(_time):
        t = datetime.strptime(_time, "上传于 %Y-%m-%d")
        if (datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d") - t).days > CRAWL_DAY:
            return True
        return False

    @staticmethod
    def check_exist(url):
        if redis_cli.sismember("youku", url):
            return True
        return False


class YoukuSavePipeline(object):

    def process_item(self, item, spider):
        did = str(int(time.time() * 1000)) + str(random.randrange(100000, 999999))
        video = Video()
        video.title = item["name"]
        video.type_name = youku_channel_dict[item["channel"]]
        video.publish_time = datetime.strptime(item["publish_time"], "上传于 %Y-%m-%d")
        video.publish_name = item['publish_name']
        video.imgurl = item['imgurl']
        video.create_time = datetime.now()
        video.intro = None
        video.source_url = item["playUrl"]
        video.path = item["path"]
        video.plat_name = item["site"]
        video.type_id = type_dict[youku_channel_dict[item["channel"]]]
        video.is_reader = 1
        video.is_use = 1
        video.is_index = 1
        video.pid = 15         #
        video.did = did
        session.add(video)
        try:
            session.commit()
        except Exception as e:
            spider.logger.error("数据保存失败 from :{} 错误: {}".format(video.source_url, e))
            session.rollback()
            redis_cli.hdel("youku", video.source_url)
            raise DropItem
        spider.logger.info("添加youku条目 标题{} playUrl:{}".format(video.title, video.source_url))
        return item


class P0601PipeLine(object):

    def process_item(self, item, spider):
        title = item['title']
        source = item["source_url"]
        vtype = item["vtype"]
        theme = item["theme"]
        if self.check_exist(source):
            spider.logger.warning("丢弃条目 {}".format(item))
            raise DropItem
        download_path = "D://剪辑片单/{}/{}".format(vtype, theme)
        print(download_path + "/" + title + ".mp4")
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        redis_cli.sadd("p0601", source)
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        p = subprocess.Popen('you-get -o {} {}'.format(download_path, source),
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            p.communicate(timeout=300)  # 下载单个视频最长等待时间
        except subprocess.TimeoutExpired:
            p.kill()
            spider.logger.error("下载视屏 {} 超时失败".format(item[source]))
            raise DropItem
        if p.returncode != 0:
            spider.logger.error("下载视屏 {} you-get失败".format(source))
            raise DropItem
        return item

    @staticmethod
    def check_exist(url):
        if redis_cli.sismember("p0601", url):
            return True
        return False
