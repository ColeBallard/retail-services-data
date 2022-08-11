from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import urllib
import sqlalchemy as sa
import flask
import os

# get environment variables from config if production environment
if os.getenv("app_environment") != "production":
    from config import database, user, password, dateTable, macroTable, NAICS_NAPCS, NAICSTable, NAPCSTable, salesTable, serverName

# get environment variables from heroku if development environment
else:
    database = os.getenv("database")
    dateTable = os.getenv("dateTable")
    macroTable = os.getenv("macroTable")
    NAICS_NAPCS = os.getenv("NAICS_NAPCS")
    NAICSTable = os.getenv("NAICSTable")
    NAPCSTable = os.getenv("NAPCSTable")
    salesTable = os.getenv("salesTable")
    user = os.getenv("user")
    password = os.getenv("password")
    serverName = os.getenv("serverName")

server = flask.Flask(__name__)

app = Dash(__name__, external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'], server = server)

# set parameters for connection string
params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};"
                                     "SERVER=" + serverName + ";"
                                     "DATABASE=" + database + ";"
                                     "UID=" + user + ";"
                                     "PWD=" + password + ";")

engine = sa.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(params))

conn = engine.connect()

def vis1():

    query = f'''
        SELECT TOP 3 NAICSID 
            FROM {NAICS_NAPCS}
            WHERE [Sales, value of shipments, or revenue of NAPCS collection code ($1,000) (NAPCSDOL)] IS NOT NULL
            GROUP BY NAICSID
            ORDER BY SUM([Sales, value of shipments, or revenue of NAPCS collection code ($1,000) (NAPCSDOL)]) desc
    '''
    
    # create dataframe from query
    top3naics = pd.read_sql(query, conn)

    df = pd.DataFrame()

    for naicsid in top3naics['NAICSID']:
        query = f'''
            SELECT TOP 3 {NAICSTable}.[Meaning of NAICS code (NAICS2017_LABEL)], {NAPCSTable}.[Meaning of NAPCS collection code (NAPCS2017_LABEL)], [Sales, value of shipments, or revenue of NAPCS collection code ($1,000) (NAPCSDOL)]
                FROM {NAICS_NAPCS}
                JOIN {NAICSTable} ON {NAICS_NAPCS}.NAICSID = {NAICSTable}.NAICSID
                JOIN {NAPCSTable} ON {NAICS_NAPCS}.NAPCSID = {NAPCSTable}.NAPCSID
                WHERE {NAICS_NAPCS}.NAICSID = {naicsid}
                GROUP BY {NAICSTable}.[Meaning of NAICS code (NAICS2017_LABEL)], {NAPCSTable}.[Meaning of NAPCS collection code (NAPCS2017_LABEL)], [Sales, value of shipments, or revenue of NAPCS collection code ($1,000) (NAPCSDOL)]
                ORDER BY [Sales, value of shipments, or revenue of NAPCS collection code ($1,000) (NAPCSDOL)] desc
    '''
        df = pd.concat([df, pd.read_sql(query, conn)])

    df.rename(columns = {'Meaning of NAICS code (NAICS2017_LABEL)':'Retail Establishment', 'Meaning of NAPCS collection code (NAPCS2017_LABEL)':'Product(s)', 'Sales, value of shipments, or revenue of NAPCS collection code ($1,000) (NAPCSDOL)':'Sales'}, inplace = True)

    fig = px.bar(df, x='Retail Establishment', y='Sales', title='2017 Top 3 Products Sold in Top 3 Types of Establishments by Sales', color='Product(s)', barmode='group', height=800)

    return fig

app.layout = html.Div(children=[

    # title
    html.H1(children='Retail Service Data'),

    # subtitle
    html.Div(children='''
        An overview of retail data over time in the United States. 
    '''),

    # example graph
    dcc.Graph(
        id='vis1',
        figure=vis1()
    ),

    # example dropdown
    dcc.Dropdown(['LA', 'NYC', 'MTL'],
        'LA',
        id='dropdown'
    ),
    html.Div(id='display-value')
])

# example callback for dropdown
@app.callback(Output('display-value', 'children'),
                [Input('dropdown', 'value')])
def display_value(value):
    return f'You have selected {value}'

if __name__ == '__main__':

    app.run_server(debug=True)

    # set parameters for connection string
    params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};"
                                     "SERVER=" + serverName + ";"
                                     "DATABASE=" + database + ";"
                                     "UID=" + user + ";"
                                     "PWD=" + password + ";")

    engine = sa.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(params))

# local development server runs on http://127.0.0.1:8050/