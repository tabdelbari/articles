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
        self.start_urls = ['https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=%s' %keywords]
        self.topic = topic

    def start_requests(self):
        for url in self.start_requests:
            yield SplashRequest(url, callback=self.find_articles, args={ 'wait': 2 })

    def find_articles(self, response):
        logging.info(response.text)
        articles = response.xpath(
            '//*[@id="xplMainContent"]/div[2]/div[2]/xpl-results-list/div[3]/xpl-results-item/div[1]/div[1]/div[2]/h2/a').getall()
        logging.info(f'{len(articles)} articles found')
        for article_id in articles:
            article_id = re.findall("\d+", article_id)[-1]
            article_url = 'https://ieeexplore.ieee.org/document/' + \
                str(article_id)
            yield scrapy.Request(article_url, callback=self.parse)

        # finding and visiting next page
        ###

        ###next_page = response.xpath('//*[@class="w-button-more"]/a/@href').get(default='')
        ###logging.info('Next page found:')
        # if next_page != '':
        ###    next_page = 'https://mobile.twitter.com' + next_page
        # yield scrapy.Request(next_page, callback=self.find_tweets)
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
