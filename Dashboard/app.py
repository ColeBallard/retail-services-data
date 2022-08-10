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
    from config import database, user, password, dateTable, macroTable, NAICS_NAPCS, NAICSTable, NAPCSTable, serverName

# get environment variables from heroku if development environment
else:
    database = os.getenv("database")
    dateTable = os.getenv("dateTable")
    macroTable = os.getenv("macroTable")
    NAICS_NAPCS = os.getenv("NAICS_NAPCS")
    NAICSTable = os.getenv("NAICSTable")
    NAPCSTable = os.getenv("NAPCSTable")
    user = os.getenv("user")
    password = os.getenv("password")
    serverName = os.getenv("serverName")

server = flask.Flask(__name__)

app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'], server = server)

def createBarGraph():
    
    # set parameters for connection string
    params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};"
                                     "SERVER=" + serverName + ";"
                                     "DATABASE=" + database + ";"
                                     "UID=" + user + ";"
                                     "PWD=" + password + ";")

    engine = sa.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(params))

    # example query
    query = f"SELECT * FROM {macroTable}"

    conn = engine.connect()
    
    # create dataframe from query
    df = pd.read_sql(query, conn)

    # example graph
    fig = px.bar(df, x='MacroID', y='CPI', title='MacroID by CPI', labels = {'MacroID': 'Macro ID', 'CPI': 'CPI'})

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
        id='example-graph',
        figure=createBarGraph()
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

# local development server runs on http://127.0.0.1:8050/