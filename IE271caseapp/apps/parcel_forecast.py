# Import necessary libraries
import dash
from dash import dcc, html
import dash_table
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from apps import dbconnect as db
from sklearn.preprocessing import MinMaxScaler
from datetime import timedelta
import tensorflow as tf

# Load the model
model = tf.keras.models.load_model('assets/parcel_forecasting.h5')

# Define sequence length and scaler
seq_length = 60
scaler = MinMaxScaler(feature_range=(0, 1))

# Initialize the Dash app
app = dash.Dash(__name__)

# Define SQL query to retrieve parcel status data
query = "SELECT * FROM parcel_status"

# Retrieve data from the database or any other source
df = db.querydatafromdatabase(query, values=[], dfcolumns=['parcel_id','status_id','update_timestamp','staff_id', 'location'])

# Convert update_timestamp to datetime
df['update_timestamp'] = pd.to_datetime(df['update_timestamp'])

# Filter the DataFrame where status_id is 1
df_filter = df[df['status_id'] == 1]

# Group by update_timestamp and count the number of parcels for each date
df = df_filter.groupby(df_filter['update_timestamp'].dt.date).size().reset_index(name='parcel_count')

# Prepare the data
df['update_timestamp'] = pd.to_datetime(df['update_timestamp'])

# Normalize the data
scaled_data = scaler.fit_transform(df[['parcel_count']])

# Forecast for the next 30 days
forecast = []
last_sequence = scaled_data[-seq_length:].reshape((1, seq_length, 1))
for _ in range(30):
    next_pred = model.predict(last_sequence)
    forecast.append(next_pred[0, 0])
    last_sequence = np.roll(last_sequence, -1, axis=1)
    last_sequence[0, -1, 0] = next_pred

# Inverse transform forecast
forecast = scaler.inverse_transform(np.array(forecast).reshape(-1, 1))

# Create forecast DataFrame
forecast_dates = pd.date_range(start=df['update_timestamp'].max() + timedelta(days=1), periods=30)
forecast_df = pd.DataFrame({'Date': forecast_dates.strftime('%Y-%m-%d'), 'Forecast': forecast.flatten()})
forecast_df.set_index('Date', inplace=True)

# Merge forecast dataframe with original dataframe
merged_df = pd.concat([df.set_index('update_timestamp'), forecast_df])
merged_df['Forecast'] = merged_df['Forecast'].round(1)


# Dash app layout
layout = html.Div([
    html.H1("Parcel Forecast", className="display-4 text-center mt-5 mb-4"),
    html.Div([
        dcc.Graph(
            id='forecast-graph',
            figure={
                'data': [
                    {'x': merged_df.index, 'y': merged_df['parcel_count'], 'type': 'line', 'name': 'Historical Data'},
                    {'x': merged_df.index[-30:], 'y': merged_df['Forecast'][-30:], 'type': 'line', 'name': 'Forecast'}
                ],
                'layout': {
                    'title': 'Historical Parcel Count and Forecast',
                    'xaxis': {'title': 'Date'},
                    'yaxis': {'title': 'Parcel Count'},
                }
            }
        )
    ], className="container mt-5"),
    html.Div([
        html.H2("Forecast Table", className="text-center mt-5 mb-4"),
        dash_table.DataTable(
            id='forecast-table',
            columns=[
                {"name": "Date (yyyy-mm-dd)", "id": "Date"},
                {"name": "Forecast", "id": "Forecast", "type": "numeric", "format": {"specifier": ".1f"}}
            ],
            data=forecast_df.reset_index().to_dict('records'),
            style_table={'overflowX': 'auto'},  # Enable horizontal scroll if needed
            style_cell={'textAlign': 'center', 'padding': '5px'},  # Center align cell content
            style_header={'backgroundColor': '#f2f2f2', 'fontWeight': 'bold'},  # Gray header with bold text
            style_data_conditional=[  # Apply striped rows
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                {'if': {'column_id': 'Forecast'}, 'textAlign': 'right'}  # Align 'Forecast' column to the right
            ],
            style_cell_conditional=[
                {'if': {'column_id': 'Date'}, 'width': '200px', 'minWidth': '70px', 'maxWidth': '70px'},
                {'if': {'column_id': 'Forecast'}, 'width': '100px', 'minWidth': '30px', 'maxWidth': '30px'}
            ],
        )
    ], className="row justify-content-center", style={'width': '15%', 'margin': 'auto'})
])


if __name__ == '__main__':
    app.run_server(debug=True)
