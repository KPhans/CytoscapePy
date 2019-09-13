#Sample app for the bank of canada using cytoscape.

import requests
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto
import pandas as pd
import plotly.graph_objs as go
import dash_design_kit as ddk
import theme
from logistic import pred_y_0
import logistic

url = 'https://raw.githubusercontent.com/plotly/dash-cytoscape/master/demos/data/sample_network.txt'
data = requests.get(url).text.split('\n')
dataa= pd.read_excel('data/HRDATA.xlsx')

nodes = set()
cy_edges, cy_nodes = [], []
edges = data[:100]
colors = ['red', 'blue', 'green', 'yellow', 'pink']

colorr = {
    "Male": 'blue',
    "Female": 'red'}


def axis_template_3d(title, type='linear'):
    return dict(
        showbackground=True,
        backgroundcolor='gray',
        gridcolor='rgb(255, 255, 255)',
        title=title,
        type=type,
        zerolinecolor='rgb(255, 255, 255)'
    )

colors = ['red', 'blue', 'green', 'yellow', 'pink']
def blackout_axis(axis):
    axis['showgrid'] = False
    axis['zeroline'] = False
    axis['color'] = 'white'
    return axis

colorr = {
    "Male": 'blue',
    "Female": 'red'}

def scatter_plot_3d(Value):
    data = []
    clusters = []
    colors = ["black", "silver", "crimson"]
    colorscale = [
        [2, "rgb(244,236,21)"],
        [3, "rgb(249,210,41)"],
        [4, "crimson"],
    ]
    for i in range(len(dataa['PerformanceRating'].unique())):
        name = dataa['PerformanceRating'].unique()[i]
        color = colors[i]
        x = dataa[dataa['PerformanceRating'] == name]['Age']
        y = dataa[dataa['PerformanceRating'] == name]['YearsSinceLastPromotion']
        z = dataa[dataa['PerformanceRating'] == name][Value]

        trace = dict(
            name=name,
            x=x, y=y, z=z,
            type="scatter3d",
            mode='markers',
            marker=dict(size=3, color=color, line=dict(width=0)
                        ))
        data.append(trace)


    layout = dict(
        width='100%',
        height='100%',
        autosize=False,
        title='Cluster Analysis: Performance Rating',
        scene=dict(
            xaxis=axis_template_3d('Age'),
            yaxis=axis_template_3d('YearsSinceLastPromotion'),
            zaxis=axis_template_3d(Value),
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=0.08, y=2.2, z=0.08)
            )
        ),
    )

    return dict(data=data, layout=layout)

default_stylesheet = [
    {
        "selector": 'node',
        'style': {
            "opacity": 0.9,
            'height': 15,
            'width': 15,
            'background-color': '#222222'
        }
    },
    {
        "selector": 'edge',
        'style': {
            "curve-style": "bezier",
            "opacity": 0.3,
            'width': 2
        }
    },
    *[{
        "selector": '.' + color,
        'style': {'line-color': color}
    } for color in colors]
]


for edge in edges:
    source, target = edge.split(" ")
    color = colors[len(cy_nodes) % 5]

    if source not in nodes:  # Add the source node
        nodes.add(source)
        cy_nodes.append({"data": {"id": source}, "classes": color})

    if target not in nodes:  # Add the target node
        nodes.add(target)
        cy_nodes.append({"data": {"id": target}, "classes": color})

    cy_edges.append({  # Add the Edge Node
        'data': {'source': source, 'target': target},
        'classes': color
    })
placeholder_content = html.Div(style={'height': 300})

app = dash.Dash(__name__)
server = app.server


fig = go.Figure(data=go.Scatter(
    x=[1, 2, 3, 4],
    y=[10, 11, 12, 13],
    mode='markers',
    marker=dict(size=[40, 60, 80, 100],
                color=[0, 1, 2, 3])
))
networklayouts = ['random',
                        'grid',
                        'circle',
                        'concentric',
                        'breadthfirst',
                        'cose',
                        'cose-bilkent',
                        'dagre',
                        'cola',
                        'klay',
                        'spread',
                        'euler']
placeholder_content = html.Div(html.H3('This plot shows the 3d rerpresentation'
                                       'of Hr Data. We can visualize clusters based on'
                                       'our selected variable. Please select a variable.'), style={'height': 200, })
