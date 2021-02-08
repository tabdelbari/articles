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
    'abstract': response.meta['abstract'],
    'year': response.meta['publicationYear'],
    'journal': response.meta['publicationTitle'],
    'publisher': response.meta['publisher'],
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
