from dash import html
from dash.dependencies import Input, Output, State
from dash_bipartite.bipartite import from_pandas_edgelist, BipartiteCytoscape
import pandas as pd
import json


from dash import Dash

df = pd.DataFrame({"A": [0, 1, 2, 3, 3], "B": [4, 5, 6, 7, 4]})

G = from_pandas_edgelist(df=df, source="A", target="B")
nodes_dict = {node: {"label": str(node), "grabbable": False} for node in G.nodes}
edges_dict = {(key1, key2): {"selectable": False} for key1, key2 in G.edges}
plotly_component = BipartiteCytoscape(
    G,
    nodes_supplementary_parameters=nodes_dict,
    edges_supplementary_parameters=edges_dict,
    id="bipartite-network",
    scale=100,
)


app = Dash(__name__)
app.layout = html.Div(
    [
        plotly_component,
        html.P(id="cytoscape-tapNodeData-output"),
    ]
)


@app.callback(
    Output("cytoscape-tapNodeData-output", "children"),
    Input("bipartite-network", "tapNode"),
    Input("bipartite-network", "elements"),
)
def displayTapNodeData(tapnode, elements):

    if tapnode:

        return json.dumps(tapnode, indent=2)


app.run_server(debug=True)
