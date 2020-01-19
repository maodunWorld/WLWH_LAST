# -*- coding: utf-8 -*-
import json
import scrapy
from wl_spider_video.items import IqiyiItem


class IqiyiSpider(scrapy.Spider):
    name = 'iqiyi'
    allowed_domains = ['iqiyi.com']

    custom_settings = {
        'ITEM_PIPELINES': {'wl_spider_video.pipelines.IqiyiDownloadVideoPipeline': 300,
                           'wl_spider_video.pipelines.IqiyiSavePipeline': 400}
    }

    # format(页数, 每页数量) 1 900 为这个接口返回的最大数量 19/5/22
    start_urls = ["https://pcw-api.iqiyi.com/search/video/videolists?access_play_control_platform=14&channel_id=10&"
                  "data_type=2&from=pcw_list&is_album_finished=&is_purchase=&key=&market_release_date_level=&"
                  "mode=4&pageNum={}&pageSize={}&site=iqiyi&source_type=1&"
                  "three_category_id=1006;must&without_qipu=1".format(1, 900),

                  "https://pcw-api.iqiyi.com/search/video/videolists?access_play_control_platform=14&"
                  "channel_id=10&data_type=2&from=pcw_list&is_album_finished=&is_purchase=&key=&"
                  "market_release_date_level=&mode=4&pageNum={}&pageSize={}&site=iqiyi&source_type=1&"
                  "three_category_id=1007;must&without_qipu=1".format(1, 900),

                  "https://pcw-api.iqiyi.com/search/video/videolists?access_play_control_platform=14&channel_id=30"
                  "&data_type=2&from=pcw_list&is_album_finished=&is_purchase=&key=&market_release_date_level=&mode=4"
                  "&pageNum={}&pageSize={}&site=iqiyi&source_type=1&"
                  "three_category_id=27974;must&without_qipu=1".format(1, 900),

                  "https://pcw-api.iqiyi.com/search/video/videolists?access_play_control_platform=14&channel_id=27&"
                  "data_type=2&from=pcw_list&is_album_finished=&is_purchase=&key=&market_release_date_level=&mode=4&"
                  "pageNum={}&pageSize={}&site=iqiyi&source_type=1&three_category_id=&without_qipu=1".format(1, 900),
                  ]

    def parse(self, response):
        result = json.loads(response.text)
        assert result["code"] == "A00000", "获取爱奇艺视屏列表数据异常"
        ret_list = result["data"]["list"]
        items = []
        for ret in ret_list:
            item = IqiyiItem()
            item["name"] = ret["name"]
            item["description"] = ret["description"]
            item["playUrl"] = ret["playUrl"]
            item["site"] = ret["siteId"]
            item["duration"] = ret["duration"]
            item["imageUrl"] = ret["imageUrl"]
            item["channelId"] = ret["channelId"]
            item["time"] = ret["formatPeriod"]
            items.append(item)
        return items
