import pandas as pd
import requests
import time
import matplotlib.pyplot as plt
import seaborn as sns
start = time.perf_counter()

header = {'User-Agent': "mr.muffin235@gmail.com"}

def get_cik(symbol):
    companyTickers = requests.get("https://www.sec.gov/files/company_tickers.json", headers=header)
    T_list = companyTickers.json().values()
    for list1 in T_list:
        if list1['ticker'] == symbol:
            cik = list1['cik_str']
            return cik

def get_AccFY(acc, year, symbol):
    companyFrames = requests.get((f'https://data.sec.gov/api/xbrl/frames/us-gaap/{acc}/USD/CY{year}Q4I.json'), headers=header)
    frame = companyFrames.json()['data']
    frameDF = pd.DataFrame(frame)
    frameDF2 = frameDF.drop(columns=['accn', 'end', 'loc', 'entityName'])
    frameDF2.insert(loc=0, column=symbol, value=acc)
    frameDF2.rename(columns={'val': year}, inplace=True)
    x = frameDF2[frameDF2['cik'] == get_cik(symbol)]
    return x

acc_list = ['AssetsCurrent','Liabilities']

def getDF_acc(list, year, symbol):
    df_list = []
    for acc in list:
        i = get_AccFY(acc, year, symbol)
        df_list.append(i)
    newDF = pd.concat(df_list, ignore_index=True)
    return newDF

years_list = [2022, 2021, 2020, 2019, 2018, 2017, 2016]
def getDf_yrs(AccList, list, symbol):
    bs = getDF_acc(AccList, years_list[0], symbol)
    bs[years_list[0]] = bs[years_list[0]].astype(float)
    years_list.pop(0)
    for year in list:
        i = getDF_acc(AccList, year, symbol)
        i[year] = i[year].astype(float)
        bs = pd.merge(bs, i)
    bs.drop(columns='cik', inplace=True)
    return bs

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.options.display.float_format = '{:,}'.format

df = getDf_yrs(acc_list, years_list, 'META')
df2 = df.T
df2['Acid'] = df['AssetsCurrent'] / df['Liabilities']
print(df2)
#sns.lineplot(data=df)
#plt.show()

end = time.perf_counter()
print(f"Runtime:{end - start:.3}s")
