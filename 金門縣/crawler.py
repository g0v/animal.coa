# -*- coding: utf-8 -*-
# 用gevent寫到一半想試試concurrent futures, 所以mix了... XD
import concurrent.futures
import os
import cgi
import shutil
import re
from urlparse import urljoin, parse_qs

from gevent import monkey; monkey.patch_all()
import gevent
import requests
from bs4 import BeautifulSoup

html_path = "htmls"
file_path = "files"
domain = "http://www.kinmen.gov.tw"
base_url = domain + "/Layout/sub_A/News_NewsListAll.aspx?CategoryID=266&Keyword=&frame=93&DepartmentID=41&LanguageType=1"

news_content = []

for path in [html_path, file_path]:
    if not os.path.exists(path):
        os.makedirs(path)

def start_workers(jobs):
    gevent.wait(jobs)

def save_html(filename, content):
    with open(os.path.join(html_path, filename), 'w') as f:
        f.write(content)

def fetch_page(page=1):
    r = requests.get(base_url + '&Page=%d' % page)
    content = r.text.encode('utf-8').strip()
    save_html("page-%d.html" % page, content)
    return content

def fetch_news_page(url):
    [news_id] = parse_qs(url.split('?')[-1])["NewsID"]
    news_id = int(news_id)

    try:
        with open(os.path.join(html_path, "news-%d.html" % news_id)) as f:
            content = f.read()
            soup = BeautifulSoup(content)
            if soup.find('title').contents[0] == u".:: Astrill Error ::.":
                raise IOError
    except IOError:
        r = requests.get(url)
        content = r.text.encode('utf-8').strip()
        save_html("news-%d.html" % news_id, content)

    news_content.append(content)

def download_file(url):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        _, obj = cgi.parse_header(r.headers['content-disposition'])
        with open(os.path.join(file_path, obj['filename']), 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

print "Fetching index page..."
content = fetch_page()

# fetch all pages
print "Fetching all pages..."
soup = BeautifulSoup(content)
[total_page] = parse_qs(soup.find("div", class_="tfood").find_all('a')[-1].get('href'))['Page']
start_workers([gevent.spawn(fetch_page, i) for i in range(2, int(total_page) + 1)])

def extra_news_links(filename, stored=[]):
    with open(os.path.join(html_path, filename), 'r') as f:
        content = f.read()

    soup = BeautifulSoup(content)
    links = soup.find("table", id="ctl00_ContentPlaceHolder1_News_ListAllPageGridView1_GridView1").find_all("a")
    for link in links:
        if u"踴躍領養" in link.contents[0]:
            stored.append(urljoin(domain, link.get('href')))

print "Extract all news link..."
news_links = []
for pagefile in next(os.walk(html_path))[2]:
    if not pagefile.startswith('page'):
        continue

    extra_news_links(pagefile, news_links)

print "Fetch all news page..."
start_workers([gevent.spawn(fetch_news_page, link) for link in news_links])

print "Fetch all news attached files..."
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Start the load operations and mark each future with its URL
    urls = {}
    for news in news_content:
        soup = BeautifulSoup(news)
        try:
            file_url = soup.find("div", id="page_matter").find("a").get('href')
        except AttributeError:
            print soup

        urls[executor.submit(download_file, file_url)] = file_url

    for future in concurrent.futures.as_completed(urls):
        url = urls[future]
        print url

print 'Done'
