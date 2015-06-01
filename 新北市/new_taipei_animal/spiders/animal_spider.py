#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import urlparse
import os
import csv
import fileinput
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

BASE_URL = "http://www.ahiqo.ntpc.gov.tw/"
to_crawl_list_file_name = 'to_crawl_list'
crawled_list_file_name = 'crawled_list'
to_crawl_urls = []
crawled_urls = []
csv_row_titles = [u'id', u'病歷號碼', u'毛　　色', u'體　　型', u'品　　種', u'性　　別', u'年　　齡', u'籠　　號', u'進所原因', u'拾獲地點', u'收容日期', u'開放認養日期', u'晶片號碼', u'頸牌號碼', u'相片網址', u'資料來源']

with open(to_crawl_list_file_name, 'rw') as urls:
        for url in urls:
            to_crawl_urls.append(url)

with open(crawled_list_file_name, 'rw') as urls:
    for url in urls:
        crawled_urls.append(url)

class AnimalSpider(scrapy.Spider):
    name = 'animal_spider'
    allowed_domains = ["ahiqo.ntpc.gov.tw"]
    start_urls = []
    for url in to_crawl_urls:
        start_urls.append(url)

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        to_crawl_list_file = open(to_crawl_list_file_name, 'w')
        crawled_list_file = open(crawled_list_file_name, 'w')

        for url in to_crawl_urls:
            to_crawl_list_file.write(url)

        for url in crawled_urls:
            crawled_list_file.write(url)

        to_crawl_list_file.close()
        crawled_list_file.close()


    def parse(self, response):
        query = urlparse.urlparse(response.url).query
        params = urlparse.parse_qs(query)

        # raw datas
        animal_id = params['id'][0]
        detail_url = response.url
        image_path = response.xpath('//ul[@class="galThumb"]//img/@src').extract()
        image_url = BASE_URL+image_path[0] if image_path else None
        animal_data = response.xpath('//div[contains(@class, "galInfoBox")]/ul/li/text()').extract()
        for i in range(len(animal_data)):
            animal_data[i] = animal_data[i].split(u"\uff1a")    # separated by u"："
            animal_data[i] = [animal_data[i][0], animal_data[i][-1]]    # solve edge case: "頸牌號碼：：***"

        # transform animal_data from list to dictionary
        animal_data_dict = {}
        for each in animal_data:
            animal_data_dict[each[0]] = each[1]
        self.write_item_to_corresponding_csv(animal_id, detail_url, image_url, animal_data_dict)

    def write_item_to_corresponding_csv(self, animal_id, detail_url, image_url, animal_data_dict):
        date_string = animal_data_dict[u'收容日期']
        del animal_data_dict[u'開放認養日期']

        # create csv file with title if not exists
        if not os.path.exists(date_string):
            os.makedirs(date_string)
            with open(date_string+'/'+date_string+'.csv', 'a+') as csv_file:
                csv_writer = csv.writer(csv_file)

                # encode with utf-8
                for i in range(len(row_title)):
                    csv_row_titles[i] = csv_row_titles[i].encode('utf-8')

                csv_writer.writerow(csv_row_titles)

        # generate value list to write into csv
        with open(date_string+'/'+date_string+'.csv', 'a+') as csv_file:
            csv_writer = csv.writer(csv_file)
            row_value = [animal_id]
            for row_title in csv_row_titles[1:-2]:
                if row_title in animal_data_dict:
                    row_value.append(animal_data_dict[row_title])
                else:
                    row_value.append('')
            row_value.append(image_url)
            row_value.append(detail_url)

            # encode with utf-8
            for i in range(len(row_value)):
                row_value[i] = row_value[i].encode('utf-8') if row_value[i] else row_value[i]

            csv_writer.writerow(row_value)

        for url in to_crawl_urls:
            if 'id='+animal_id in url:
                crawled_urls.append(url)
                to_crawl_urls.remove(url)
                break
