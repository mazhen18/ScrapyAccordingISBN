import scrapy
import logging
from ..inner_spider_utils import generate_item
from ..inner_spider_utils import get_allowed_domains
from local_utils.data_check_utils import check_data
from local_utils.sqlutils import query_title
from local_utils.myutils import get_valid_search_text
import urllib.parse
from local_utils.myutils import get_log_msg
logger = logging.getLogger('classfication_spider')


class CurrencySpider(scrapy.Spider):

    name = 'classfication'

    allowed_domains = get_allowed_domains()

    def __init__(self, *args, **kwargs):
        super(CurrencySpider, self).__init__(*args, **kwargs)
        self.isbn13 = kwargs.get('isbn13')
        self.url_code = urllib.parse.quote(get_valid_search_text((query_title(self.isbn13))[0][0]))
        self.start_urls = ['http://search.dangdang.com/?key=' + self.url_code + '&act=input']
        print('isbn13=%s, spider_name=%s, start_url=%s' % (self.isbn13, 'classfication', self.start_urls[0]))
    def parse(self, response):
        try:
            xpath = '//li[1]/p[1]/a/@href'

            data = response.xpath(xpath).extract()[0]

            yield scrapy.Request(data, callback=self.get_classfication, dont_filter=True)
        except Exception as e:
            logger.warning(get_log_msg('parse', 'isbn13=%, e.msg=%s' % (self.isbn13, e)))

    def get_classfication(self, response):
        try:
            url1 = response.url

            xpath1 = ''
            if url1.find('e.dangdang.com') != -1:
                xpath1 = '//*[@id="productBookDetail"]/div[3]/p[5]/span/a/text()'
            else:
                xpath1 = '//*[@id="detail-category-path"]/span/a/text()'

            data2 = response.xpath(xpath1).extract()

            result = check_data('classfication', '>'.join(data2))

            yield generate_item('classfication', self.isbn13, result)
        except Exception as e:
            print(get_log_msg('parse', 'isbn13=%, e.msg=%s' % (self.isbn13, e)))
