# -*- coding: utf-8 -*-
import scrapy


class SciencedirectSpider(scrapy.Spider):
    name = 'sciencedirect'
    allowed_domains = ['scienced.com']
    
    
