import sqlite3
import json
import time
from financials import Financials

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
    cursor.execute("SELECT * FROM companies")  # Fetch all symbols from the 'companies' table
    companies_list = cursor.fetchall()
    conn.close()
    return companies_list


def main():
    """
    get completed financial statement data for companies, after each iteration convert to json and append to list
    :return:
    json file with clean data to upload to mongoDB
    """
    financials_db = []
    companies_list = fetch_companies_list()
    for company in companies_list:
        company_ticker = company[0]
        company_name = company[1]
        try:
            instance = Financials(company_ticker)
            df = instance.financial_statement_df()
        except KeyError as e:
            print(f"{company_ticker} error: {e}")
            continue
        value = df.tail(3)["Operating cash flow"].mean()
        value_dict = {'valuation': format_values(value * 15)}
        df = df.applymap(format_values)
        financials_dict = df.to_dict()
        result_dict = {'ticker': company_ticker, 'companyName': company_name}
        result_dict.update(value_dict)
        result_dict.update(financials_dict)
        financials_db.append(result_dict)

    json_string = json.dumps(financials_db, indent=2)

    try:
        # Write the JSON string to the file
        json_file_path = 'C:/Users/cornf/Documents/test.json'
        with open(json_file_path, 'w') as json_file:
            json_file.write(json_string)

        print(f"JSON data has been saved to {json_file_path}")
    except:
        print(json_string)


start = time.perf_counter()

main()

end = time.perf_counter()
runtime = end - start
minutes, seconds = divmod(int(runtime), 60)
print(f"Runtime: {minutes}min {seconds}sec")