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

        

        
        
########################################        
import pandas as pd
account = ['AssetsCurrent', 'Liabilities']
year = '2022'

fin_dict = {'Account': [a for a in account]}
for ticker in symbol_list:
    fin_dict[ticker] = []


for acc in account:
    companyFrames = requests.get((f'https://data.sec.gov/api/xbrl/frames/us-gaap/{acc}/USD/CY{year}Q4I.json'),
                                 headers=header)
    data = companyFrames.json()['data']
    count = 0
    for cik in cik_list:
        for data_list in data:
            if cik == data_list['cik']:
                num = format(data_list['val'], ',d')
                fin_dict[symbol_list[count]] += [num]
                count += 1
                break
print(fin_dict)

pd.set_option('display.max_columns', None)
fdata_DF = pd.DataFrame(fin_dict)
fdata_DF.set_index('Account', inplace=True)
z = fdata_DF.rename(index={'RetainedEarningsAccumulatedDeficit': 'RetainedEarnings'})
print(z)
