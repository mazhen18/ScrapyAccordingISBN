import scrapy
from local_utils.myutils import google_translate
from local_utils.sqlutils import query_title
from local_utils.sqlutils import query_trans_name
from ..inner_spider_utils import get_allowed_domains
from ..inner_spider_utils import generate_item
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

        logger().info('isbn13=%s, spider_name=%s, start_url=%s'
                      % (self.isbn13, 'trans_name', self.start_urls[0]))

    def parse(self, response):
        try:
            title = query_title(self.isbn13)[0][0]

            trans_name_list = query_trans_name(title)

            trans_name = ''

            if not trans_name_list:
                trans_name = trans_name_list[0][0]
            else:
                trans_name = google_translate(title)

            yield generate_item('trans_name', self.isbn13, trans_name)
        except Exception as e:

            logger('e').error(get_log_msg('parse', 'isbn13=%s, spider_name=%s, e.msg=%s'
                                          % (self.isbn13, 'trans_name', e)))










