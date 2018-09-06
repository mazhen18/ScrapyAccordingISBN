from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import argparse


def run_spider(spider_name, isbn13):

    process = CrawlerProcess(get_project_settings())

    process.crawl(spider_name, isbn13=isbn13)

    process.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--spider_name',
        type=str,
        default='classfication',
        help='input spider name'
    )

    parser.add_argument(
        '--isbn13',
        type=str,
        default='9781501124020',
        help='input isbn13, example: "123456789123" '
    )

    args = parser.parse_args()

    spider_name = args.spider_name

    isbn13 = args.isbn13

    run_spider(spider_name, isbn13)