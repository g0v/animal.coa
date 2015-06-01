# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewTaipeiAnimalItem(scrapy.Item):
    animal_id = scrapy.Field()
    detail_url = scrapy.Field()
    image_url = scrapy.Field()
    data = scrapy.Field()
