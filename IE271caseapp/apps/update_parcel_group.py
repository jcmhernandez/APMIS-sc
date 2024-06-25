import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from apps import dbconnect as db
from app import app
from datetime import datetime

dash.register_page(__name__, path='/update_parcel_group')

# Function to fetch available parcel group IDs
def get_available_parcel_group_ids():
    try:
        query = "SELECT parcelgroup_id FROM parcel_group ORDER BY 1 ASC"
        result = db.querydatafromdatabase(query, values=[], dfcolumns=['parcelgroup_id'])
        return result['parcelgroup_id'].tolist()
    except Exception as e:
        print(f"Error fetching parcel group IDs: {e}")
        return []

# Define the layout without directly populating dropdown options
layout = dbc.Container([
    html.H1("Update Parcel Group", className="display-4 text-center mt-5 mb-4"),
    dbc.Form([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label('Parcel Group ID:', className="font-weight-bold"),
                        dcc.Dropdown(id='update-group-id', className="mb-3"),
                        dbc.Label('3PL Rider ID:', className="font-weight-bold"),
                        dbc.Input(id='pl3-rider-id', type='text', className="form-control mb-3"),
                        dbc.Label('Status of Parcels:', className="font-weight-bold"),
                        dcc.Dropdown(id='dispatch-dropdown', options=[{'label': 'Dispatched', 'value': 'Dispatched'}], value='Dispatched', className="mb-3"),
                        dbc.Button('Update', id='update-button', color="primary", className="btn btn-lg btn-block mb-3"),
                        html.Div(id='output-div', className="mt-3")
                    ]),
                ], className="border-0"),
            ], width=6, align='center')
        ], justify='center')
    ], className="container-fluid"),

    # Interval component to trigger callback periodically (optional)
    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0)
])

# Callback to populate dropdown options on page load
@app.callback(
    Output('update-group-id', 'options'),
    [Input('interval-component', 'n_intervals')]
)
def populate_group_id_dropdown(n):
    if n == 0:  # Only fetch data on the initial page load
        available_ids = get_available_parcel_group_ids()
        options = [{'label': group_id, 'value': group_id} for group_id in available_ids]
        return options
    else:
        # If n_intervals > 0, options remain unchanged (prevents unnecessary fetching)
        raise dash.exceptions.PreventUpdate



@app.callback(
    Output('output-div', 'children'),
    [Input('update-button', 'n_clicks')],
    [State('update-group-id', 'value'),
     State('pl3-rider-id', 'value'),
     State('currentuserid', 'data')]
)
def update_parcel_group(n_clicks, group_id, pl3_rider_id, currentuserid):
    # print("Callback triggered!")
    if n_clicks is None:
        return None

    try:
        # Update the PL3 Rider ID in parcel_group table
        query_update_parcel_group = "UPDATE parcel_group SET pl3_riderid = %s WHERE parcelgroup_id = %s"
        values_update_parcel_group = (pl3_rider_id, group_id)
        db.modifydatabase(query_update_parcel_group, values_update_parcel_group)

        # Retrieve all parcel_ids for the given group_id
        query_select_parcels = "SELECT parcel_id FROM parcel WHERE parcelgroup_id = %s"
        values_select_parcels = (group_id,)
        parcel_ids_df = db.querydatafromdatabase(query_select_parcels, values_select_parcels, dfcolumns=['parcel_id'])

        # # Debugging print statement to check the retrieved parcel_ids
        # print("Retrieved parcel_ids:", parcel_ids_df)

        # Convert dataframe to list of parcel_ids if necessary
        parcel_ids = parcel_ids_df['parcel_id'].tolist() if not parcel_ids_df.empty else []
        
        # # Debugging print statement to check the list of parcel_ids
        # print("List of parcel_ids:", parcel_ids)

        # Insert a new status for each parcel
        query_insert_parcel_status = "INSERT INTO parcel_status (parcel_id, status_id, update_timestamp, staff_id, location) VALUES (%s, %s, %s, %s, %s)"
        for parcel_id in parcel_ids:
            values_insert_parcel_status = (parcel_id, 4, datetime.now(), currentuserid, '')
            db.modifydatabase(query_insert_parcel_status, values_insert_parcel_status)

        return dbc.Alert("Parcel Group updated successfully!", color="success")
    except Exception as e:
        print("Error:", str(e))
        return dbc.Alert(f"Error updating parcel group: {e}", color="danger")

