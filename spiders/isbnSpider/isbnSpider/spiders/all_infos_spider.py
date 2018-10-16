# coding=utf-8
import scrapy

from local_utils import myutils
# from local_utils.scrapyutils import txt_lock
from local_utils.sqlutils import check_sql_str
from ..inner_spider_utils import get_allowed_domains
from ..inner_spider_utils import get_data_by_selenium
from ..inner_spider_utils import get_bs4html_by_chromedriver
from local_utils.data_check_utils import check_data_validity, check_isbn10
import urllib.parse
from local_utils.myutils import get_log_msg, google_translate, get_valid_search_text, get_xpath_result
from local_utils.myutils import logger
from ..items import AllInfosItem



class AllInfosSpider(scrapy.Spider):

    name = 'all_infos'

    allowed_domains = get_allowed_domains()

    def __init__(self, *args, **kwargs):
        super(AllInfosSpider, self).__init__(*args, **kwargs)
        self.isbn13 = kwargs.get('isbn13')
        self.start_urls = ['https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=' + self.isbn13]


    def parse(self, response):
        try:
            if response.status == 200:
                item = AllInfosItem()

                item['isbn13'] = self.isbn13

                title_xpath = '//*[@id="result_0"]/div/div/div/div[2]/div[1]/div[1]/a/@title'
                title = response.xpath(title_xpath).extract()

                if title:

                    item['title'] = check_sql_str(title[0]) if len(title) > 0 else ''

                    pic_xpath = '//*[@id="result_0"]/div/div/div/div[1]/div/div/a/img/@src'
                    pic = response.xpath(pic_xpath).extract()
                    item['pic'] = pic[0] if len(pic) > 0 else ''

                    pubdate_xpath = '//*[@id="result_0"]/div/div/div/div[2]/div[1]/div[1]/span[3]/text()'
                    pubdate = response.xpath(pubdate_xpath).extract()
                    item['pubdate'] = pubdate[0] if len(pubdate) > 0 else ''

                    author_xpath = '//*[@id="result_0"]/div/div/div/div[2]/div[1]/div[2]/span[position()>1]/text()'
                    author = response.xpath(author_xpath).extract()
                    item['author'] = check_sql_str(''.join(author)) if len(author) > 0 else ''

                    binding_xpath = '//*[@id="result_0"]/div/div/div/div[2]/div[2]/div[1]/div[1]/a/h3/text()'
                    binding = response.xpath(binding_xpath).extract()
                    item['binding'] = binding[0] if len(binding) > 0 else ''

                    price_xpath = '//*[@id="result_0"]/div/div/div/div[2]/div[2]/div[1]/div[2]/span[2]/text()'
                    price = response.xpath(price_xpath).extract()
                    item['price'] = check_data_validity('price', price[0]) if len(price) > 0 else ''

                    currency_xpath = '//*[@id="result_0"]/div/div/div/div[2]/div[2]/div[1]/div[2]/a/span[2]/span/sup[1]/text()'
                    currency_xpath1 = '//*[@id="result_0"]/div/div/div/div[2]/div[3]/div[1]/div[2]/a/span[2]/span/sup[1]/text()'
                    currency_xpath2 = '//*[@id="result_0"]/div/div/div/div[2]/div[3]/div[1]/div[1]/a/span[2]/span/sup[1]/text()'
                    item['currency'] = get_xpath_result(response, 'currency', [currency_xpath, currency_xpath1, currency_xpath2])

                    amazon_sec_href_xpath = '//*[@id="result_0"]/div/div/div/div[2]/div[1]/div[1]/a/@href'
                    amazon_sec_href = response.xpath(amazon_sec_href_xpath).extract()
                    if len(amazon_sec_href) > 0:
                        bs4html = get_bs4html_by_chromedriver(amazon_sec_href[0])
                        try:
                            li_list = bs4html.find('table', {'id': "productDetailsTable"}).findAll('li')
                            for li in li_list:
                                b = li.find('b')
                                if b and b.get_text().find('Paperback') != -1:
                                    item['page'] = li.get_text()
                                if b and b.get_text().find('Publisher') != -1:
                                    item['publisher'] = check_sql_str(((str)(li.contents[1])).strip())
                                if b and b.get_text().find('ISBN-10') != -1:
                                    item['isbn10'] = check_isbn10(((str)(li.contents[1])).strip())
                        except Exception as e:
                            logger('e').error(get_log_msg('parse', 'get page、piblisher、isbn10 fail, isbn13=%s, spider_name=%s, e.msg=%s'
                                                          % (self.isbn13, 'all_infos', e)))

                    if len(title) > 0:
                        item['trans_name'] = check_sql_str(google_translate(title[0]))
                        self.url_code = urllib.parse.quote(get_valid_search_text(title[0]))
                        dangdang_urls = 'http://search.dangdang.com/?key=' + self.url_code + '&act=input'
                        yield scrapy.Request(url=dangdang_urls,
                                             callback=self.get_dangdang_contain_infos,
                                             meta={'item': item},
                                             dont_filter=True)
                    else:
                        yield item
                # else:
                    # myutils.update_unfound_isbn13_to_txt(self.isbn13, 'i')
            # else:
                # myutils.update_unfound_isbn13_to_txt(self.isbn13, 'i')
        except Exception as e:
            logger('e').error(get_log_msg('parse', 'isbn13=%s, spider_name=%s, e.msg=%s'
                                          % (self.isbn13, 'all_infos', e)))

    def get_dangdang_contain_infos(self, response):

        item = response.meta['item']

        try:
            xpath = '//li[1]/p[1]/a/@href'

            data = response.xpath(xpath).extract()

            if len(data) > 0:
                data = data[0]
                yield scrapy.Request(url=data,
                                     callback=self.get_infos,
                                     meta={'item': item},
                                     dont_filter=True)
            else:
                logger().info(get_log_msg('get_dangdang_contain_infos',
                                          'isbn13=%s, not get dangdang second level href'))
                yield item
        except Exception as e:
            logger().info(get_log_msg('get_dangdang_contain_infos',
                                      'isbn13=%s, get exception e.msg=%s' % e))
            yield item

    def get_infos(self, response):
        try:
            item = response.meta['item']

            url1 = response.url

            if url1.find('e.dangdang.com') != -1:
                classfication_xpath = '//*[@id="productBookDetail"]/div[3]/p[5]/span/a/text()'
            else:
                classfication_xpath = '//*[@id="detail-category-path"]/span/a/text()'

            classfication = response.xpath(classfication_xpath).extract()

            if not classfication:
                search_text = get_valid_search_text(item['title'])

                classfication = get_data_by_selenium('taobao', search_text, 'classfication')

            item['classfication'] = check_sql_str(check_data_validity('classfication', '>'.join(classfication)))

            summary_xpath = '//*[@id="description"]/div[2]/div[1]/div[2]/text()'
            summary = response.xpath(summary_xpath).extract()
            item['summary'] = check_sql_str(summary[0]) if len(summary) > 0 else ''

            yield item

        except Exception as e:
            logger('e').error(get_log_msg('parse',
                                          'isbn13=%s, get exception in second level, e.msg=%s'
                                          % (self.isbn13, e)))
            yield item