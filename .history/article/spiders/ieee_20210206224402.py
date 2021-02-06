import scrapy
import logging
import re
from scrapy_splash import SplashRequest, request
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
        self.totalPages = 0

    def start_requests(self):
        post_data = '{"queryText": "' + self.topic + \
            '", "highlight": true, "returnType": "SEARCH", "matchPubs": true, "rowsPerPage": 100, "returnFacets": ["ALL"]}'
        yield SplashRequest(self.post_url, self.init_articles, endpoint='execute',
                            magic_response=True, meta={'handle_httpstatus_all': True, 'data': 'hello'},
                            args={'lua_source': self.lua_script, 'http_method': 'POST', 'body': post_data, 'headers': self.headers})

    def init_articles(self, response):
        # response.meta['data'] -> "hello"
        jr = json.loads(response.xpath('//*/pre/text()').get(default=''))
        self.totalPages = jr['totalPages']
        for i in range(1, (self.totalPages+1)):
            post_data = '{"queryText": "' + self.topic + \
                '", "highlight": true, "returnType": "SEARCH", "matchPubs": true, "rowsPerPage": 100, "returnFacets": ["ALL"], "pageNumber": '+str(i)+'}'
            yield SplashRequest(self.post_url, self.parse_1, endpoint='execute',
                                magic_response=True, meta={'handle_httpstatus_all': True, 'data': i},
                                args={'lua_source': self.lua_script, 'http_method': 'POST', 'body': post_data, 'headers': self.headers})
        pass

    def parse_1(self, response):
        logging.info('##################################Processing:' + str(response.meta['data']))
        jr = json.loads(response.xpath('//*/pre/text()').get(default=''))

        for record in jr['records']:
            result = {
                'title': record['articleTitle'],
                'authors': '|'.join(list(map(lambda author: author['preferredName'], record['authors']))),
                'country': '',
                'abstract': record['abstract'],
                'date_pub': record['publicationDate'],
                'journal': record['publicationTitle'],
                'topic': self.topic
            }

            # search for country
            details_url = "https://ieeexplore.ieee.org/document/" + record['articleNumber'] + "/authors#authors"
            yield SplashRequest(details_url, self.parse, endpoint='execute',
                            magic_response=True, meta={'handle_httpstatus_all': True, 'data': result},
                            args={'lua_source': self.lua_script, 'http_method': 'GET', 'body': None, 'headers': self.headers})
            # find abstract for this article and pass as meta the half of object: record['articleNumber']
        pass
    
    def parse(self, response):
        result = response.meta['data']
        # search for country using xpath
        result.country = 
        yield result

        pass
