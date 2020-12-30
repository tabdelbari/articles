# -*- coding: utf-8 -*-
import scrapy


class IeeeSpider(scrapy.Spider):
    name = 'ieee'
    allowed_domains = ['ieee.org']

    def parse(self, response):
        pass
