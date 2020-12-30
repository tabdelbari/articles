# -*- coding: utf-8 -*-
import scrapy


class IeeeSpider(scrapy.Spider):
    name = 'ieee'
    allowed_domains = ['ieee.org']

    def __init__(self, topic='', keywords='', **kwargs):
        super().__init__(**kwargs)
        self.start_urls = ['https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=%s' %keywords]
        self.topic = topic

    def start_requests(self):
        for url in self.start_requests:
            yield SplashRequest(url, callback=self.find_articles, args={ 'wait': 2 })
        search_url = "https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=" + \
            self.keyword.lower()
        yield SplashRequest(search_url, callback=self.find_articles, args={ 'wait': 2 })

    def find_articles(self, response):
        logging.error(response.text)
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
        logging.info('Processing --> ' + response.url)

        title = response.xpath(
            '//*[@id="LayoutWrapper"]/div/div/div/div[3]/div/xpl-root/div/xpl-document-details/div/div[1]/section[2]/div/xpl-document-header/section/div[2]/div/div/div[1]/div/div/h1/span').get(default='')
        abstract = response.xpath(
            '//*[@id="LayoutWrapper"]/div/div/div/div[3]/div/xpl-root/div/xpl-document-details/div/div[1]/div/div[2]/section/div[2]/div/xpl-document-abstract/section/div[3]/div[1]/div/div/div').get(default='')
        published_in = response.xpath(
            '//*[@id="LayoutWrapper"]/div/div/div/div[3]/div/xpl-root/div/xpl-document-details/div/div[1]/div/div[2]/section/div[2]/div/xpl-document-abstract/section/div[3]/div[2]/a').get(default='')
        date = response.xpath(
            '//*[@id="LayoutWrapper"]/div/div/div/div[3]/div/xpl-root/div/xpl-document-details/div/div[1]/div/div[2]/section/div[2]/div/xpl-document-abstract/section/div[3]/div[3]/div[1]/div[1]/text()').get(default='')
        # authors = response.xpath('//*[@id="authors"]/div[1]/xpl-author-item/div/div[1]/div').getall()
        isbn = response.xpath(
            '//*[@id="LayoutWrapper"]/div/div/div/div[3]/div/xpl-root/div/xpl-document-details/div/div[1]/div/div[2]/section/div[2]/xpl-document-abstract/section/div[3]/div[3]/div[1]/div[3]/div/div/span').get(default='')

        result = {
            'title': title,
            'abstract': abstract,
            'article_url': response.url,
            'published_in': published_in,
            'date': date,
            'isbn': isbn,
            'keyword': self.keyword

        }

        yield result
