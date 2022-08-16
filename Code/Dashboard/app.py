from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import urllib
import sqlalchemy as sa
import flask
import os

# get environment variables from config if production environment
if os.getenv("app_environment") != "production":
    from config import database, user, password, dateTable, macroTable, NAICS_NAPCS, NAICSTable, NAPCSTable, salesTable, Adjusted_Sales_by_Date, AllMacro_v_AdjustedSales, Sales_by_Category, serverName

# get environment variables from heroku if development environment
else:
    database = os.getenv("database")
    dateTable = os.getenv("dateTable")
    macroTable = os.getenv("macroTable")
    NAICS_NAPCS = os.getenv("NAICS_NAPCS")
    NAICSTable = os.getenv("NAICSTable")
    NAPCSTable = os.getenv("NAPCSTable")
    salesTable = os.getenv("salesTable")
    Adjusted_Sales_by_Date = os.getenv("Adjusted_Sales_by_Date")
    AllMacro_v_AdjustedSales = os.getenv("AllMacro_v_AdjustedSales")
    Sales_by_Category = os.getenv("Sales_by_Category")
    user = os.getenv("user")
    password = os.getenv("password")
    serverName = os.getenv("serverName")

server = flask.Flask(__name__)

app = Dash(__name__, external_stylesheets = [dbc.themes.SLATE], server = server)

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
    # labels={"Supermarkets and other grocery (except convenience) stores": "Supermarkets and other grocery <br> (except convenience) stores",  "Warehouse clubs and supercenters": "Warehouse clubs <br> and supercenters", "Electronic shopping and mail-order houses": "Electronic shopping and <br> mail-order houses"}
    df['Retail Establishment'] = df['Retail Establishment'].replace(["Supermarkets and other grocery (except convenience) stores"], "Supermarkets and <br> other grocery <br> (except convenience) stores")
    df['Retail Establishment'] = df['Retail Establishment'].replace(["Warehouse clubs and supercenters"], "Warehouse clubs <br> and supercenters")
    df['Retail Establishment'] = df['Retail Establishment'].replace(["Electronic shopping and mail-order houses"], "Electronic shopping <br> and mail-order houses")

    df['Product(s)'] = df['Product(s)'].replace(['Retail sales of food dry goods and other foods purchased for future consumption'], 'Food dry goods and <br>other foods purchased <br>for future consumption')
    df['Product(s)'] = df['Product(s)'].replace(['Retail sales of fresh fruit and vegetables'], 'Fresh fruit and vegetables')
    df['Product(s)'] = df['Product(s)'].replace(['Retail sales of fresh meat and poultry'], 'Fresh meat and poultry')
    df['Product(s)'] = df['Product(s)'].replace(['Retail sales of candy, prepackaged cookies, and snack foods'], 'Candy, prepackaged <br>cookies, and snack foods')
    df['Product(s)'] = df['Product(s)'].replace(["Retail sales of women's clothing"], "Women's clothing")
    df['Product(s)'] = df['Product(s)'].replace(["Retail sales of footwear and footwear accessories"], "Footwear and <br>footwear accessories")


    fig = px.bar(df, x='Retail Establishment', y='Sales', title='2017 Top 3 Products Sold in Top 3 Types of Establishments by Sales', color='Product(s)', barmode='group')

    fig.update_layout(title_x=0.5)

    return fig

def vis2():

    query = f'''
        SELECT * FROM {Adjusted_Sales_by_Date}
    '''
    
    # create dataframe from query
    df = pd.read_sql(query, conn)

    print("Building sales over time df")
    df["Date"] = df["Year"].astype(str) + '-' + df["Month"].astype(str)
    df["Date"] = pd.to_datetime(df["Date"])

    df.rename(columns = {'Adjusted_Sales':'Adjusted Sales (USD, Millions)'}, inplace = True)
    df = df.sort_values(by=["Date"])
    df = df.reset_index()
    df = df.drop(columns=['index', 'Month', 'Year'])

    fig = px.line(df, x='Date', y='Adjusted Sales (USD, Millions)', 
                    title='US Retail Sales Over Time')

    fig.update_layout(title_x=0.5)

    return fig
    
