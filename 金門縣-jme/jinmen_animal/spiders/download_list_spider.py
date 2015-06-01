#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import mmap
import os
import urlparse
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

to_crawl_announcement_list_file_name = 'to_crawl_announcement_list'
crawled_announcement_list_file_name = 'crawled_announcement_list'
to_download_list_file_name = 'to_download_list'
downloaded_list_file_name = 'downloaded_list'
base_url = 'http://www.kinmen.gov.tw'

to_crawl_announcement_list = []
with open(to_crawl_announcement_list_file_name) as urls:
    for url in urls:
        to_crawl_announcement_list.append(url)
crawled_announcement_list = []
with open(crawled_announcement_list_file_name) as urls:
    for url in urls:
        crawled_announcement_list.append(url)
to_download_list = []
with open(to_download_list_file_name) as urls:
    for url in urls:
        to_download_list.append(url)
downloaded_list = []
with open(downloaded_list_file_name) as urls:
    for url in urls:
        downloaded_list.append(url)

class DownloadListSpider(scrapy.Spider):
    name = 'download_list_spider'
    allowed_domains = 'kinmen.gov.tw'
    start_urls = []
    with open(to_crawl_announcement_list_file_name, 'r') as urls:
        for url in urls:
            start_urls.append(url)

    # touch to_download_list, downloaded_list if not exist
    if not os.path.isfile(to_download_list_file_name):
        with open(to_download_list_file_name, 'a'):
            os.utime(to_download_list_file_name, None)
    if not os.path.isfile(downloaded_list_file_name):
        with open(downloaded_list_file_name, 'a'):
            os.utime(downloaded_list_file_name, None)

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        to_crawl_announcement_list_file = open(to_crawl_announcement_list_file_name, 'w')
        crawled_announcement_list_file = open(crawled_announcement_list_file_name, 'w')
        for url in to_crawl_announcement_list:
            to_crawl_announcement_list_file.write(url)
        for url in crawled_announcement_list:
            crawled_announcement_list_file.write(url)
        to_crawl_announcement_list_file.close()
        crawled_announcement_list_file.close()

        to_download_list_file = open(to_download_list_file_name, 'w')
        downloaded_list_file = open(downloaded_list_file_name, 'w')
        for url in to_download_list:
            to_download_list_file.write(url+'\n')
        for url in downloaded_list:
            downloaded_list_file.write(url+'\n')
        to_download_list_file.close()
        downloaded_list_file.close()

    def parse(self, response):

        # update to_crawl_announcement_list and crawled_announcement_list
        query = urlparse.urlparse(response.url).query
        params = urlparse.parse_qs(query)
        news_id = params['NewsID'][0]
        for url in to_crawl_announcement_list[:]:
            if 'NewsID='+news_id in url:
                crawled_announcement_list.append(url)
                to_crawl_announcement_list.remove(url)
                break

        # find download url and write to to_download_list if not present in downloaded_list
        for sel in response.xpath(u'//a[contains(text(), "收容公告")]/@href'):
            download_url = sel.extract()
            if download_url not in downloaded_list:
                print(download_url)
                to_download_list.append(download_url)
