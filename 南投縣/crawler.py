#! /usr/bin/env python
# -*- coding: utf-8 -*-
import re
import csv
import codecs
import subprocess
import hashlib
import urllib
import requests
from urlparse import urljoin
from scrapy.selector import Selector


refs = [
    {
        'category': 'keep',
        'urls': ['http://adcc.nantou.gov.tw/introduce/leading.asp?id={AAF1647F-051F-47C0-BCFC-03E9C497E4D2}'],
        'header': [u'編號', u'入所', u'捕捉/拾獲地點', u'動物別', u'品種', u'性別', u'毛色特徵', u'身份註記', u'備註', u'照片']
    },
    {
        'category': 'adopt',
        'urls': ['http://adcc.nantou.gov.tw/introduce/leading.asp?id={F8D1EE49-C251-424F-B145-BA84F111E897}'],
        'header': [u'編號', u'品種', u'年齡', u'毛色', u'體型', u'性別', u'絕育狀況', u'醫療情形', u'性格/特質', u'照片']
    }
]

for ref in refs:
    r = requests.get(ref['urls'][0])
    tree = Selector(text=r.text, type='html')
    pages = tree.xpath('//select[@name="PageNo"]/option/@value').extract()
    ref['urls'].extend(['%s&PageNo=%s' % (ref['urls'][0], x) for x in pages[1:]])

date = subprocess.check_output('date +"%Y-%m-%d"', shell=True).strip()
for ref in refs:
    print ref['category']
    cmd = 'mkdir -p csv/{date} images/{date} html/{date}'.format(date=date)
    subprocess.call(cmd, shell=True)
    with open('csv/{date}/{category}.csv'.format(date=date, category=ref['category']), 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
        keys = [x.encode('utf-8') for x in ref['header']]
        writer.writerow(keys)
        for i in range(len(ref['urls'])):
            html_path = 'html/{date}/{category}-{i}.html'.format(date=date, category=ref['category'], i=i)
            cmd = 'wget -nc -O {html_path} "{url}"'.format(html_path=html_path, url=ref['urls'][i])
            subprocess.call(cmd, shell=True)
            tree = Selector(text=codecs.open(html_path, 'r', encoding='utf-8').read(), type="html")
            stories = tree.css('td[align="left"][valign="top"]').xpath('a/parent::td')
            for story in stories:
                lines = [x.strip() for x in story.xpath('.//text()').extract() if x.strip()]
                if ref['category'] == 'keep': # delete 公告照片僅供飼主辨識 column
                    del lines[2]
                # unexpect newline with content within headers
                line = []
                if len(lines) > (len(ref['header'])-1):
                    for j in range(2, len(lines)):
                        if re.search(':', lines[j]):
                            line.append(lines[j])
                    lines = line
                #
                row = [re.sub('^.*?:', '', line).encode('utf-8') for line in lines]
                img_src = story.xpath('.//img/@src').extract()[0].encode('utf8')
                img_url = urljoin(ref['urls'][i], img_src)
                img_hash = hashlib.sha1(img_src).hexdigest()
                img_path = 'images/%s/%s.jpg' % (date, img_hash)
                cmd = 'wget -nc -O %s "%s"' % (img_path, img_url)
                subprocess.call(cmd, shell=True)
                row.append('https://g0v.github.io/animal.coa/%E5%8D%97%E6%8A%95%E7%B8%A3/{path}'.format(path=img_path))
                writer.writerow(row)
