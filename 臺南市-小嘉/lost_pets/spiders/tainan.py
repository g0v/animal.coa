# coding=utf-8
import scrapy
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
import csv
import os.path

class Tainan(scrapy.Spider):
  name = "tainan"
  allowed_domains = ["asms.wsn.com.tw"]
  start_urls = ["http://asms.wsn.com.tw/TN/ieland/el_LoseList.aspx?Page=1"]

  def __init__(self):
    self.pets_csv_path = 'lost.csv'
    self.pets = []
    self.history_pet_urls = []
    if os.path.isfile(self.pets_csv_path) :
      with open(self.pets_csv_path) as file:
        for row in csv.DictReader(file):
          self.history_pet_urls.append(row['網頁連結'])

    dispatcher.connect(self.spider_closed, signals.spider_closed)

  def spider_closed(self, spider):
    fieldnames = ['收容編號','進所日期','捕獲鄉鎮市','進所原因','年齡','性別','毛色','品種','體型','絕育','晶片號碼','位置','籠舍','照片連結','網頁連結']
    csvFile = open(self.pets_csv_path, 'ab')
    csvWriter = csv.DictWriter(csvFile, fieldnames=fieldnames)
    if len(self.history_pet_urls) == 0:
      csvWriter.writeheader()
    self.pets.sort(key=lambda item: item['進所日期'])
    for petDict in self.pets:
      csvWriter.writerow(petDict)
    csvFile.close()

  def parse(self, response):
    pages_count = response.xpath('//span[@id="showpage"]/text()').extract()[0]
    for i in xrange(1,int(pages_count)+1):
      index_url = "http://asms.wsn.com.tw/TN/ieland/el_LoseList.aspx?Page="+str(i)
      yield scrapy.Request(index_url, callback=self.parse_index)

  def parse_index(self, response):
    for div in response.xpath('//div[@class="divAnimalListTxt"]'):
      detail_path = div.xpath('ul/li')[-1].xpath('a/@href').extract()[0].lstrip('..')
      detail_url = "http://asms.wsn.com.tw/TN"+detail_path
      if not detail_url in self.history_pet_urls:
        yield scrapy.Request( detail_url, callback=self.parse_detail )

  def parse_detail(self, response):
    petDict = {}
    cells = response.xpath('//div[@id="main"]/table')[0].xpath('tr')[0].xpath('td')
    petDict['網頁連結'] = response.url
    petDict['照片連結'] = "http://asms.wsn.com.tw/TN"+cells[0].xpath('img/@src').extract()[0].lstrip('..')
    for line in cells[1].xpath('text()').extract():
      data = line.strip().encode('utf-8').split('：')
      if len(data) >= 2:
        petDict[data[0]] = data[1]

    self.pets.append(petDict)

