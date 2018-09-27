import scrapy
import logging
from local_utils.data_check_utils import check_data_validity
from ..inner_spider_utils import get_allowed_domains
from ..inner_spider_utils import generate_item
from local_utils.myutils import get_log_msg
from local_utils.myutils import logger



class CurrencySpider(scrapy.Spider):

    name = 'price'

    allowed_domains = get_allowed_domains()

    def __init__(self, *args, **kwargs):
        super(CurrencySpider, self).__init__(*args, **kwargs)
        self.isbn13 = kwargs.get('isbn13')
        self.start_urls = ['https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=' + self.isbn13]
        # logger().info('isbn13=%s, spider_name=%s, start_url=%s'
        #               % (self.isbn13, 'price', self.start_urls[0]))

    def parse(self, response):
        try:
            xpath = '//*[@id="result_0"]/div/div/div/div[2]/div[2]/div[1]/div[2]/span[2]/text()'


            data = response.xpath(xpath).extract()
            result = ''
            if not data:
                xpath1 = '//*[@id="result_0"]/div/div/div/div[2]/div[3]/div[1]/div[2]/span[2]/text()'
                data = response.xpath(xpath1).extract()

            if data:
                result = data[0]

            result = check_data_validity('price', result)

            yield generate_item('price', self.isbn13, result)
        except Exception as e:
            logger('e').error(get_log_msg('parse', 'isbn13=%s, spider_name=%s, data=%s, e.msg=%s'
                                          % (self.isbn13, 'price', result, e)))




