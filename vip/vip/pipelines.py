# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
from pymysql.cursors import DictCursor


class VipPipeline(object):

    def __init__(self):
        dbparams = dict(
            host='localhost',
            user='root',
            password='root',
            db='vip',
            charset='utf8',
            cursorclass=DictCursor,
            use_unicode=True
        )
        self.dbpool = adbapi.ConnectionPool('pymysql', **dbparams)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_err, item, spider)
        return item

    def handle_err(self, failure, item, spider):
        spider.logger.error('Error insert url: %s' % item['url'])
        spider.logger.error(failure)

    def do_insert(self, cursor, item):
        sql = """insert into products_v2(`goods_name`, `goods_price`, `skin_type`, `goods_type`, `effect`, `brand_name`, `goods_from`,
        `goods_num`, `goods_comments`, `specifications`, `goods_url`, `img_urls`) values(%s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s);"""
        params = (item['goods_name'], item['goods_price'], item['skin_type'], item['types'], item['effect'], item['brand_name'], item['goods_from'],
                  item['goods_num'], item['goods_comments'], item['specifications'], item['url'], item['goods_imgs'])
        cursor.execute(sql, params)
