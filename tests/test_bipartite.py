from dash_bipartite.bipartite import from_pandas_edgelist, BipartiteCytoscape
import networkx as nx
import pandas as pd


def test_BipartiteCytoscape():
    df = pd.DataFrame({"A": [0, 1, 2, 3, 3], "B": [4, 5, 6, 7, 4]})

    G = from_pandas_edgelist(df=df, source="A", target="B")
    nodes_dict = {node: {"label": "node", "grabbable": False} for node in G.nodes}
    edges_dict = {tuple_: {"selectable": False} for tuple_ in G.edges}
    plotly_component = BipartiteCytoscape(
        G,
        nodes_supplementary_parameters=nodes_dict,
        edges_supplementary_parameters=edges_dict,
    )

    G2 = nx.from_pandas_edgelist(df, source="A", target="B")

    nodes = [
        {"data": {"id": str(node), "label": "node"}, "grabbable": False}
        for node in G2.nodes
    ]
    edges = [
        {"data": {"source": str(source), "target": str(target)}, "selectable": False}
        for source, target in G2.edges
    ]
    elements = nodes + edges

    bipartite_elements = plotly_component.elements
    for dict_ in bipartite_elements:
        dict_.pop("renderedPosition", None)

    print("\n\n", bipartite_elements, "\n\n", elements)

    assert len(bipartite_elements) == len(elements) and all(
        x in bipartite_elements for x in elements
    )
