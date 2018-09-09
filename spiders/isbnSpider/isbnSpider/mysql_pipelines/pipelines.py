# -*- coding:utf-8 -*-
from local_utils.sqlutils import update_bookbaseinfos
from local_utils.myutils import get_log_msg
from local_utils.myutils import logger


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
                msg = ('%s' % e) + ',' + error_msg
        else:
            msg = error_msg

        msg = get_log_msg('process_item', msg)

        if result == 'success':
            logger('i').info(msg)
        else:
            logger('e').error(msg)