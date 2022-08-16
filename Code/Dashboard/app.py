import dash
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
    from config import database, user, password, dateTable, macroTable, NAICS_NAPCS, NAICSTable, NAPCSTable, salesTable, CPI_v_RPI, USTRADE_v_USWTRADE, Adjusted_Sales_by_Date, AllMacro_v_AdjustedSales, serverName

# get environment variables from heroku if development environment
else:
    database = os.getenv("database")
    dateTable = os.getenv("dateTable")
    macroTable = os.getenv("macroTable")
    NAICS_NAPCS = os.getenv("NAICS_NAPCS")
    NAICSTable = os.getenv("NAICSTable")
    NAPCSTable = os.getenv("NAPCSTable")
    salesTable = os.getenv("salesTable")
    CPI_v_RPI = os.getenv("CPI_v_RPI")
    USTRADE_v_USWTRADE = os.getenv("USTRADE_v_USWTRADE")
    Adjusted_Sales_by_Date = os.getenv("Adjusted_Sales_by_Date")
    AllMacro_v_AdjustedSales = os.getenv("AllMacro_v_AdjustedSales")
    user = os.getenv("user")
    password = os.getenv("password")
    serverName = os.getenv("serverName")

server = flask.Flask(__name__)

app = Dash(__name__, external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'], server = server)

# # Was trying to implement pages with the below code, but stopped trying. We can remove this probably
# dash.register_page("home",  path='/', layout=html.Div('Home Page'))
# dash.register_page("analytics", layout=html.Div('Analytics'))

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

    print("Building top3naics df")

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

def vis2():

    query = f'''
        SELECT * FROM {Adjusted_Sales_by_Date}
    '''
    
    # create dataframe from query
    sales_v_date = pd.read_sql(query, conn)

    df = pd.DataFrame()

    print("Building sales over time df")
    for sales in sales_v_date['Adjusted_Sales']:
        query = f'''
            SELECT *
                FROM {Adjusted_Sales_by_Date}
                WHERE {Adjusted_Sales_by_Date}.[Adjusted_Sales] = {sales}
    '''
        df = pd.concat([df, pd.read_sql(query, conn)])
        df["Date"] = df["Year"].astype(str) + '-' + df["Month"].astype(str)
        df["Date"] = pd.to_datetime(df["Date"])

    df.rename(columns = {'Adjusted_Sales':'Adjusted Sales'}, inplace = True)
    df = df.drop(columns=['Month', 'Year'])
    df = df.sort_values(by=["Date"])

    fig = px.line(df, x='Date', y='Adjusted Sales', 
                    title='US Retail Sales Over Time', 
                    height=800)

    return fig
    
def vis3():

    query = f'''
        SELECT CPI, Adjusted_Sales 
            FROM {AllMacro_v_AdjustedSales}
    '''
    
    # create dataframe from query
    allmacro_v_adjustedsales = pd.read_sql(query, conn)

    df = pd.DataFrame()

    print("Building cpi_v_adjustedsales df")
    for cpi in allmacro_v_adjustedsales['CPI']:
        query = f'''
            SELECT CPI, Adjusted_Sales
                FROM {AllMacro_v_AdjustedSales}
                WHERE {AllMacro_v_AdjustedSales}.CPI = {cpi}
    '''
        df = pd.concat([df, pd.read_sql(query, conn)])
        # print(df2)

    df.rename(columns = {'Adjusted_Sales':'Adjusted Sales', 'CPI':'CPI (2015 = 100)'}, inplace = True)

    fig = px.scatter(df, x='CPI (2015 = 100)', y='Adjusted Sales', 
                    title='Consumer Price Index (CPI) vs Retail Sales', trendline='ols', 
                    trendline_color_override='black', height=800)

    return fig

def vis4():

    query = f'''
        SELECT RPI, Adjusted_Sales 
            FROM {AllMacro_v_AdjustedSales}
    '''
    
    # create dataframe from query
    allmacro_v_adjustedsales = pd.read_sql(query, conn)

    df = pd.DataFrame()

    print("Building rpi_v_adjustedsales df")
    for rpi in allmacro_v_adjustedsales['RPI']:
        query = f'''
            SELECT RPI, Adjusted_Sales
                FROM {AllMacro_v_AdjustedSales}
                WHERE {AllMacro_v_AdjustedSales}.RPI = {rpi}
    '''
        df = pd.concat([df, pd.read_sql(query, conn)])

    df.rename(columns = {'Adjusted_Sales':'Adjusted Sales', 'RPI':'RPI (USD, Billions)'}, inplace = True)
    
    fig = px.scatter(df, x='RPI (USD, Billions)', y='Adjusted Sales', 
                    title='Real Person Income (RPI) vs Retail Sales', trendline='ols', 
                    trendline_color_override='black', height=800)

    return fig

def vis5():

    query = f'''
        SELECT USTRADE, Adjusted_Sales 
            FROM {AllMacro_v_AdjustedSales}
    '''
    
    # create dataframe from query
    allmacro_v_adjustedsales = pd.read_sql(query, conn)

    df = pd.DataFrame()

    print("Building ustrade_v_adjustedsales df")
    for ustrade in allmacro_v_adjustedsales['USTRADE']:
        query = f'''
            SELECT USTRADE, Adjusted_Sales
                FROM {AllMacro_v_AdjustedSales}
                WHERE {AllMacro_v_AdjustedSales}.USTRADE = {ustrade}
    '''
        df = pd.concat([df, pd.read_sql(query, conn)])

    df.rename(columns = {'Adjusted_Sales':'Adjusted Sales', 'USTRADE':'Retail Employees'}, inplace = True)

    fig = px.scatter(df, x='Retail Employees', y='Adjusted Sales', 
                    title='Number of Retail Employees vs Retail Sales', trendline='ols', 
                    trendline_color_override='black', height=800)

    return fig

def vis6():

    query = f'''
        SELECT USWTRADE, Adjusted_Sales 
            FROM {AllMacro_v_AdjustedSales}
    '''
    
    # create dataframe from query
    allmacro_v_adjustedsales = pd.read_sql(query, conn)

    df = pd.DataFrame()

    print("Building uswtrade_v_adjustedsales df")
    for uswtrade in allmacro_v_adjustedsales['USWTRADE']:
        query = f'''
            SELECT USWTRADE, Adjusted_Sales
                FROM {AllMacro_v_AdjustedSales}
                WHERE {AllMacro_v_AdjustedSales}.USWTRADE = {uswtrade}
    '''
        df = pd.concat([df, pd.read_sql(query, conn)])

    df.rename(columns = {'Adjusted_Sales':'Adjusted Sales', 'USWTRADE':'Wholesale Employees'}, inplace = True)

    fig = px.scatter(df, x='Wholesale Employees', y='Adjusted Sales', 
                    title='Number of Wholesale Employees vs Retail Sales', trendline='ols', 
                    trendline_color_override='black', height=800)

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

     # AdustedSales_v_Date graph
    dcc.Graph(
        id='vis2',
        figure=vis2()
    ),

    # cpi_v_adjustedsales graph
    dcc.Graph(
        id='vis3',
        figure=vis3()
    ),

    # rpi_v_adjustedsales graph
    dcc.Graph(
        id='vis4',
        figure=vis4()
    ),

    # ustrade_v_adjustedsales graph
    dcc.Graph(
        id='vis5',
        figure=vis5()
    ),

    # uswtrade_v_adjustedsales graph
    dcc.Graph(
        id='vis6',
        figure=vis6()
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