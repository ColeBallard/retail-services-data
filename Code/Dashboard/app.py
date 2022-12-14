from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
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

app = Dash(__name__, external_stylesheets = [dbc.themes.SLATE, dbc.icons.FONT_AWESOME], server = server)

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

    df.rename(columns = {'Meaning of NAICS code (NAICS2017_LABEL)':'Retail Establishment', 'Meaning of NAPCS collection code (NAPCS2017_LABEL)':'Product(s)', 'Sales, value of shipments, or revenue of NAPCS collection code ($1,000) (NAPCSDOL)':'Sales (USD, Thousands)'}, inplace = True)
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


    fig = px.bar(df, x='Retail Establishment', y='Sales (USD, Thousands)', title='Top 3 Products Sold in Top 3 Types of Retail Establishments by Sales (2017)', color='Product(s)', barmode='group')

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

    df.rename(columns = {'Adjusted_Sales':'Adjusted Retail Sales (USD, Millions)', 'CPI':'CPI (2015 = 100)'}, inplace = True)

    fig = px.scatter(df, x='CPI (2015 = 100)', y='Adjusted Retail Sales (USD, Millions)', 
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

    df.rename(columns = {'Adjusted_Sales':'Adjusted Retail Sales (USD, Millions)', 'RPI':'RPI (USD, Billions)'}, inplace = True)
    
    fig = px.scatter(df, x='RPI (USD, Billions)', y='Adjusted Retail Sales (USD, Millions)', 
                    title='Real Person Income (RPI) vs Retail Sales', trendline='ols', 
                    trendline_color_override='white')

    fig.update_yaxes(range=[250000, 900000])

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

    df.rename(columns = {'Adjusted_Sales':'Adjusted Retail Sales (USD, Millions)', 'USTRADE':'Retail Employees (Thousands of Persons)'}, inplace = True)

    fig = px.scatter(df, x='Retail Employees (Thousands of Persons)', y='Adjusted Retail Sales (USD, Millions)', 
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

    df.rename(columns = {'Adjusted_Sales':'Adjusted Retail Sales (USD, Millions)', 'USWTRADE':'Wholesale Employees (Thousands of Persons)'}, inplace = True)

    fig = px.scatter(df, x='Wholesale Employees (Thousands of Persons)', y='Adjusted Retail Sales (USD, Millions)', 
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

    # remove duplicate DateID column
    df = df.loc[:,~df.columns.duplicated()].copy()

    fig = px.line(df, x='Date', y=df.columns[2:31], title='US Retail Sales Over Time', labels={'value':'Adjusted Sales (USD, Millions)', 'variable': 'Retail Establishment'})

    traces_to_hide = df.columns[3:31]

    fig.for_each_trace(lambda trace: trace.update(visible="legendonly") 
                   if trace.name in traces_to_hide else ())

    fig.update_layout(title_x=0.5)

    return fig

def vis8():
    #include note that says data is being updated daily to make stronger predictions

    # https://fred.stlouisfed.org/series/PCECTPI

    mldf = pd.read_csv('assets/MLData.csv')

    mldf.rename(columns = {'Unnamed: 0':'Date'}, inplace = True)

    df = pd.DataFrame(data={'Quarter':['2021 Q3', '2021 Q4', 'Predicted 2022 Q1'], 'Adjusted Retail Sales (USD, Millions)':[mldf['Prediction'][1:4].sum(), mldf['Prediction'][4:7].sum(), mldf['Prediction'][7:10].sum()]})

    fig = px.bar(df, x='Quarter', y='Adjusted Retail Sales (USD, Millions)', title='Predicted Retail Sales for the next Quarter', color='Quarter', color_discrete_map = {'2021 Q3' : '#646cfc', '2021 Q4' : '#646cfc', 'Predicted 2022 Q1' : '#04cc94'})

    fig.update_layout(title_x=0.5)

    fig.update_layout(yaxis_range=[1600000,1680000])

    return fig

def vis9():
    # 1.72% increase for RPI

    # 2.22% increase for CPI

    # 0.01% increase for RPI

    # 0.73% increase for CPI

    # 553309.8086125777
    # 554708.300897474
    # 555813.092349442

    df = pd.DataFrame(data={'Trend':['Predicted Adjusted <br>Retail Sales', 'Adjusted CPI', 'Adjusted RPI'], 'Quarterly Change':[0.0032, 0.0222, 0.0172]})

    fig = px.bar(df, x='Trend', y='Quarterly Change', title='Trends for Q1 2022', color='Trend', color_discrete_map = {'Predicted Adjusted <br>Retail Sales' : '#636efa', 'Adjusted CPI' : '#ffa15a', 'Adjusted RPI' : '#ab63fa'})

    fig.update_layout(title_x=0.5)

    fig.update_layout(yaxis_tickformat = '.1%')

    return fig

def vis10():
    mldf = pd.read_csv('assets/MLData.csv')

    defdf = pd.read_csv('assets/defdata.csv')

    print(defdf.to_string)

    mldf.rename(columns = {'Unnamed: 0':'Date'}, inplace = True)

    defdf.rename(columns = {'Unnamed: 0':'Date'}, inplace = True)

    fig = px.line(mldf, x='Date', y='Prediction', labels={'Prediction': 'Adjusted Retail Sales (USD, Millions)'},
                    title='Monthly Retail Sales')

    fig.add_trace(go.Scatter(x = defdf['Date'], y = defdf['Retail sales, total'], name='Actual Retail sales, total'))
    fig.add_trace(go.Scatter(x = mldf['Date'], y = mldf['Prediction'], name='Predicted Retail sales, total'))

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
                                ], style={'textAlign': 'center', 'color': 'white'}) 
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
                                            html.H6('Overview', style={'color':'#aaa'}),
                                            html.P('''
                                            For this dashboard we looked at nationwide retail data, including product and industry classifications 
                                            from 1960 to 2022.
                                            ''', style={'line-height': '165%'}),
                                            html.P('''
                                            The goal of the time series analysis we made was to create a machine learning model that predicts future retail 
                                            sales in the United States.
                                            ''', style={'line-height': '165%'})
                                        ], style={'textAlign': 'center', 'color': 'white'}) 
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
                                            html.H6('The Team'),
                                            html.A('Nathaniel Van Schyndel', href='https://www.linkedin.com/in/nathaniel-van-schyndel-764b9b148/'),
                                            html.Br(),
                                            html.A('James Miller', href='https://www.linkedin.com/in/james-miller-0b994036/'),
                                            html.Br(),
                                            html.A('Gavan VanOver', href='https://www.linkedin.com/in/gavan-vanover-041160223/'),
                                            html.Br(),
                                            html.A('Cole Ballard', href='https://www.linkedin.com/in/cole-ballard/'),
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
                    drawFigure(vis7()) 
                ], width=10),
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Div([
                                    html.P([
                                        html.Strong('Adjusted sales,'),
                                        html.Span(
                                        '''
                                        also known as net sales, represent gross sales less returns and allowances. 
                                        This measure is a gauge of market demand and pricing power, and is commonly used to determine relative 
                                        market share for various industries including retail, apparel, manufacturing and technology hardware.
                                        '''
                                        )
                                    ], style={'line-height': '160%'}),
                                    html.P('''
                                    Adjusted sales is a better indicator of relative commerce.
                                    ''', style={'line-height': '160%'})
                                ], style={'textAlign': 'center', 'color': 'white'}) 
                            ])
                        ),
                    ])
                ], width=2),
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
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Div([
                                    html.P([
                                        html.Strong('Consumer Price Index'),
                                        html.Span(''' is the price of a weighted average market basket of consumer goods and 
                                        services purchased by households and changes in measured CPI track changes in prices over time.
                                        ''')
                                    ], style={'line-height': '175%'}),
                                ], style={'textAlign': 'center', 'color': 'white'}) 
                            ])
                        ),
                    ])
                ], width=6),
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Div([
                                    html.P([
                                        html.Strong('Real Person Income'),
                                        html.Span(''' is how much money an individual or entity makes after accounting for inflation and 
                                        is sometimes called real wage.
                                        ''')
                                    ], style={'line-height': '175%'})
                                ], style={'textAlign': 'center', 'color': 'white'}) 
                            ])
                        ),
                    ])
                ], width=6)
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    drawFigure(vis5()) 
                ], width=6),
                dbc.Col([
                    drawFigure(vis6()) 
                ], width=6),
            ], align='center'), 
            html.Br(),
            dbc.Row([
                dbc.Col([
                    drawFigure(vis8()) 
                ], width=12),
                # dbc.Col([
                #     dbc.Row([
                #         dbc.Col([
                #             html.Div([
                #                 dbc.Card(
                #                     dbc.CardBody([
                #                         html.Div([
                #                             html.H5([
                #                                 html.Span('Based on our time series model, Adjusted Retail Sales are predicted to increase by '),
                #                                 html.Strong('0.32%', style={'color': 'red'}),
                #                                 html.Span(' for Q1 2022.')
                #                             ], style={'line-height': '200%'})
                #                         ], style={'textAlign': 'center', 'color': 'white'})
                #                     ])
                #                 ),
                #             ])
                #         ], width=12),
                #     ]),
                #     html.Br(),
                #     dbc.Row([
                #         dbc.Col([
                #             html.Div([
                #                 dbc.Card(
                #                     dbc.CardBody([
                #                         html.Div([
                #                             html.P([
                #                                 html.Span('Consumer Price Index (CPI) is projected to increase almost '),
                #                                 html.Strong('7 times'),
                #                                 html.Span(' as much as Adjusted Retail Sales while Real Person Income (RPI) is supposed to increase by over '),
                #                                 html.Strong('5 times'),
                #                                 html.Span(' as much as Adjusted Retail Sales.')
                #                             ], style={'line-height': '175%'}),
                #                             html.P([
                #                                 html.Span('Data from '),
                #                                 html.A('FRED Economic Data', href='https://fred.stlouisfed.org/'),
                #                                 html.Span('.'),
                #                             ])
                #                         ], style={'textAlign': 'center', 'color': 'white'})
                #                     ])
                #                 ),
                #             ])
                #         ], width=12)
                #     ]),
                # ], width=3),
            ], align='center'), 
            html.Br(),
            dbc.Row([
                dbc.Col([
                    drawFigure(vis10()) 
                ], width=12),
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
                ], width=4),
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Div([
                                    html.A([
                                        html.I(className="fa-brands fa-github", style={'font-size': '7.5em'})
                                    ], href='https://github.com/ColeBallard/retail-services-data', style={'padding':'48px'}),
                                    html.A([
                                        html.I(className="fa-brands fa-trello", style={'font-size': '7.5em'})
                                    ], href='https://trello.com/b/mZfSYbxw/capstonedev10', style={'padding':'48px'}),
                                    html.A([
                                        html.Img(src='../assets/dev10.ico', style={'width': 105, 'vertical-align': '-7px'})
                                    ], href='https://www.genesis10.com/dev10', style={'padding':'48px'})
                                ], style={'textAlign': 'center'})
                            ])
                        ),
                    ])
                ], width=8)
            ])                 
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