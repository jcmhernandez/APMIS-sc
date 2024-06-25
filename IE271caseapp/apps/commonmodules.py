# Usual Dash dependencies
from dash import dcc, html, callback_context, Input, Output, dash
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

# Let us import the app object in case we need to define
# callbacks here
from app import app

# CSS Styling for the NavLink components
navlink_style = {
    'color': '#000',  # Change text color to black for light theme
}

navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(dbc.NavbarBrand("APMIS", className="ml-4", style={"font-size": "24px", "font-weight": "bold"})),
                ],
                align="center",
                className='g-0' # remove gutters (i.e. horizontal space between cols)
            ),
            href="/home",
        ),
        dbc.Nav(
            [
                dbc.NavLink("Parcel Management", id="parcel_management", href="/parcel_management", className="navlink", style=navlink_style),
                dbc.NavLink("Dashboard", id="dashboard", href="/dashboard", className="navlink", style=navlink_style),
                dbc.NavLink("Parcel Forecast", id="parcel_forecast", href="/parcel_forecast", className="navlink", style=navlink_style),
                dbc.NavLink("Logout", id="logout", href="/logout", className="navlink", style=navlink_style),
            ],
            className="ml-auto",  # Align links to the right
            navbar=True,
            style={'backgroundColor': '#fff'}  # Ensure navbar has a clean light background
        ),
    ],
    light=True,  # Change to light theme
    color='light'  # Change to light theme
)

# Callback to update NavLink styles
@app.callback(
    Output("parcel_management", "style"),
    Output("dashboard", "style"),
    Output("parcel_forecast", "style"),
    Output("logout", "style"),
    Input("url", "pathname"),
)
def update_navlink_style(pathname):
    active_color = "#ffc107"  # Change this to the color you want for the active link
    inactive_color = "#000"  # Change text color to black for light theme
    active_style = {**navlink_style, 'backgroundColor': active_color}
    inactive_style = navlink_style
    if not pathname:
        raise PreventUpdate
    styles = {
        "/parcel_management": active_style if pathname in ["/parcel_management", "/parcel_management/add_new_group", "/parcel_management/add_new_parcel", "/parcel_management/update_parcel_group", "/parcel_management/update_parcel_status"] else inactive_style,
        "/dashboard": active_style if pathname == "/dashboard" else inactive_style,
        "/parcel_forecast": active_style if pathname == "/parcel_forecast" else inactive_style,
        "/logout": active_style if pathname == "/logout" else inactive_style,
    }
    return styles["/parcel_management"], styles["/dashboard"], styles["/parcel_forecast"], styles["/logout"]

