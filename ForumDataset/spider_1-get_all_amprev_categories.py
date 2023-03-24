# 23 Mar 2023
# nrobot

# Given base url (for a Xenforo forum),
# Get links of all subcategory homepages (those that list threads, not further
# sub-sub-categories) 

# NOTE: overwrite csv set to false in settings at bottom
# NOTE: hardcoded with ampreviews specific link features 

import sys

import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.crawler import CrawlerProcess
import logging
from scrapy.utils.log import configure_logging 

# - Pseudocode
# for all links on page
    # if link has "reviews" or "disucssions" in the url
        # get the no. threads or no. messages for subcategory
        # yield data 
    # else 
        # follow the link to the subcategory and parse again 

class AmpRevSpider(CrawlSpider):
    name = 'extract_cities_and_categories'

    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='nogit_data/categories_spider.log',
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%d/%b/%Y %H:%M:%S',
    )


    def start_requests(self):
        self.cities = set()
        self.base_url = 'https://ampreviews.net'

        url = 'https://ampreviews.net/index.php'
        self.logger.debug(f'starting with url {url}')
        yield scrapy.Request(url=url, callback=self.parse_item)

    def parse_item(self, response):
        for category in response.css("div.node-main"):

            category_link = category.css("a::attr(href)").extract_first() 

            if 'boardwide-' or 'reviews-' in category_link or 'discussion-' in category_link:
                title = category.css("a::text").get()
                num_threads, num_msgs = category.css("dd::text").extract()
                
                if 'boardwide-' in category_link:
                    city = 'N/A'
                else:
                    city = title.split(' - ')[-1]
                    self.cities.add(city)
                    self.logger.info(f'Got city: {city}, from link: {category_link}')
                    
                yield {
                    'title': title,
                    'city': city,
                    'link': category_link,
                    'num_threads':  num_threads,
                    'num_messages': num_msgs
                }
                self.logger.debug(f'List of cities so far: {self.cities}')

            elif 'categories' in category_link:
                constructed_url = self.base_url + category_link
                self.logger.info(f'!-- Recursing down to {constructed_url}')
                yield scrapy.Request(url=constructed_url, callback=self.parse_item)
            
c = CrawlerProcess(
    settings = {
        "FEEDS":{
            "nogit_data/list_of_categories.csv" : {"format" : "csv",
                                "overwrite":True,
                                "encoding": "utf8",
                            }},
        "CONCURRENT_REQUESTS":1, # default 16
        "CONCURRENT_REQUESTS_PER_DOMAIN":1, # default 8 
        "CONCURRENT_ITEMS":1, # DEFAULT 100
        "DOWNLOAD_DELAY": 2,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
    }
)

c.crawl(AmpRevSpider)
c.start()