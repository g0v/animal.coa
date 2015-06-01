#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import mmap
import os

to_crawl_list_file_name = 'to_crawl_list'
crawled_list_file_name = 'crawled_list'

class ToCrawlListSpider(scrapy.Spider):
    name = 'to_crawl_list_spider'
    BASE_URL = "http://www.ahiqo.ntpc.gov.tw/"
    allowed_domains = ["ahiqo.ntpc.gov.tw"]
    pages_count = 10
    start_urls = []

    for i in range(pages_count): # given existing detail_url_list file, we only check the most recent [pages_count] pages
        start_urls.append("http://www.ahiqo.ntpc.gov.tw/adopt_list.php?page="+str(i+1))

    # touch to_crawl_list, crawled_list if not exist
    if not os.path.isfile(to_crawl_list_file_name):
        with open(to_crawl_list_file_name, 'a'):
            os.utime(to_crawl_list_file_name, None)
    if not os.path.isfile(crawled_list_file_name):
        with open(crawled_list_file_name, 'a'):
            os.utime(crawled_list_file_name, None)

    def parse(self, response):
        to_crawl_list_file = open(to_crawl_list_file_name, 'a+')
        crawled_list_file = open(crawled_list_file_name, 'r')
        for sel in response.xpath('//div[@class="galImg"]/a/@href'):
            animal_detail_path = sel.extract()
            if os.stat(crawled_list_file_name).st_size == 0:
                print >> to_crawl_list_file, BASE_URL+animal_detail_path
            else:
                s = mmap.mmap(crawled_list_file.fileno(), 0, access=mmap.ACCESS_READ)
                if s.find(animal_detail_path) == -1:
                    print >> to_crawl_list_file, BASE_URL+animal_detail_path

        to_crawl_list_file.close()
        crawled_list_file.close()
