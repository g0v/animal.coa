# -*- coding: utf-8 -*-
# Extract all csv to all.csv
import os
import operator
import csv
import collections
import re

rows = []

for csvfile in next(os.walk('files'))[2]:
    if not csvfile.endswith('csv'):
        continue

    with open('files/' + csvfile, 'rb') as f:
        csv_reader = csv.reader(f, delimiter=' ', quotechar='|')
        for row in csv_reader:
            if re.match('\d+-.+', row[0]):
                result = row[0].split(',')

                # 少"年紀"
                if len(result) == 11:
                    result.insert(5, "")

                if len(result) != 12:
                    result += [''] * (12 - len(result))

                rows.append(result)

sortedrows = sorted(rows, key=operator.itemgetter(0), reverse=False)

with open("all.csv", 'wb') as csvfile:
    print "Exported csv"
    csv_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(["編號", "拾獲地點", "送交單位", "動物類別", "品種", "年紀", "體型", "毛色", "動物性別", "公告時間", "晶片號碼", "備註"])
    csv_writer.writerows(sortedrows)
