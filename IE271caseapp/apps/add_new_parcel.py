import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app
from apps import dbconnect as db
from dash.exceptions import PreventUpdate
from datetime import datetime


dash.register_page(__name__, path='/')



layout = dbc.Container([
    html.H1("Add New Parcel", className="display-4 text-center mt-5 mb-4"),
    dbc.Form([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Parcel ID*", className="font-weight-bold"),
                        dbc.Input(type="text", id="parcel-id"),
                    ]),
                ], className="border-0"),
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Parcel Weight*", className="font-weight-bold"),
                        dbc.Input(type="number", id="parcel-weight"),
                    ]),
                ], className="border-0"),
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Seller ID*", className="font-weight-bold"),
                        dbc.Input(type="text", id="seller-id"),
                    ]),
                ], className="border-0"),
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("3PL Rider ID*", className="font-weight-bold"),
                        dbc.Input(type="text", id="3pl-rider-id"),
                    ]),
                ], className="border-0"),
            ], width=4, align='center'),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Is Fragile?*", className="font-weight-bold"),
                        dbc.RadioItems(
                            options=[
                                {"label": "Yes", "value": True},
                                {"label": "No", "value": False}
                            ],
                            id="is-fragile",
                            inline=True
                        ),
                    ]),
                ], className="border-0"),
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Location*", className="font-weight-bold"),
                        dbc.Input(type="text", id="location"),
                    ]),
                ], className="border-0"),
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Buyer ID*", className="font-weight-bold"),
                        dbc.Input(type="text", id="buyer-id"),
                    ]),
                ], className="border-0"),
                dbc.Card([], className="border-0", style={"visibility": "hidden", "height": "90px"}),
            ], width=4, align='center')
        ], justify='center'),
        dbc.Row([
            dbc.Col([
                html.Br(),
                html.H3("Seller Information", className="font-weight-bold")
            ], width=8, align='center')
        ], justify='center'),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Region"),
                        dbc.Input(type="text", id="seller-region"),
                    ]),
                ], className="border-0"),
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("City"),
                        dbc.Input(type="text", id="seller-city"),
                    ]),
                ], className="border-0"),
            ], width=4, align='center', className="align-items-center"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Province"),
                        dbc.Input(type="text", id="seller-province"),
                    ]),
                ], className="border-0"),
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Location Detail"),
                        dbc.Input(type="text", id="seller-locdetail"),
                    ]),
                ], className="border-0"),
            ], width=4, align='center', className="align-items-center")
        ], justify='center'),
        dbc.Row([
            dbc.Col([
                html.Br(),
                html.H3("Buyer Information", className="font-weight-bold")
            ], width=8, align='center')
        ], justify='center'),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Region"),
                        dbc.Input(type="text", id="buyer-region"),
                    ]),
                ], className="border-0"),
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("City"),
                        dbc.Input(type="text", id="buyer-city"),
                    ]),
                ], className="border-0"),
            ], width=4, align='center', className="align-items-center"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Province"),
                        dbc.Input(type="text", id="buyer-province"),
                    ]),
                ], className="border-0"),
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Location Detail"),
                        dbc.Input(type="text", id="buyer-locdetail"),
                    ]),
                ], className="border-0"),
            ], width=4, align='center', className="align-items-center")
        ], justify='center'),
        html.Br(),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Button("Submit", id="submit-button", color="primary", className="btn btn-lg d-block mx-auto"),
                html.Div(id='output-container-button')        
            ], width=4)
        ], justify='center'),
        html.Br(),
        html.Br(),
        html.Br(),
    ]),
], fluid=True)



# Define callback function
@app.callback(
    Output('output-container-button', 'children'),
    [Input('submit-button', 'n_clicks')],
    [
        State('parcel-id', 'value'),
        State('is-fragile', 'value'),
        State('parcel-weight', 'value'),
        State('location', 'value'),
        State('seller-id', 'value'),
        State('buyer-id', 'value'),
        State('seller-region', 'value'),
        State('seller-province', 'value'),
        State('seller-city', 'value'),
        State('seller-locdetail', 'value'),
        State('buyer-region', 'value'),
        State('buyer-province', 'value'),
        State('buyer-city', 'value'),
        State('buyer-locdetail', 'value'),
        State('3pl-rider-id', 'value'),
        State('currentuserid', 'data')
    ]
)

def add_new_parcel_submit(n_clicks, parcel_id, is_fragile, parcel_weight, location,
                          seller_id, buyer_id, seller_region, seller_province,
                          seller_city, seller_locdetail, buyer_region,
                          buyer_province, buyer_city, buyer_locdetail, 
                          pl3_rider_id, currentuserid):

    if not n_clicks:
        raise PreventUpdate

    alert_open = True
    alert_color = 'danger'
    alert_text = 'Failed to add new parcel.'
    modal_open = False

    if not all([parcel_id, (is_fragile is not None), parcel_weight, seller_id, buyer_id, location, pl3_rider_id]):
        alert_text = 'Check your inputs. Please fill in all the required fields.'

    else:
        try:
            # Constructing the SQL query
            sql = '''
                INSERT INTO parcel (parcel_id, is_fragile, parcel_weight, seller_id, buyer_id, pl3_riderid
            '''
            # Adding the values to the values list
            values = [parcel_id, int(is_fragile), parcel_weight, seller_id, buyer_id, pl3_rider_id]

            # Adding optional fields to both SQL query and values list if they have values
            optional_fields = [
                ('seller_region', seller_region),
                ('seller_province', seller_province),
                ('seller_city', seller_city),
                ('seller_locdetail', seller_locdetail),
                ('buyer_region', buyer_region),
                ('buyer_province', buyer_province),
                ('buyer_city', buyer_city),
                ('buyer_locdetail', buyer_locdetail)
            ]
            for field, value in optional_fields:
                if value:
                    sql += f', {field}'
                    values.append(value)

            sql += ') VALUES (' + ', '.join(['%s'] * len(values)) + ')'
            
            db.modifydatabase(sql, values)

            # Constructing the SQL query
            sql = '''
                INSERT INTO parcel_status (parcel_id, status_id, update_timestamp, location, staff_id
            '''
            # Adding the values to the values list
            values = [parcel_id, 1, datetime.now(), location, currentuserid]

            sql += ') VALUES (' + ', '.join(['%s'] * len(values)) + ')'
            
            db.modifydatabase(sql, values)


            alert_open = True
            alert_color = 'success'
            alert_text = 'New parcel added successfully.'
            modal_open = True
        except Exception as e:
            alert_text = f'Failed to add new parcel: {str(e)}'

    return [html.Div(alert_text, className=f'alert alert-{alert_color}', role='alert'), modal_open]













