#Get acces to API
import requests
header = {'User-Agent': "mr.muffin235@gmail.com"}
companyTickers = requests.get("https://www.sec.gov/files/company_tickers.json", headers=header)

#Find data and assign ticker symbol to cik#
import pandas as pd
T_list = companyTickers.json().values() #Turn data in a dictionary
symbol = input('Enter company ticker symbol: ').upper()
for info in T_list:
    if symbol == info['ticker']:
        new = info['cik_str'] #if there is a match assign cik# to a new variable
        print(f'{new:010d}') #format cik# with leading zeros (length of 10)
