import sqlite3
import pandas as pd
import zipfile
import time
import json

#constants
zip_file_path = 'C:/Users/cornf/Downloads/companyfacts.zip'
json_file_path = 'C:/Users/cornf/Documents/financial_data.json'


def format_values(num):
    """To make data more readable(i.e. 1230000000 => 1.23B)"""
    if abs(num) >= 1e12:
        return "{:.2f}T".format(num / 1e12)
    elif abs(num) >= 1e9:
        return "{:.2f}B".format(num / 1e9)
    elif abs(num) >= 1e6:
        return "{:.2f}M".format(num / 1e6)
    else:
        return num


def fetch_companies_list():
    conn = sqlite3.connect("companies.db")  # Create connection
    cursor = conn.cursor()  # Create cursor
    cursor.execute("SELECT ticker FROM companies")  # Fetch all symbols from the 'companies' table
    companies_list = cursor.fetchall()
    conn.close()
    return companies_list


def fetch_db(company):
    """
    Connects to db to retrieve the CIK (Central Index Key) associated with the given stock ticker.

    Parameters:
    - company (str): The stock ticker symbol (e.g., "META").

    Returns:
    - str or None: If the company is found in the database, retrieves and returns the corresponding
      data from a ZIP file downloaded from SEC.gov. If not found, prints a message and returns None.
    """

    conn = sqlite3.connect("companies.db")  # Create connection
    cursor = conn.cursor()  # Create cursor
    cursor.execute("SELECT cik FROM companies WHERE ticker = ?", (company,))
    symbol = cursor.fetchone() #if N/A, returns None, else returns ('1326801',)
    if symbol:
        cik = f'{int(symbol[0]):010d}'
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
                with zip_file.open(f'CIK{cik}.json') as json_file:
                    data = json_file.read().decode('utf-8')  # Decode bytes to a JSON string
            return data
        except KeyError as e:
            print(e)
    else:
        print(f"company {company} not found in db.")
        #continue
    conn.close()


def get_data_df(account, data):
    """
    Converts and cleans JSON data to a DataFrame with yearly values only found in the '10-K' filing.
    Extracts relevant financial data columns 'val' and 'year' for the specified account.

    Parameters:
    - account (str): The financial account we want to retrieve data for (e.g., "Assets", "NetIncomeLoss", etc.).
    - data (JSON): Data obtained from the database.

    Returns:
    - pandas.DataFrame: If company data is found, returns a cleaned DataFrame containing yearly values
      for the specified account found in the '10-K' filings. If data is not found, returns an empty DataFrame.
    """
    if data:
        processed_json = pd.read_json(data)['facts']['us-gaap'][account]['units']['USD']
        df = pd.DataFrame(processed_json)
        df = df[df['form'] == '10-K']
        df['year'] = pd.to_datetime(df['end']).dt.year
        df.drop_duplicates(subset=['val', 'year'], keep="last", inplace=True)
        df = df[['year', 'val']]
        df.rename(columns={'val': account}, inplace=True)
        return df
    else:
        return pd.DataFrame()


def get_assets_df(company):
    assets_df = get_data_df("Assets", fetch_db(company))
    return assets_df


def get_equity_df(company):
    try:
        equity_df = get_data_df("StockholdersEquity", fetch_db(company))
        equity_df.rename(columns={'StockholdersEquity': 'Equity'}, inplace=True)
        return equity_df
    except KeyError:
        equity_df = get_data_df("StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", fetch_db(company))
        equity_df.rename(columns={'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest': 'Equity'}, inplace=True)
        return equity_df


def get_liabilities_df(company):
    try:
        liabilities_df = get_data_df("Liabilities", fetch_db(company))
        return liabilities_df
    except KeyError:
        liabilities_df = pd.merge(get_assets_df(company), get_equity_df(company), on="year")
        liabilities_df['Liabilities'] = liabilities_df["Assets"] - liabilities_df["Equity"]
        liabilities_df = liabilities_df[['year', 'Liabilities']]
        return liabilities_df


