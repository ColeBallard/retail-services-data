from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import pymssql
from dash.dependencies import Input, Output
import numpy as np
import urllib
import sqlalchemy as sa
from sqlalchemy import create_engine, event
from sqlalchemy.engine.url import URL
import os

if os.getenv("app") != "prod":
    from config import database, user, password, dateTable, macroTable, NAICS_NAPCS, NAICSTable, NAPCSTable, server

else:
    database = os.getenv("Password")
    dateTable = os.getenv("dateTable")
    macroTable = os.getenv("macroTable")
    NAICS_NAPCS = os.getenv("NAICS_NAPCS")
    NAICSTable = os.getenv("NAICSTable")
    NAPCSTable = os.getenv("NAPCSTable")
    user = os.getenv("user")
    password = os.getenv("password")
    server = os.getenv("server")
    
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

def createBarGraph():

    print(type("DRIVER={SQL Server};"))
    print(type("SERVER="+server+";"))
    
    params = urllib.parse.quote_plus("DRIVER={SQL Server};"
                                     "SERVER="+server+";"
                                     "DATABASE="+database+";"
                                     "UID="+user+";"
                                     "PWD="+password+";")

    engine = sa.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(params))

    query = f"SELECT * FROM {macroTable}"

    con = engine.connect()
    
    df = pd.read_sql(query,con)

    fig = px.bar(df, x='MacroID', y='CPI', title='MacroID by CPI',
        labels={'MacroID': 'Macro ID', 'CPI': 'CPI'})

    return fig

app.layout = html.Div(children=[
    html.H1(children='Retail Service Data'),

    html.Div(children='''
        An overview of retail data over time in the United States. 
    '''),

    dcc.Graph(
        id='example-graph',
        figure=createBarGraph()
    ),

    dcc.Dropdown(['LA', 'NYC', 'MTL'],
        'LA',
        id='dropdown'
    ),
    html.Div(id='display-value')
])

@app.callback(Output('display-value', 'children'),
                [Input('dropdown', 'value')])
def display_value(value):
    return f'You have selected {value}'

if __name__ == '__main__':
    app.run_server(debug=True)

# http://127.0.0.1:8050/