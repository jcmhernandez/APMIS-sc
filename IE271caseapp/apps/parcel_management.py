import dash
from dash import html, callback_context
from dash import dcc
from dash.dependencies import Input, Output
from app import app
from apps import add_new_parcel_group, add_new_parcel, update_parcel_group, update_parcel_status

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H1('Parcel Management Page', className="display-4 text-center mt-5 mb-4"),
    html.Div('Welcome to our Parcel Management page. Here you can manage parcel groups and parcels.', className="text-center"),
    html.Br(),
    html.Div([
        # Left column
        html.Div([
            dcc.Link(html.Button('Add New Parcel', id='add_new_parcel_btn', n_clicks=0, className="btn btn-success btn-lg btn-block mb-3"), href='/parcel_management/add_new_parcel'),
            dcc.Link(html.Button('Add New Parcel Group', id='add_new_group_btn', n_clicks=0, className="btn btn-success btn-lg btn-block"), href='/parcel_management/add_new_group')       
        ], className='col-lg-6'),
        
        # Right column
        html.Div([
            dcc.Link(html.Button('Update Parcel Status', id='update_status_btn', n_clicks=0, className="btn btn-primary btn-lg btn-block mb-3"), href='/parcel_management/update_parcel_status'),
            dcc.Link(html.Button('Update Parcel Group', id='update_group_btn', n_clicks=0, className="btn btn-primary btn-lg btn-block"), href='/parcel_management/update_parcel_group')
        ], className='col-lg-6')
    ], className='row justify-content-center')
])





