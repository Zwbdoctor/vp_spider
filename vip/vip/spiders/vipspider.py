# -*- coding: utf-8 -*-
# import scrapy
from scrapy import Spider, Request
import re
import json
# from scrapy.spiders.crawl import CrawlSpider, Rule, Request
# from scrapy.linkextractors import LinkExtractor
# from chardet import detect
# from items import VipItem


class VipspiderSpider(Spider):
    # class VipspiderSpider(CrawlSpider):
    name = 'vipspider'
    allowed_domains = ['vip.com', 'detail.vip.com']
    # start_urls = ['http://category.vip.com/search-1-0-1.html?q=3|290322||&rp=288533|289925&ff=|0|6|1']

    def start_requests(self):
        with open('./vip/spiders/url.dat', 'r') as f:
            urls = f.read().split('\n')
        for u in urls:
            yield Request(u, callback=self.parse)
    
    def parse(self, response):
        c_url = response.url
        try:
            total_page = int(response.xpath('//span[@class="total-item-nums"]/text()').extract()[0][1:-1])
        except:
            return 
        reg = r'search-1-0-\d+'
        for i in range(total_page):
            url = re.sub(reg, 'search-1-0-%s' % str(i+1), c_url)
            yield Request(url, callback=self.deal_plist)
    
    def deal_plist(self, response):
        reg = r'"productIds":(.*?),"cateName"'
        plist = re.search(reg, response.body).group(1)[1:-1].strip().replace('"', '').split(',')
        # print(plist)
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
        page = response.body.replace('\n', '').replace('\r', '').replace('\t', '')
        page = re.sub(r'\s', '', page)
        reg = r'<thclass="dc-table-tit">(.*?)</th><td>(.*?)</td>'
        tr_list = re.findall(reg, page)
        # tr_list = response.xpath('string(//div[@class="dc-info clearfix"]//tr)').extract()
        i['url'] = response.url
        try:
            i['goods_price'] = response.xpath('//*[@id="J-pi-price-box"]//em[@class="J-price"]/text()').extract()[0]
        except:
            i['goods_price'] = ''
        tmaps = {'skin_type': '适用肤质', 'types': '类型', 'effect': '护理功效', 'brand_name': '品牌名称',
                 'goods_name': '商品名称', 'goods_from': '产地', 'goods_num': '商品编号', 'goods_comments': '配件/备注',
                 'specifications': '规格'}
        for e in tr_list:
            if not e[0] or not e[1]:
                continue
            for k, v in tmaps.items():
                if e[0].strip()[:-3] == v:
                    i[k] = e[1]
                    tmaps.pop(k)
                    break
                elif e[0].strip()[:-3] == '功效':
                    i['effect'] = e[1]
                    tmaps.pop('effect')
                    break
            else:
                its.append('%s:%s' % (e[0][:-1], e[1]))
        if len(tmaps.keys()) > 0:
            for k in tmaps.keys():
                i[k] = ''
        i['extends'] = ','.join(its) if len(its) > 0 else ''
        try:
            imgs = response.xpath('//div[@class="pic-sliderwrap"]//img/@data-original').extract()
            i['goods_imgs'] = ','.join(['http:%s' % e for e in imgs])
        except:
            i['goods_imgs'] = 'no imgs'
        return i
