import hashlib
import dash_bootstrap_components as dbc
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from apps import dbconnect as db

layout = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H1('APMIS', className="text-center mb-4"),
                html.H4('Login', className="text-center mb-4"),
                dbc.Alert('Username or password is incorrect.', color="danger", id='login_alert', is_open=False),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.CardGroup(
                                [
                                    dbc.Label("Username"),
                                    dbc.Input(type="text", id="login_username", placeholder="Enter username"),
                                ]
                            ),
                            width=12,
                            className="mb-3"
                        ),
                    ],
                    className="justify-content-center",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.CardGroup(
                                [
                                    dbc.Label("Password"),
                                    dbc.Input(type="password", id="login_password", placeholder="Enter password"),
                                ]
                            ),
                            width=12,
                            className="mb-3"
                        ),
                    ],
                    className="justify-content-center",
                ),
                dbc.Button('Login', color="primary", id='login_loginbtn', className="btn-block"),
                html.Br(),
                html.Br(),
                html.Div([
                    html.P("Don't have an account?"),
                    html.A('Signup Now!', href='/signup', className="btn btn-outline-secondary btn-block custom-btn"),
                ], className="text-center")
            ]
        ),
    ],
    className="container mt-5",
    style={"background-color": "#f0f0f0", "padding": "20px", "max-width": "500px", "margin": "auto"}  # Adjust max-width
)
@app.callback(
    [
        Output('login_alert', 'is_open'),
        Output('currentuserid', 'data'),
    ],
    [
        Input('login_loginbtn', 'n_clicks'), # begin login query via button click
        Input('sessionlogout', 'modified_timestamp'), # reset session userid to -1 if logged out
    ],
    [
        State('login_username', 'value'),
        State('login_password', 'value'),   
        State('sessionlogout', 'data'),
        State('currentuserid', 'data'), 
        State('url', 'pathname'), 
    ]
)
def loginprocess(loginbtn, sessionlogout_time,
                 username, password,
                 sessionlogout, currentuserid,
                 pathname):
    
    ctx = callback_context
    
    if ctx.triggered:
        openalert = False
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
    else:
        raise PreventUpdate
    
    if eventid == 'login_loginbtn': # trigger for login process
        if loginbtn and username and password:
            sql = """SELECT staff_id
            FROM soc_staff
            WHERE 
                username = %s AND
                user_password = %s"""
            
            # we match the encrypted input to the encrypted password in the db
            encrypt_string = lambda string: hashlib.sha256(string.encode('utf-8')).hexdigest() 
            
            values = [username, encrypt_string(password)]
            cols = ['staff_id']
            df = db.querydatafromdatabase(sql, values, cols)
            
            if df.shape[0]: # if query returns rows
                currentuserid = df['staff_id'][0]

            else:
                currentuserid = -1
                openalert = True
                
    elif eventid == 'sessionlogout' and pathname == '/logout': # reset the userid if logged out
        currentuserid = -1
        
    else:
        raise PreventUpdate
    
    return [openalert, currentuserid]

@app.callback(
    [
        Output('url', 'pathname'),
    ],
    [
        Input('currentuserid', 'modified_timestamp'),
    ],
    [
        State('currentuserid', 'data'), 
    ]
)
def routelogin(logintime, userid):
    ctx = callback_context
    if ctx.triggered:
        if userid > 0:
            url = '/home'
        else:
            url = '/'
    else:
        raise PreventUpdate
    return [url]



