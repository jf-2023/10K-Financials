import sqlite3
import pandas as pd
import zipfile
import time
import json
start = time.perf_counter()

zip_file_path = '...'
financials_db = []
financials_errors = []
count = 0


def format_number(num):
    if abs(num) >= 1e12:
        return "{:.2f}T".format(num / 1e12)
    elif abs(num) >= 1e9:
        return "{:.2f}B".format(num / 1e9)
    elif abs(num) >= 1e6:
        return "{:.2f}M".format(num / 1e6)
    else:
        return num


def show(account):
    bug = pd.read_json(data)['facts']['us-gaap'][account]['units']['USD']
    df = pd.DataFrame(bug)
    df = df[df['form'] == '10-K']
    df['end'] = pd.to_datetime(df['end'])
    df['year'] = df['end'].dt.year
    df.drop_duplicates(subset='val', keep="last", inplace=True)
    df.drop_duplicates(subset='year', keep="last", inplace=True)
    df = df[['year', 'val']]
    df.rename(columns={'val': account}, inplace=True)
    return df


def get_equity():
    try:
        df_e = show('StockholdersEquity')
        df_e.rename(columns={'StockholdersEquity': 'Equity'}, inplace=True)
        return df_e
    except KeyError:
        df_e = show('StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest')
        df_e.rename(columns={'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest': 'Equity'}, inplace=True)
        return df_e


conn = sqlite3.connect("companies.db")  # Create connection
cursor = conn.cursor()  # Create cursor
cursor.execute("SELECT ticker FROM companies") # Fetch all symbols from the 'companies' table
symbols = cursor.fetchall()
for symbol in symbols: # Loop over the symbols and execute your code for each one
    symbol = symbol[0]  # Extract the symbol from the tuple
    cursor.execute("SELECT cik FROM companies WHERE ticker = ?", (symbol,))

    row = cursor.fetchone()
    if row:
        cik_value = row[0]
        cik = f'{int(cik_value):010d}'

        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
                with zip_file.open(f'CIK{cik}.json') as json_file:
                    data = json_file.read().decode('utf-8')  # Decode bytes to a JSON string
        except:
            count += 1
            print(f"There is no item named 'CIK{cik}.json' in the archive, {count}")
            financials_errors.append({"stock": cik})
            continue

        #Maybe add separate functions for each, get Assets, Liabilities, etc.
        try:
            df_a = show("Assets")
        except KeyError:
            count += 1
            financials_errors.append({"stock": symbol})
            print(f"something went wrong: {symbol}, {count}")
            continue

        try:
            merged_df = pd.merge(df_a, get_equity(), on='year')
        except KeyError:
            count += 1
            financials_errors.append({"stock": symbol})
            print(f"something went wrong for equity: {symbol}, {count}")
            continue


        try:
            df_l = show("Liabilities")
            final_df = pd.merge(merged_df, df_l, on='year')
        except KeyError:
            merged_df['Liabilities'] = merged_df['Assets'] - merged_df['Equity']
            final_df = merged_df
            continue

        final_df.set_index("year", inplace=True)
        value = final_df.tail(3)["Equity"].mean()
        value_dict = {'valuation': format_number(value)}
        final_df = final_df.applymap(format_number)
        #value = final_df.tail(3)["Equity"].mean() / final_df.head(3)["Equity"].mean()
        dict_data = final_df.to_dict()
        result_dict = {'ticker': symbol}
        result_dict.update(value_dict)
        result_dict.update(dict_data)
        financials_db.append(result_dict)


        json_string = json.dumps(financials_db)
        json_string_errors = json.dumps(financials_errors)

    else:
        count += 1
        financials_errors.append({"stock": symbol})
        print(f"No matching record found for primary key {symbol} {count}")
        continue


conn.close()

# Specify the file path where you want to save the JSON data
json_file_path = 'C:\\Users\\cornf\\Documents\\financial_data.json'


# Write the JSON string to the file
with open(json_file_path, 'w') as json_file:
    json_file.write(json_string)

print(f"JSON data has been saved to {json_file_path}")

# Specify the file path where you want to save the JSON data
json_file_path_errors = 'C:\\Users\\cornf\\Documents\\financial_errors.json'


# Write the JSON string to the file
with open(json_file_path_errors, 'w') as json_file:
    json_file.write(json_string_errors)

print(f"JSON data has been saved to {json_file_path_errors}")

end = time.perf_counter()
runtime = end - start
seconds = int(runtime % 60)
minutes = int(runtime // 60)
print(f"Runtime: {minutes}min {seconds}sec")