# -*- coding: utf-8 -*-
import re
from datetime import datetime
from urllib import parse

import scrapy
from wl_spider_video.items import P0601Item


class P0601Spider(scrapy.Spider):
    name = 'p0601'
    v_site = {
        "军旅": ["雪豹", "人间正道是沧桑", "激战", "激情燃烧的岁月", "士兵突击", "我的团长我的团", "我的兄弟叫顺溜"],
        "家庭": ["回家的诱惑", "贤妻", "我的宝贝", "两个女人的战争", "正阳门下", "情满四合院", "男人四十要出嫁", "我的体育老师", "妻子的谎言", "小别离", "哑巴新娘"],
        "悬疑": ["神探狄仁杰", "大宋提刑官", "伪装者", "胭脂", "猎人", "剃刀边缘", "天龙八部 胡军", "倚天屠龙记 苏有朋", "武林外史", "风云", "封神英雄", "木府风云", "山海经之赤影传说", "绝代双骄"],
        "真人秀": ["挑战灰姑娘", "好好学习吧", "中国星跳跃"],
        "情感": ["情牵一线", "爱的就是你", "约会万人迷", "转身遇到TA"]
    }

    custom_settings = {
        'ITEM_PIPELINES': {'wl_spider_video.pipelines.P0601PipeLine': 300}
    }
    allowed_domains = ['v.qq.com']

    url = 'https://v.qq.com/x/search/?ses=tabname_list=%E5%85%A8%E9%83%A8%7C%E6%B8%B8%E6%88%8F%7C%E5%B' \
                  '0%91%E5%84%BF%7C%E7%94%B5%E5%BD%B1%7C%E7%94%B5%E8%A7%86%E5%89%A7%7C%E7%BB%BC%E8%89%BA%7C%E6%9' \
                  '5%99%E8%82%B2&q={}&cur={}&rrr={}&stag=4&filter=sort%3D0%26pubfilter%3D0%26duration%3D0%26tabi' \
                  'd%3D2%26resolution%3D0#!filtering=1'

    @property
    def start_urls(self):
        urls = []
        for vtype in self.v_site:
            for theme in self.v_site[vtype]:
                for page in range(1, 21):
                    urls.append(self.url.format(theme, page, vtype))
        return urls

    def parse(self, response):
        ul = response.xpath("//div[@class='result_item result_item_h _quickopen']")
        vtype = parse.unquote(re.search(r"&rrr=(.*?)&", response.url).group(1))
        theme = parse.unquote(re.search(r"&q=(.*?)&", response.url).group(1))
        for li in ul:
            # 时常筛选
            video_time = li.xpath(".//span[@class='figure_info']/text()").extract_first()
            hour, minute, second = video_time.split(":")

            if hour != '0' or int(minute) > 4:
                continue
            # --- 时长筛选 end ----

            # 发布时间筛选
            publish_time = li.xpath(".//div[@class='info_item info_item_odd']/span[@class='content']/text()").extract_first()
            publish_time = datetime.strptime(publish_time, "%Y-%m-%d")
            if (datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d") - publish_time).days > 365:
                continue
            # 发布时间筛选 end ---
            item = P0601Item()
            item['title'] = li.xpath(".//h2[@class='result_title']/a").xpath("string(.)").extract_first()
            item['source_url'] = li.xpath(".//a[@class='figure result_figure']/@href").extract_first()
            item["theme"] = theme
            item["vtype"] = vtype
            yield item

