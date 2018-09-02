import utils.myutils as myutils
import utils.sqlutils as sqlutils
from spiders.SpiderThread import SpiderThread
logger = myutils.init_logging()


def main(list_isbn):
    isbn_list = [1234567898]
    spider_thread_list = []
    count = 1
    for isbn in isbn_list:
        if count <= 100:
            spider_thread_list.append(SpiderThread('thread-%d-%s' % (count, isbn), isbn))
        else:
            logger.warning("fun:main, query count > 100")
            break

    for thread in spider_thread_list:
        thread.start()

    for thread in spider_thread_list:
        thread.join()

    #查询数据库中数据，返回list
    result_list = sqlutils.query_list_isbn(list_isbn)

    return result_list

main()