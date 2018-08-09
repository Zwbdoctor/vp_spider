# -*- coding: utf-8 -*-
# import scrapy
import re
import json
from scrapy.spiders.crawl import CrawlSpider, Rule, Request
from scrapy.linkextractors import LinkExtractor
# from items import VipItem


# class VipspiderSpider(scrapy.Spider):
class VipspiderSpider(CrawlSpider):
    name = 'vipspider'
    allowed_domains = ['vip.com']
    # start_urls = ['http://www.vip.com/']
    start_urls = ['http://category.vip.com/search-1-0-1.html?q=3|290322||&rp=288533|289925&ff=|0|6|1']

    rules = [
        Rule(LinkExtractor(allow=r'search-1-0-\d+', restrict_xpaths='//*[@id="J_pagingCt"]'),
        callback='deal_plist')
    ]

    # def start_requests(self):
    #     with open('./vip/spiders/url.dat', 'r') as f:
    #         urls = f.read().split('\n')
    #     for u in urls:
    #         yield Request(u, callback=self.deal_plist)
    
    def deal_plist(self, response):
        reg = r'"productIds":(.*?),"cateName"'
        plist = re.search(reg, response.body).group(1)
        le = len(plist)
        p = [plist[:le/2], plist[le/2:]]
        for u in p:
            url = 'https://category.vip.com/ajax/mapi.php?service=product_info&prodcutIds=%s&warehouse=VIP_NH' % ('%2C'.join(u))
            yield Request(url, callback=self.detail_list)
    
    def detail_list(self, response):
        data = json.loads(response.body)
        print(data)
        its = data['data']['products']
        for u in its:
            url = 'http://detail.vip.com/detail-%s-%s.com' % (u['brandId'], u['product'])
            print(url)
            yield Request(url, callback=self.parse_item)

    def parse_item(self, response):
        i = {}
        i['goods_type'] = response.xpath('//tr[1]/td[1]').extract()[0]
        i['goods_name'] = response.xpath('//tr[2]/td[1]').extract()[0]
        i['box_detail'] = response.xpath('//tr[3]/td[1]').extract()[0]
        i['goods_size'] = response.xpath('//tr[4]/td[1]').extract()[0]
        i['brand_name'] = response.xpath('//tr[1]/td[2]').extract()[0]
        i['goods_from'] = response.xpath('//tr[2]/td[2]').extract()[0]
        i['useful_time'] = response.xpath('//tr[3]/td[2]').extract()[0]
        i['goods_num'] = response.xpath('//tr[4]/td[2]').extract()[0]
        imgs = response.xpath('//div[@class="pic-sliderwrap"]//div[@class="zoomPad"]/img/@src').extract()
        i['goods_imgs'] = ','.join(['http:%s' % e for e in imgs])
        return i
