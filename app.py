from dash import Dash, dcc, html, Input, Output, callback, callback_context
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
from pandas_ta import bbands
import dash
from google.cloud import storage


# csv_file_path = "gs://alpha_advantage_stock_api/output/stockmarket_transformed.csv"
# Reading JSON file from HDFS
print('Reading file from docker and converting to spark df')

# create a client object for cloud storage
storage_client = storage.Client()
bucket = storage_client.bucket("alpha_advantage_stock_api")
blob = bucket.blob("output/stockmarket_transformed.csv")

# Reading JSON file from cloud storage
print('Reading file from docker and converting to spark df')
with blob.open("r") as myfile:  
    df = pd.read_csv(myfile)

print("create index on df")
df.reset_index(inplace=True)
df[["date", "last_refreshed"]] = df[["date", "last_refreshed"]].apply(pd.to_datetime)
df["symbol"] = df["symbol"].astype('string')
df = df.astype({"open":'float', "close":'float', "high":'float', "low":'float', "volume":'float'})

# Create a Dash app.
print("create dash app")
app = dash.Dash(__name__)
# Expose Flask instance
server = app.server

# change default app title in browser
app.title = "StockMarketTrends"
app.layout = html.Div([
                dbc.Row([
                    html.H1(children='Stock Market Analysis', style={'textAlign':'center', 'color':'grey', 'margin-top':'10px'}),
                    dbc.Col([
                        html.Label('Select the stock to be displayed', style={'margin-left': '40px', 'color':'grey'}),
                        dcc.Dropdown(options=df.symbol.unique(), value='MSFT', id='dropdown-selection', 
                                style={'margin-left': '20px', 'margin-top': 10 , 'width': '400px'}, searchable=True, placeholder="Search stock symbol"),
                            ], width=6)
                        ]),
                dbc.Row([
        
                        # Firstly, the candlestick chart is invoked. It is contained in a dcc.Loading
                        # object, which presents a loading animation while the data is retrieved.
                        dcc.Loading(
                        [dcc.Graph(id='graph-content', figure={})], 
                        id='loading-price-chart', type='dot', color='grey'),

                ]),
                html.Div([
                        # The buttons occupy 1/3 of the available width.
                            html.Div([
                            # This Div contains the time span buttons for adjusting
                            # of the x-axis' length.
                                html.Button('1W', id='1W-button',
                                            n_clicks=0, className='btn-secondary'),
                                html.Button('1M', id='1M-button',
                                            n_clicks=0, className='btn-secondary'),
                                html.Button('3M', id='3M-button',
                                            n_clicks=0, className='btn-secondary'),
                                html.Button('6M', id='6M-button',
                                            n_clicks=0, className='btn-secondary'),
                                html.Button('YTD', id='YTD-button',
                                            n_clicks=0, className='btn-secondary'),
                                html.Button('52W', id='52W-button',
                                            n_clicks=0, className='btn-secondary'),
                                html.Button('ALL', id='ALL-button',
                                            n_clicks=0, className='btn-secondary'),
                            ], style={'width': '30%', 'display': 'inline-block','color':'grey'}),
                            # The indicators have the remaining two thirds of the space.
                            html.Div([
                                dcc.Checklist(
                                    ['Rolling Mean','Exponential Rolling Mean','Bollinger Bands'],
                                    inputStyle={'margin-left': '20px',
                                                'margin-right': '5px'},
                                    id='complements-checklist',
                                    style={'margin-top': '20px', 'color':'grey'}, inline=True)
                                ], style={'width': '70%', 'display': 'inline-block'})
                ], style={'padding': '15px', 'margin-left': '20px'})
            ], style={'backgroundColor': 'black'})

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value'),
    Input('complements-checklist', 'value'),
    Input('1W-button', 'n_clicks'),
    Input('1M-button', 'n_clicks'),
    Input('3M-button', 'n_clicks'),
    Input('6M-button', 'n_clicks'),
    Input('YTD-button', 'n_clicks'),
    Input('52W-button', 'n_clicks'),
    Input('ALL-button', 'n_clicks'),
)

