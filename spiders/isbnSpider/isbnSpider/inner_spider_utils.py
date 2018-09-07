from scrapy.exceptions import CloseSpider
from .items import CurrencyItem, TransNameItem, ClassficationItem, PriceItem
from selenium import webdriver
from exception.selenium_exception import SeleniumDriverException
from local_utils.myutils import get_log_msg
import re
import difflib
import logging
logger = logging.getLogger('inner_spider_utils')


def break_scrapy(spider_name, isbn13, result, msg):
    msg = get_log_msg('break_scrapy', msg)

    print(msg) if result == 'fail' else print(msg)

    # raise CloseSpider("scrapy %s %s, isbn13=%s" % (spider_name, result, isbn13))


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


def get_first_level_xpath(domain):
    xpath_href = ''
    if domain == 'taobao':
        xpath_href = '//*[@id="mainsrp-itemlist"]/div/div/div[1]/div/div[2]/div[2]/a'
    return xpath_href


def get_url(domain, search_txt):
    url_code = search_txt
    url = ''
    if domain == 'taobao':

        url_code = re.sub(":|\'|,|\?|!|%|@|#|\$|&|\*|\(|\)|>|<", ' ', url_code)

        url_code = re.replace(" +", '+', url_code)

        url = "https://s.taobao.com/search?q=%s&imgfile=&commend" \
              "=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm" \
              "=a21bo.2017.201856-taobao-item.1&ie=utf8&initiative_id" \
              "=tbindexz_20170306" % url_code
    return url


def get_max_sim_index(str_list, target_str):

    sim_ratio_list = []

    for str in enumerate(str_list):

        str_rm_zh = remove_zh(str)

        seq = difflib.SequenceMatcher(None, str_rm_zh, target_str)

        ratio = seq.ratio()

        sim_ratio_list.append(ratio)

    return sim_ratio_list.index(max(sim_ratio_list))


def remove_zh(str):
    result_list = re.findall('[a-zA-Z0-9]+', str)
    return ' '.join(result_list)


def get_next_href(domain, search_txt):

    url = get_url(domain, search_txt)

    xpath = get_first_level_xpath(domain)

    href_list = get_data_by_chromedriver(url, xpath, 'href')

    title_list = []

    for i, title in enumerate(get_data_by_chromedriver(url, xpath)):
        if i <= 4:
            title_list.append(' '.join(title))
        else:
            break

    max_sim_index = get_max_sim_index(title_list, search_txt)

    next_href = href_list[max_sim_index]

    return next_href


def get_sec_level_xpath(domain):
    xpath_href = ''
    if domain == 'taobao':
        xpath_href = '//*[@id="mainsrp-itemlist"]/div/div/div[1]/div/div[2]/div[2]/a'
    return xpath_href


def get_sec_level_data_by_selenium(domain, search_txt):

    next_href = get_next_href(domain, search_txt)

    sec_level_xpath = get_sec_level_xpath(domain)

    data_list = get_data_by_chromedriver(next_href, sec_level_xpath)

    return data_list













