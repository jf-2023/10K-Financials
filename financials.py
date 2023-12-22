import sqlite3
import pandas as pd
import zipfile

class Financials:
    def __init__(self, ticker, sec_data_zip_file_path='C:/Users/cornf/Downloads/companyfacts2023.zip', db_tickers_path="companies.db"):
        self.zip_file_path = sec_data_zip_file_path
        self.db_path = db_tickers_path
        self.ticker = ticker

    def fetch_data(self):
        """
        Connects to db to retrieve the CIK (Central Index Key) associated with the given stock ticker.
        Returns:
        - str or None: If the company is found in the database, retrieves and returns the corresponding
          data from a ZIP file downloaded from SEC.gov. If not found, prints a message and returns None.
        """
        conn = sqlite3.connect(self.db_path)  # Create connection
        cursor = conn.cursor()  # Create cursor
        cursor.execute("SELECT cik FROM companies WHERE ticker = ?", (self.ticker,))
        symbol = cursor.fetchone()  # if N/A, returns None, else returns ('1326801',)
        if symbol:
            cik = f'{int(symbol[0]):010d}'
            try:
                with zipfile.ZipFile(self.zip_file_path, 'r') as zip_file:
                    with zip_file.open(f'CIK{cik}.json') as json_file:
                        data = json_file.read().decode('utf-8')  # Decode bytes to a JSON string
                return data
            except KeyError as e:
                print(e)
        else:
            print(f"company {self.ticker} not found in db.")
            # continue
        conn.close()

    def get_data_df(self, account, data):
        """
        Converts and cleans JSON data to a DataFrame with yearly values only found in the '10-K' filing.
        Extracts relevant financial data columns 'val' and 'year' for the specified account.

        Parameters:
        - account (str): The financial account we want to retrieve data for (e.g., "Assets", "NetIncomeLoss", etc.).
        - data (JSON): Data obtained from the database.

        Returns:
        - pandas.DataFrame: If company data is found, returns a cleaned DataFrame containing yearly values
          for the specified account found in the '10-K' filings. If data is not found, return empty DataFrame.
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

    def get_assets_df(self):
        data = self.fetch_data()
        assets_df = self.get_data_df("Assets", data)
        return assets_df

    def get_equity_df(self):
        data = self.fetch_data()
        try:
            equity_df = self.get_data_df("StockholdersEquity", data)
            equity_df.rename(columns={'StockholdersEquity': 'Equity'}, inplace=True)
            return equity_df
        except KeyError:
            equity_df = self.get_data_df("StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
                                    data)
            equity_df.rename(
                columns={'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest': 'Equity'},
                inplace=True)
            return equity_df

    def get_liabilities_df(self):
        data = self.fetch_data()
        try:
            liabilities_df = self.get_data_df("Liabilities", data)
            return liabilities_df
        except KeyError:
            liabilities_df = pd.merge(self.get_assets_df(), self.get_equity_df(), on="year")
            liabilities_df['Liabilities'] = liabilities_df["Assets"] - liabilities_df["Equity"]
            liabilities_df = liabilities_df[['year', 'Liabilities']]
            return liabilities_df

    def get_balance_sheet(self):
        data = self.fetch_data()
        merged_df = pd.merge(self.get_assets_df(), self.get_equity_df(), on="year")
        try:
            liabilities_df = self.get_data_df("Liabilities", data)
            balance_sheet_df = pd.merge(merged_df, liabilities_df, on="year")
            balance_sheet_df.drop_duplicates(subset='year', keep="last", inplace=True)
            return balance_sheet_df
        except KeyError:
            merged_df['Liabilities'] = merged_df["Assets"] - merged_df["Equity"]
            merged_df.drop_duplicates(subset='year', keep="last", inplace=True)
            return merged_df

    def get_net_income(self):
        net_income_df = self.get_data_df("NetIncomeLoss", self.fetch_data())
        net_income_df.rename(columns={"NetIncomeLoss": "Net income"}, inplace=True)
        return net_income_df

    def get_operating_income(self):
        operating_income_df = self.get_data_df("OperatingIncomeLoss", self.fetch_data())
        operating_income_df.rename(columns={"OperatingIncomeLoss": "Operating income"}, inplace=True)
        return operating_income_df

    def get_income_statement(self):
        income_statement_df = pd.merge(self.get_net_income(), self.get_operating_income(), on="year")
        income_statement_df.drop_duplicates(subset='year', keep="last", inplace=True)
        return income_statement_df

    def get_operating_cashflows(self):
        operating_cashflows_df = self.get_data_df('NetCashProvidedByUsedInOperatingActivities', self.fetch_data())
        operating_cashflows_df.rename(columns={"NetCashProvidedByUsedInOperatingActivities": "Operating cash flow"},
                                      inplace=True)
        return operating_cashflows_df

    def get_investing_cashflows(self):
        investing_cashflows_df = self.get_data_df('NetCashProvidedByUsedInInvestingActivities', self.fetch_data())
        investing_cashflows_df.rename(columns={"NetCashProvidedByUsedInInvestingActivities": "Investing cash flow"},
                                      inplace=True)
        return investing_cashflows_df

    def get_financing_cashflows(self):
        financing_cashflows_df = self.get_data_df('NetCashProvidedByUsedInFinancingActivities', self.fetch_data())
        financing_cashflows_df.rename(columns={"NetCashProvidedByUsedInFinancingActivities": "Financing cash flow"},
                                      inplace=True)
        return financing_cashflows_df

    def get_cashflow_statement(self):
        merged_df = pd.merge(self.get_operating_cashflows(), self.get_investing_cashflows(), on="year")
        cashflow_statement_df = pd.merge(merged_df, self.get_financing_cashflows(), on="year")
        cashflow_statement_df.drop_duplicates(subset='year', keep="last", inplace=True)
        return cashflow_statement_df

    def financial_statement_df(self):
        merged_df = pd.merge(self.get_income_statement(), self.get_balance_sheet(), on="year")
        final_df = pd.merge(merged_df, self.get_cashflow_statement(), on="year")
        final_df.drop_duplicates(subset='year', keep="last", inplace=True)
        final_df.set_index("year", inplace=True)
        return final_df