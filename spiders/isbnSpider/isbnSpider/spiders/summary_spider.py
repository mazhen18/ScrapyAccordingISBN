import urllib

import scrapy
import logging
from local_utils.data_check_utils import check_data_validity
from local_utils.sqlutils import query_title, check_sql_str
from ..inner_spider_utils import get_allowed_domains
from ..inner_spider_utils import generate_item
from local_utils.myutils import get_log_msg, get_xpath_result, get_valid_search_text
from local_utils.myutils import logger



class SummarySpider(scrapy.Spider):

    name = 'summary'

    allowed_domains = get_allowed_domains()

    def __init__(self, *args, **kwargs):
        super(SummarySpider, self).__init__(*args, **kwargs)
        self.isbn13 = kwargs.get('isbn13')
        self.search_text = get_valid_search_text((query_title(self.isbn13))[0][0])
        self.url_code = urllib.parse.quote(self.search_text)
        self.start_urls = ['http://search.dangdang.com/?key=' + self.url_code + '&act=input']

    def parse(self, response):

        try:
            xpath = '//li[1]/p[1]/a/@href'

            data = response.xpath(xpath).extract()

            if len(data) > 0:
                data = data[0]
                yield scrapy.Request(url=data, callback=self.get_infos, dont_filter=True)
            else:
                logger('e').error(get_log_msg('get_dangdang_contain_infos',
                                          'isbn13=%s, not get dangdang second level href'))

                # 其他获取summary的方法先略
                result = ''
                yield generate_item('summary', self.isbn13, result)

        except Exception as e:
            logger('e').error(get_log_msg('parse', 'isbn13=%s, spider_name=%s, e.msg=%s'
                                          % (self.isbn13, 'summary', e)))

    def get_infos(self, response):
        try:
            summary_xpath = '//*[@id="description"]/div[2]/div[1]/div[2]/text()'

            summary = response.xpath(summary_xpath).extract()

            result = check_sql_str(summary[0]) if len(summary) > 0 else ''

            yield generate_item('summary', self.isbn13, result)

        except Exception as e:
            logger('e').error(get_log_msg('parse', 'isbn13=%s, spider_name=%s, e.msg=%s'
                                          % (self.isbn13, 'summary', e)))




