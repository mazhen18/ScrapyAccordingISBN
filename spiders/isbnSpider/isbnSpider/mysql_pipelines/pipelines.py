# -*- coding:utf-8 -*-
from utils.sqlutils import update_bookbaseinfos
import logging
from utils.myutils import obj2dict
from ..inner_spider_utils import break_scrapy

logger = logging.getLogger('piplines')


class isbnPipeline(object):

    def process_item(self, item, spider): #这个函数的参数必须这样写

        spider_name = spider.name

        value = item._values.get(spider_name)

        error_msg = 'data update fail, isbn13:%s, %s:%s' % (item['isbn13'], spider_name, value)

        msg = ''
        result = 'fail'
        if value:

            try:

                update_bookbaseinfos(item._values)

                msg = 'data update succes, isbn13:%s, %s:%s' % (item['isbn13'], spider_name, value)

                result = 'success'
            except Exception as e:
                msg = e + ',' + error_msg
        else:
            msg = error_msg

        break_scrapy(spider_name, item['isbn13'], result, msg)