def get_balance_sheet(company):
    merged_df = pd.merge(get_assets_df(company), get_equity_df(company), on="year")
    try:
        liabilities_df = get_data_df("Liabilities", fetch_db(company))
        balance_sheet_df = pd.merge(merged_df, liabilities_df, on="year")
        balance_sheet_df.drop_duplicates(subset='year', keep="last", inplace=True)
        return balance_sheet_df
    except KeyError:
        merged_df['Liabilities'] = merged_df["Assets"] - merged_df["Equity"]
        merged_df.drop_duplicates(subset='year', keep="last", inplace=True)
        return merged_df


def get_net_income(company):
    net_income_df = get_data_df("NetIncomeLoss", fetch_db(company))
    net_income_df.rename(columns={"NetIncomeLoss": "Net income"}, inplace=True)
    return net_income_df


def get_operating_income(company):
    operating_income_df = get_data_df("OperatingIncomeLoss", fetch_db(company))
    operating_income_df.rename(columns={"OperatingIncomeLoss": "Operating income"}, inplace=True)
    return operating_income_df


def get_income_statement(company):
    income_statement_df = pd.merge(get_net_income(company), get_operating_income(company), on="year")
    income_statement_df.drop_duplicates(subset='year', keep="last", inplace=True)
    return income_statement_df


def get_operating_cashflows(company):
    operating_cashflows_df = get_data_df( 'NetCashProvidedByUsedInOperatingActivities', fetch_db(company))
    operating_cashflows_df.rename(columns={"NetCashProvidedByUsedInOperatingActivities": "Operating cash flow"}, inplace=True)
    return operating_cashflows_df


def get_investing_cashflows(company):
    investing_cashflows_df = get_data_df('NetCashProvidedByUsedInInvestingActivities', fetch_db(company))
    investing_cashflows_df.rename(columns={"NetCashProvidedByUsedInInvestingActivities": "Investing cash flow"}, inplace=True)
    return investing_cashflows_df


def get_financing_cashflows(company):
    financing_cashflows_df = get_data_df('NetCashProvidedByUsedInFinancingActivities', fetch_db(company))
    financing_cashflows_df.rename(columns={"NetCashProvidedByUsedInFinancingActivities": "Financing cash flow"}, inplace=True)
    return financing_cashflows_df


def get_cashflow_statement(company):
    merged_df = pd.merge(get_operating_cashflows(company), get_investing_cashflows(company), on="year")
    cashflow_statement_df = pd.merge(merged_df, get_financing_cashflows(company), on="year")
    cashflow_statement_df.drop_duplicates(subset='year', keep="last", inplace=True)
    return cashflow_statement_df


def financial_statement_df(company):
    merged_df = pd.merge(get_income_statement(company), get_balance_sheet(company), on="year")
    final_df = pd.merge(merged_df, get_cashflow_statement(company), on="year")
    final_df.drop_duplicates(subset='year', keep="last", inplace=True)
    final_df.set_index("year", inplace=True)
    return final_df


def main():
    """
    get completed financial statement data for companies, after each iteration convert to json and append to list
    :return:
    json file with clean data to upload to mongoDB
    """
    financials_db = []
    companies_list = fetch_companies_list()
    for company in companies_list:
        company = company[0]
        try:
            df = financial_statement_df(company)
        except KeyError as e:
            print(f"{company} error: {e}")
            continue
        value = df.tail(3)["NetCashProvidedByUsedInOperatingActivities"].mean()
        value_dict = {'valuation': format_values(value * 15)}
        df = df.applymap(format_values)
        financials_dict = df.to_dict()
        result_dict = {'ticker': company}
        result_dict.update(value_dict)
        result_dict.update(financials_dict)
        financials_db.append(result_dict)

    json_string = json.dumps(financials_db)
    data_filtered = []
    for item in json_string:
        if item['Assets'] != {}:
            data_filtered.append(item)

    final_json = json.dumps(data_filtered, indent=2)
    # Write the JSON string to the file
    with open(json_file_path, 'w') as json_file:
        json_file.write(final_json)

    print(f"JSON data has been saved to {json_file_path}")



start = time.perf_counter()

main()

end = time.perf_counter()
runtime = end - start
minutes, seconds = divmod(int(runtime), 60)
print(f"Runtime: {minutes}min {seconds}sec")
