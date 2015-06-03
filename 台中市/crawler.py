#! /usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import codecs
import subprocess
import hashlib
import urllib
from urlparse import urljoin
from scrapy.selector import Selector


def take_first(l):
    ret = l[0] if l else ''
    return ret

urls = {'keep': 'http://www.animal.taichung.gov.tw/lp.asp?CtNode=3725&CtUnit=1688&BaseDSD=58&mp=119020&nowPage=1&pagesize=1000', 'adopt': 'http://www.animal.taichung.gov.tw/lp.asp?CtNode=3724&CtUnit=1687&BaseDSD=57&mp=119020&htx_iHave=N&nowPage=1&pagesize=1000'}
date = subprocess.check_output('date +"%Y-%m-%d"', shell=True).strip()
for category, url in urls.items():
    file_name = '{date}-{category}'.format(date=date, category=category)
    cmd = 'mkdir -p {date} && wget -nc -O {file_name}.html "{url}"'.format(date=date, file_name=file_name, url=url)
    subprocess.call(cmd, shell=True)
    tree = Selector(text=codecs.open('%s.html' % file_name, 'r', encoding='utf-8').read(), type="html")
    tables = tree.xpath('//section[@class="list"]/ul/li/table')
    with open('%s.csv' % file_name, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
        keys = [x.encode('utf-8') for x in tables[0].xpath('tr/th/text()').extract()]
        keys.append(u'照片'.encode('utf-8'))
        writer.writerow(keys)
        for table in tables:
            values = [take_first(td.xpath('descendant-or-self::text()').extract()).encode('utf-8') for td in table.xpath('tr/td')]
            img_src = table.xpath('following-sibling::figure/a/img/@src').extract()[0].encode('utf8')
            img_url = urljoin(url, urllib.quote(img_src))
            img_hash = hashlib.sha1(img_src).hexdigest()
            img_path = '%s/%s.jpg' % (date, img_hash)
            cmd = 'wget -nc -O %s "%s"' % (img_path, img_url)
            subprocess.call(cmd, shell=True)
            values.append('https://g0v.github.io/animal.coa/%E5%8F%B0%E4%B8%AD%E5%B8%82/{path}'.format(path=img_path))
            writer.writerow(values)
