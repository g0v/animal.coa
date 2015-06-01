import urllib2
import os
import csv
import xlrd

files_dir = 'files/'
to_download_list = []
downloaded_list = []
to_download_list_file_name = 'to_download_list'
downloaded_list_file_name = 'downloaded_list'

# read file into list
with open(to_download_list_file_name, 'rw') as urls:
    for url in urls:
        to_download_list.append(url)

with open(downloaded_list_file_name, 'rw') as urls:
    for url in urls:
        downloaded_list.append(url)

def download(url):
    # create directory if not exists
    if not os.path.exists(os.path.dirname(files_dir)):
        os.makedirs(os.path.dirname(files_dir))

    # open connection
    try:
        u = urllib2.urlopen(url)
    except URLError, e:
        print("Error when downloading: " + url)
        return False

    meta = u.info()

    # deciding file_name
    file_name = ''
    if 'Content-Disposition' in meta and 'filename=' in meta['Content-Disposition'] and len(meta['Content-Disposition'].split('filename=')[-1])>0:
        original_filename = meta['Content-Disposition'].split('filename=')[-1].split('.')[0]
        original_fileext = meta['Content-Disposition'].split('filename=')[-1].split('.')[-1]
        file_name = original_filename[0:7]+'.'+original_fileext
    else:
        fiel_name = url.split('/')[-1].split('=')[-1].rstrip()
    print("file_name = "+file_name)

    # download file
    f = open(files_dir+file_name, 'wb')
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()
    return True

def process_unclassified_files():

    # get all unclassified files
    filenames = next(os.walk(files_dir))[2]

    for filename in filenames:
        # create date_string folder (usually named with data string)
        date_string = filename.split('.')[0]
        if not os.path.exists(files_dir+date_string):
            os.makedirs(files_dir+date_string)

        # read each xls file and transform to corresponding csv file
        workbook = xlrd.open_workbook(files_dir+filename)

        # write xls to date_string/ in csv format (only fow first worksheet in the xls)
        worksheets = workbook.sheet_names()
        for worksheet_name in worksheets:
            worksheet = workbook.sheet_by_name(worksheet_name)

            if not os.path.isfile(files_dir+date_string+'/'+date_string+'.csv'):
                with open(files_dir+date_string+'/'+date_string+'.csv', 'a+') as csv_file:
                    csv_writer = csv.writer(csv_file)

                    # real content starts from line4 (index = 3)
                    for row_number in xrange(3, worksheet.nrows):
                        row_value = worksheet.row_values(row_number)
                        csv_writer.writerow([a.encode('utf-8') for a in row_value])

        # move xls file to date_string folder
        os.rename(files_dir+filename, files_dir+date_string+'/'+filename)



def main():
    # download urls from to_download_list
    for url in to_download_list[:]:
        success = download(url)
        if success:
            to_download_list.remove(url)
            downloaded_list.append(url)

    # write lists to file
    to_download_list_file = open(to_download_list_file_name, 'wb')
    for url in to_download_list:
        to_download_list_file.write(url)
    to_download_list_file.close()

    downloaded_list_file = open(downloaded_list_file_name, 'wb')
    for url in downloaded_list:
        downloaded_list_file.write(url)
    downloaded_list_file.close()

    # classify files and tranform to csv
    process_unclassified_files()

main()
