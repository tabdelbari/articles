import scrapy
import logging
import re
from scrapy_splash import SplashRequest
from article.items import ArticleItem


class AcmSpider(scrapy.Spider):
    name = 'acm'
    allowed_domains = ['acm.org']
    
    def __init__(self, topic='', keywords='', **kwargs):
        super().__init__(**kwargs)
        self.start_urls = ['https://dl.acm.org/action/doSearch?AllField=%s' %keywords]
        self.topic = topic

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, callback=self.find_articles, args={ 'wait': 2 })

    def find_articles(self, response):
        articles_urls = response.xpath('.//*/div[contains(@class,"issue-item")]/*/h5/span/a/@href').getall()
        logging.info(f'{len(articles_urls)} articles found')
        for url in articles_urls:
            article_url = 'https://dl.acm.org' + url
            yield scrapy.Request(article_url, callback=self.parse)

        next_page = response.xpath('.//*/nav[contains(@class, "pagination")]/span/a[@title="Next Page"]/@href').get(default='')
        logging.info('Next page found:')
        if next_page != '':
            yield SplashRequest(next_page, callback=self.find_articles)

    def parse(self, response):
        article = ArticleItem()
        logging.info('Processing --> ' + response.url)

        article['title'] = ''
        article['authors'] = ''
        article['country'] = ''
        article['abstract'] = ''
        article['date_pub'] = ''
        article['journal'] = ''
        article['topic'] = self.topic
        article['latitude'] = ''
        article['longitude'] = ''
        
        yield article
