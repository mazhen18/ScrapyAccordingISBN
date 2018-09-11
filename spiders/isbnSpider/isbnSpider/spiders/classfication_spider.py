import scrapy
from ..inner_spider_utils import generate_item
from ..inner_spider_utils import get_allowed_domains
from ..inner_spider_utils import get_data_by_selenium
from ..inner_spider_utils import get_classfication
from local_utils.data_check_utils import check_data_validity
from local_utils.sqlutils import query_title
from local_utils.myutils import get_valid_search_text
import urllib.parse
from local_utils.myutils import get_log_msg
from local_utils.myutils import logger



class CurrencySpider(scrapy.Spider):

    name = 'classfication'

    allowed_domains = get_allowed_domains()

    def __init__(self, *args, **kwargs):
        super(CurrencySpider, self).__init__(*args, **kwargs)
        self.isbn13 = kwargs.get('isbn13')
        self.search_text = get_valid_search_text((query_title(self.isbn13))[0][0])
        self.url_code = urllib.parse.quote(self.search_text)
        self.start_urls = ['http://search.dangdang.com/?key=' + self.url_code + '&act=input']

        # logger().info('isbn13=%s, spider_name=%s, start_url=%s'
        #               % (self.isbn13, 'classfication', self.start_urls[0]))

    def parse(self, response):
        try:
                result = get_classfication(response, self.isbn13, self.search_text)

                yield generate_item('classfication', self.isbn13, result)
        except Exception as e:
            logger('e').error(get_log_msg('parse', 'isbn13=%s, spider_name=%s, e.msg=%s'
                                          % (self.isbn13, 'classfication', e)))

