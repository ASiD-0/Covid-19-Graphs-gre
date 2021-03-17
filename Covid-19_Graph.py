import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# read data from excel and make DataFrame
df = pd.read_excel(r"C:\Users\ARIS\Desktop\test.xlsx", index_col=0)

app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Dropdown(
        id='dropdown-for-districts',

        # options=[
        #     {'label': 'New York City', 'value': 'NYC'},
        #     {'label': 'Montreal', 'value': 'MTL'},
        #     {'label': 'San Francisco', 'value': 'SF'}
        # ],
        options=[

            # from this list the user chooses a district
            {'label': x, 'value': x} for x in list(df.keys())
        ],

        # initiate the graph with a default choice
        value=['Θεσσαλονίκης'],
        multi=True

    ),
    html.Div(id='drop-down-box-output-container', children=[]),


    dcc.Graph(id='corona-map', style={'height': '90vh'}, figure={})
])


@app.callback(
    [Output(component_id='drop-down-box-output-container', component_property='children'),
     Output(component_id='corona-map', component_property='figure')],
    [Input(component_id='dropdown-for-districts', component_property='value')]
)
def update_output(user_choice):

    # if user_choice not empty
    if user_choice:
        container = f'Έχετε επιλέξει τις Π.Ε. {", ".join(user_choice)}.' if len(user_choice) > 1 else f'Έχετε επιλέξει την Π.Ε. {"".join(user_choice)}.'

    # else if user_choice is empty
    else:
        container = 'Παρακαλώ επιλέξτε Π.Ε.'

    trace_list = []

    # make a list of the choices the user return
    periferies = list(user_choice)
    for onoma in periferies:
        trace1 = go.Scatter(x=df.index, y=df[onoma], name=onoma, mode='lines')
        trace_list.append(trace1)

    # set your desired layout of the graph
    layout = go.Layout(
        # template='plotly_white',
        title='Κρούσματα σε Περιφεριακές Ενότητες ανα την Ελλάδα.',
        # title_x=0.5,  # centers the title
        yaxis=dict(
            title='Αριθμός κρουσμάτων'
        ),
        xaxis=dict(
            title='Ημερομηνίες'
        )
        # height=1080

    )

    fig = go.Figure(data=trace_list, layout=layout, )
    return container, fig


if __name__ == '__main__':

    app.run_server(debug=True)
