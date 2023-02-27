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
'''This sets the index to the ticker, so that we can call the stock by its ticker, not the index number'''
companyData = companyData.set_index('ticker') 

#print(companyData1)
# Add zeros in front of cik_str
companyData['cik_str'] = companyData['cik_str'].astype(str).str.zfill(10)

#print(companyData[0:2])

# cik = companyData[0:5].cik_str[0:5]

'''Prompt the user for which Stock ticker they want'''
ticker = input("Stock ticker: ")

#print(companyData[0:1])
company = companyData.cik_str[ticker]  #changed the variable name from MSFT to company

companyConcept = requests.get(
    (f'https://data.sec.gov/api/xbrl/companyconcept/CIK{company}'
     f'/us-gaap/Assets.json'), headers=header)


# review data
print(companyConcept.json().keys())
#print(companyConcept.json()['units'])
#print(companyConcept.json()['units'].keys())
#   print(companyConcept.json()['units']['USD'])
#   print(companyConcept.json()['units']['USD'][0])

list1 = companyConcept.json()['units']['USD']
print(f"{companyConcept.json()['entityName']} (Total Assets):")

# Previous year's value stored. Initially this is set to zero, because first element does not have a previous
prev_year = 0

for key in list1:
    if '10-K/A' not in key['form']:
        if 'frame' not in key:
            if '10-K' in key['form']:
                if key['val'] != prev_year:  # This if statement checks if the previous year's value is NOT equal to current year's value
                    print(key['fy'], key['val'])
                    prev_year = key['val']  # set the current value to previous, to prepare for next key in for loop

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
