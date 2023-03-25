# 24 Mar 2023
# nrobot

# Given a list of thread (links), 
# get post text (and post, post author metadata) from those threads (following 
# next page links if present). 

# Applies to Xenforo forums. Outputs csv.

import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.crawler import CrawlerProcess
import logging
from scrapy.utils.log import configure_logging 
from bs4 import BeautifulSoup
from datetime import datetime
import re

import pandas as pd
# import time

# Example link formats for
# Thread: https://ampreviews.net/index.php?threads/spa-browns-rd.137/
# Post: https://ampreviews.net/index.php?threads/anyone-seen-this.13/post-95

class PostSpider(CrawlSpider):
    name = 'extract_posts'

    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='nogit_data/posts_spider.log',
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%d/%b/%Y %H:%M:%S',
        level=logging.INFO # NOTE: doesn't actually do anything
    )

    def start_requests(self):
        self.base_url = 'https://ampreviews.net'

        # -- Make list of URLs to scrape

        # NOTE: because each city has a discussion and a reviews category
        # Sort categories by discussions first (review categories second), then 
        # order within each category by date posted thread was posted
        # (Most so have data to explore while scraper runs)

        threads_list = pd.read_csv('nogit_data/list_of_threads.csv')
        urls_list = threads_list.dropna().sort_values(
            by=['comment','posted_date_data'],
            ascending=[True, False]).link

        for url in urls_list:
            url = self.base_url + url
            self.logger.error(f'Now working with url {url}')
            yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        self.logger.debug(f'Parsing url {response.url}')

        page_name_and_pagination = response.css('title::text').get() # e.g. Discussion-Dallas | Page 2 | AMPReviews
        thread_url = response.url  
        thread_max_pages = response.css(
            'li.pageNav-page:last-child a::text').get(default=1)

        src_category_name = response.css('.p-breadcrumbs li:last-child span::text').get()
        thread_page_num = response.css('.pageNav-page--current a::text').get(default=1)
        thread_page_name = response.css('.p-title-value::text').get()

        posts = response.css('article.message--post')
        for post in posts: 
            data = {}
            data['time_downloaded'] = datetime.now().strftime('%d/%b/%Y %H:%M:%S')
            
            # -- POST Metadata
            # 
            data['post_id'] = post.css('::attr(data-content)').get()
            data['posted_date_readable'] = post.css('.message-date time::attr(title)').get()
            data['posted_date_data'] = post.css('.message-date time::attr(data-time)').get()
            post_ordinal = post.css('.message-attribution-opposite a::text').get() # example: "#19"
            post_ordinal = post_ordinal[1:] if post_ordinal else None # in case CSS selector fails / website changes, scraper so not completely fail
            data['post_ordinal'] = post_ordinal

            # -- POST TEXT 
            # 
            #data['post_text'] = ''.join(post.css('div.bbWrapper::text').getall())
            #data['post_html'] = ''.join(post.css('div.bbWrapper').getall())
            post_text = post.css('div.bbWrapper').get() 
            post_text = BeautifulSoup(post_text, 'html.parser')
            if post_text.find('div', class_='bbCodeBlock'):
                post_text.find('div', class_='bbCodeBlock').decompose()
            data['post_text'] = post_text.text

            # -- QUOTES
            # Handle quotes if exist
            quotes = post.css('div.bbCodeBlock--quote')
            data['num_quotes'] = len(quotes) # store as checksum in case want to unconcatenate quotes


            if quotes: 
                quoted_post_ids = []
                quoted_authors = []
                quoted_contents = []
                for quote in quotes:
                    # Example output: 
                    # <a href="/index.php?goto/post&amp;ipostd=955852" class="bbCodeBlock-sourceJump" 
                    # data-xf-click="attribution" data-content-selector="#post-955852">
                    # XYZ said:</a>
                    quoted_post_id = quote.css('.bbCodeBlock-sourceJump::attr(data-content-selector)').get()
                    quoted_author = quote.css('a::text').get()  #.replace(' said:', '')
                    quoted_author = quoted_author.split()[0] if quoted_author else None
                    quoted_post_content = quote.css(
                        '.bbCodeBlock-expandContent::text').get()

                    quoted_authors.append(quoted_author)
                    quoted_post_ids.append(quoted_post_id)
                    quoted_contents.append(quoted_post_content)

            data['quoted_post_ids'] = ' ~-~ '.join(quoted_post_ids) if quotes else ''
            data['quoted_authors'] = ' ~-~ '.join(quoted_authors) if quotes else '' 
            data['quoted_contents'] = ' ~-~ '.join(quoted_contents) if quotes else ''

            # --  LIKES
            # 
            likers = post.css('div.likesBar a * ::text').getall()
            num_likers = len(likers) # could be interesting stat # TODO: fix this count
            data['num_likers'] = num_likers 

            if num_likers == 3:
                if re.findall(likers[-1], ' and \d+ other'):
                    _num = likers[-1].split(' other')[0].split(' and ')[1]
                    num_likers += int(_num)
            likers = ' - '.join(likers)
            data['likers'] = likers

            # -- AUTHOR Metadata 
            # 
            data['author'] = post.css('::attr(data-author)').get()
            data['author_url'] = post.css('a.username::attr(href)').get()
            author_title, author_num_posts, author_num_reviews = None, None, None 

            try:
                author_title, author_num_posts, author_num_reviews = post.css(
                    '.userTitle ::text').getall()[:3]
                    # Example output: ['Review Contributor', 'Messages: 46', 'Reviews: 13']
                    # OR ['Registered Member', 'Messages: 30, 'Joined ']
                author_num_posts = author_num_posts.split()[-1]
                author_num_reviews = author_num_reviews.split()[-1]
                if author_num_reviews == 'Joined':
                    author_num_reviews = 'N/A'
            except: # May produce indexing error if no results
                self.warning.warning('Attempt to extract author stats failed')

            data['author_title'] = author_title
            data['author_num_posts'] = author_num_posts
            data['author_num_reviews'] = author_title # TODO FIX

            data['join_date_readable'] = post.css('.userTitle time::attr(title)').get()
            data['join_date_data'] = post.css('.userTitle time::attr(data-time)').get()

            data['src_category_name'] = src_category_name
            data['thread_page_url'] = thread_url
            data['thread_page_name'] = thread_page_name
            data['thread_page_num'] = thread_page_num
            data['thread_max_pages'] = thread_max_pages

            self.logger.info(
                f'Now scraped: {page_name_and_pagination} -- {thread_url} -- TotalPages {thread_max_pages}')

            # -- Post metadata
            #
            data['comment'] = '' 
            yield data

        # dirty hack to insert "comment" into bottom of csv file
        # which contains the current page and url, just in case
        yield {
            'comment': f'{page_name_and_pagination} -- {thread_url} -- TotalPages {thread_max_pages}'
        }

        next_page = response.css('a.pageNav-jump--next::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            self.logger.info(f'going to next page: {next_page}')
            yield scrapy.Request(next_page, callback=self.parse_page)

c = CrawlerProcess(
    settings={
        "FEEDS":{
            "nogit_data/list_of_post_contents.csv" : {"format" : "csv",
                                "overwrite":True,
                                "encoding": "utf8",
                            }},
        "CONCURRENT_REQUESTS":1, # default 16
        "CONCURRENT_REQUESTS_PER_DOMAIN":1, # default 8 
        "CONCURRENT_ITEMS":1, # DEFAULT 100
        "DOWNLOAD_DELAY": 10, # default 0
        "DEPTH_LIMIT":0,
        #"AUTOTHROTTLE_ENABLED": True,
        #"AUTOTHROTTLE_START_DELAY": 1,
        #"AUTOTHROTTLE_MAX_DELAY": 3
        "JOBDIR":'nogit_data/crawls/amprev_posts',
        "DUPEFILTER_DEBUG":True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
    }
)

    #'CLOSESPIDER_PAGECOUNT': 3,
c.crawl(PostSpider)
c.start()