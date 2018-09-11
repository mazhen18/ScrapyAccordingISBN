# coding=utf-8
import scrapy
from ..inner_spider_utils import generate_item
from ..inner_spider_utils import get_allowed_domains
from ..inner_spider_utils import get_data_by_selenium
from ..inner_spider_utils import get_bs4html_by_chromedriver
from ..inner_spider_utils import get_trans_name_by_google_translate
from local_utils.data_check_utils import check_data_validity
from local_utils.sqlutils import query_title
from local_utils.myutils import get_valid_search_text
import urllib.parse
from local_utils.myutils import get_log_msg
from local_utils.myutils import logger
from ..items import AllInfosItem



class AllInfosSpider(scrapy.Spider):

    name = 'all_infos'

    allowed_domains = get_allowed_domains()

    def __init__(self, *args, **kwargs):
        super(AllInfosSpider, self).__init__(*args, **kwargs)
        self.isbn13 = kwargs.get('isbn13')
        self.search_text = get_valid_search_text((query_title(self.isbn13))[0][0])
        self.url_code = urllib.parse.quote(self.search_text)
        self.start_urls = ['https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=' + self.isbn13]


    def parse(self, response):
        try:
            item = AllInfosItem()

            item['isbn13'] = self.isbn13

            item['trans_name'] = get_trans_name_by_google_translate(self.isbn13)


            pic_xpath = '//*[@id="result_0"]/div/div/div/div[1]/div/div/a/img/@src'
            pic = response.xpath(pic_xpath).extract()
            item['pic'] = pic[0] if len(pic) > 0 else ''

            title_xpath = '//*[@id="result_0"]/div/div/div/div[2]/div[1]/div[1]/a/@title'
            title = response.xpath(title_xpath).extract()
            item['title'] = title[0] if len(title) > 0 else ''

            pubdate_xpath = '//*[@id="result_0"]/div/div/div/div[2]/div[1]/div[1]/span[3]/text()'
            pubdate = response.xpath(pubdate_xpath).extract()
            item['pubdate'] = pubdate[0] if len(pubdate) > 0 else ''

            author_xpath = '//*[@id="result_0"]/div/div/div/div[2]/div[1]/div[2]/span[2]/a/text()'
            author = response.xpath(author_xpath).extract()
            item['author'] = author[0] if len(author) > 0 else ''

            binding_xpath = '//*[@id="result_0"]/div/div/div/div[2]/div[2]/div[1]/div[1]/a/h3/text()'
            binding = response.xpath(binding_xpath).extract()
            item['binding'] = binding[0] if len(binding) > 0 else ''

            price_xpath = '//*[@id="result_0"]/div/div/div/div[2]/div[2]/div[1]/div[2]/span[2]/text()'
            price = response.xpath(price_xpath).extract()
            item['price'] = check_data_validity('price', price[0]) if len(price) > 0 else ''

            currency_xpath = '//*[@id="result_0"]/div/div/div/div[2]/div[2]/div[1]/div[2]/a/span[2]/span/sup[1]/text()'
            currency = response.xpath(currency_xpath).extract()
            item['currency'] = currency[0] if len(currency) > 0 else ''

            amazon_sec_href_xpath = '//*[@id="result_0"]/div/div/div/div[2]/div[1]/div[1]/a/@href'
            amazon_sec_href = response.xpath(amazon_sec_href_xpath).extract()
            if len(amazon_sec_href) > 0:
                bs4html = get_bs4html_by_chromedriver(amazon_sec_href[0])
                li_list = bs4html.find('table', {'id': "productDetailsTable"}).findAll('li')
                for li in li_list:
                    b = li.find('b')
                    if b and b.get_text() == 'Paperback':
                        item['page'] = li.get_text()
                    if b and b.get_text() == 'Publisher':
                        item['publisher'] = li.get_text()

            if title:
                dangdang_urls = 'http://search.dangdang.com/?key=' + self.url_code + '&act=input'
                yield scrapy.Request(url=dangdang_urls,
                                     callback=self.get_dangdang_contain_infos,
                                     meta={'item': item},
                                     dont_filter=True)
            else:
                yield item

        except Exception as e:
            logger('e').error(get_log_msg('parse', 'isbn13=%s, spider_name=%s, e.msg=%s'
                                          % (self.isbn13, 'classfication', e)))

    def get_dangdang_contain_infos(self, response):

        item = response.meta['item']

        # item['classfication'] = get_classfication(response, self.isbn13, self.search_text)

        def get_infos(response, isbn13, search_text):
            try:
                url1 = response.url

                classfication_xpath = ''
                if url1.find('e.dangdang.com') != -1:
                    classfication_xpath = '//*[@id="productBookDetail"]/div[3]/p[5]/span/a/text()'
                else:
                    classfication_xpath = '//*[@id="detail-category-path"]/span/a/text()'

                classfication = response.xpath(classfication_xpath).extract()

                if not classfication:
                    classfication = get_data_by_selenium('taobao', search_text, 'classfication')

                item['classfication'] = check_data_validity('classfication', '>'.join(classfication))

                summary_xpath = '//*[@id="description"]/div[2]/div[1]/div[2]/text()'
                summary = response.xpath(summary_xpath).extract()
                item['summary'] = summary[0] if len(summary) > 0 else ''

                yield item

            except Exception as e:
                logger('e').error(get_log_msg('parse',
                                              'isbn13=%s, get exception in second level, e.msg=%s'
                                              % (isbn13, e)))
                yield item

        try:
            xpath = '//li[1]/p[1]/a/@href'

            data = response.xpath(xpath).extract()

            if len(data) > 0:
                data = data[0]
                yield scrapy.Request(url=data,
                                     callback=get_infos,
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