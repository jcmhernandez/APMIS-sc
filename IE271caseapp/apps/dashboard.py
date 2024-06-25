from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go
from app import app
from apps import dbconnect as db
from datetime import datetime

import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



layout = html.Div([
    html.H2('Dashboards', className="display-4 text-center mt-5 mb-4"),
    html.Hr(),
    dbc.Card([
        dbc.CardHeader(html.H3('View Reports', className="card-title")),
        dbc.CardBody([
            html.Div([
                dbc.Form([
                    dbc.Row([
                        dbc.Label("Status", width=1, className="font-weight-bold"),
                        dbc.Col(
                            dcc.Dropdown(
                                id='dashboard_statusfilter',
                                placeholder='Select status',
                                searchable=True,
                                options=[],
                                multi=True,
                                className="w-100"
                            ),
                            width=2
                        ),
                        dbc.Label("Date Range", width=1, className="font-weight-bold"),
                        dbc.Col(
                            dcc.DatePickerRange(
                                id='date_range_picker',
                                display_format='YYYY-MM-DD',
                                start_date_placeholder_text='Start Date',
                                end_date_placeholder_text='End Date',
                                clearable=True,
                                className="w-100"
                            ),
                            width=5
                        ),
                        dbc.Col(
                            dbc.Button("Reset Filters", id="reset-button", color="secondary", className="w-100"),
                            width=2
                        )
                    ], className='mb-5')
                ]),
                
                # First row
                dbc.Row([
                    # Left column for cards
                    dbc.Col([
                        dcc.Loading(
                            id="loading",
                            type="circle",
                            children=[
                                html.Div(id='card-container', children=[
                                    html.Div(id='total-orders', className='card'),
                                    html.Div(id='total-sales', className='card'),
                                    html.Div(id='average-price', className='card')
                                ])
                            ]
                        ),
                        dcc.Interval(
                            id='interval-component',
                            interval=60000,  # in milliseconds
                            n_intervals=0
                        )
                    ], width=4),
                    
                    # Middle column for reportbodystatus
                    dbc.Col([
                        dcc.Loading(
                            id="reportbodystatusload",
                            children=[
                                dcc.Graph(id='reportbodystatus')
                            ],
                            type="circle"
                        )
                    ], width=4),
                    
                    # Right column for sla_left_plot
                    dbc.Col([
                        dcc.Loading(
                            id="reportbodystatusload2",
                            children=[
                                dcc.Graph(id='sla_left_plot')
                            ],
                            type="circle"
                        )
                    ], width=4)
                ], className="mb-5"),  # Added margin bottom
                
                # Second row
                dbc.Row([
                    # Full-width column for reportbodyload
                    dbc.Col([
                        dcc.Loading(
                            id="reportbodyload",
                            children=[
                                dcc.Graph(id='reportbodyreceipts')
                            ],
                            type="circle"
                        )
                    ], width=12, align='center', style={'height': '500px', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center'})
                ])
                
            ])
        ])
    ])
])


# Callback to update the card values with the metrics fetched from SQL
@app.callback(
    [Output('total-orders', 'children'),
     Output('total-sales', 'children'),
     Output('average-price', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_cards(n):

    sql_queries = {
        'parcel_count_for_processing': """
            SELECT COUNT(DISTINCT parcel_id) AS parcel_count_for_processing
            FROM parcel_status
            WHERE status_id != 4;
        """,
        'average_processing_time_L7D_in_hours': """
            SELECT ROUND(AVG(EXTRACT(EPOCH FROM (CAST(ps4.update_timestamp AS TIMESTAMP) - CAST(ps1.update_timestamp AS TIMESTAMP)))/3600)::numeric, 2) AS average_processing_time_L7D_in_hours
            FROM parcel_status ps1
            JOIN parcel_status ps4 ON ps1.parcel_id = ps4.parcel_id
            WHERE ps4.status_id = 4
            AND ps4.update_timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days';
        """,
        'total_backlog_parcels': """
            SELECT COUNT(*) AS total_backlog_parcels
            FROM (
                SELECT ps1.parcel_id
                FROM parcel_status ps1
                LEFT JOIN parcel_status ps4 
                    ON ps1.parcel_id = ps4.parcel_id 
                    AND ps4.status_id = 4
                WHERE ps1.status_id = 1
                AND EXTRACT(EPOCH FROM (COALESCE(ps4.update_timestamp, CURRENT_TIMESTAMP) - ps1.update_timestamp))/3600 > 24
            ) AS backlog_parcels;
        """
    }


    card_contents = []

    # Function to format number with commas and 1 decimal place
    def format_number(value):
        if value is None:
            return ''
        else:
            formatted_value = f"{value:,.0f}"
            return formatted_value

    for metric, query in sql_queries.items():
        try:
            # Execute the SQL query to fetch data from the database
            df = db.querydatafromdatabase(query, values=[], dfcolumns=['value'])
            value = df['value'].iloc[0]  # Extract the value from the DataFrame
        except Exception as e:
            print(f"Error fetching data for {metric}: {e}")
            value = None

        formatted_value = format_number(value)  # Format the value with commas and 1 decimal place

        card = html.Div([
            html.Div([
                html.H4(metric.replace('_', ' ').title(), style={'color': 'rgb(77, 77, 77)', 'font-weight': 'bold', 'margin-bottom': '5px', 'font-size': '16px', 'text-align': 'center'})
            ], style={'width': '33%', 'float': 'left', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'background-color': 'white', 'border': 'none' }),
            html.Div([
                html.Div([
                    html.H2(formatted_value, style={'color': 'white', 'font-size': '48px', 'margin': '0', 'text-align': 'center'}),
                ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '100%', 'width': '100%'})
            ], style={'width': 'calc(66% - 2px)', 'float': 'left', 'height': '100%', 'background-color': 'rgb(13,110,253)', 'border': 'none' })
        ], style={'background-color': 'white', 'padding': '20px', 'margin-bottom': '20px', 'overflow': 'hidden', 'border': 'none', 'box-shadow': 'none'})

        card_contents.append(card)

    return card_contents


# # Run the Dash app
# if __name__ == '__main__':
#     app.run_server(debug=True)







#callback to populate dropdown options
@app.callback(
    [
        Output('dashboard_statusfilter', 'options'),
        
    ],
    [
        Input('url', 'pathname'),
    ]
)
def moviehome_loadmovielist(pathname):
    if pathname == '/dashboard':
        sql = """ SELECT DISTINCT b.status_desc as label, 
                    a.status_id as value
                FROM parcel_status a
                JOIN parcelstatus_mapping b ON a.status_id=b.status_id
            """


        # sql = """ SELECT country_name as label, 
        #             country_id as value
        #         FROM countries
        #         WHERE country_delete_ind = %s
        #     """
        columns = ['label', 'value']
        values = [False]
        dfsql = db.querydatafromdatabase(sql, values, columns)

        # print (dfsql)

        return [dfsql.to_dict('records')]
    
    else:
        raise PreventUpdate


#callback for figure and table
@app.callback(
    [

        Output('reportbodyreceipts', 'figure')
    ],
    [
        Input('url', 'pathname'),
        Input('dashboard_statusfilter', 'value'),
        Input('date_range_picker', 'start_date'),
        Input('date_range_picker', 'end_date')
    ]
)
def moviehome_loadmovielist(pathname, filter_country, start_date, end_date):
    if pathname == '/dashboard': 
        sql = """ WITH parcel_counts AS (
    SELECT 
        CASE 
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 0 AND 1 THEN '12:00 AM - 1:00 AM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 1 AND 2 THEN '1:00 AM - 2:00 AM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 2 AND 3 THEN '2:00 AM - 3:00 AM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 3 AND 4 THEN '3:00 AM - 4:00 AM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 4 AND 5 THEN '4:00 AM - 5:00 AM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 5 AND 6 THEN '5:00 AM - 6:00 AM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 6 AND 7 THEN '6:00 AM - 7:00 AM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 7 AND 8 THEN '7:00 AM - 8:00 AM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 8 AND 9 THEN '8:00 AM - 9:00 AM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 9 AND 10 THEN '9:00 AM - 10:00 AM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 10 AND 11 THEN '10:00 AM - 11:00 AM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 11 AND 12 THEN '11:00 AM - 12:00 PM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 12 AND 13 THEN '12:00 PM - 1:00 PM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 13 AND 14 THEN '1:00 PM - 2:00 PM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 14 AND 15 THEN '2:00 PM - 3:00 PM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 15 AND 16 THEN '3:00 PM - 4:00 PM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 16 AND 17 THEN '4:00 PM - 5:00 PM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 17 AND 18 THEN '5:00 PM - 6:00 PM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 18 AND 19 THEN '6:00 PM - 7:00 PM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 19 AND 20 THEN '7:00 PM - 8:00 PM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 20 AND 21 THEN '8:00 PM - 9:00 PM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 21 AND 22 THEN '9:00 PM - 10:00 PM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 22 AND 23 THEN '10:00 PM - 11:00 PM'
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 23 AND 24 THEN '11:00 PM - 12:00 AM'
        END AS time_interval,
        CASE 
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 0 AND 1 THEN 1
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 1 AND 2 THEN 2
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 2 AND 3 THEN 3
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 3 AND 4 THEN 4
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 4 AND 5 THEN 5
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 5 AND 6 THEN 6
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 6 AND 7 THEN 7
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 7 AND 8 THEN 8
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 8 AND 9 THEN 9
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 9 AND 10 THEN 10
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 10 AND 11 THEN 11
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 11 AND 12 THEN 12
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 12 AND 13 THEN 13
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 13 AND 14 THEN 14
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 14 AND 15 THEN 15
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 15 AND 16 THEN 16
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 16 AND 17 THEN 17
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 17 AND 18 THEN 18
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 18 AND 19 THEN 19
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 19 AND 20 THEN 20
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 20 AND 21 THEN 21
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 21 AND 22 THEN 22
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 22 AND 23 THEN 23
            WHEN EXTRACT(HOUR FROM update_timestamp) BETWEEN 23 AND 24 THEN 24
        END AS sort_col,
        COUNT(parcel_id) AS parcel_count,
        status_id,
        cast(update_timestamp as date) as date
    FROM 
        parcel_status
	WHERE TRUE
            """
            #     sql = """ select 
            #         sum(count(parcel_id)) OVER (order by update_timestamp) as parcel_count
            #         , a.status_id
            #         , update_timestamp
            #     from parcel_status a
            #     JOIN parcelstatus_mapping b ON a.status_id = b.status_id
            #     WHERE TRUE
            # """
        values = []

        if filter_country:
            sql += " AND status_id IN %s"
            values += [tuple(filter_country)]

        if start_date and end_date:
            sql += " AND update_timestamp BETWEEN %s AND %s"
            values += [start_date, end_date]
        
        sql += """GROUP BY 
        time_interval,
	 	sort_col,
        status_id,
        date
        )
        SELECT 
            AVG(parcel_count) AS avg_parcel_count_per_day,
            time_interval

        FROM 
            parcel_counts
        GROUP BY 
            time_interval, sort_col
        
                ORDER BY 
            sort_col ASC     
                    
        """

        cols = ['Avg Parcel Count', 'Update Timestamp']

        df = db.querydatafromdatabase(sql, values, cols)



        if df.empty:
            # Return a message or empty values
            return "No data available", {}



        df = df[['Avg Parcel Count', 'Update Timestamp']]

        # listofgenre = df["Status"].unique().tolist()

        # Compute cumulative sum of parcel count
        df['Cumulative Avg Parcel Count'] = df['Avg Parcel Count'].cumsum()

        # Sort the DataFrame by "Update Timestamp"
        # df.sort_values(by='Update Timestamp', inplace=True)




        # Convert 'Cumulative Avg Parcel Count' column to numeric
        df['Cumulative Avg Parcel Count'] = pd.to_numeric(df['Cumulative Avg Parcel Count'])
        df['Avg Parcel Count'] = pd.to_numeric(df['Avg Parcel Count'])

        # Round off values to 2 decimal places
        df[['Avg Parcel Count', 'Cumulative Avg Parcel Count']] = df[['Avg Parcel Count', 'Cumulative Avg Parcel Count']].round(2)

        # Print the DataFrame
        # logger.info("DataFrame from SQL query:")
        # logger.info(df)




        tracebar = go.Bar(
            y=df['Avg Parcel Count'],
            x=df["Update Timestamp"],
            name='Avg Parcel Count',
            marker=dict(color='rgb(13,110,253)')
        )

        traceline = go.Scatter(
            y=df['Cumulative Avg Parcel Count'],
            x=df["Update Timestamp"],
            mode='lines+markers',
            name='Cumulative Avg Parcel Count',
            yaxis='y2',
            line=dict(color='rgb(255,193,7)'),
            marker=dict(color='rgb(255,193,7)')
        )

        data = [tracebar, traceline]


        layout = go.Layout(
            title={'text': "Average Parcel Count", 'x': 0.5, 'xanchor': 'center'},  # Title centered horizontally
            legend={'orientation': 'h', 'x': 0.5, 'y': 3.1, 'xanchor': 'center', 'yanchor': 'middle'},  # Legend below the title and centered horizontally
            yaxis={'title': "Average Parcel Count", 'showgrid': False},
            yaxis2={'title': "Cumulative Average Parcel Count", 'overlaying': 'y', 'side': 'right', 'showgrid': False},
            xaxis={'title': "Time of Day", 'range': [df["Update Timestamp"].min(), df["Update Timestamp"].max()], 'showgrid': False},
            height=600,
            width=1200,
            margin={'b': 100, 't': 80, 'l': 100, 'r': 100},  # Adjusted margin to accommodate title and legend
            hovermode='closest',
            autosize=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )





        figure3 = {'data':data, 'layout':layout }
        


        
        if df.shape[0]:
            return [figure3]
        else:
            return ['No records to display', 'No figure to display']
    else:
        raise PreventUpdate

#Callback for the barchart per parcel status
@app.callback(
    Output('reportbodystatus', 'figure'),
    [Input('url', 'pathname'),
     Input('dashboard_statusfilter', 'value'),
     Input('date_range_picker', 'start_date'),
     Input('date_range_picker', 'end_date')]
)
def update_status_graph(pathname, filter_status, start_date, end_date):
    if pathname == '/dashboard':
        # Base query to get the highest-priority status for each parcel_id
        sql_status = """
            WITH ranked_parcels AS (
                SELECT 
                    parcel_id, 
                    status_id,
                    update_timestamp,
                    ROW_NUMBER() OVER (PARTITION BY parcel_id ORDER BY 
                                       CASE 
                                           WHEN status_id = 3 THEN 1
                                           WHEN status_id = 2 THEN 2
                                           WHEN status_id = 1 THEN 3
                                       END, 
                                       update_timestamp DESC) AS rnk
                FROM parcel_status
                WHERE parcel_id NOT IN (
                    SELECT DISTINCT parcel_id
                    FROM parcel_status
                    WHERE status_id = 4
                )
            )
            SELECT 
                CASE 
                    WHEN status_id = 1 THEN 'Received'
                    WHEN status_id = 2 THEN 'Sorted'
                    WHEN status_id = 3 THEN 'Stored'
                END AS status_description,
                COUNT(DISTINCT parcel_id) AS parcel_count
            FROM ranked_parcels
            WHERE rnk = 1
        """
        
        # List to hold query parameters
        values = []

        # Add filter for status if provided
        if filter_status:
            status_placeholders = ', '.join(['%s'] * len(filter_status))
            sql_status += f" AND status_id IN ({status_placeholders})"
            values.extend(filter_status)
        
        # Add date range filter if both dates are provided
        if start_date and end_date:
            sql_status += " AND update_timestamp BETWEEN %s AND %s"
            values.extend([start_date, end_date])
        
        # Group by status_description
        sql_status += " GROUP BY status_description"
        
        # Execute the query and fetch data
        columns = ['status_description', 'parcel_count']
        df_status = db.querydatafromdatabase(sql_status, values, columns)


        # Create the bar chart

        status_fig = go.Figure(
            data=[
                go.Bar(
                    x=df_status["status_description"],
                    y=df_status["parcel_count"],
                    text=df_status["parcel_count"],
                    textposition='auto',
                    marker=dict(color='rgb(13,110,253)')
                )
            ],
            layout=go.Layout(
                title='Parcel Counts per Status',
                xaxis={'title': 'Status Description', 'showgrid': False},
                yaxis={'showticklabels': False, 'showgrid': False},
                yaxis2={'showticklabels': False, 'showgrid': False},
                annotations=[],
                margin={'b': 100, 't': 80, 'l': 100, 'r': 100},  # Adjust margins as needed
                hovermode='closest',
                autosize=True,  # Automatically adjust size based on content
                plot_bgcolor='rgba(0,0,0,0)',  # Remove background color
                paper_bgcolor='rgba(0,0,0,0)'  # Remove background color
            )
        )

        
        return status_fig
    else:
        raise PreventUpdate



# Callback for the SLA Left plot
@app.callback(
    Output('sla_left_plot', 'figure'),
    [Input('url', 'pathname'),
     Input('dashboard_statusfilter', 'value'),
     Input('date_range_picker', 'start_date'),
     Input('date_range_picker', 'end_date')]
)
def update_sla_left_graph(pathname, filter_status, start_date, end_date):
    if pathname == '/dashboard':
        # Base query to fetch parcels without status 4
        sql_sla = """
            SELECT parcel_id, MIN(update_timestamp) AS earliest_timestamp
            FROM parcel_status
            WHERE parcel_id NOT IN (
                SELECT DISTINCT parcel_id
                FROM parcel_status
                WHERE status_id = 4
            )
        """
        
        # List to hold query parameters
        values = []
        
        # Add filter for status if provided
        if filter_status:
            status_placeholders = ', '.join(['%s'] * len(filter_status))
            sql_sla += f" AND status_id IN ({status_placeholders})"
            values.extend(filter_status)
        
        # Add date range filter if both dates are provided
        if start_date and end_date:
            sql_sla += " AND update_timestamp BETWEEN %s AND %s"
            values.extend([start_date, end_date])
        
        # Group by parcel_id
        sql_sla += " GROUP BY parcel_id"
        
        # Execute the query and fetch data
        columns = ['parcel_id', 'earliest_timestamp']
        df_sla = db.querydatafromdatabase(sql_sla, values, columns)

        # Calculate SLA left categories
        current_time = datetime.now()
        df_sla['sla_left'] = (current_time - df_sla['earliest_timestamp']).dt.total_seconds() / 3600

        # Categorize into bins
        bins = [0, 12, 24, 36, 48, float('inf')]
        labels = ['0-12 hours', '12-24 hours', '24-36 hours', '36-48 hours', '> 48 hours']
        df_sla['sla_category'] = pd.cut(df_sla['sla_left'], bins=bins, labels=labels, right=False)

        # Count parcels in each SLA category
        sla_counts = df_sla['sla_category'].value_counts().sort_index()



        sla_fig = go.Figure(
            data=[
                go.Bar(
                    x=sla_counts.index,
                    y=sla_counts.values,
                    text=sla_counts.values,
                    textposition='auto',
                    marker=dict(color='rgb(13,110,253)')
                )
            ],
            layout=go.Layout(
                title='SLA Left for Orders',
                xaxis={'title': 'SLA Time Range', 'showgrid': False},
                yaxis={'showticklabels': False, 'showgrid': False},
                annotations=[],
                margin={'b': 100, 't': 80, 'l': 100, 'r': 100},  # Adjust margins as needed
                hovermode='closest',
                autosize=True,  # Automatically adjust size based on content
                plot_bgcolor='rgba(0,0,0,0)',  # Remove background color
                paper_bgcolor='rgba(0,0,0,0)'  # Remove background color
            )
        )


        return sla_fig
    else:
        raise PreventUpdate

@app.callback(
    [
        Output('dashboard_statusfilter', 'value'),
        Output('date_range_picker', 'start_date'),
        Output('date_range_picker', 'end_date')
    ],
    [Input('reset-button', 'n_clicks')]
)
def reset_filters(n_clicks):
    if n_clicks is None:
        # Prevent the callback from running if the button has not been clicked
        raise PreventUpdate
    return [], None, None
