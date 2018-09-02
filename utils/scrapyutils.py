import utils.myutils as myutils
import utils.sqlutils as sqlutils
import logging
logger = logging.getLogger('scrapyutils')


def scrap_bookinfs(isbn):
    if myutils.check_isbn(isbn):
        if sqlutils.query_isbn_exist(isbn):
            # 更新一些可能变化的数据
            print("更新数据")
        else:
            #开始爬取数据
            print("开始爬取数据")
    else:
        logger.warning("fun:scrap_bookinfs, invalid argumant isbn:%s" % isbn)