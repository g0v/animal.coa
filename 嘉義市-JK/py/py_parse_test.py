# -*- coding: utf-8 -*-
from html.parser import HTMLParser
from urllib.request import urlopen  
from urllib import parse
import csv

class MyHTMLParser(HTMLParser):
    dict_tag = {'捕捉日期': 0, '捕捉地點': 1, '品種': 2, '性別': 3, '體型': 4, '捕捉來源': 5, '備註': 6, '晶片號碼': 7, '照片': 8}    
    each_animal_data=['無資料','無資料','無資料','無資料','無資料','無資料','無資料','無資料','無資料']   
    inner_dataset=[each_animal_data,each_animal_data,each_animal_data,each_animal_data,each_animal_data,each_animal_data]
    row_data=""
    start_key = 0
    i=1
    def handle_starttag(self, tag, attrs):
        if tag == "img" and attrs[0][1].split(r'/')[1]=='upload' and len(attrs[0][1].split(r'banner')) < 2:
            self.each_animal_data[self.dict_tag['照片']] = 'http://www.dog.dias.com.tw' + attrs[0][1]
    def parse_data(self, data):
        if len(data)==10 and data[4]=="-":
            self.each_animal_data[self.dict_tag['捕捉日期']] = data
        elif data[:5]=="捕捉地點：":
            self.each_animal_data[self.dict_tag['捕捉地點']] = data[5:len(data)]
        elif data[:3]=="品種：": 
            self.each_animal_data[self.dict_tag['品種']] = data[3:len(data)]
        elif data[:3]=="體型：": 
            self.each_animal_data[self.dict_tag['體型']] = data[3:len(data)]
        elif data[:3]=="性別：": 
            self.each_animal_data[self.dict_tag['性別']] = data[3:len(data)]
        elif data[:5]=="捕捉來源：": 
            self.each_animal_data[self.dict_tag['捕捉來源']] = data[5:len(data)]
        elif data[:3]=="備註：": 
            if "(晶片:" in data:
                self.each_animal_data[self.dict_tag['晶片號碼']] = data.split(":")[1][0:-1]
            self.each_animal_data[self.dict_tag['備註']] = data[3:len(data)]
    def handle_data(self, data):
        if self.start_key == 1:
            self.parse_data(data)
    def getLinks(self, url, data_set):       
        self.links = []
        self.baseUrl = url
        response = urlopen(url)
        if response.getheader('Content-Type')=='text/html':
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)
            data_set.extend(self.inner_dataset)
    def handle_comment(self,data):
        if data==" content start ":
            self.start_key= 0
            #for key,value in self.dict_tag.items():
                #self.each_animal_data[value]=key
            #self.inner_dataset[0]=self.each_animal_data
            #self.each_animal_data=['無資料','無資料','無資料','無資料','無資料','無資料','無資料','無資料','無資料']
        elif data==" box1 " and self.start_key==0:
            print(data,self.start_key)
            self.start_key=1
        elif data==" box1 " and self.start_key==1:           
            print(data,self.start_key)
            self.inner_dataset[self.i]=self.each_animal_data
            self.each_animal_data=['無資料','無資料','無資料','無資料','無資料','無資料','無資料','無資料','無資料']
            self.i+=1
        elif data==" content end " and self.start_key==1:
            print(data,self.start_key)            
            self.inner_dataset[5]=self.each_animal_data
            self.start_key= 0

f = open("eggs.csv",'w',encoding='utf-8')  
w = csv.writer(f, delimiter=',')      
w.writerow(['捕捉日期', '捕捉地點', '品種', '性別', '體型', '捕捉來源', '備註', '晶片號碼', '照片'])
f.close()
for i in range(7):
    aniset =[]
    parser = MyHTMLParser()
    parser.getLinks("http://www.dog.dias.com.tw/index.php?op=announcement&page="+str(i),aniset)
    print(aniset)
    f = open("eggs.csv",'a',encoding='utf-8')  
    w = csv.writer(f, delimiter=',')      
    w.writerows(aniset)
    f.close()