def update_dropdown(value, checklist_values, button_1w, button_1m, button_3m, 
                            button_6m, button_ytd, button_52w, button_all):

    df_filtered = df[df.symbol==value]

    # Applying some indicators to its closing prices. Below we are measuring 
    # Bollinger Bands.
    df_bbands = bbands(df_filtered['close'], length=20, std=2)
    print("df_bbands", df_bbands)
    # Measuring the Rolling Mean and Exponential Rolling means
    df_filtered['Rolling Mean'] = df_filtered['close'].rolling(window=9).mean()
    df_filtered['Exponential Rolling Mean'] = df_filtered['close'].ewm(
        span=9, adjust=False).mean()
    print("df_final", df_filtered)

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if '1W-button' in changed_id:
        df_final = df_filtered.loc[(df_filtered["date"] >= pd.Timestamp.today().normalize() - pd.Timedelta(days=7)) & \
                        (df_filtered["date"] <= pd.Timestamp.today().normalize())]
    elif '1M-button' in changed_id:
        df_final = df_filtered.loc[(df_filtered["date"] >= pd.Timestamp.today().normalize() - pd.Timedelta(days=30)) & (df_filtered["date"] <= pd.Timestamp.today().normalize())]
    elif '3M-button' in changed_id:
        df_final = df_filtered.loc[(df_filtered["date"] >= pd.Timestamp.today().normalize() - pd.Timedelta(days=90)) & (df_filtered["date"] <= pd.Timestamp.today().normalize())]
    elif '6M-button' in changed_id:
        df_final = df_filtered.loc[(df_filtered["date"] >= pd.Timestamp.today().normalize() - pd.Timedelta(days=180)) & (df_filtered["date"] <= pd.Timestamp.today().normalize())]
    elif 'YTD-button' in changed_id:
        df_final = df_filtered.loc[(df_filtered["date"] >= pd.Timestamp.today().normalize() - pd.Timedelta(days = (pd.Timestamp.today().normalize().day_of_year - 1))) & (df_filtered["date"] <= pd.Timestamp.today().normalize())]
    elif '52W-button' in changed_id:
        df_final = df_filtered.loc[(df_filtered["date"] >= pd.Timestamp.today().normalize() - pd.Timedelta(weeks=52)) & (df_filtered["date"] <= pd.Timestamp.today().normalize())]
    elif 'ALL-button' in changed_id:
        df_final = df_filtered.copy()
    else:
        df_final = df_filtered.copy()

    # create figure object
    print("create chart layout")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df_final['date'],
                open=df_final['open'],
                high=df_final['high'],
                low=df_final['low'],
                close=df_final['close']))
    
    fig.update_layout(
    xaxis_rangeslider_visible=True, 
    paper_bgcolor='black',
    font_color='white',
    height = 500, 
    margin=dict(l=20, r=20, t=30, b=30),
    )
    
    # Each metric will have its own color in the chart.
    colors = {'Rolling Mean': '#6fa8dc',
            'Exponential Rolling Mean': '#03396c', 'Bollinger Bands Low': 'darkorange',
            'Bollinger Bands AVG': 'brown',
            'Bollinger Bands High': 'darkorange'}
        
    # If the user has selected any of the indicators in the checklist, we'll represent it in the chart.
    if checklist_values != None:
        for metric in checklist_values:

            # Adding the Bollinger Bands' typical three lines.
            if metric == 'Bollinger Bands':
                fig.add_trace(go.Scatter(
                    x=df_final['date'], y=df_bbands.iloc[:, 0],
                    mode='lines', name=metric, 
                        line={'color': colors['Bollinger Bands Low'], 'width': 1}))

                fig.add_trace(go.Scatter(
                    x=df_final['date'], y=df_bbands.iloc[:, 1],
                    mode='lines', name=metric, 
                        line={'color': colors['Bollinger Bands AVG'], 'width': 1}))

                fig.add_trace(go.Scatter(
                    x=df_final['date'], y=df_bbands.iloc[:, 2],
                    mode='lines', name=metric, 
                        line={'color': colors['Bollinger Bands High'], 'width': 1}))

            # Plotting any of the other metrics remained, if they are chosen.
            else:
                fig.add_trace(go.Scatter(
                    x=df_final['date'], y=df_final[metric], mode='lines', name=metric, 
                        line={'color': colors[metric], 'width': 1}))
            return fig       
    return fig

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)