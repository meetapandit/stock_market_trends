import pandas as pd
from datetime import timedelta
from pyhdfs import HdfsClient

def transform_stock_data():

    
    # Reading JSON file from HDFS
    print('Reading file from cloud storage bucket and converting to pandas df')
    csv_file_path = "gs://alpha_advantage_stock_api/stockmarket_data.csv"

    # client = HdfsClient(hosts="localhost:9870")
    # print("statement after calling HDFS client",client)

    # with client.open("/user/root/input/stockmarket_data.csv") as f:
    df_stockmarket_data = pd.read_csv(csv_file_path)

    df_stockmarket_data["date"] = pd.to_datetime(df_stockmarket_data["date"]).dt.normalize()
    df_stockmarket_data["last_refreshed"] = pd.to_datetime(df_stockmarket_data["last_refreshed"]).dt.normalize()
    df_stockmarket_data = df_stockmarket_data.astype({"symbol": "string"})

    df_stockmarket_data["week_start_date"] = pd.Timestamp.today().normalize() - pd.Timedelta(days=pd.Timestamp.today().day_of_week)
    df_stockmarket_data["week_end_date"] = df_stockmarket_data["week_start_date"] + pd.Timedelta(days=6)
 
    # adding week num col
    df_stockmarket_data["week_number"] = df_stockmarket_data["date"].dt.year


    # # add month number
    df_stockmarket_data["month_number"] = df_stockmarket_data["date"].dt.month

    # # adding year column
    df_stockmarket_data["week_number"] = df_stockmarket_data["date"].dt.year
       
    df_stockmarket_data.to_csv("gs://alpha_advantage_stock_api/output/stockmarket_transformed.csv", index=False)