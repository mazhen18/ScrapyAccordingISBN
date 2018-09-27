from local_utils import myutils
import local_utils.sqlutils as sqlutils
from local_utils.pathutils import get_run_spider_path
from local_utils.pathutils import get_virtualenv_python_path as get_python_path
from data_struct.book import BookBaseInfos
import threading
import os
from .data_check_utils import check_data_validity
from .sqlutils import check_sql_str
from local_utils.myutils import get_log_msg
from local_utils.myutils import get_time_span_cmp_curr
from local_utils.myutils import logger


def scrap_bookinfos(isbn13):
    try:
        if myutils.check_isbn(isbn13):
            result = sqlutils.query_list_isbn([isbn13])
            if len(result) > 0 and result[0] != '':
                # 更新一些可能变化的数据，暂时不更新
                # logger.info('func:scrap_bookinfos, isbn already in database:%s:' % isbn)
                # 判断是否存在空的必填值，如果有这要查询剩余值
                book_base_infos = convert_db_data_to_bookbaseinfos(result[0])
                if not check_data_integrity(book_base_infos):
                    scrapy_api_unable_get_infos(book_base_infos)
            else:
                #开始爬取数据，先从api获取
                book_infos = myutils.query_book_infos(isbn13, company_code=1)

                if book_infos:

                    logger().info(get_log_msg('scrap_bookinfos', 'isbn13=%s,book_infos=%s' % (isbn13, book_infos)))
                    #获取api查询中的数据
                    book_base_infos = get_book_base_infos_from_api(book_infos)
                    sqlutils.insert_bookbaseinfos(myutils.obj2dict(book_base_infos))
                    # 如果查询到就去之前的unfound列表删除unfound的记录
                    myutils.update_unfound_isbn13_to_txt(isbn13)
                    scrapy_api_unable_get_infos(book_base_infos)
                else:
                    #全部数据都需要爬取，暂时不做
                    logger().info('API数据库没有该ISBN数据信息：%s，尝试从网页爬取' % isbn13)
                    scrapy_all_infos(isbn13)
        else:
            logger().info(get_log_msg('scrap_bookinfos',
                                      'isbn13 len invalid or in unfound_isbn13.txt: isbn13=%s'
                                      % isbn13))
    except Exception as e:
        logger('e').error(get_log_msg('scrap_bookinfos',
                                      'isbn13 scrap_bookinfos exception, isbn13=%s, e.msg=%s'
                                      % (isbn13, e)))


def scrapy_all_infos(isbn13):
    spider_name = 'all_infos'
    t = SpiderStartThread('thread-%s-%s' % (spider_name, isbn13), isbn13, spider_name)
    logger().info('线程%s开始爬取，isbn13=%s, spider_name=%s' % (t.name, isbn13, spider_name))
    t.start()
    t.join()
    logger().info('线程%s爬取结束，isbn13=%s, spider_name=%s' % (t.name, isbn13, spider_name))


def get_title(title, subtitle):
    if subtitle == '':
        return title
    else:
        return title + ':' + subtitle


def get_book_base_infos_from_api(book_infos):
    book_base_infos = BookBaseInfos()
    book_base_infos.isbn13 = book_infos.get('isbn')
    book_base_infos.title = check_sql_str(get_title(book_infos.get('title'), book_infos.get('subtitle')))
    book_base_infos.pic = check_sql_str(book_infos.get('pic'))
    book_base_infos.author = check_sql_str(book_infos.get('author'))
    book_base_infos.summary = check_sql_str(book_infos.get('summary'))
    book_base_infos.pubdate = check_sql_str(book_infos.get('pubdate'))
    book_base_infos.publisher = check_sql_str(book_infos.get('publisher'))
    book_base_infos.page = check_sql_str(book_infos.get('page'))
    book_base_infos.binding = check_sql_str(book_infos.get('binding'))
    book_base_infos.price = check_sql_str(check_data_validity('price', book_infos.get('price')))
    book_base_infos.pubplace = check_sql_str(book_infos.get('pubplace'))
    book_base_infos.isbn10 = check_sql_str(book_infos.get('isbn10'))
    book_base_infos.keyword = check_sql_str(book_infos.get('keyword'))
    book_base_infos.edition = check_sql_str(book_infos.get('edition'))
    book_base_infos.impression = check_sql_str(book_infos.get('impression'))
    book_base_infos.body_language = check_sql_str(book_infos.get('language'))
    book_base_infos.format = check_sql_str(book_infos.get('format'))
    book_base_infos.class_cn = check_sql_str(book_infos.get('class'))
    # book_base_infos.last_update_time = get_current_timestamp_str('m')
    return book_base_infos


