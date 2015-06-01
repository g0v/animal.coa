#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import mmap
import os

to_crawl_announcement_list_file_name = 'to_crawl_announcement_list'
crawled_announcement_list_file_name = 'crawled_announcement_list'
base_url = 'http://www.kinmen.gov.tw'

class AnnouncementListSpider(scrapy.Spider):
    name = 'announcement_list_spider'
    allowed_domains = 'kinmen.gov.tw'
    page_count = 17  # crawl the most recent [page_count] pages
    start_urls = []

    for page in xrange(page_count):
        start_urls.append('http://www.kinmen.gov.tw/Layout/sub_A/News_NewsListAll.aspx?frame=93&DepartmentID=41&LanguageType=1&CategoryID=266&Page='+str(page+1))

    # touch to_crawl_list, crawled_list if not exist
    if not os.path.isfile(to_crawl_announcement_list_file_name):
        with open(to_crawl_announcement_list_file_name, 'a'):
            os.utime(to_crawl_announcement_list_file_name, None)
    if not os.path.isfile(crawled_announcement_list_file_name):
        with open(crawled_announcement_list_file_name, 'a'):
            os.utime(crawled_announcement_list_file_name, None)

    def parse(self, response):

        to_crawl_announcement_list_file = open(to_crawl_announcement_list_file_name, 'a+')
        crawled_announcement_list_file = open(crawled_announcement_list_file_name, 'r')

        # find announcement url and write to to_crawl_announcement_list if not present in crawled_announcement_list
        for sel in response.xpath(u'//td[@class="linkitem"]/a[contains(@title, "領養")]/@href'):
            announcement_path = sel.extract()
            announcement_url = base_url + announcement_path

            if os.stat(crawled_announcement_list_file_name).st_size == 0:
                print >> to_crawl_announcement_list_file, announcement_url
            else:
                f = mmap.mmap(crawled_announcement_list_file.fileno(), 0, access=mmap.ACCESS_READ)
                if f.find(announcement_path) == -1:
                    print >> to_crawl_announcement_list_file, announcement_url

        to_crawl_announcement_list_file.close()
        crawled_announcement_list_file.close()
