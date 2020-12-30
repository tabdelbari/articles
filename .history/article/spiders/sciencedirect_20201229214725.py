# -*- coding: utf-8 -*-
import scrapy


class SciencedirectSpider(scrapy.Spider):
    name = 'sciencedirect'
    allowed_domains = ['scienced.com']
    start_urls = ['http://scienced.com/']

    def parse(self, response):
        pass
