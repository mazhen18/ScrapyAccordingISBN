import scrapy
from ..inner_spider_utils import get_allowed_domains
from ..inner_spider_utils import generate_item
from ..inner_spider_utils import get_trans_name_by_google_translate
from ..items import TransNameItem
from local_utils.myutils import get_log_msg
from local_utils.myutils import logger



class TransNameItem(scrapy.Spider):

    name = 'trans_name'

    allowed_domains = get_allowed_domains()

    def __init__(self, *args, **kwargs):
        super(TransNameItem, self).__init__(*args, **kwargs)
        self.isbn13 = kwargs.get('isbn13')
        self.start_urls = ['https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=' + self.isbn13]

        # logger().info('isbn13=%s, spider_name=%s, start_url=%s'
        #               % (self.isbn13, 'trans_name', self.start_urls[0]))

    def parse(self, response):
        try:
            yield generate_item('trans_name', self.isbn13,
                                get_trans_name_by_google_translate(self.isbn13))
        except Exception as e:

            logger('e').error(get_log_msg('parse', 'isbn13=%s, spider_name=%s, e.msg=%s'
                                          % (self.isbn13, 'trans_name', e)))










