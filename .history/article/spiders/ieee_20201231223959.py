import scrapy
import logging
import re
# from scrapy_splash import SplashRequest
from article.items import ArticleItem


class IeeeSpider(scrapy.Spider):
    name = 'ieee'
    allowed_domains = ['ieee.org']
    custom_settings = {'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}

    def __init__(self, topic='', keywords='', **kwargs):
        super().__init__(**kwargs)
        self.start_urls = ['https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=%s' %keywords]
        self.topic = topic

    def start_requests(self):
        req = scrapy.Request('https://ieeexplore.ieee.org/rest/search', method='POST', headers={ 
            'Origin': 'https://ieeexplore.ieee.org',
            'Host': 'ieeexplore.ieee.org',
            ''
            })
        for url in self.start_urls:
            scrapy.Request
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
            yield SplashRequest(article_url, callback=self.parse, args={ 'wait': 2 })

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
