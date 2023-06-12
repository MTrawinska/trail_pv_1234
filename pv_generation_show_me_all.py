from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import pandas as pd
import sqlalchemy
import numpy as np
import requests
import datetime as dt
import os
from datetime import datetime
from datetime import timedelta
from datetime import date
import sys
import glob
import os
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

pd.options.mode.chained_assignment = None

pd.set_option('expand_frame_repr', False)
engine = sqlalchemy.create_engine("postgresql+pg8000://monika:ratownika@orion.polenergia.pl/EnergyMarkets")
engine.dialect.description_encoding = None

yesterday = pd.read_sql_query("select max(cet_datetime) from forecasts.pv_generation", con=engine).iloc[0, 0]

yesterday = yesterday.strftime('%Y-%m-%d')

df = pd.read_sql_query("select * from forecasts.pv_generation where cet_datetime > '2023-06-11'", con=engine)
df = df.sort_values('uploaded').drop_duplicates(['cet_datetime','model_name'], keep='last')
df.drop(['area', 'utc_datetime','remarks','uploaded'], axis=1, inplace=True)

df1 = df.loc[df['model_name'] == 'ranFor2']
df1.rename(columns={'gen_forecast': 'ranFor2'}, inplace=True)
df1['cet_datetime']=pd.to_datetime(df1.cet_datetime)
df1.drop(['model_name'], axis=1, inplace=True)

df2 = df.loc[df['model_name'] == 'linReg2']
df2.rename(columns={'gen_forecast': 'linReg2'}, inplace=True)
df2.drop(['model_name'], axis=1, inplace=True)
df2['cet_datetime']=pd.to_datetime(df2.cet_datetime)

df3 = df.loc[df['model_name'] == 'Avg2']
df3.rename(columns={'gen_forecast': 'Avg2'}, inplace=True)
df3.drop(['model_name'], axis=1, inplace=True)
df3['cet_datetime']=pd.to_datetime(df3.cet_datetime)

df4 = df.loc[df['model_name'] == 'aNN2']
df4.rename(columns={'gen_forecast': 'aNN2'}, inplace=True)
df4.drop(['model_name'], axis=1, inplace=True)
df4['cet_datetime']=pd.to_datetime(df4.cet_datetime)

merge=pd.merge(df1,df2, how = 'outer', on='cet_datetime')
merge=pd.merge(merge,df3, how = 'outer', on='cet_datetime')
dfM=pd.merge(merge,df4, how = 'outer', on='cet_datetime')
dfM = dfM.sort_values('cet_datetime')

# df11 = dfM.groupby('cet_datetime')['ranFor2'].sum().reset_index()
# df12 = dfM.groupby('cet_datetime')['linReg2'].sum().reset_index()
# df13 = dfM.groupby('cet_datetime')['Avg2'].sum().reset_index()
# df14 = dfM.groupby('cet_datetime')['aNN2'].sum().reset_index()
#
# merge11=pd.merge(df11,df12, how = 'outer', on='cet_datetime')
# merge11=pd.merge(merge11,df13, how = 'outer', on='cet_datetime')
# dfM1=pd.merge(merge11,df14, how = 'outer', on='cet_datetime')

app = Dash(__name__)


app.layout = html.Div([
    html.H4('PV model analysis'),
    dcc.Graph(id="time-series-chart"),
    html.P("Select model:"),
    dcc.Dropdown(
        id="ticker",
        options=["linReg2", "ranFor2", "Avg2", "aNN2"],
        value="linReg2",
        clearable=False,
    ),
])


@app.callback(
    Output("time-series-chart", "figure"),
    Input("ticker", "value"))
def display_time_series(ticker):
    df = dfM
    print(df)
    fig = px.line(df, x='cet_datetime', y=ticker)
    return fig


app.run_server(debug=True)