def convert_db_data_to_bookbaseinfos(db_data):
    book_base_infos = BookBaseInfos()
    book_base_infos.isbn13 =        db_data[0]
    book_base_infos.isbn10 =        db_data[1]
    book_base_infos.title =         db_data[2]
    book_base_infos.trans_name =    db_data[3]
    book_base_infos.author =        db_data[4]
    book_base_infos.summary =       db_data[5]
    book_base_infos.pubdate =       db_data[6]
    book_base_infos.publisher =     db_data[7]
    book_base_infos.binding =       db_data[8]
    book_base_infos.page =          db_data[9]
    book_base_infos.currency =      db_data[10]
    book_base_infos.price =         db_data[11]
    book_base_infos.classfication = db_data[12]
    book_base_infos.pic =           db_data[13]
    book_base_infos.pubplace =      db_data[14]
    book_base_infos.keyword =       db_data[15]
    book_base_infos.edition =       db_data[16]
    book_base_infos.impression =    db_data[17]
    book_base_infos.body_language = db_data[18]
    book_base_infos.format =        db_data[19]
    book_base_infos.class_cn =      db_data[20]
    book_base_infos.last_update_time=db_data[21]
    return book_base_infos


def check_data_integrity(book_base_infos):
    return not (book_base_infos.pic == ''
                or book_base_infos.trans_name == ''
                or book_base_infos.author == ''
                or book_base_infos.summary == ''
                or book_base_infos.classfication == ''
                or book_base_infos.pubdate == ''
                or book_base_infos.publisher == ''
                or book_base_infos.page == ''
                or book_base_infos.binding == ''
                or book_base_infos.currency == ''
                or book_base_infos.price == '')


def scrapy_api_unable_get_infos(book_base_infos):

    last_update_time = book_base_infos.last_update_time

    delta = ''

    if last_update_time:
        delta = get_time_span_cmp_curr(last_update_time)

    if last_update_time == '' or delta.days > 5:
        if book_base_infos.trans_name == '':
            start_scrapy('trans_name', book_base_infos.isbn13)
        if book_base_infos.classfication == '':
            start_scrapy('classfication', book_base_infos.isbn13)
        if book_base_infos.currency == '':
            start_scrapy('currency', book_base_infos.isbn13)
        if book_base_infos.price == '' \
                or float(book_base_infos.price) < 0.5:
            start_scrapy('price', book_base_infos.isbn13)



class SpiderStartThread(threading.Thread):
    """"""

    def __init__(self, name, isbn13, spider_name):
        """Constructor"""
        threading.Thread.__init__(self)
        self.name = name
        self.isbn13 = isbn13
        self.spider_name = spider_name

    def run(self):
        command_start_spider = get_python_path() + " " \
                               + get_run_spider_path() \
                               + (' --spider_name=%s --isbn13=%s' % (self.spider_name, self.isbn13))
        os.system(command_start_spider)



def start_scrapy(spider_name, isbn13):
    #在线程里启动爬虫
    t = SpiderStartThread('thread-%s-%s' % (spider_name, isbn13), isbn13, spider_name)
    logger().info('线程%s开始爬取，isbn13=%s, spider_name=%s' % (t.name, isbn13, spider_name))
    t.start()
    t.join()
    logger().info('线程%s爬取结束，isbn13=%s, spider_name=%s' % (t.name, isbn13, spider_name))

