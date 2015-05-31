import csv
import re
import json
import urllib.request

import xlrd
from bs4 import BeautifulSoup


results = json.loads(urllib.request.urlopen("https://www.kimonolabs.com/api/9qw4dthk?apikey=Bp3aV3DB8QZXf21wy1rx5w8Wy8o35BcM").read().decode("utf-8"))
release_no = 9 # 0~9 in last 10
url = results['results']['collection1'][release_no]['property1']['href']


### download xls
#"http://www.phldcc.gov.tw/ch/home.jsp?mserno=201110130001&serno=201110130001&contlink=ap\\\/unit1_view.jsp&dataserno=201505260002"
page = urllib.request.urlopen(url)
soup = BeautifulSoup(page)
text1 = soup.find_all(href=re.compile(".xls"))[0]
text2 = str(text1).split('.xls')[0][-15:]
url_download = '%s%s%s' % (
    'http://www.phldcc.gov.tw/uploaddowndoc?file=/pubpenghu/unitdata/',
    text2,
    '.xls&flag=doc')
file_name = '%s.xls' % text2
urllib.request.urlretrieve(url_download, file_name)


### to csv
workbook = xlrd.open_workbook(file_name)
worksheet = workbook.sheet_by_index(0)
num_rows = worksheet.nrows - 1
input_data = [['animal_opendate', 'animal_found_place', 'animal_pedigree',
    'animal_sex', 'animal_bodytype', 'animal_colour', 'animal_chip_number',
    'animal_entry_reason']]
curr_row = -1
while curr_row < num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    tmp_input_data = [x.value for x in row]
    input_data += [tmp_input_data]

csv_name = '%s.csv' % text2
with open(csv_name, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for data in input_data:
            writer.writerow(data)
