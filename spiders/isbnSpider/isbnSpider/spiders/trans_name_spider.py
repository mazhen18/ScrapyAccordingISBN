import scrapy
import logging
from scrapy.exceptions import CloseSpider
logger = logging.getLogger('trans_name_spider')


class TransNameSpider(scrapy.Spider):

    name = 'trans_name'

    allowed_domains = ['amazon.com',
                       'book.dangdang.com',
                       'taobao.com',
                       'tmall.com',
                       'jd.com']

    def __init__(self, *args, **kwargs):
        super(TransNameSpider, self).__init__(*args, **kwargs)
        self.isbn13 = kwargs.get('isbn13')
        self.start_urls = ['https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=' + self.isbn13]

    def parse(self, response):
        cu = response.xpath('/html/body/div[1]/div[2]/div/div[3]/div[2]/div/div[4]/div[1]/div/ul/li/div/div/div/div[2]/div[2]/div[1]/div[2]/a/span[2]/span/sup[1]/text()').extract()
        print('cu:%s,isbn13:%s' % (cu, self.isbn13))
        raise CloseSpider("suucess scrapy data")