def vis3():

    query = f'''
        SELECT CPI, Adjusted_Sales 
            FROM {AllMacro_v_AdjustedSales}
    '''
    
    # create dataframe from query
    df = pd.read_sql(query, conn)

    df.rename(columns = {'Adjusted_Sales':'Adjusted Sales (USD, Millions)', 'CPI':'CPI (2015 = 100)'}, inplace = True)

    fig = px.scatter(df, x='CPI (2015 = 100)', y='Adjusted Sales (USD, Millions)', 
                    title='Consumer Price Index (CPI) vs Retail Sales', trendline='ols', 
                    trendline_color_override='white')

    fig.update_layout(title_x=0.5)

    return fig

def vis4():

    query = f'''
        SELECT RPI, Adjusted_Sales 
            FROM {AllMacro_v_AdjustedSales}
    '''
    
    # create dataframe from query
    df = pd.read_sql(query, conn)

    print("Building rpi_v_adjustedsales df")

    df.rename(columns = {'Adjusted_Sales':'Adjusted Sales (USD, Millions)', 'RPI':'RPI (USD, Billions)'}, inplace = True)
    
    fig = px.scatter(df, x='RPI (USD, Billions)', y='Adjusted Sales (USD, Millions)', 
                    title='Real Person Income (RPI) vs Retail Sales', trendline='ols', 
                    trendline_color_override='white')

    fig.update_layout(title_x=0.5)

    return fig

def vis5():

    query = f'''
        SELECT USTRADE, Adjusted_Sales 
            FROM {AllMacro_v_AdjustedSales}
    '''
    
    # create dataframe from query
    df = pd.read_sql(query, conn)

    print("Building ustrade_v_adjustedsales df")

    df.rename(columns = {'Adjusted_Sales':'Adjusted Sales (USD, Millions)', 'USTRADE':'Retail Employees'}, inplace = True)

    fig = px.scatter(df, x='Retail Employees', y='Adjusted Sales (USD, Millions)', 
                    title='Number of Retail Employees vs Retail Sales')

    fig.update_layout(title_x=0.5)

    return fig

def vis6():

    query = f'''
        SELECT USWTRADE, Adjusted_Sales 
            FROM {AllMacro_v_AdjustedSales}
    '''
    
    # create dataframe from query
    df = pd.read_sql(query, conn)

    print("Building uswtrade_v_adjustedsales df")

    df.rename(columns = {'Adjusted_Sales':'Adjusted Sales (USD, Millions)', 'USWTRADE':'Wholesale Employees'}, inplace = True)

    fig = px.scatter(df, x='Wholesale Employees', y='Adjusted Sales (USD, Millions)', 
                    title='Number of Wholesale Employees vs Retail Sales')

    fig.update_layout(title_x=0.5)

    return fig

def vis7():
    
    # create dataframe from query
    
    query = f'''
        SELECT * 
            FROM {Sales_by_Category}
            JOIN {dateTable} ON {Sales_by_Category}.DateID = {dateTable}.DateID
'''
    df = pd.read_sql(query, conn)

    df["Date"] = df["Year"].astype(str) + '-' + df["Month"].astype(str)
    df["Date"] = pd.to_datetime(df["Date"])

    df = df.sort_values(by=["Date"])

    df = df.reset_index()
    df = df.drop(columns=['index', 'Month', 'Year'])

    # df.rename(columns = {'Meaning of NAICS code (NAICS2017_LABEL)':'Retail Establishment', 'Meaning of NAPCS collection code (NAPCS2017_LABEL)':'Product(s)', 'Sales, value of shipments, or revenue of NAPCS collection code ($1,000) (NAPCSDOL)':'Sales'}, inplace = True)
    # # labels={"Supermarkets and other grocery (except convenience) stores": "Supermarkets and other grocery <br> (except convenience) stores",  "Warehouse clubs and supercenters": "Warehouse clubs <br> and supercenters", "Electronic shopping and mail-order houses": "Electronic shopping and <br> mail-order houses"}
    # df['Retail Establishment'] = df['Retail Establishment'].replace(["Supermarkets and other grocery (except convenience) stores"], "Supermarkets and <br> other grocery <br> (except convenience) stores")
    # df['Retail Establishment'] = df['Retail Establishment'].replace(["Warehouse clubs and supercenters"], "Warehouse clubs <br> and supercenters")
    # df['Retail Establishment'] = df['Retail Establishment'].replace(["Electronic shopping and mail-order houses"], "Electronic shopping <br> and mail-order houses")

    # df['Product(s)'] = df['Product(s)'].replace(['Retail sales of food dry goods and other foods purchased for future consumption'], 'Food dry goods and <br>other foods purchased <br>for future consumption')
    # df['Product(s)'] = df['Product(s)'].replace(['Retail sales of fresh fruit and vegetables'], 'Fresh fruit and vegetables')
    # df['Product(s)'] = df['Product(s)'].replace(['Retail sales of fresh meat and poultry'], 'Fresh meat and poultry')
    # df['Product(s)'] = df['Product(s)'].replace(['Retail sales of candy, prepackaged cookies, and snack foods'], 'Candy, prepackaged <br>cookies, and snack foods')
    # df['Product(s)'] = df['Product(s)'].replace(["Retail sales of women's clothing"], "Women's clothing")
    # df['Product(s)'] = df['Product(s)'].replace(["Retail sales of footwear and footwear accessories"], "Footwear and <br>footwear accessories")


    fig = px.line(df, x='Date', y='Retail sales, total', title='Hey')

    fig.update_layout(title_x=0.5)

    return fig

