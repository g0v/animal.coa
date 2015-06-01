# -*- coding: utf-8 -*-
import os
import csv
import re
import sqlite3
import collections
from twisted.web.client import getPage, downloadPage
from twisted.internet import reactor
from twisted.internet import defer
from urlparse import urljoin, parse_qs
from datetime import date

from bs4 import BeautifulSoup

html_path = "htmls"
image_url = "http://www.klaphio.gov.tw/uploadfiles/cd/"
base_url = "http://www.klaphio.gov.tw/receiving_notice.php"
data_schema = collections.OrderedDict((
    (u"進所日期：", "enter_date"),
    (u"進所原因：", "reason"),
    (u"性別：", "gender"),
    (u"毛色：", "color"),
    (u"品種：", "variety"),
    (u"體型：", "body_type"),
    (u"晶片號碼：", "wafer_number"),
    (u"來源地點：", "source")
))


class DB(object):
    def __init__(self, table_name=None):
        if not table_name:
            raise Exception("table name invalid")

        self.conn = sqlite3.connect('animal.db')
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.table_name = table_name
        self.github_photo_url = "https://g0v.github.io/animal.coa/%E5%9F%BA%E9%9A%86%E5%B8%82/"

        try:
            sql = "CREATE TABLE %s (id, photo, %s);" % (self.table_name, ",".join(data_schema.values()))
            self.cursor.execute(sql)
            print "table %s created." % table_name
        except Exception as e:
            print e
            pass

    def get_animal(self, animal_id):
        sql = "SELECT * FROM %s WHERE id=?;" % self.table_name
        self.cursor.execute(sql, (animal_id,))
        return self.cursor.fetchone()

    def find_all(self):
        sql = "SELECT * FROM %s ORDER BY id;" % self.table_name
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def count_rows(self):
        sql = "SELECT count(*) as count FROM %s;" % self.table_name
        self.cursor.execute(sql)
        return self.cursor.fetchone()["count"]

    def save(self, data):
        try:
            print "save data to db, id=", data.get("id")
            sql = "INSERT INTO %s (id, photo, color, enter_date, source, gender, reason, wafer_number, body_type, variety) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);" % self.table_name
            self.cursor.execute(sql, (
                data.get("id"),
                data.get("photo"),
                data.get("color"),
                data.get("enter_date"),
                data.get("source"),
                data.get("gender"),
                data.get("reason"),
                data.get("wafer_number"),
                data.get("body_type"),
                data.get("variety")
            ))
            self.conn.commit()
        except Exception as e:
            print e
            pass

    def to_csv(self):
        with open("all.csv", 'wb') as csvfile:
            print "Exported csv"
            spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(["來源地點", "入園日期", "品種", "備註", "性別", "收容原因", "晶片號碼", "毛色", "體型", "相片網址"])
            for row in self.find_all():
                photo_url = os.path.join(self.github_photo_url, row["enter_date"], row["photo"].split('/')[-1].lower())
                y, m, d = tuple(map(int, row["enter_date"].split('-')))
                enter_date = "%d年%d月%d日" % (y - 1911, m, d)
                data = [
                    row["source"].encode('utf-8'),
                    enter_date,
                    row["variety"].encode('utf-8'),
                    u"",
                    row["gender"].encode('utf-8'),
                    row["reason"].encode('utf-8'),
                    row["wafer_number"].encode('utf-8'),
                    row["color"].encode('utf-8'),
                    row["body_type"].encode('utf-8'),
                    photo_url
                ]
                spamwriter.writerow(data)


