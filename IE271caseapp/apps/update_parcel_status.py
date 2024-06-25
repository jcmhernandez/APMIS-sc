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
    html.H1("Update Parcel Status", className="display-4 text-center mt-5 mb-4"),
    dbc.Row([
        dbc.Col([
            dbc.Form(className="text-center", children=[
                dbc.Card([
                    dbc.CardBody(style={'text-align': 'left'}, children=[
                        dbc.Label("Parcel ID*", className="font-weight-bold"),
                        dcc.Dropdown(
                            id='parcel-id',
                            placeholder="Select Parcel ID",
                            style={'width': '100%'}
                        ),
                    ]),
                ], className="border-0"),
                dbc.Card([
                    dbc.CardBody(style={'text-align': 'left'}, children=[
                        dbc.Label("Status*", className="font-weight-bold"),
                        dcc.Dropdown(
                            id='status-id',
                            placeholder="Select Status",
                            style={'width': '100%'}
                        ),
                    ]),
                ], className="border-0"),
                dbc.Card([
                    dbc.CardBody(style={'text-align': 'left'}, children=[
                        dbc.Label("Location", className="font-weight-bold"),
                        dbc.Input(type="text", id="location"),
                    ]),
                ], className="border-0"),
                html.Br(),
                dbc.Button("Update Status", id="update-button1", color="primary", className="btn btn-lg btn-block"),
                html.Div(id='output-container-button1', className="mt-3"),
            ]),
        ], width={"size": 6, "offset": 3})  # Centering the column within the container
    ]),
    dcc.Interval(
        id='interval-component',
        interval=60000,  # in milliseconds
        n_intervals=0
    )
], fluid=True)

# Update status options callback
@app.callback(
    Output('status-id', 'options'),
    [Input('interval-component', 'n_intervals')]
)
def update_status_options(n):
    try:
        query = """
            SELECT status_id, status_desc
            FROM parcelstatus_mapping
            WHERE status_id  NOT IN (1,4);
        """
        df = db.querydatafromdatabase(query, values=[], dfcolumns=['status_id', 'status_desc'])
        options = [{'label': desc, 'value': str(status_id)} for status_id, desc in zip(df['status_id'], df['status_desc'])]
    except Exception as e:
        print(f"Error fetching data for status options: {e}")
        options = []

    return options

# Update parcel options callback
@app.callback(
    Output('parcel-id', 'options'),
    [Input('interval-component', 'n_intervals')]
)
def update_parcel_options(n):
    try:
        query = """
            SELECT DISTINCT parcel_id
            FROM parcel_status
            ORDER BY 1 ASC;
        """
        df = db.querydatafromdatabase(query, values=[], dfcolumns=['parcel_id'])
        options = [{'label': str(parcel_id), 'value': str(parcel_id)} for parcel_id in df['parcel_id']]
    except Exception as e:
        print(f"Error fetching data for parcel options: {e}")
        options = []

    return options

# Add new parcel submit callback
@app.callback(
    Output('output-container-button1', 'children'),
    [Input('update-button1', 'n_clicks')],
    [
        State('parcel-id', 'value'),
        State('status-id', 'value'),
        State('location', 'value'),
        State('currentuserid', 'data')  # Include 'currentuserid' as a State
    ]
)
def add_new_parcel_submit(n_clicks, parcel_id, status_id, location, currentuserid):
    if not n_clicks:
        raise PreventUpdate

    alert_open = True
    alert_color = 'danger'
    alert_text = 'Failed to add new parcel.'

    # print(currentuserid)

    if not all([parcel_id, status_id, location, currentuserid]):
        alert_text = 'Check your inputs. Please fill in all the required fields.'
        print("Not all fields filled:", parcel_id, status_id, location, currentuserid)
    else:
        try:
            sql = '''
                INSERT INTO parcel_status (parcel_id, status_id, update_timestamp, staff_id, location)
                VALUES (%s, %s, %s, %s, %s)
            '''
            values = [parcel_id, status_id, datetime.now(), currentuserid, location]
            db.modifydatabase(sql, values)

            alert_open = True
            alert_color = 'success'
            alert_text = 'New parcel added successfully.'
        except Exception as e:
            alert_text = f'Failed to add new parcel: {str(e)}'
            print("Exception occurred:", e)

    return [html.Div(alert_text, className=f'alert alert-{alert_color}', role='alert')]