def drawFigure(fig):
    return  html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=fig.update_layout(
                        template='plotly_dark',
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)',
                    ),
                    config={
                        'displayModeBar': False
                    }
                ) 
            ])
        ),  
    ])


app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Div([
                                    html.H1('Retail Service Data'),
                                ], style={'textAlign': 'center'}) 
                            ])
                        ),
                    ])
                ], width=12)
            ], align='center'), 
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Div([
                                    html.H6('An overview of retail data over time in the United States.'),
                                ], style={'textAlign': 'center'}) 
                            ])
                        ),
                    ])
                ], width=12)
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                dbc.Card(
                                    dbc.CardBody([
                                        html.Div([
                                            html.P('''
                                            For this dashboard we looked at nationwide retail data, including product and industry classifications 
                                            from 1960 to 2022.
                                            '''),
                                            html.P('''
                                            The goal of the time series analysis we made was to create a machine learning model that predicts future retail 
                                            sales in the United States.
                                            ''')
                                        ], style={'textAlign': 'center'}) 
                                    ])
                                ),
                            ])
                        ], width=12)
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                dbc.Card(
                                    dbc.CardBody([
                                        html.Div([
                                            html.H6('Sources'),
                                            html.A('Monthly Retail Trade Report', href='https://www.census.gov/retail/index.html'),
                                            html.Br(),
                                            html.A('Consumer Price Index (CPI) United States', href='https://www.kaggle.com/datasets/sfktrkl/consumer-price-index-cpi-united-states'),
                                            html.Br(),
                                            html.A('Macroeconomics US', href='https://www.kaggle.com/datasets/denychaen/usmacro?select=US_MACRO110522.csv'),
                                            html.Br(),
                                            html.A('All Sectors: Products by Industry for the U.S.', href='https://data.census.gov/cedsci/table?q=ECNNAPCSPRD2017.EC1700NAPCSPRDIND&n=N0600.44&tid=ECNNAPCSPRD2017.EC1700NAPCSPRDIND&hidePreview=true'),
                                        ], style={'textAlign': 'center'})
                                    ])
                                ),
                            ])
                        ], width=12)
                    ]),
                ], width=3),
                dbc.Col([
                    drawFigure(vis1()) 
                ], width=9),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    drawFigure(vis2()) 
                ], width=12),
            ], align='center'), 
            html.Br(),
            dbc.Row([
                dbc.Col([
                    drawFigure(vis3()) 
                ], width=6),
                dbc.Col([
                    drawFigure(vis4())
                ], width=6),
            ], align='center'), 
            html.Br(),
            dbc.Row([
                dbc.Col([
                    drawFigure(vis5()) 
                ], width=6),
                dbc.Col([
                    drawFigure(vis6()) 
                ], width=6),
            ], align='center'),
            # dbc.Row([
            #     dbc.Col([
            #         drawFigure(vis7()) 
            #     ], width=6),
            #     dbc.Col([
            #         drawFigure(vis7()) 
            #     ], width=6),
            # ], align='center'),                  
        ]), color = 'dark'
    )
])    

#     # example dropdown
#     dcc.Dropdown(['LA', 'NYC', 'MTL'],
#         'LA',
#         id='dropdown'
#     ),
#     html.Div(id='display-value')
# ])

# # example callback for dropdown
# @app.callback(Output('display-value', 'children'),
#                 [Input('dropdown', 'value')])
# def display_value(value):
#     return f'You have selected {value}'

if __name__ == '__main__':

    app.run_server(debug=True)

# local development server runs on http://127.0.0.1:8050/