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
        sql = """insert into products(`name`, `goods_type`, `box_detail`, `chart_stars`, `chart_count`, `whole_chart`, 
        `others`) values(%s, %s, %s, %s, %s, %s, %s);"""
        params = (item['name'], item['tag'], item['info'], item['chart_stars'], item['chart_count'],
                  item['whole_chart'], item['others'])
        cursor.execute(sql, params)