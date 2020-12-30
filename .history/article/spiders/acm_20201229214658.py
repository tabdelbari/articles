# -*- coding: utf-8 -*-
import scrapy


class AcmSpider(scrapy.Spider):
    name = 'acm'
    allowed_domains = ['acm.org']
    start_urls = ['http://acm.org/']

    def parse(self, response):
        pass
