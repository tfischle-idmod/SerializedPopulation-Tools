import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import change_serialized_population
import utils

individidual_labels = [
                {'label': 'age', 'value': 'm_age'},
                {'label': 'gender', 'value': 'm_gender'},
                {'label': 'infections', 'value': 'infections'}
            ]

# the values are functions from change_serialized_popultion
distributions_label = change_serialized_population.getAvailableDistributions()

selected_property = None
selected_distribution = None
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Graph(id='graph-with-slider'),
    html.Label('Individual Property'),
    dcc.Dropdown(
        id='myDropdown',
        options=individidual_labels,
        value='m_age'
    ),
    dcc.Graph(id='graph-output-new'),
    html.Label('Distribution'),
    dcc.Dropdown(
        id='distributions',
        options=distributions_label,
        value=''
    ),
    html.Div(id='output-container'),
    html.Label(' '),
    html.Div(dcc.Input(id='input-box', type='text')),
    html.Button('Save Population', id='button', value="pressed"),
    html.Div(id='container-button-basic',
             children='Enter a value and press submit')
])

@app.callback(
    dash.dependencies.Output('graph-with-slider', 'figure'),
    [dash.dependencies.Input('myDropdown', 'value')])
def update_output(value):
    global selected_property
    if not value:
        return {}
    selected_property = value
    ind_values = change_serialized_population.getPropertyValues_Individual(0, change_serialized_population.dtk, value)
    trace = [go.Histogram(x=ind_values)]

    return {
        'data': trace,
        'layout': go.Layout(
                title=value,
                bargap=0.2,
                bargroupgap=0.1
        )
    }


@app.callback(
    dash.dependencies.Output('graph-output-new', 'figure'),
    [dash.dependencies.Input('distributions', 'value')])
def update_output(value):
    global selected_property
    global selected_distribution

    if not value or not selected_property:
        return {}

    selected_distribution = []
    fct = getattr(change_serialized_population, value)
    if selected_property == 'infections':
        new_infection = change_serialized_population.createInfection("Generic", change_serialized_population.getNextInfectionSuid(change_serialized_population.dtk))
        change_serialized_population.addInfectionToIndividuals(0, change_serialized_population.dtk, new_infection, lambda ind: ind["m_age"] > 43500)
    else:
        selected_distribution = utils.createDistribution(selected_property, len(change_serialized_population.dtk.nodes[0].individualHumans), fct)
        change_serialized_population.setPropertyValues_Individual(0, selected_distribution, change_serialized_population.dtk)

    new_ind_values = change_serialized_population.getPropertyValues_Individual(0, change_serialized_population.dtk, selected_property)
    trace = [go.Histogram(x=new_ind_values)]

    return {
        'data': trace,
        'layout': go.Layout(
                title=value,
                bargap=0.2,
                bargroupgap=0.1
        )
    }


@app.callback(
    dash.dependencies.Output('container-button-basic', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('input-box', 'value')])
def update_output(n_clicks, value):
    global selected_distribution
    if not selected_distribution:
        return ""
    change_serialized_population.write(change_serialized_population.dtk)
    return 'The input value was "{}" and the button has been clicked {} times'.format(
        value,
        n_clicks
    )


# @app.callback(
#     dash.dependencies.Output('graph-with-slider', 'figure'),
#     [dash.dependencies.Input('year-slider', 'value')])
# def update_figure(selected_year):
#     filtered_df = df[df.year == selected_year]
#     traces = []
#     for i in filtered_df.continent.unique():
#         df_by_continent = filtered_df[filtered_df['continent'] == i]
#         traces.append(go.Scatter(
#             x=df_by_continent['gdpPercap'],
#             y=df_by_continent['lifeExp'],
#             text=df_by_continent['country'],
#             mode='markers',
#             opacity=0.7,
#             marker={
#                 'size': 15,
#                 'line': {'width': 0.5, 'color': 'white'}
#             },
#             name=i
#         ))
#
#     return {
#         'data': traces,
#         'layout': go.Layout(
#             xaxis={'type': 'log', 'title': 'GDP Per Capita'},
#             yaxis={'title': 'Life Expectancy', 'range': [20, 90]},
#             margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
#             legend={'x': 0, 'y': 1},
#             hovermode='closest'
#         )
#     }


if __name__ == '__main__':
    app.run_server(debug=True)