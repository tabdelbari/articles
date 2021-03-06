import scrapy
import logging
import re
from scrapy_splash import SplashRequest
from article.items import ArticleItem


class SciencedirectSpider(scrapy.Spider):
    name = 'sciencedirect'
    allowed_domains = ['scienced.com']
    
    def __init__(self, topic='', keywords='', **kwargs):
        super().__init__(**kwargs)
        self.start_urls = ['https://www.sciencedirect.com/search?qs=%s' %keywords]
        self.topic = topic

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, callback=self.find_articles, args={ 'wait': 2 })

    def find_articles(self, response):
        logging.info(response.text)
        articles_urls = response.xpath('//*/div/h2/span/a/@href').getall()
        logging.info(f'{len(articles_urls)} articles found')
        for article_url in articles_urls:
            article_url = 'https://www.sciencedirect.com' + article_url
            yield SplashRequest(article_url, callback=self.parse)

        # finding and visiting next page
        ###

        next_page = response.xpath('//*[@id="srp-pagination"]/li[@class="pagination-link next-link"]/a/@href').get(default='')
        logging.info('Next page found:')
        if next_page != '':
            next_page = 'https://www.sciencedirect.com' + next_page
            yield SplashRequest(next_page, callback=self.find_articles)
        ###

    def parse(self, response):
        article = ArticleItem()
        logging.info('Processing --> ' + response.url)

        article.title = ''
        article.authors = ''
        article.country = ''
        article.abstract = ''
        article.date_pub = ''
        article.journal = ''
        article.topic = self.topic
        article.latitude = ''
        article.longitude = ''
        
        yield article
