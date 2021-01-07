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

    def __init__(self, topic='', keywords='', **kwargs):
        super().__init__(**kwargs)
        self.start_urls = ['https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=%s' %keywords]
        self.topic = topic

    def start_requests(self):
        post_url = 'https://ieeexplore.ieee.org/rest/search'
        post_data = '{"queryText": "' + self.topic + '", "highlight": true, "returnType": "SEARCH", "matchPubs": true, "rowsPerPage": 100, "returnFacets": ["ALL"]}'
        headers={ 
            'Origin': 'https://ieeexplore.ieee.org',
            'Host': 'ieeexplore.ieee.org',
            'Accept-Language': 'fr-MA,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar-MA;q=0.6,ar;q=0.5,fr-FR;q=0.4',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
            }
        # yield scrapy.Request(post_url, self.init_articles, method='POST', headers=headers, body=post_data)
        yield SplashRequest(post_url, self.init_articles, endpoint='execute',
                            magic_response=True, meta={'handle_httpstatus_all': True},
                            args={'lua_source': self.lua_script, 'http_method': 'POST', 'body': post_data, 'headers': headers})
    
    def init_articles(self, response):
        jr = json.loads(response.xpath('//*/pre/text()').get(default=''))
        logging.info('===============================Total Records:' + str(jr['totalRecords']))
        for id in jr['records']:
            logging.info('===============================Article:' + str(id['articleTitle']) + ' - ' + str(id['articleTitle']) + ' - ' + articleNumber)
        pass

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
