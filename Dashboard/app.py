from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import urllib
import sqlalchemy as sa
import os

if os.getenv("app_environment") != "production":
    from config import database, user, password, dateTable, macroTable, NAICS_NAPCS, NAICSTable, NAPCSTable, server

else:
    database = os.getenv("database")
    dateTable = os.getenv("dateTable")
    macroTable = os.getenv("macroTable")
    NAICS_NAPCS = os.getenv("NAICS_NAPCS")
    NAICSTable = os.getenv("NAICSTable")
    NAPCSTable = os.getenv("NAPCSTable")
    user = os.getenv("user")
    password = os.getenv("password")
    server = os.getenv("server")
    
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

dashApp = Dash(__name__, external_stylesheets=external_stylesheets)
app = dashApp.server

def createBarGraph():
    
    params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};"
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

dashApp.layout = html.Div(children=[
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

@dashApp.callback(Output('display-value', 'children'),
                [Input('dropdown', 'value')])
def display_value(value):
    return f'You have selected {value}'

if __name__ == '__main__':
    dashApp.run_server(debug=True)

# http://127.0.0.1:8050/