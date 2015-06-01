# -*- coding: utf-8 -*-
import os
import csv
import shutil
import re
import sqlite3
import collections
from urlparse import urlparse, urljoin, parse_qs
from datetime import date

from bs4 import BeautifulSoup
import requests

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
        self.cursor.execute("SELECT DISTINCT(enter_date) FROM %s;" % self.table_name)
        for (day,) in self.cursor.fetchall():
            with open('%s.csv' % day, 'wb') as csvfile:
                print "Export csv = %s.csv" % day
                spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow(["來源地點", "入園日期", "品種", "備註", "性別", "收容原因", "晶片號碼", "毛色", "體型", "相片網址"])
                sql = "SELECT * FROM %s WHERE enter_date = ? ORDER BY id;" % self.table_name
                self.cursor.execute(sql, (day,))
                for row in self.cursor.fetchall():
                    photo_url = os.path.join(self.github_photo_url, day, row["photo"].split('/')[-1].lower())
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


def ensure_directories(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_html(path, filename, content):
    with open(os.path.join(path, filename), 'w') as f:
        f.write(content)


def fetch_page(page=1, total=None):
    page = int(page)
    print "Fetching page %d" % page
    r = requests.post(base_url, {"page": page})
    content = r.text.encode('utf-8').strip()
    if r.status_code == 200:
        save_html(html_path, "page-%d.html" % page, content)

    if (page < total):
        fetch_page(page + 1, total=total)
    else:
        return content


def get_total_page(content):
    soup = BeautifulSoup(content)
    total_page_html = soup.find('a', href="javascript:goPage('5');").get('href')
    return int(re.match(r".+goPage\(\'(\d+)\'\)", total_page_html).group(1))


def download_image(filename, animal_id, save_path, save_name):
    if not os.path.exists(os.path.join(save_path, save_name)):
        print "downloading image, id=", animal_id
        ensure_directories(save_path)
        r = requests.get(image_url + filename, stream=True)
        if r.status_code == 200:
            with open(os.path.join(save_path, save_name), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
    else:
        print "photo exists, skip. %s/%s" % (save_path, save_name)


def fetch_detail_page(url, animal_id):
    try:
        with open(os.path.join(html_path, "detail-page-%d.html" % animal_id), 'r') as f:
            print "use detail-page-%d.html cached file." % animal_id
            content = f.read()
    except IOError:
        print "fetching detail page, id =", animal_id
        r = requests.get(urljoin(base_url, url))
        if r.status_code == 200:
            content = r.text.encode('utf-8').strip()
            save_html(html_path, 'detail-page-%d.html' % animal_id, content)

    return extract_detail_info(content)


def extract_detail_info(content):
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

    # download image
    img_src = soup.find("div", class_="photo").select("img")[0].get('src').split('/')[-1]
    data["photo"] = image_url + img_src

    filename, ext = os.path.splitext(img_src)
    save_path = data['enter_date']
    save_name = filename + ext.lower()

    download_image(img_src, animal_id, save_path, save_name)

    return data


def extract_animal_id(content):
    detail_url = "%s?%s" % (base_url, content.split('?')[-1])
    qs = parse_qs(urlparse(detail_url).query)
    [animal_id] = qs.get('id')
    return int(animal_id)

if __name__ == "__main__":
    ensure_directories(html_path)
    db = DB(table_name="keelung")

    result = fetch_page()
    total_pages = get_total_page(result)
    print "Total: %d pages" % total_pages
    fetch_page(2, total=total_pages)

    count = 0
    page_files = next(os.walk(html_path))[2]
    for page_file in page_files:
        if not page_file.startswith('page'):
            continue

        with open(os.path.join(html_path, page_file), 'r') as f:
            content = f.read()
            soup = BeautifulSoup(content)
            animal_link_list = soup.find("ol", class_="search_img_list").find_all("li")
            animal_link_list = [l.find('a').get('href') for l in animal_link_list]

            for link in animal_link_list:
                count += 1
                animal_id = extract_animal_id(link)

                animal = db.get_animal(animal_id)

                if animal:
                    print "animal id: %d exists, skip fetch" % animal_id
                    continue

                data = fetch_detail_page(link, animal_id)
                db.save(data)
    db.to_csv()
    print "All %d items." % count
