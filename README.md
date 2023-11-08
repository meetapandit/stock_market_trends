# Stock Market Trends
This project aims at exploring various components of data engineering like extraction, storage using Gooogle Cloud Storage and hosted on Google Cloud Run. The visualization is built using Plotly's Dash library.
<img width="1423" alt="Screenshot 2023-11-07 at 4 42 29 PM" src="https://github.com/meetapandit/stock_market_trends/assets/15186489/e4623cd4-7263-4b5f-8ff9-39d1105ed747">

Architecture Diagram:

<img width="669" alt="Screenshot 2023-11-07 at 5 08 31 PM" src="https://github.com/meetapandit/stock_market_trends/assets/15186489/cafef792-9d9d-4a94-bdc5-7ee29e3287f7">

The data is downloaded in JSON format using the AlphaAdvantageStock API: [Example link](https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=IBM&outputsize=full&apikey=demo)
The API downloads data for each stock. Inorder to have more stocks to choose from I scraped stocks list from [Stock Analysis](https://stockanalysis.com/list/biggest-companies/)
