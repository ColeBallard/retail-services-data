from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from idna import intranges_contain
import plotly.graph_objects as go
import pymssql
from dash.dependencies import Input, Output
import numpy as np

from config import database, user, password, dateTable, macroTable, NAICS_NAPCS, NAICSTable, NAPCSTable, server

app = Dash(__name__)

def createBarGraph():

    conn = pymssql.connect(server,user,password,database)
    conn.cursor()
    query = f"SELECT * FROM {macroTable}"
    df = pd.read_sql(query,conn)

    print(df.columns)

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
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)

# http://127.0.0.1:8050/