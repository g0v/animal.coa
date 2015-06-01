import os
import csv

for root, subFolders, files in os.walk('./'):
    for filename in files:
        if filename.endswith('.csv'):
            filepath = os.path.join(root, filename)
            with open(filepath, 'r') as csv_file:
                reader = csv.reader(csv_file)
                columns_count = 0
                for row in reader:
                    if row[0]=='id':
                        columns_count = len(row)
                    else:
                        if len(row) != columns_count:
                            print(filename)