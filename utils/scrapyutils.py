from utils import myutils
import utils.sqlutils as sqlutils
import logging
from data_struct.book import BookBaseInfos
import threading
logger = logging.getLogger('scrapyutils')


def scrap_bookinfos(isbn13):
    if myutils.check_isbn(isbn13):
        result = sqlutils.query_list_isbn([isbn13])
        if len(result) > 0:
            # 更新一些可能变化的数据，暂时不更新
            # logger.info('func:scrap_bookinfos, isbn already in database:%s:' % isbn)
            # 判断是否存在空的必填值，如果有这要查询剩余值
            book_base_infos = convert_db_data_to_bookbaseinfos(result[0])
            if not check_data_integrity(book_base_infos):
                scrapy_api_unable_get_infos(book_base_infos)
        else:
            #开始爬取数据，先从api获取
            # book_infos = myutils.query_book_infos(isbn13, company_code=1)
            book_infos = {'title': 'Principles', 'subtitle': 'Life and Work', 'pic': 'http://api.jisuapi.com/isbn/upload/201808/30214633_82281.jpg', 'author': 'Ray Dalio', 'summary': 'Ray Dalio, one of the world’s most successful investors and entrepreneurs, shares the unconventional principles that he’s developed, refined, and used over the past forty years to create unique results in both life and business—and which any person or organization can adopt to help achieve their goals.\nIn 1975, Ray Dalio founded an investment firm, Bridgewater Associates, out of his two-bedroom apartment in New York City. Forty years later, Bridgewater has made more money for its clients than an', 'publisher': 'Simon & Schuster', 'pubplace': '', 'pubdate': '2017-9-19', 'page': '592', 'price': '0.00', 'binding': 'Hardcover', 'isbn': '9781501124020', 'isbn10': '1501124021', 'keyword': '', 'edition': '', 'impression': '', 'language': '', 'format': '', 'class': ''}
            if book_infos:
                #获取api查询中的数据
                book_base_infos = get_book_base_infos_from_api(book_infos)
                sqlutils.insert_bookbaseinfos(myutils.obj2dict(book_base_infos))
                scrapy_api_unable_get_infos(book_base_infos)
            else:
                #全部数据都需要爬取，暂时不做
                print('没有该ISBN数据信息：%s' % isbn13)
    else:
        logger.warning("func:scrap_bookinfs, invalid argumant isbn:%s" % isbn13)


def get_book_base_infos_from_api(book_infos):
    book_base_infos = BookBaseInfos()
    book_base_infos.isbn13 = book_infos.get('isbn')
    book_base_infos.title = book_infos.get('title')
    book_base_infos.pic = book_infos.get('pic')
    book_base_infos.author = book_infos.get('author')
    book_base_infos.summary = book_infos.get('summary')
    book_base_infos.pubdate = book_infos.get('pubdate')
    book_base_infos.publisher = book_infos.get('publisher')
    book_base_infos.page = book_infos.get('page')
    book_base_infos.binding = book_infos.get('binding')
    book_base_infos.price = book_infos.get('price')
    book_base_infos.subtitle = book_infos.get('subtitle')
    book_base_infos.pubplace = book_infos.get('pubplace')
    book_base_infos.isbn10 = book_infos.get('isbn10')
    book_base_infos.keyword = book_infos.get('keyword')
    book_base_infos.edition = book_infos.get('edition')
    book_base_infos.impression = book_infos.get('impression')
    book_base_infos.body_language = book_infos.get('language')
    book_base_infos.format = book_infos.get('format')
    book_base_infos.class_cn = book_infos.get('class')
    return book_base_infos


def convert_db_data_to_bookbaseinfos(db_data):
    book_base_infos = BookBaseInfos()
    book_base_infos.isbn13 = db_data[1]
    book_base_infos.title = db_data[2]
    book_base_infos.pic = db_data[3]
    book_base_infos.author = db_data[4]
    book_base_infos.summary = db_data[5]
    book_base_infos.pubdate = db_data[6]
    book_base_infos.publisher = db_data[7]
    book_base_infos.page = db_data[8]
    book_base_infos.binding = db_data[9]
    book_base_infos.price = db_data[10]
    book_base_infos.trans_name = db_data[11]
    book_base_infos.classfication = db_data[12]
    book_base_infos.currency = db_data[13]
    book_base_infos.subtitle = db_data[14]
    book_base_infos.pubplace = db_data[15]
    book_base_infos.isbn10 = db_data[16]
    book_base_infos.keyword = db_data[17]
    book_base_infos.edition = db_data[18]
    book_base_infos.impression = db_data[19]
    book_base_infos.body_language = db_data[20]
    book_base_infos.format = db_data[21]
    book_base_infos.class_cn = db_data[22]
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
        print('启动爬虫')


def start_scrapy(spider_name, isbn13):
    #在线程里启动爬虫
    t = SpiderStartThread('thread-%s-%s' % (isbn13, spider_name), isbn13, spider_name)
    t.start()
    t.join()
