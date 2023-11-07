# import libraries
import pandas as pd
import requests
from google.cloud import storage
from bs4 import BeautifulSoup
import datetime
import json
import gcsfs 

def extract_stock_data():
    # symbol_values = ['IBM', 'MSFT', 'GOOGL','AAPL']
    url = "https://stockanalysis.com/list/biggest-companies/"

    # request access to url from host
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    table1 = soup.find("table", id="main-table")

    # Create a list of column headers
    print()
    print("Create a list of column headers\n")
    headers = []
    for thead in table1.find_all('th'):
        title = thead.text.strip()
        headers.append(title)

    print("create df of stocks list\n")
    stocks = pd.DataFrame(columns = headers)

    # Loop through 'tr' tag to get 'td' tag and row data
    print("loop through table rows\n")
    for j in table1.find_all('tr')[1:]:
        row_data = j.find_all('td')
        row_text = [i.text for i in row_data]
        length = len(stocks)
        # append to the dataframe
        stocks.loc[length] = row_text
    print("remove a stock from the list\n")
    stocks.drop(stocks[stocks["Symbol"].str.contains('.A')].index, inplace=True)
    # Create request call for for each tickr symbol
    print("loop through df\n")
    for i, val in enumerate(stocks['Symbol']):
        try:
            url = ''
            url += 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&outputsize=full&apikey=W3BMUCZT63KDH0ER'.format(val)
            r = requests.get(url)
            data = json.loads(r.text)
            
            # Create dataframe from json
            print("create dataframe from json\n")
            df_stockmarket_data = pd.DataFrame(data)
            
            # Replace index to interger index
            df_stockmarket_data.reset_index(inplace=True)
            
            print("format df to have necessary columns\n")
            # Rename index column to date
            df_stockmarket_data['date'] = df_stockmarket_data['index']

            # Select value of symbol from meta Data column and add new column for symbol in df
            df_stockmarket_data['symbol'] = val
            
            # repeat previous step for adding new columns for refresh date, output size and time zone
            df_stockmarket_data['last_refreshed'] = datetime.date.today()
            # df_stockmarket_data['output_size'] = df_stockmarket_data.loc[3,'Meta Data']
            # df_stockmarket_data['time_zone'] = df_stockmarket_data.loc[4,'Meta Data']
            
            # Select and reorder columns in df
            df_stockmarket_data = pd.DataFrame(df_stockmarket_data, columns=['date', 'symbol', 'Time Series (Daily)', 'last_refreshed'])

            # Remove first 5 rows starting from index 0 to 4 as it is metadata
            df_stockmarket_data = df_stockmarket_data[5:]
            
            # Convert time Series Daily column from dictionary to data frame columns
            print("Convert time series column into a dict\n")
            df_stockmarket_all_columns = pd.concat([df_stockmarket_data.drop('Time Series (Daily)', axis=1), df_stockmarket_data['Time Series (Daily)'].apply(pd.Series)], axis=1)
            
            # Reset index after removing top 5 rows
            df_stockmarket_all_columns = df_stockmarket_all_columns.reset_index().drop('index', axis=1)
            # Rename columns split from dictionary
            df_stockmarket_all_columns.rename(columns = {'1. open':'open', '2. high': 'high', '3. low': 'low', '4. close': 'close', '5. volume':'volume'}  , inplace=True)

            # Append data from each ticker symbol to data set created from previous step
            if i == 0:
                
                # Copy rows of current tickr symbol to a copy df
                df_stockmarket_all_columns_copy2 = df_stockmarket_all_columns.copy(deep=True)
                
                # convert to dict
                df_stockmarket_all_columns = pd.DataFrame(df_stockmarket_all_columns)
                
                # Create a new df to append current rows
                df_stockmarket_all_final = pd.concat([df_stockmarket_all_columns,df_stockmarket_all_columns_copy2.loc[:]]).reset_index(drop=True)
                
                # Copy the newly appended dataset to a new dataset which stores the previous state
                df_stockmarket_all_columns_previous = df_stockmarket_all_columns_copy2.copy(deep=True)
            else:
                # convert to dict
                df_stockmarket_all_columns = pd.DataFrame(df_stockmarket_all_columns)
                
                # From second tickr symbol onwards append the current rows to data stored from previous step
                df_stockmarket_all_final = pd.concat([df_stockmarket_all_columns,df_stockmarket_all_columns_previous.loc[:]]).reset_index(drop=True)
                
                # Copy the newly appended df into previous_df and repeat the process until we have data for all symbols
                df_stockmarket_all_columns_previous = df_stockmarket_all_final.copy(deep=True)
        except Exception:
            print(f'No data found for symbol:{val}')

    # Pass DataFrame and the filename as parameters to write method of client
    print("saving file to cloud storage")
    # with storage_client.write('gs://alpha_advantage_stock_api/stockmarket_data.csv', overwrite=True) as writer:
    df_stockmarket_all_final.to_csv('gs://alpha_advantage_stock_api/stockmarket_data.csv')
    
    