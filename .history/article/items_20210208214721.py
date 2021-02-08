# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticleItem(scrapy.Item):

    'if'= scrapy.Field()
    'scoupus'= scrapy.Field()
    'title'= scrapy.Field()
    'abstract'= scrapy.Field()
    'year'= scrapy.Field()
    'journal'= scrapy.Field()
    'publisher'= scrapy.Field()
    'doi': response.meta['doi'],
    title = scrapy.Field()
    authors = scrapy.Field()
    country = scrapy.Field()
    abstract = scrapy.Field()
    date_pub = scrapy.Field()
    journal = scrapy.Field()
    topic = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    pass
