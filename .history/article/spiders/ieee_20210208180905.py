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
        self.topic = topic
        self.keywords = keywords
        self.totalPages = 0

    def start_requests(self):
        post_data = '{"queryText": "' + self.topic + \
            '", "highlight": true, "returnType": "SEARCH", "matchPubs": true, "rowsPerPage": 100, "returnFacets": ["ALL"], "newsearch": true}'
        headers = {
            'Origin': 'https://ieeexplore.ieee.org',
            'Host': 'ieeexplore.ieee.org',
            'Accept-Language': 'fr-MA,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar-MA;q=0.6,ar;q=0.5,fr-FR;q=0.4',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        search_url = 'https://ieeexplore.ieee.org/rest/search'
        yield SplashRequest(search_url, self.parse_0, endpoint='execute',
                            magic_response=True, meta={'handle_httpstatus_all': True, 'data': 'hello'},
                            args={'lua_source': self.lua_script, 'http_method': 'POST', 'body': post_data, 'headers': headers})

    def parse_0(self, response):
        logging.debug(response)
        jr = json.loads(response.xpath('//*/pre/text()').get(default=''))

        self.totalPages = jr['totalPages']
        headers = {
            'Origin': 'https://ieeexplore.ieee.org',
            'Host': 'ieeexplore.ieee.org',
            'Accept-Language': 'fr-MA,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar-MA;q=0.6,ar;q=0.5,fr-FR;q=0.4',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        search_url = 'https://ieeexplore.ieee.org/rest/search'
        for i in range(1, (self.totalPages+1)):
            post_data = '{"queryText": "' + self.topic + \
                '", "highlight": true, "newsearch": true, "returnType": "SEARCH", "matchPubs": true, "rowsPerPage": 100, "returnFacets": ["ALL"], "pageNumber": '+str(i)+'}'
            yield SplashRequest(search_url, self.parse_1, endpoint='execute',
                                magic_response=True, meta={'handle_httpstatus_all': True, 'data': i},
                                args={'lua_source': self.lua_script, 'http_method': 'POST', 'body': post_data, 'headers': headers})
        pass

    def parse_1(self, response):
        jr = json.loads(response.xpath('//*/pre/text()').get(default=''))

        headers = {
            'Origin': 'https://ieeexplore.ieee.org',
            'Host': 'ieeexplore.ieee.org',
            'Accept-Language': 'fr-MA,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar-MA;q=0.6,ar;q=0.5,fr-FR;q=0.4',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        for record in jr['records']:
            result = {
                'title': record['articleTitle'],
                'authors': '|'.join(list(map(lambda author: author['preferredName'], record['authors']))),
                'lab': '',
                'organisation': '',
                'city': '',
                'country': '',
                'abstract': record['abstract'],
                'date_pub': record['publicationDate'],
                'journal': record['publicationTitle'],
                'topic': self.topic,
                'publisher': record['publisher'],
                'if': 0,
                'scoupus': 0,
                'doi': ''
            }
            metrics_url = "https://ieeexplore.ieee.org/rest/document/" + record['articleNumber'] + "/metrics"
            
            yield SplashRequest(metrics_url, self.parse_2, endpoint='execute',
                            magic_response=True, meta={'handle_httpstatus_all': True, 'data': result},
                            args={'lua_source': self.lua_script, 'http_method': 'GET', 'body': None, 'headers': headers})
        pass

    def parse_2(self, response):
        result = response.meta['data']
        jr = json.loads(response.xpath('//*/pre/text()').get(default=''))
        try:
            result['if'] = self.safe_cast(jr['metrics']['citationCountPaper'], int, 0)
            result['scoupus'] = self.safe_cast(jr['metrics']['scopus_count'], int, 0)
            result['doi'] = jr['metrics']['doi']
        finally:
            headers = {
                'Origin': 'https://ieeexplore.ieee.org',
                'Host': 'ieeexplore.ieee.org',
                'Accept-Language': 'fr-MA,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar-MA;q=0.6,ar;q=0.5,fr-FR;q=0.4',
                'Accept-Encoding': 'gzip, deflate, br'
            }
            authors_url = "https://ieeexplore.ieee.org/document/" + jr['articleNumber'] + "/authors#authors"
            yield SplashRequest(authors_url, self.parse, endpoint='execute',
                                magic_response=True, meta={'handle_httpstatus_all': True, 'data': result},
                                args={'lua_source': self.lua_script, 'http_method': 'GET', 'body': None, 'headers': headers})
        pass

    def parse(self, response):
        result = response.meta['data']
        try:
            adresses = response.xpath('//*/div[@class="author-card"]/div/div/div/div/text()').getall().split(', ')
            
            result['organisation'] = adresses[0]
            result['lab'] = adresses[1]
            result['city'] = adresses[2]
            result['country'] = adresses[4]
        finally:
            yield result
        pass

    def safe_cast(val, to_type, default=None):
        try:
            return to_type(val)
        except (ValueError, TypeError):
            return default
