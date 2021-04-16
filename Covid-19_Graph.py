import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# read data from excel and make DataFrame
df = pd.read_excel("official.xlsx", index_col=0)

# use this to pass index column as dates which makes it able to sort the data by date and fixes 15-01-2021 bug
# also makes the dates axis more readable
df.index = pd.to_datetime(df.index, format='%d-%m-%Y')

# sort the data frame
df.sort_index()

app = dash.Dash(__name__)
server = app.server
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
        value=['Αττικής', 'Θεσσαλονίκης'],
        placeholder='Παρακαλώ επιλέξτε Π.Ε.',
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

    container = ''

    # if user_choice not empty
    if user_choice:
        container = f'Έχετε επιλέξει τις Π.Ε. {", ".join(user_choice)}.' if len(user_choice) > 1 else f'Έχετε επιλέξει την Π.Ε. {"".join(user_choice)}.'


    trace_list = []

    # make a list of the choices the user return
    periferies = list(user_choice)
    for onoma in periferies:
        # go.Scatter(...) if you want graph to be a line
        trace1 = go.Bar(x=df.index, y=df[onoma], name=onoma, hovertemplate='Date %{x}<br>Cases %{y}')
        trace_list.append(trace1)

    # set your desired layout of the graph
    layout = go.Layout(
        # template='plotly_dark',
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

    fig = go.Figure(data=trace_list, layout=layout )
    return container, fig


if __name__ == '__main__':

    app.run_server(debug=True)
