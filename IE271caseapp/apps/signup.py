import hashlib
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from apps import dbconnect as db

layout = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H1('APMIS', className="text-center mb-4"),
                html.H4('Sign Up', className="text-center mb-4"),
                dbc.Alert('Please supply details.', color="danger", id='signup_alert', is_open=False),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Username", className="font-weight-bold"),
                                dbc.Input(type="text", id="signup_username", placeholder="Enter a username"),
                            ],
                            width=12,
                            className="mb-3",
                        ),
                    ],
                    className="justify-content-center",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Password", className="font-weight-bold"),
                                dbc.Input(type="password", id="signup_password", placeholder="Enter a password"),
                            ],
                            width=12,
                            className="mb-3",
                        ),
                    ],
                    className="justify-content-center",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Confirm Password", className="font-weight-bold"),
                                dbc.Input(type="password", id="signup_passwordconf", placeholder="Re-type the password"),
                            ],
                            width=12,
                            className="mb-3",
                        ),
                    ],
                    className="justify-content-center",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Given Name", className="font-weight-bold"),
                                dbc.Input(type="text", id="signup_givenname", placeholder="Enter your given name"),
                            ],
                            width=12,
                            className="mb-3",
                        ),
                    ],
                    className="justify-content-center",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Surname", className="font-weight-bold"),
                                dbc.Input(type="text", id="signup_surname", placeholder="Enter your surname"),
                            ],
                            width=12,
                            className="mb-3",
                        ),
                    ],
                    className="justify-content-center",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Birthdate", className="font-weight-bold"),
                                dbc.Input(type="date", id="signup_birthdate"),
                            ],
                            width=12,
                            className="mb-3",
                        ),
                    ],
                    className="justify-content-center",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Phone Number", className="font-weight-bold"),
                                dbc.Input(type="text", id="signup_phone", placeholder="Enter your phone number"),
                            ],
                            width=12,
                            className="mb-3",
                        ),
                    ],
                    className="justify-content-center",
                ),
                dbc.Button('Sign up', id='signup_signupbtn', className="btn-block"),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("User Saved")),
                        dbc.ModalBody("User has been saved", id='signup_confirmation'),
                        dbc.ModalFooter(
                            dbc.Button("Okay", href='/', className="btn btn-secondary")
                        ),
                    ],
                    id="signup_modal",
                    is_open=False,
                ),
            ]
        ),
    ],
    className="container mt-5",
    style={"background-color": "#f0f0f0", "padding": "20px", "max-width": "500px", "margin": "auto"}
)

# Disable the signup button if passwords do not match or fields are missing
@app.callback(
    [
        Output('signup_signupbtn', 'disabled'),
        Output('signup_signupbtn', 'color'),
    ],
    [
        Input('signup_username', 'value'),
        Input('signup_password', 'value'),
        Input('signup_passwordconf', 'value'),
        Input('signup_givenname', 'value'),
        Input('signup_surname', 'value'),
        Input('signup_birthdate', 'value'),
        Input('signup_phone', 'value'),
    ]
)
def update_button_state(username, password, passwordconf, givenname, surname, birthdate, phone):
    # Check if all fields are filled and the passwords match
    all_fields_filled = all([username, password, passwordconf, givenname, surname, birthdate, phone])
    passwords_match = password == passwordconf

    if all_fields_filled and passwords_match:
        return [False, "primary"]  # Enable button and set color to primary
    else:
        return [True, "secondary"]  # Disable button and set color to secondary

# To save the user
@app.callback(
    [
        Output('signup_alert', 'is_open'),
        Output('signup_modal', 'is_open')   
    ],
    [
        Input('signup_signupbtn', 'n_clicks')
    ],
    [
        State('signup_username', 'value'),
        State('signup_password', 'value'),
        State('signup_givenname', 'value'),
        State('signup_surname', 'value'),
        State('signup_birthdate', 'value'),
        State('signup_phone', 'value'),
    ]
)
def saveuser(signupbtn, username, password, givenname, surname, birthdate, phone):
    openalert = openmodal = False
    if signupbtn:
        if username and password and givenname and surname and birthdate and phone:
            sql = """INSERT INTO soc_staff (username, user_password, staff_givenname, staff_surname, staff_birthdate, staff_phone)
                     VALUES (%s, %s, %s, %s, %s, %s)"""  
            # This lambda function encrypts the password before saving it
            encrypt_string = lambda string: hashlib.sha256(string.encode('utf-8')).hexdigest()  
            values = [username, encrypt_string(password), givenname, surname, birthdate, phone]
            try:
                db.modifydatabase(sql, values)
                openmodal = True
            except Exception as e:
                openalert = True
        else:
            openalert = True
    else:
        raise PreventUpdate
    return [openalert, openmodal]
