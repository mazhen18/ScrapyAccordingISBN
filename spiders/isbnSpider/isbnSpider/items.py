# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IsbnspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class CurrencyItem(scrapy.Item):

    isbn13 = scrapy.Field()

    currency = scrapy.Field()

    last_update_time = scrapy.Field()


class PriceItem(scrapy.Item):

    isbn13 = scrapy.Field()

    price = scrapy.Field()

    last_update_time = scrapy.Field()


class ClassficationItem(scrapy.Item):

    isbn13 = scrapy.Field()

    classfication = scrapy.Field()

    last_update_time = scrapy.Field()


class TransNameItem(scrapy.Item):
    isbn13 = scrapy.Field()

    trans_name = scrapy.Field()

    last_update_time = scrapy.Field()

class SummaryItem(scrapy.Item):
    isbn13 = scrapy.Field()

    summary = scrapy.Field()

    last_update_time = scrapy.Field()


class AllInfosItem(scrapy.Item):
    isbn13 = scrapy.Field()
    title = scrapy.Field()
    pic = scrapy.Field()
    author = scrapy.Field()
    summary = scrapy.Field()
    pubdate = scrapy.Field()
    publisher = scrapy.Field()
    page = scrapy.Field()
    binding = scrapy.Field()
    price = scrapy.Field()

    trans_name = scrapy.Field()
    classfication = scrapy.Field()
    currency = scrapy.Field()  # 币种

    # subtitle = '' #副标题
    pubplace = scrapy.Field()
    isbn10 = scrapy.Field()
    keyword = scrapy.Field()
    edition = scrapy.Field()  # 版次
    impression = scrapy.Field()  # 印次
    body_language = scrapy.Field()
    format = scrapy.Field()  # 开本
    class_cn = scrapy.Field()  # 中图分类号

    last_update_time = scrapy.Field()


