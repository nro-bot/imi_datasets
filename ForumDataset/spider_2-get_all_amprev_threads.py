# 23 Mar 2023
# nrobot

# Given a list of category (links), 
# get all threads from those categories (following next page links if present) 
# Outputs csv.

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider
from scrapy.utils.log import configure_logging 

from datetime import datetime
import logging
import pandas as pd

# Example link formats
# Category: https://ampreviews.net/index.php?forums/discussion-somecity.89/
# Thread: https://ampreviews.net/index.php?threads/my-spa-browns.137/

class ThreadSpider(CrawlSpider):
    name = 'extract_threads'

    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='nogit_data/threads_spider.log',
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%d/%b/%Y %H:%M:%S',
    )

    def start_requests(self):
        self.base_url = 'https://ampreviews.net'
        self.pages_scraped = 0
        yield scrapy.Request(url=self.base_url, callback=self.tally_progress)

        forum_data = pd.read_csv('nogit_data/list_of_categories.csv')

        for category_url in forum_data.link:
            url = self.base_url + category_url
            self.logger.info(f'Now working with url {url}')
            yield scrapy.Request(url=url, callback=self.parse_page)

    def tally_progress(self, response):
        thread_counts = response.css('div.node-stats dl:first-child dd::text').getall()
        thread_counts = [int(num.replace(',', '')) for num in thread_counts]
        self.TOTAL_THREAD_PAGES = round(sum(thread_counts)/20) + 1
        # NOTE: assuming delay setting is 2 seconds ! 
        self.TOTAL_HOURS = self.TOTAL_THREAD_PAGES * 2 / 3600 
        self.logger.warning(f'Total thread pages: {self.TOTAL_THREAD_PAGES}')
        self.logger.warning(f'Approximate time needed (at 2 secs per page): {self.TOTAL_HOURS:.2f} hrs')

    def parse_page(self, response):
        self.pages_scraped += 1

        max_pages = response.css(
            'li.pageNav-page:last-child a::text').get(default=1)

        category_text = response.css('.p-title-value::text').get() # e.g. Discussion-Dallas
        page_name_and_pagination = response.css('title::text').get() # e.g. Discussion-Dallas | Page 2 | AMPReviews
        page_url = response.url  

        if 'boardwide-' in page_url:
            city = 'N/A'
        else: 
            city = category_text.split(' - ')[-1]

        self.logger.info(f'Now scraping: {page_name_and_pagination} -- {page_url} -- TotalPages {max_pages}')
        ratio_complete = self.pages_scraped / self.TOTAL_THREAD_PAGES
        self.logger.warning(f'Approximate progress: [ {self.pages_scraped} / {self.TOTAL_THREAD_PAGES} ]'
            f' [ {ratio_complete*100:.2f}% ]'
                            f' [ {(1 - ratio_complete)*self.TOTAL_HOURS:.2f} HRS LEFT ]')

        for thread in response.css('div.structItem--thread'):
            data = {}
            data['city'] = city

            # Thread info
            data['title'] = thread.css('div.structItem-title a::text').get()
            data['link'] = thread.css('div.structItem-title a::attr(href)').get()
            data['num_replies'], data['num_views'] = \
                thread.css('dd::text').getall()

            data['posted_date_readable'], data['latest_date_readable'] = \
                thread.css('time::attr(title)').getall()
            data['posted_date_data'], data['latest_date_data'] = \
                thread.css('time::attr(data-time)').getall()

            # - Original poster info
            data['author'] = thread.css('a.username:first-child::text').get()
            data['latest_author'] = thread.css('a.username:last-child::text').get()
            data['author_url'], data['latest_author_url'] = \
                thread.css('a.username::attr(href)').getall()

            data['time_downloaded'] = datetime.now().strftime('%d/%b/%Y %H:%M:%S')
            data['comment'] = f'Category: {category_text}'
            yield data 

        # Dirty hack to insert a single line "comment" into bottom of csv file
        # which logs the current page and url for reference
        yield {
            'comment': f'{page_name_and_pagination} -- {page_url} -- TotalPages {max_pages}'
        }

        next_page = response.css('a.pageNav-jump--next::attr(href)').get()

        if next_page is not None:
            next_page = response.urljoin(next_page)
            self.logger.info(f'going to next page: {next_page}')
            yield scrapy.Request(next_page, callback=self.parse_page)

c = CrawlerProcess(
    settings={
        "FEEDS":{
            "nogit_data/list_of_threads.csv" : {"format" : "csv",
                                "overwrite":True,
                                "encoding": "utf8",
                }},
        "CONCURRENT_REQUESTS":1, # default 16
        "CONCURRENT_REQUESTS_PER_DOMAIN":1, # default 8 
        "CONCURRENT_ITEMS":1, # DEFAULT 100
        "DOWNLOAD_DELAY": 2, # default 0
        "DEPTH_LIMIT":0,
        "JOBDIR":'nogit_data/crawls/amprev_threads',
        "DUPEFILTER_DEBUG":True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
    }
)
    #'CLOSESPIDER_PAGECOUNT': 3,
c.crawl(ThreadSpider)
c.start()

# DEBUG NOTE: if running into struct error needs unpack 4 bytes,
# remove the job resume directory (crawls/amprev); make sure to stop scrapy with a
# single ctrl-c, which will take 'download-delay' seconds to take effect