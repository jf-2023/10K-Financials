import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import requests
header = {'User-Agent': "mr.muffin235@gmail.com"}
companyTickers = requests.get("https://www.sec.gov/files/company_tickers.json",
                              headers=header)
#companyTickers.json() returns a dict of the company symbol, name, etc.
#.keys() returns the keys of the dict
#print(companyTickers.json().keys())
#print(companyTickers.json()['0']['cik_str'])
#print(companyTickers.json()['0']['cik_str'])

# Turn dict into dataframe
#companyData1 = pd.DataFrame(companyTickers.json())
# Format dict into nice dataframe
companyData = pd.DataFrame.from_dict(companyTickers.json(), orient='index')
#print(companyData1)
#print(companyData)
# Add zeros in front of cik_str
companyData['cik_str'] = companyData['cik_str'].astype(str).str.zfill(10)
#print(companyData['cik_str'])

#print(companyData[0:2])

# cik = companyData[0:5].cik_str[0:5]

#print(companyData[0:1])
MSFT = companyData.cik_str[1]
#print(AAPL)
companyConcept = requests.get(
    (f'https://data.sec.gov/api/xbrl/companyconcept/CIK{MSFT}'
     f'/us-gaap/Assets.json'), headers=header)


# review data
print(companyConcept.json().keys())
#print(companyConcept.json()['units'])
#print(companyConcept.json()['units'].keys())
#   print(companyConcept.json()['units']['USD'])
#   print(companyConcept.json()['units']['USD'][0])

list1 = companyConcept.json()['units']['USD']
print(f"{companyConcept.json()['entityName']} (Total Assets):")
for key in list1:
    if '10-K/A' not in key['form']:
        if 'frame' not in key:
            if '10-K' in key['form']:
                #print(key)
                print(key['fy'], key['val'])

'''
## Version 1
list1 = companyConcept.json()['units']['USD']
for i in list1:
    print(i)
    if '10-K' in i['form']:
        print('YAY!!!!')
    for j in i.values():
        print(j)
'''

# parse assets from single filing
#   companyConcept.json()['units']['USD'][0]['val']

'''
# get all filings data
assetsData = pd.DataFrame.from_dict((
               companyConcept.json()['units']['USD']))
# review data
print(assetsData)
assetsData.columns
assetsData.form
print(assetsData)
'''
'''
# get assets from 10Q forms and reset index
assets10Q = assetsData[assetsData.form == '10-K']
assets10Q = assets10Q.reset_index(drop=True)
print(assets10Q)
'''


#get html file of website and use regular expressions