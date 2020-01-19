# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IqiyiItem(scrapy.Item):
    name = scrapy.Field()              # 标题
    description = scrapy.Field()       # 描述
    playUrl = scrapy.Field()           # 播放地址 (非视屏mp4地址)
    time = scrapy.Field()              # 发布时间 (日作为单位)
    site = scrapy.Field()              # 标识站点 (例: iqiyi)
    duration = scrapy.Field()          # 视屏时长
    imageUrl = scrapy.Field()          # 封面图片
    channelId = scrapy.Field()         # 采集分类
    path = scrapy.Field()              # 视频文件路径


class VideoItem(scrapy.Item):

    name = scrapy.Field()           # 标题
    intro = scrapy.Field()          # 介绍
    playUrl = scrapy.Field()        # 播放url
    imgurl = scrapy.Field()         # 封面url
    publish_time = scrapy.Field()   # 发布时间
    publish_name = scrapy.Field()   # 发布者
    path = scrapy.Field()           # 文件保存路径
    site = scrapy.Field()           # 站点
    channel = scrapy.Field()        # 类型


class P0601Item(scrapy.Item):
    vtype = scrapy.Field()
    theme = scrapy.Field()
    title = scrapy.Field()
    source_url = scrapy.Field()



