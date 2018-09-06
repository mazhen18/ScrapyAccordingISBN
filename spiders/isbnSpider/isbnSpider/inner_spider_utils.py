from scrapy.exceptions import CloseSpider
from .items import CurrencyItem, TransNameItem, ClassficationItem, PriceItem
from selenium import webdriver
from exception.selenium_exception import SeleniumDriverException
from utils.myutils import get_log_msg
import logging
logger = logging.getLogger('inner_spider_utils')


def break_scrapy(spider_name, isbn13, result, msg):
    msg = get_log_msg('break_scrapy', msg)

    logger.error(msg) if result == 'fail' else logger.info(msg)

    raise CloseSpider("scrapy %s %s, isbn13=%s" % (spider_name, result, isbn13))


def generate_item(spider_name, isbn13, result):
    if not result:
        raise Exception(get_log_msg('generate_item',
                                    'spider_name:%s,isbn13:%s,result:%s' % (spider_name, isbn13, result)))
    item = object()
    if spider_name == 'currency':
        item = CurrencyItem()
    if spider_name == 'trans_name':
        item = TransNameItem()
    if spider_name == 'classfication':
        item = ClassficationItem()
    if spider_name == 'price':
        item = PriceItem()

    item['isbn13'] = isbn13
    item[spider_name] = result

    return item


def get_allowed_domains():
    allowed_domains = ['amazon.com',
                       'book.dangdang.com',
                       'taobao.com',
                       'tmall.com',
                       'jd.com',
                       'edelweiss.plus']
    return allowed_domains


def get_data_by_chromedriver(url, xpath, attr=None):

    option = webdriver.ChromeOptions()

    option.add_argument('headless')

    driver = webdriver.Chrome(chrome_options=option)

    try:

        driver.get(url)

        element = driver.find_element_by_xpath(xpath) #Selenium的xpath只能获取到元素，连text()都不能加，属性要靠get_attribute获取

        if attr:
            return element.get_attribute(attr)
        else:
            return element.text
    except BaseException as e:

        raise SeleniumDriverException(message=('通过Selenium Driver 请求数据失败，e.msg=%s' % e))

    finally:
        driver.quit()



