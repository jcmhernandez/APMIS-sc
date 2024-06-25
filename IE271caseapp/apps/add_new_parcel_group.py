import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from apps import dbconnect as db
from app import app
from datetime import datetime

dash.register_page(__name__, path='/')

# Function to get the next available group ID (max + 1)
def get_next_group_id():
    try:
        query = "SELECT MAX(parcelgroup_id) AS max_group_id FROM parcel_group;"
        result = db.querydatafromdatabase(query, values=[], dfcolumns=['max_group_id'])
        max_group_id = result.iloc[0]['max_group_id']
        return max_group_id + 1 if max_group_id is not None else 1
    except Exception as e:
        print(f"Error fetching next group ID: {e}")
        return 1  # Default to 1 if there's an error



layout = dbc.Container([
    html.H1("Add New Parcel Group", className="display-4 text-center mt-5 mb-4"),
    dbc.Form([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label('Parcel Group ID:', className="font-weight-bold"),
                        dcc.Input(id='next-group-id', type='text', value=get_next_group_id(), disabled=True, className="form-control mb-3"),
                    ]),
                ], className="border-0"),
            ], width=6),
        ], justify="center"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label('Parcel IDs (select any number):', className="font-weight-bold"),
                        dcc.Dropdown(id='parcel-id2', multi=True, className="mb-3"),
                    ]),
                ], className="border-0"),
            ], width=6),
        ], justify="center"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Button('Submit', id='submit-button22', color="primary", className="btn btn-lg btn-block"),
                        html.Div(id='output-div22', className="mt-3"),
                        html.Div(id='hidden-div', style={'display': 'none'})  # Hidden div to trigger the update of next-group-id
                    ]),
                ], className="border-0"),
            ], width=6),
        ], justify="center"),
    ], className="container"),
    dcc.Interval(
        id='interval-component',
        interval=60000,  # in milliseconds
        n_intervals=0
    )
])





@app.callback(
    [Output('output-div22', 'children'),
     Output('next-group-id', 'value'),
     Output('parcel-id2', 'value')],  # Reset the parcel ID dropdown
    [Input('submit-button22', 'n_clicks')],
    [State('next-group-id', 'value'),
     State('parcel-id2', 'value'),
     State('currentuserid', 'data')
]
)
def insert_parcel_group(n_clicks, group_id, parcel_ids, currentuserid):
    print("Callback triggered!")
    if n_clicks is None:
        return False, group_id, None  # Return the current group ID and reset the parcel ID dropdown if no clicks

    try:
        if parcel_ids:
            # Get the next group ID
            next_group_id = int(get_next_group_id())
            # print('currentuserid')
            # print(currentuserid)
            # print('parcel_ids')
            # print(parcel_ids)

            
            # Insert into parcel_group table
            query_insert_parcel_group = "INSERT INTO parcel_group (parcelgroup_id, pl3_riderid, staff_id, update_timestamp) VALUES (%s, %s, %s, %s)"
            values_insert_parcel_group = (next_group_id, None, currentuserid, datetime.now())
            db.modifydatabase(query_insert_parcel_group, values_insert_parcel_group)
        
            # Update the parcelgroup_id for all entries with the specific parcel_id in parcel_status table
            for parcel_id in parcel_ids:
                query_update = "UPDATE parcel SET parcelgroup_id = %s WHERE parcel_id = %s"
                values_update = (next_group_id, parcel_id)
                db.modifydatabase(query_update, values_update)

            # Return success message, next group ID, and reset parcel IDs
            return dbc.Alert("Parcel IDs inserted successfully into the database!", color="success"), get_next_group_id(), None
        else:
            return dbc.Alert("No parcel IDs selected!", color="warning"), group_id, None
    except Exception as e:
        print(f"Error inserting parcel IDs: {e}")
        return dbc.Alert(f"Error inserting parcel IDs: {e}", color="danger"), group_id, None




@app.callback(
    Output('parcel-id2', 'options'),
    [Input('interval-component', 'n_intervals')]
)
def update_parcel_options(n):
    try:
        # Fetch data from the parcel_status table
        query = """
            SELECT parcel_id
            FROM parcel_status;
        """
        df = db.querydatafromdatabase(query, values=[], dfcolumns=['parcel_id'])
        # Convert DataFrame to a list of dictionaries suitable for dropdown options
        options = [{'label': str(parcel_id), 'value': str(parcel_id)} for parcel_id in df['parcel_id']]
    except Exception as e:
        print(f"Error fetching data for parcel options: {e}")
        options = []

    return options
