# Dash related dependencies
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
# To open browser upon running your app
import webbrowser

# Importing your app definition from app.py so we can use it
from app import app

from apps import commonmodules as cm

from apps import home, signup, login, parcel_management, dashboard, parcel_forecast, add_new_parcel_group, add_new_parcel, update_parcel_group, update_parcel_status


CONTENT_STYLE = {
    "margin-top": "1em",
    "margin-left": "1em",
    "margin-right": "1em",
    "padding": "1em 1em",
}

app.layout = html.Div(
    [
        # Location Variable -- contains details about the url
        dcc.Location(id='url', refresh=True),
        
        # LOGIN DATA
        # 1) logout indicator, storage_type='session' means that data will be retained
        #  until browser/tab is closed (vs clearing data upon refresh)
        dcc.Store(id='sessionlogout', data=True, storage_type='session'),
        
        # 2) current_user_id -- stores user_id
        dcc.Store(id='currentuserid', data=-1, storage_type='session'),
        
        # 3) currentrole -- stores the role
        # we will not use them but if you have roles, you can use it
        dcc.Store(id='currentrole', data=-1, storage_type='session'),


        # Adding the navbar
        html.Div(
            cm.navbar,
            id='navbar_div'
        ),

        # Page Content -- Div that contains page layout
        html.Div(id='page-content', style=CONTENT_STYLE),

    ]
)
@app.callback(
    [
        Output('page-content', 'children'),
        Output('sessionlogout', 'data'),
        Output('navbar_div', 'className'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('sessionlogout', 'data'),
        State('currentuserid', 'data'),
    ]
)
def displaypage(pathname, sessionlogout, userid):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
    else:
        raise PreventUpdate
    
    if eventid == 'url':
        if userid < 0: # if logged out
            if pathname == '/':
                return login.layout, True, 'd-none'
            elif pathname == '/signup':
                return signup.layout, True, 'd-none'
            else:
                return '404: request not found', True, ''
            
        else:    
            if pathname == '/logout':
                return login.layout, True, ''
                
            elif pathname in ['/', '/home']:
                return home.layout, False, 'd-none'  # Hide the navbar on home page
                
            elif pathname == '/parcel_management':
                return parcel_management.layout, False, ''
                
            elif pathname == '/parcel_management/add_new_group':
                return add_new_parcel_group.layout, False, ''
            elif pathname == '/parcel_management/add_new_parcel':
                return add_new_parcel.layout, False, ''
            elif pathname == '/parcel_management/update_parcel_group':
                return update_parcel_group.layout, False, ''
            elif pathname == '/parcel_management/update_parcel_status':
                return update_parcel_status.layout, False, ''

            elif pathname == '/dashboard':
                return dashboard.layout, False, ''

            elif pathname == '/parcel_forecast':
                return parcel_forecast.layout, False, ''

            else:
                returnlayout = '404: request not found'
                
        # decide sessionlogout value
        logout_conditions = [
            pathname in ['/', '/logout'],
            userid == -1,
            not userid
        ]
        sessionlogout = any(logout_conditions)
        
        # hide navbar if logged-out; else, set class/style to default
        navbar_classname = 'd-none' if sessionlogout else ''
        
        return [returnlayout, sessionlogout, navbar_classname]
    else:
        raise PreventUpdate


if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/', new=0, autoraise=True)
    app.run_server(debug=False)



