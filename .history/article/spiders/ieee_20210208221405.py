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
      assert(splash:wait(1))
      return splash:html()
    end
    """

    lua_script2 = """
    function main(splash, args)
      assert(splash:go{
        splash.args.url,
        headers=splash.args.headers,
        http_method=splash.args.http_method
      })
      assert(splash:wait(1))
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
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8'
        }
        search_url = 'https://ieeexplore.ieee.org/rest/search'
        yield SplashRequest(search_url, self.parse_0, endpoint='execute',
                            magic_response=True, meta={'handle_httpstatus_all': True},
                            args={'lua_source': self.lua_script, 'http_method': 'POST', 'body': post_data, 'headers': headers})

    def parse_0(self, response):
        jr = json.loads(response.xpath('//*/pre/text()').get(default=''))

        self.totalPages = jr['totalPages']

        headers = {
            'Origin': 'https://ieeexplore.ieee.org',
            'Host': 'ieeexplore.ieee.org',
            'Accept-Language': 'fr-MA,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar-MA;q=0.6,ar;q=0.5,fr-FR;q=0.4',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8'
        }
        search_url = 'https://ieeexplore.ieee.org/rest/search'
        for i in range(1, (self.totalPages+1)):
            post_data = '{"queryText": "' + self.topic + \
                '", "highlight": true, "newsearch": true, "returnType": "SEARCH", "matchPubs": true, "rowsPerPage": 100, "returnFacets": ["ALL"], "pageNumber": '+str(i)+'}'
            yield SplashRequest(search_url, self.parse_1, endpoint='execute',
                                magic_response=True, meta={'handle_httpstatus_all': True},
                                args={'lua_source': self.lua_script, 'http_method': 'POST', 'body': post_data, 'headers': headers})

    def parse_1(self, response):
        jr = json.loads(response.xpath('//*/pre/text()').get(default=''))

        headers = {
            'Origin': 'https://ieeexplore.ieee.org',
            'Host': 'ieeexplore.ieee.org',
            'Accept-Language': 'fr-MA,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar-MA;q=0.6,ar;q=0.5,fr-FR;q=0.4',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8'
        }
        for record in jr['records']:
            authors_ids = list(map(lambda author: author['id'], record['authors']))
            metrics_url = "https://ieeexplore.ieee.org/rest/document/" + record['articleNumber'] + "/metrics"
            yield SplashRequest(metrics_url, self.parse_2, endpoint='execute',
                                magic_response=True,
                                meta={
                                    'handle_httpstatus_all': True, 
                                    'data' : {
                                        'title'= record['articleTitle'],
                                        'abstract'=record['abstract'],
                                        'year'= record['publicationYear'],
                                        'journal'= record['publicationTitle'],
                                        publisher= record['publisher'],
                                        doi= record['doi'],
                                        authors_ids= authors_ids
                                    }
                                },
                                args={'lua_source': self.lua_script2, 'http_method': 'GET', 'headers': headers})
    def parse_2(self, response):
        # result = response.meta['data']
        authors_ids = response.meta['authors_ids']
        jr = json.loads(response.xpath('//*/pre/text()').get(default=''))
        citationCountPaper = 0
        scoupus = 0
        try:
            citationCountPaper = self.safe_cast(jr['metrics']['citationCountPaper'], int, 0)
        except:
            pass
        try:
            scoupus = self.safe_cast(jr['metrics']['scopus_count'], int, 0)
        except:
            pass
        headers = {
            'Origin': 'https://ieeexplore.ieee.org',
            'Host': 'ieeexplore.ieee.org',
            'Accept-Language': 'fr-MA,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar-MA;q=0.6,ar;q=0.5,fr-FR;q=0.4',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8'
        }
        for author_id in authors_ids:
                author_url = 'https://ieeexplore.ieee.org/rest/author/' + str(author_id)
                yield SplashRequest(author_url, self.parse, endpoint='execute',
                                magic_response=True,
                                meta=dict(
                                    handle_httpstatus_all= True,
                                    data = dict(
                                        impf= citationCountPaper,
                                        scoupus= scoupus,
                                        title= response.meta['data']['articleTitle'],
                                        abstract= response.meta['data']['abstract'],
                                        year= response.meta['data']['publicationYear'],
                                        journal= response.meta['data']['publicationTitle'],
                                        publisher= response.meta['data']['publisher'],
                                        doi= response.meta['data']['doi'],
                                    ) 
                                ), 
                                args={'lua_source': self.lua_script2, 'http_method': 'GET', 'headers': headers})
    def parse(self, response):
        result = {
            'impf': response.meta['data']['impf'],
            'scoupus': response.meta['data']['scoupus'],
            'title': response.meta['data']['articleTitle'],
            'abstract': response.meta['data']['abstract'],
            'year': response.meta['data']['publicationYear'],
            'journal': response.meta['data']['publicationTitle'],
            'publisher': response.meta['data']['publisher'],
            'doi': response.meta['data']['doi'],
        }
        try:
            jr = json.loads(response.xpath('//*/pre/text()').get(default=''))[0]
            id = jr['id']
            author = jr['preferredName']
            adresses = jr['currentAffiliation'].split(', ')
            result['author'] = author
            result['organisation'] = adresses[0]
            result['lab'] = adresses[1]
            result['city'] = adresses[2]
            result['country'] = adresses[3]
            result['_id'] = result['doi'] + '_' + str(id)
        except:
            pass
        yield result

    def safe_cast(self, val, to_type, default=None):
        try:
            return to_type(val)
        except:
            return default
