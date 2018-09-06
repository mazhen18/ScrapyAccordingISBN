import scrapy
import logging
from ..data_scrapy.data_check import check_data
from ..inner_spider_utils import get_allowed_domains
from ..inner_spider_utils import generate_item
logger = logging.getLogger('price_spider')


class CurrencySpider(scrapy.Spider):

    name = 'price'

    allowed_domains = get_allowed_domains()

    def __init__(self, *args, **kwargs):
        super(CurrencySpider, self).__init__(*args, **kwargs)
        self.isbn13 = kwargs.get('isbn13')
        self.start_urls = ['https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=' + self.isbn13]

    def parse(self, response):
        xpath = '//*[@id="result_0"]/div/div/div/div[2]/div[2]/div[1]/div[2]/span[2]/text()'

        data = response.xpath(xpath).extract()[0]

        result = check_data('price', data)

        yield generate_item('price', self.isbn13, result)



