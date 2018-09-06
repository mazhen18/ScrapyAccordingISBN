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


class PriceItem(scrapy.Item):

    isbn13 = scrapy.Field()

    price = scrapy.Field()


class ClassficationItem(scrapy.Item):

    isbn13 = scrapy.Field()

    classfication = scrapy.Field()


class TransNameItem(scrapy.Item):
    isbn13 = scrapy.Field()

    trans_name = scrapy.Field()