class Crawler(object):
    def __init__(self):
        self.count = 0
        self.db = DB(table_name="keelung")
        self.page_content = []
        self.detail_content = []
        self.start()

    def start(self):
        print "Satrt fetching index page."
        d = self.queue_page(1)
        self.start_worker([d], self.queue_all_pages)

    def start_worker(self, tasks, cb=None):
        defer.DeferredList(tasks).addCallback(cb)

    def queue_page(self, page):
        d = self.fetch_page(page)
        d.addCallback(self.save_html)
        return d

    def stop(self, _):
        self.db.to_csv()
        print "All %d items done." % self.db.count_rows()
        reactor.stop()

    @defer.inlineCallbacks
    def fetch_page(self, page):
        print "Fetching page %d" % page

        response = yield getPage(
            base_url,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            method="POST",
            postdata="page=%d" % page
        )
        response = response.strip()

        self.page_content.append(response)
        defer.returnValue((response, "page-%d.html" % page))

    def queue_all_pages(self, cb_state=None):
        tasks = []
        content = self.page_content[0]

        soup = BeautifulSoup(content)
        total_page_html = soup.find('a', href="javascript:goPage('5');").get('href')
        total_page = int(re.match(r".+goPage\(\'(\d+)\'\)", total_page_html).group(1))

        print "All %d pages. start fetch..." % total_page
        for page in range(2, total_page + 1):
            d = self.queue_page(page)
            tasks.append(d)

        self.start_worker(tasks, cb=self.queue_details)

    @defer.inlineCallbacks
    def fetch_detail_page(self, url, animal_id):
        try:
            with open(os.path.join(html_path, "detail-page-%d.html" % animal_id), 'r') as f:
                print "use detail-page-%d.html cached file." % animal_id
                response = f.read()
        except IOError:
            print "Fetching detail page, id =", animal_id
            response = yield getPage(
                urljoin(base_url, url),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                method="POST"
            )
            response = response.strip()

        self.detail_content.append(response)
        defer.returnValue((response, "detail-page-%d.html" % animal_id))

    def save_html(self, data):
        content, html_name = data
        with open(os.path.join(html_path, html_name), 'w') as f:
            f.write(content)

        return content

    def queue_details(self, cb_state=None):
        tasks = []
        for content in self.page_content:
            soup = BeautifulSoup(content)
            animal_link_list = soup.find("ol", class_="search_img_list").find_all("li")
            animal_link_list = [l.find('a').get('href') for l in animal_link_list]

            for link in animal_link_list:
                [animal_id] = parse_qs(link.split('?')[-1]).get('id')
                d = self.fetch_detail_page(link, int(animal_id))
                d.addCallback(self.save_html)
                d.addCallback(self.extract_detail, animal_id)
                tasks.append(d)

        self.start_worker(tasks, cb=self.download_all_images)

    def extract_detail(self, content, animal_id):
        if self.db.get_animal(animal_id):
            print 'Animal data exists, id=', animal_id
            return

        soup = BeautifulSoup(content)
        data = {
            "id": animal_id
        }

        infos = soup.find("div", class_="word").find_all("li")
        for info in infos:
            title = info.find("span").contents[0]
            title = title.replace(" ", "")
            if title in data_schema.keys():
                animal_info = ""
                try:
                    animal_info = info.contents[1]
                except:
                    pass

                data[data_schema[title]] = animal_info

        parsed_date = tuple(map(int, data['enter_date'].split('-')))
        y, m, d = parsed_date
        data['enter_date'] = date(y + 1911, m, d).strftime("%Y-%m-%d")

        img_src = soup.find("div", class_="photo").select("img")[0].get('src').split('/')[-1]
        data["photo"] = image_url + img_src

        self.db.save(data)

    def download_all_images(self, cb_state=None):
        print "Downloading all iamges..."
        tasks = []
        for row in self.db.find_all():
            save_folder = row['enter_date']
            photo_url = str(row["photo"])
            photo_name = photo_url.split('/')[-1]
            filename, ext = os.path.splitext(photo_name)
            save_name = filename + ext.lower()
            ensure_directories(save_folder)

            save_path = os.path.join(save_folder, save_name)
            if not os.path.exists(save_path):
                d = downloadPage(photo_url, save_path)
                tasks.append(d)

        self.start_worker(tasks, cb=self.stop)


def ensure_directories(path):
    if not os.path.exists(path):
        os.makedirs(path)

if __name__ == "__main__":
    ensure_directories(html_path)
    Crawler()
    reactor.run()
