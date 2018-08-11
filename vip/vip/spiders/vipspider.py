# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider, Request
import re
import json
# from scrapy.spiders.crawl import CrawlSpider, Rule, Request
# from scrapy.linkextractors import LinkExtractor
from chardet import detect
# from items import VipItem


class VipspiderSpider(Spider):
# class VipspiderSpider(CrawlSpider):
    name = 'vipspider'
    allowed_domains = ['vip.com', 'detail.vip.com']
    start_urls = ['http://category.vip.com/search-1-0-1.html?q=3|290322||&rp=288533|289925&ff=|0|6|1']

    # def start_requests(self):
    #     with open('./vip/spiders/url.dat', 'r') as f:
    #         urls = f.read().split('\n')
    #     for u in urls:
    #         yield Request(u, callback=self.page_list)
    
    def page_list(self, response):
        c_url = response.url
        total_page = int(response.xpath('//span[@class="total-item-nums"]/text()').extract()[0][1:-1])
        reg = r'search-1-0-\d+'
        for i in range(total_page):
            url = re.sub(reg, 'search-1-0-%s' % str(i), c_url)
            yield Request(url, callback=self.deal_plist)
    
    def deal_plist(self, response):
        reg = r'"productIds":(.*?),"cateName"'
        plist = re.search(reg, response.body).group(1)[1:-1].strip().replace('"', '').split(',')
        print(plist)
        if len(plist) > 50:
            le = len(plist)
            p = [plist[:le/2], plist[le/2:]]
            for u in p:
                url = 'https://category.vip.com/ajax/mapi.php?service=product_info&productIds=%s&warehouse=VIP_NH' % ','.join(u)
                yield Request(url, callback=self.detail_list)
        elif len(plist) == 1:
            pass
        else:
            url = 'https://category.vip.com/ajax/mapi.php?service=product_info&productIds=%s&warehouse=VIP_NH' % ','.join(plist)
            yield Request(url, callback=self.detail_list, dont_filter=True)
        
    def detail_list(self, response):
        data = json.loads(response.body, encoding='utf-8')
        # print(data['data'])
        headers = self.settings['DEFAULT_REQUEST_HEADERS']
        headers['Host'] = 'detail.vip.com'
        item_list = ''
        for k, v in data['data'].items():
            if k.encode('utf-8') == 'products':
                item_list = v
                break
        for e in item_list:
            u1, u2 = '', ''
            for k, v in e.items():
                if k.encode('utf-8') == 'brandId':
                    u1 = v.encode('utf-8')
                elif k.encode('utf-8') == 'productId':
                    u2 = v.encode('utf-8')
            url = 'http://detail.vip.com/detail-%s-%s.html' % (u1, u2)
            yield Request(url, callback=self.parse_item, dont_filter=True, headers=headers)

    def parse_item(self, response):
        i = {}
        its = []
        tr_list = response.xpath('//div[@class="dc-info clearfix"]//tr')
        for e in tr_list:
            ths = [x for x in e.xpath('.//th/text()').extract()]
            tds = [x for x in e.xpath('.//td/text()').extract()]
            d = ','.join(['%s:%s' % (ths[t], tds[t]) for t in range(len(ths))])
            its.append(d)
        data = ','.join(its)
        i['goods_info'] = data
        imgs = response.xpath('//div[@class="pic-sliderwrap"]//img/@data-original').extract()
        i['goods_imgs'] = ','.join(['http:%s' % e for e in imgs])
        return i
