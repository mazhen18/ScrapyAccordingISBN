import scrapy
import logging
from utils.myutils import google_translate
from utils.sqlutils import query_title
from utils.sqlutils import query_trans_name
from ..inner_spider_utils import get_allowed_domains
from ..inner_spider_utils import generate_item
from ..inner_spider_utils import break_scrapy
from ..items import TransNameItem
logger = logging.getLogger('trans_name_spider')


class TransNameItem(scrapy.Spider):

    name = 'trans_name'

    allowed_domains = get_allowed_domains()

    def __init__(self, *args, **kwargs):
        super(TransNameItem, self).__init__(*args, **kwargs)
        self.isbn13 = kwargs.get('isbn13')
        self.start_urls = ['https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=' + self.isbn13]

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

            break_scrapy('trans_name', self.isbn13, 'fail', e)










