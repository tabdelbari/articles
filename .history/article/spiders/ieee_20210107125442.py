import scrapy
import logging
import re
from scrapy_splash import SplashRequest
from article.items import ArticleItem
import json


class IeeeSpider(scrapy.Spider):
    name = 'ieee'
    allowed_domains = ['ieee.org']
    lua_script = """
    function main(splash, args)
      assert(splash:go{
        splash.args.url,
        headers=splash.args.headers,
        http_method=splash.args.http_method,
        body=splash.args.body,
      })
      assert(splash:wait(10))
      return splash:html()
    end
    """

    # create lua for article detail to obtain abstract

    def __init__(self, topic='', keywords='', **kwargs):
        super().__init__(**kwargs)
        # self.start_urls = ['https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=%s' %keywords]
        self.post_url = 'https://ieeexplore.ieee.org/rest/search'
        self.headers = {
            'Origin': 'https://ieeexplore.ieee.org',
            'Host': 'ieeexplore.ieee.org',
            'Accept-Language': 'fr-MA,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar-MA;q=0.6,ar;q=0.5,fr-FR;q=0.4',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.topic = topic
        self.keywords = keywords
        self.totalRecords = 0

    def start_requests(self):
        post_data = '{"queryText": "' + self.topic + \
            '", "highlight": true, "returnType": "SEARCH", "matchPubs": true, "rowsPerPage": 100, "returnFacets": ["ALL"]}'
        yield SplashRequest(self.post_url, self.init_articles, endpoint='execute',
                            magic_response=True, meta={'handle_httpstatus_all': True, 'data': 'hello'},
                            args={'lua_source': self.lua_script, 'http_method': 'POST', 'body': post_data, 'headers': self.headers})

    def init_articles(self, response):
        # response.meta['data'] -> "hello"
        jr = json.loads(response.xpath('//*/pre/text()').get(default=''))
        self.totalRecords = jr['totalRecords']
        for record in jr['records']:
            result = {
                'title': record[''],
                'authors': '|'.join(authors),
                'country': '',
                'abstract': record[''],
                'date_pub': record[''],
                'journal': record[''],
                'topic': self.topic,
                'latitude': '',
                'longitude': ''
            }
            yield SplashRequest(post_url, self.init_articles, endpoint='execute',
                                magic_response=True, meta={'handle_httpstatus_all': True, 'data': 'hello'},
                                args={'lua_source': self.lua_script, 'http_method': 'POST', 'body': post_data, 'headers': headers})
            # find abstract for this article and pass as meta the half of object
            logging.info('===============================Article:' +
                         str(id['articleTitle']) + ' - ' + str(id['articleNumber']))
        
        post_data = '{"queryText": "' + self.topic + \
            '", "highlight": true, "returnType": "SEARCH", "matchPubs": true, "rowsPerPage": 100, "returnFacets": ["ALL"]}'
        yield SplashRequest(self.post_url, self.init_articles, endpoint='execute',
                            magic_response=True, meta={'handle_httpstatus_all': True, 'data': 'hello'},
                            args={'lua_source': self.lua_script, 'http_method': 'POST', 'body': post_data, 'headers': self.headers})
        pass

    def find_articles(self, response, ):

        logging.info(response.text)
        articles = response.xpath(
            '//*[@id="xplMainContent"]/div[2]/div[2]/xpl-results-list/div[3]/xpl-results-item/div[1]/div[1]/div[2]/h2/a').getall()
        logging.info(f'{len(articles)} articles found')
        for article_id in articles:
            article_id = re.findall("\d+", article_id)[-1]
            article_url = 'https://ieeexplore.ieee.org/document/' + \
                str(article_id)
            yield SplashRequest(article_url, callback=self.parse, args={'wait': 2})

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
