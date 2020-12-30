# -*- coding: utf-8 -*-
import scrapy


class IeeeSpider(scrapy.Spider):
    name = 'ieee'
    allowed_domains = ['xplore.ieee.org']
    start_urls = ['http://xplore.ieee.org/']

    def parse(self, response):
        pass
