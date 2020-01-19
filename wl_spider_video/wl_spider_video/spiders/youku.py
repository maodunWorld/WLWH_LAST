# -*- coding: utf-8 -*-
import json
import re
import scrapy
from scrapy import Request
from wl_spider_video.items import VideoItem


# 如果you-get出现 客户端无权播放,201 去you-get优酷的源码里的extractors.youku改下self.ckey
# 246上修改位置在 C:\ProgramData\Anaconda3\Lib\site-packages\you_get\extractors     5/28


class YoukuSpider(scrapy.Spider):
    name = 'youku'
    allowed_domains = ['v.youku.com']
    custom_settings = {
        'ITEM_PIPELINES': {'wl_spider_video.pipelines.YoukuDownloadVideoPipeline': 300,
                           'wl_spider_video.pipelines.YoukuSavePipeline': 400}
    }
    urls = ['https://list.youku.com/category/page?c=105&p={}',
            "https://list.youku.com/category/page?c=103&p={}",
            'https://list.youku.com/category/page?c=89&p={}',
            'https://list.youku.com/category/page?c=86&p={}']

    start_urls = [url.format(page) for url in urls for page in range(1, 15)]

    def parse(self, response):
        ul = json.loads(response.text)["data"]
        channel = re.search("c=(.*?)&", str(response.request)).group(1)
        for li in ul:
            item = VideoItem()
            item['channel'] = channel
            item['imgurl'] = li["img"]
            item['playUrl'] = "https:" + li["videoLink"]
            item['name'] = li['title']
            yield Request(url=item["playUrl"], callback=self.parse_inner, meta={"item": item})

    def parse_inner(self, response):
        item = response.meta["item"]
        item["publish_time"] = response.xpath("//span[@class='video-status']/span/span/text()").extract_first()
        item["publish_name"] = response.xpath("//div[@class='desc']/span[@id='module_basic_sub']/a/text()").extract()[1].strip()
        yield item
