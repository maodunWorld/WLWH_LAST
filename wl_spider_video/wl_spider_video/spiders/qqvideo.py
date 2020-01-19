# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request
from wl_spider_video.items import VideoItem


class QqvideoSpider(scrapy.Spider):
    name = 'qqvideo'
    allowed_domains = ['v.qq.com']
    custom_settings = {
        'ITEM_PIPELINES': {'wl_spider_video.pipelines.QqDownloadVideoPipeline': 300,
                           'wl_spider_video.pipelines.QqSavePipeline': 400}
    }
    start_urls = ["https://v.qq.com/x/bu/pagesheet/list?_all=1&append=1&" \
                  "channel=tech&listpage=1&offset={}&pagesize=30&sort=5".format(i * 30) for i in range(34)]

    def parse(self, response):
        channel = re.search("channel=(.*?)&", str(response.request)).group(1)
        ul = response.xpath("//div[@class='list_item']")
        for li in ul:
            item = VideoItem()
            item["channel"] = channel
            item["playUrl"] = li.xpath("./a[@class='figure']/@href").extract_first()
            item["name"] = li.xpath("./a[@class='figure']/@title").extract_first()
            item['imgurl'] = li.xpath("./a[@class='figure']/img/@src").extract_first()
            yield Request(url=item["playUrl"], callback=self.parse_inner, meta={"item": item})

    def parse_inner(self, response):
        item = response.meta["item"]
        item['publish_time'] = response.xpath("//span[@class='date _date']/text()").extract_first()
        item['publish_name'] = response.xpath("//span[@class='user_name']/text()").extract_first()
        item['intro'] = response.xpath("//p[@class='summary _video_summary']/text()").extract_first()
        yield item


