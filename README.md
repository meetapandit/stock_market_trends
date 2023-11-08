# Stock Market Trends
This project aims at exploring various components of data engineering like extraction, and storage using Gooogle Cloud Storage and hosted on Google Cloud Run. The visualization is built using Plotly's Dash library.
[Link to Stock Market Dashboard](https://stock-market-app-mp-mx26i3fsrq-uc.a.run.app/)

<img width="1423" alt="Screenshot 2023-11-07 at 4 42 29 PM" src="https://github.com/meetapandit/stock_market_trends/assets/15186489/e4623cd4-7263-4b5f-8ff9-39d1105ed747">

### Architecture Diagram:

<img width="669" alt="Screenshot 2023-11-07 at 5 08 31 PM" src="https://github.com/meetapandit/stock_market_trends/assets/15186489/cafef792-9d9d-4a94-bdc5-7ee29e3287f7">

- The data is downloaded in JSON format using the AlphaAdvantageStock API: [Example link](https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=IBM&outputsize=full&apikey=demo)
- The API downloads data for each stock. In order to make the dashboard more user-friendly I added more stocks by scraping the stocks list from [Stock Analysis](https://stockanalysis.com/list/biggest-companies/)

### High-level Workflow
  - At a high-level, the downloaded data is cleaned and saved in the Google Cloud Storage bucket as a CSV
  - The CSV is read as a pandas dataframe and updated to add new columns
  - The transformed dataframe is saved back to the storage bucket as a CSV
  - A Python visualization is created using Plotly's Dash library to show trends in high, low, open, and close metrics for different timeframes

### EDA 
  - Performed EDA using Jupyter notebook to get stats about the sample dataset like column datatypes, distribution of values in each column, and identifying null values
  - During this process I realized that due to stock split some data points were missing or had higher than normal range of values for the specific timeframe when the split took place

### Data Cleaning and Transformation
  - Each JSON format downloaded has metadata information at the beginning of the file which is removed during the data-cleaning process
  - Each API call gets data for a single stock. The data for all stocks from the scraped stocks list is appended to the dataframe
  - The appended data frame has 5000+ stocks and their OHLC metrics for the last 20 years. The data is continuously updated at the end of each day to add the previous day's data
  - The dataframe has more than 200MB of data and is saved in Cloud Storage as a persistent layer using Python's gcsfs library

### Transformation
  - The CSV is read as a pandas dataframe and updated to add new columns for week start date, week end date, year, and week number to be able to calculate different time frames (1W, 1M,3M etc) in the visualization easily
  - The transformed dataframe is saved to Google Cloud Storage for visualization

### Visualization using Plotly's Dash Library
  - An interactive visualization is created using Dash library in Python to analyze the trends in stocks for the different timeframes
  - A candlestick chart is plotted to show open, close, high, and low statistics of a stock based on the time frame selected (1W, 1M, 3M, 6M, YTD, 52W, ALL)
  - 3 indicators provide more information about when is the best time to buy, sell, or hold a stock based on historical trends