app.layout = ddk.App(theme=Theme, children =
    [ddk.Header([
        ddk.Logo(src=("https://hrpm.ca/wp-content/uploads/2018/03/national-bank-of-canada-logo.png")
        ),
        ddk.Title('Bank of Canada Dash Analytics'),
        dcc.Dropdown(
            id='dropdown-layout',
            style={'min-width': '150px'},
            placeholder='Select a Network Layout...',
            options=[{"label": i, "value": i} for i in networklayouts],
            value='breadthfirst'
        ),
    ]),

        html.Div(
            className="header",
            children=[
                html.Div(
                    className="div-info",
                    children=[
                        ddk.Title('Network Analysis'),
                        html.A(
                            children=html.Button("Learn More", className="button"),
                            href="https://dash.plot.ly/cytoscape",
                            target="_blank",
                        ),
                    ],
                ),
                ddk.Card(
                    children=[
                        cyto.Cytoscape(
                            id='cytoscape',
                            elements=cy_edges + cy_nodes,
                            # zoomingEnabled=False,
                            stylesheet=default_stylesheet,
                            layout={'name': 'grid'},
                            style={'width': '100%', 'height': '600px'}
                        ),
                    ]
                ),
            ],
        ),
        ddk.SectionTitle('Cartesian Visualizations'),
        html.Div([
ddk.ControlCard(orientation='horizontal', children=[
            ddk.ControlItem(
                dcc.Dropdown(
                    id = 'scatteroptions',
                    options=[
                        {'label': i, 'value': i}
                        for i in ['EmpEnvironmentSatisfaction','EmpLastSalaryHikePercent','YearsSinceLastPromotion',
       'ExperienceYearsInCurrentRole']
                    ],
                    multi=False,
                    value='EmpLastSalaryHikePercent'
                ),
                label='Axis Options'

            ),
            ddk.ControlItem(
                dcc.Slider(
                    min=0,
                    max=10,
                    marks={
                        0: '0',
                        5: '5',
                        10: '10'
                    },
                    value=5
                ),
                label='Thrusters'
            )
        ]),
            html.Div([
            ddk.Graph(
                id = '3dscatter'
            ),
                ddk.Card(
                    width=50,
                    children="""
    This graph enables 3D visualiziation to better understand clusters of high performing 
    and low performing employees.
                """
                )], style={'display':'flex', 'padding': '15px'}),
        ]),
        ddk.SectionTitle('Insights'),
        ddk.ControlCard(orientation='horizontal', children = [ddk.CardHeader(title='LOGISTIC'
                                                                                   'REGRESSION PREDICTOR'),
                                                              ddk.ControlItem(
            dcc.Input(
                id='EnvironmentSatisfaction',
                value=50,
                type='number'
            ),
            label='EnvironmentSatisfaction'
        ),
ddk.ControlItem(
            dcc.Input(
                id='SalaryHikePercent',
                value=50,
                type='number'
            ),
            label='SalaryHikePercent'
        ),
            ddk.ControlItem(
                dcc.Input(
                    id='YearsSinceLastPromotion',
                    value=50,
                    type='number'
                ),
                label='YearsSinceLastPromotion'
            )
        ,
            ddk.ControlItem(
                dcc.Input(
                    id='EmpDepartment',
                    value=50,
                    type='number'
                ),
                label='EmpDepartment'
            )
        ,
            ddk.ControlItem(
                dcc.Input(
                    id='ExperienceYearsInCurrentRole',
                    value=50,
                    type='number'
                ),
                label='ExperienceYearsInCurrentRole'
            )
        ],
        ),
        ddk.Card(
            id = 'prediction'),
        ddk.Card(
            width='100%',
            children=[
                ddk.CardHeader(title='Logistic Regression Predictions: Accuracy 85%'),
                ddk.Graph(
                    figure=go.Figure(data=go.Scatter(
                        x=list(range(2025)),
                        y=pred_y_0[0:2024],
                        mode='markers'))
                )
            ]
        ),
    ],
)

@app.callback(Output('cytoscape', 'layout'),
              [Input('dropdown-layout', 'value')])
def update_cytoscape_layout(layout):
    return {'name': layout}


@app.callback(Output('3dscatter', 'figure'),
              [Input('scatteroptions', 'value')])
def update(scatteropt):
    figure = scatter_plot_3d(scatteropt)
    return figure

@app.callback(Output('prediction', 'children'),
              [
                  Input("EnvironmentSatisfaction", "value"),
                  Input("SalaryHikePercent", "value"),
                  Input("YearsSinceLastPromotion", "value"),
                  Input("EmpDepartment", "value"),
                  Input("ExperienceYearsInCurrentRole", "value"),
              ])
def update(FV,SV,TV,FOV,FIV):
    XNew = [[FV,SV,TV,FOV,FIV]]
    pred = clf_0.predict(XNew)
    if int(pred) == 0:
        return 'EMPLOYEE WILL MOST LIKELY BE A LOW PERFORMER'
    else:
        return ' EMPLOYEE WILL MOST LIKELY BE A HIGH PERFORMER'



if __name__ == "__main__":
    app.run_server()