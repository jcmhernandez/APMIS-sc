# Dash related dependencies
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Importing the app from the main file
from app import app

# Define layout for the home page
layout = html.Div([
    html.H1("Welcome to APMIS!", className="display-4 text-center mt-5 mb-4"),
    html.H5("Analytical Parcel Management Information System", className="text-muted text-center mb-4"),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H2("Parcel Management", className="card-title text-primary"),
                    html.P("Manage parcels with ease"),
                    dcc.Link('Go to Parcel Management', href='/parcel_management', className="btn btn-primary btn-block stretched-link")
                ]),
                className="mb-4 border-0 shadow-sm h-100",
                style={"background-color": "#F0F0F0"}  # Light grey background
            ),
            width=4
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H2("Dashboard", className="card-title text-success"),
                    html.P("Visualize your data"),
                    dcc.Link('Go to Dashboard', href='/dashboard', className="btn btn-success btn-block stretched-link")
                ]),
                className="mb-4 border-0 shadow-sm h-100",
                style={"background-color": "#F0F0F0"}  # Light grey background
            ),
            width=4
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H2("Parcel Forecast", className="card-title text-info"),
                    html.P("Predict future trends"),
                    dcc.Link('Go to Parcel Forecast', href='/parcel_forecast', className="btn btn-info btn-block stretched-link")
                ]),
                className="mb-4 border-0 shadow-sm h-100",
                style={"background-color": "#F0F0F0"}  # Light grey background
            ),
            width=4
        )
    ]),
], className="container")


# If you want to hide the navbar, you can do it here
# app.layout = layout