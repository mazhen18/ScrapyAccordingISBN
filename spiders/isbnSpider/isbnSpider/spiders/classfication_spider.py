import scrapy
import logging
from ..inner_spider_utils import generate_item
from ..inner_spider_utils import get_allowed_domains
from utils.data_check_utils import check_data
from utils.sqlutils import query_title
from utils.myutils import get_valid_search_text
import urllib.parse
logger = logging.getLogger('classfication_spider')


class CurrencySpider(scrapy.Spider):

    name = 'classfication'

    allowed_domains = get_allowed_domains()

    def __init__(self, *args, **kwargs):
        super(CurrencySpider, self).__init__(*args, **kwargs)
        self.isbn13 = kwargs.get('isbn13')
        self.url_code = urllib.parse.quote(get_valid_search_text((query_title(self.isbn13))[0][0]))
        self.start_urls = ['http://search.dangdang.com/?key=' + self.url_code + '&act=input']

    def parse(self, response):
        xpath = '//li[1]/p[1]/a/@href'

        data = response.xpath(xpath).extract()[0]

        yield scrapy.Request(data, callback=self.get_classfication, dont_filter=True)

    def get_classfication(self, response):

        xpath1 = '//*[@id="detail-category-path"]/span/a/text()'

        data2 = response.xpath(xpath1).extract()

        result = check_data('classfication', '>'.join(data2))

        yield generate_item('classfication', self.isbn13, result)
