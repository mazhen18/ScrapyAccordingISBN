# -*- coding:utf-8 -*-
from local_utils.sqlutils import update_bookbaseinfos, insert_bookbaseinfos
from local_utils.myutils import get_log_msg, get_current_timestamp_str
from local_utils.myutils import logger


class isbnPipeline(object):

    def process_item(self, item, spider): #这个函数的参数必须这样写

        spider_name = spider.name

        msg = 'data update fail, isbn13:%s, spider_name:%s, spider_value:%s' % (item['isbn13'], spider_name, '')

        result = 'fail'
        if item._values:

            try:
                if spider_name == 'all_infos':
                    item._values.update({'last_update_time': get_current_timestamp_str('m')})
                    insert_bookbaseinfos(item._values)
                    msg = 'data or last_update_time update succes, isbn13:%s, spider_name:%s, spider_value:%s' % (item['isbn13'], spider_name, str(item._values))
                    result = 'success'
                else:
                    value = item._values.get(spider_name)
                    if value:
                        update_bookbaseinfos(item._values)
                        msg = 'data or last_update_time update succes, isbn13:%s, spider_name:%s, spider_value:%s' % (item['isbn13'], spider_name, value)
                        result = 'success'



            except Exception as e:
                msg = ('%s' % e) + ',' + msg

        msg = get_log_msg('process_item', msg)

        if result == 'success':
            logger().info(msg)
        else:
            logger('e').error(msg)