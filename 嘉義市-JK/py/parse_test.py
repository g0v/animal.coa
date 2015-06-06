from html.parser import HTMLParser
from urllib.request import urlopen  
from urllib import parse
import csv

class MyHTMLParser(HTMLParser):
    my_animal = []
    def handle_starttag(self, tag, attrs):
        if tag == "img" and attrs[0][1].split(r'/')[1]=='upload' and len(attrs[0][1].split(r'banner')) < 2:
            print("Encountered a start tag:", tag, 'http://www.dog.dias.com.tw' + attrs[0][1])
            album_file = 'http://www.dog.dias.com.tw' + attrs[0][1]               
            self.my_animal.append(album_file)
        with open('eggs.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=' ', quoting=csv.QUOTE_NONE)
            for ani in self.my_animal:                    
                spamwriter.writerow(ani)
    def handle_data(self, data):
        if len(data)==10 and data[4]=="-":
            print(data)
    def getLinks(self, url):
        self.links = []
        self.baseUrl = url
        response = urlopen(url)
        if response.getheader('Content-Type')=='text/html':
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)

parser = MyHTMLParser()
parser.getLinks("http://www.dog.dias.com.tw/index.php?op=announcement&page=1")
