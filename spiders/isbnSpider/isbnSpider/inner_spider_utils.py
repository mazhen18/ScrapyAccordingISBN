from .items import CurrencyItem, TransNameItem, ClassficationItem, PriceItem
from selenium import webdriver
from exception.selenium_exception import SeleniumDriverException
from local_utils.bs4utils import get_element_from_bs4html, get_detail_data_from_bs4html
from bs4 import BeautifulSoup
from local_utils.myutils import get_log_msg
import re
from local_utils.data_check_utils import check_href_url
from local_utils.myutils import get_valid_search_text
import difflib
import logging
import operator as op
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


def get_bs4html_by_chromedriver(url):

    option = webdriver.ChromeOptions()

    option.add_argument('headless')

    driver = webdriver.Chrome(chrome_options=option)
    try:

        driver.get(url)

        if len(driver.page_source) > 300:

            return BeautifulSoup(driver.page_source, 'html.parser')
        else:
            return ''
    except Exception as e:
        return ''
    finally:
        driver.quit()


def get_url(domain, search_txt):
    url = ''
    if domain == 'taobao':

        url_code = re.sub(":|\'|\"|,|\?|!|%|@|#|\$|&|\*|\(|\)|>|<", ' ', search_txt)

        url_code1 = re.sub(" +", '+', url_code)

        # url = "https://s.taobao.com/search?q=%s&imgfile=&commend" \
        #       "=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm" \
        #       "=a21bo.2017.201856-taobao-item.1&ie=utf8&initiative_id" \
        #       "=tbindexz_20170306" % url_code1
        url = 'https://s.taobao.com/search?q={}'.format(url_code1)
    return url


def get_max_sim_index(title_list, target_str):

    sim_ratio_dic = {}

    for i, str in enumerate(title_list):

        str_rm_zh = get_valid_search_text(remove_zh(str))

        ratio = difflib.SequenceMatcher(None, str_rm_zh, target_str).ratio()

        sim_ratio_dic.update({i: ratio})

    sim_ratio_dic = sorted(sim_ratio_dic.items(), key=lambda d: d[1], reverse=True)

    return [d[0] for d in sim_ratio_dic]


def remove_zh(str):
    result_list = re.findall('[a-zA-Z0-9]+', str)
    return ' '.join(result_list)


def get_detail_href_list(domain, search_txt):

    try:
        url = get_url(domain, search_txt)

        bs4html = get_bs4html_by_chromedriver(url)

        include_a_div_list = get_element_from_bs4html(domain, bs4html)

        title_list = []

        href_list = []

        for i, div in enumerate(include_a_div_list):
            if i <= 4:
                href_list.append(div.find('a').get('href'))
                title_list.append(div.find('a').get_text().strip())
            else:
                break

        max_sim_index_list = get_max_sim_index(title_list, search_txt)

        return [check_href_url(domain, href_list[max_sim_index])
                for max_sim_index in max_sim_index_list]
    except:
        return ''


def get_data_by_selenium(domain, search_txt, search_type):

    try:
        detail_href_url_list = get_detail_href_list(domain, search_txt)

        for i, detail_href_url in enumerate(detail_href_url_list):

            bs4html = get_bs4html_by_chromedriver(detail_href_url)

            detail_data = get_detail_data_from_bs4html(domain, bs4html, search_type)

            if detail_data:
                return detail_data
            if i == 2:
                break

        return ''
    except:
        return ''













