# spacex_launch_dash.py
# ---------------------------------------------------------------
# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create the Dash app
app = dash.Dash(__name__)

# ------------------------- LAYOUT ------------------------------
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 40}
    ),

    # TASK 1: Launch Site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + [
            {'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())
        ],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True,
        style={'width': '60%', 'margin': '0 auto'}
    ),

    html.Br(),

    # TASK 2: Pie chart
    dcc.Graph(id='success-pie-chart'),

    html.Br(),
    html.P("Payload range (Kg):", style={'textAlign': 'center'}),

    # TASK 3: Range slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,                 # según instrucciones del lab
        max=10000,            # según instrucciones del lab
        step=1000,
        value=[min_payload, max_payload],  # selección inicial
        tooltip={"placement": "bottom", "always_visible": True}
    ),

    html.Br(),

    # TASK 4: Scatter chart
    dcc.Graph(id='success-payload-scatter-chart'),
])

# ----------------------- CALLBACKS -----------------------------

# TASK 2: Render pie chart from dropdown
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(selected_site):
    if selected_site == 'ALL':
        # Total successful launches by site
        successes = (spacex_df[spacex_df['class'] == 1]
                     .groupby('Launch Site')
                     .size()
                     .reset_index(name='successes'))
        fig = px.pie(
            successes, values='successes', names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # Success vs Failure for selected site
        site_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = (site_df.groupby('class').size()
                  .reset_index(name='count'))
        counts['Outcome'] = counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            counts, values='count', names='Outcome',
            title=f'Success vs Failure for site: {selected_site}'
        )
    return fig


# TASK 4: Render scatter from dropdown + slider
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    dff = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    if selected_site != 'ALL':
        dff = dff[dff['Launch Site'] == selected_site]
        title = f'Correlation between Payload and Success for {selected_site}'
    else:
        title = 'Correlation between Payload and Success for All Sites'

    fig = px.scatter(
        dff,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title=title
    )
    fig.update_yaxes(tickmode='array', tickvals=[0, 1],
                     ticktext=['Failure (0)', 'Success (1)'])
    return fig


# --------------------- RUN APP --------------------------------
if __name__ == '__main__':
    # En Skills Network suele requerir host 0.0.0.0 y puerto 8050
    app.run_server(debug=True, host="0.0.0.0", port=8050)

