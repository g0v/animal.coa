# animal.coa - 金門縣

```bash
# gevent and future.concurrent
python crawler.py

ll files/*.xls | wc -l

# xls to csv (LiberOffice required)
pip install unoconv
unoconv -f csv files/*.xls

ll files/*.csv | wc -l

# extract all csv to all.csv
python extract.py
```
