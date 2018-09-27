import local_utils.myutils as myutils
import local_utils.pathutils
import local_utils.sqlutils as sqlutils
from spiders.SpiderThread import SpiderThread
import argparse
import sys
import re
from local_utils.myutils import logger
from local_utils.myutils import get_log_msg
import os
from local_utils.pathutils import get_spiders_dir_path
os.chdir(get_spiders_dir_path())
sys.path.append(local_utils.pathutils.get_project_path() + '/venv/lib/python3.6/site-packages')


def main(list_isbn):
    #初始化log
    myutils.init_logging()
    #判断是否需要更新proxies.txt列表
    # myutils.update_proxies_txt()
    isbn_list = list_isbn
    spider_thread_list = []
    count = 1
    for isbn in isbn_list:
        if count <= 100:
            spider_thread_list.append(SpiderThread('thread-%d-%s' % (count, isbn), isbn))
        else:
            logger('w').warning(get_log_msg("fun:main", "query count > 100"))
            break

    for thread in spider_thread_list:
        thread.start()

    for thread in spider_thread_list:
        thread.join()

    #查询数据库中数据，返回list
    result_list = sqlutils.query_list_isbn(list_isbn)

    return result_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--isbn_list',
        type=str,
        default='9781409582489',
        help='input isbn list, example: "123456789123 1234251425621" '
    )

    args = parser.parse_args()

    list_isbn = re.split(r' +', args.isbn_list)

    list_isbn = myutils.get_isbn13_list_from_txt("/Users/mazhen/Desktop/maomao/isbn13_query/1/1.txt")

    main(list_isbn)