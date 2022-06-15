from typing import Union, Iterable, Dict, Tuple

import networkx as nx
import dash_cytoscape as cyto
import pandas as pd


class BipartiteGraph(nx.Graph):
    def __init__(self, sources: Iterable, targets: Iterable, incoming_graph_data=None):
        super().__init__(incoming_graph_data)
        self.sources = sources
        self.targets = targets


def from_pandas_edgelist(df, source: str, target: str, edge_attr=None, edge_key=None):
    G = nx.from_pandas_edgelist(
        df, source=source, target=target, edge_attr=edge_attr, edge_key=edge_key
    )
    G = BipartiteGraph(
        incoming_graph_data=G,
        sources=df[source].to_numpy(),
        targets=df[target].to_numpy(),
    )
    return G


class BipartiteCytoscape(cyto.Cytoscape):
    def __init__(
        self,
        G: BipartiteGraph,
        align: str = "vertical",
        scale: int = 100,
        nodes_supplementary_parameters: Union[
            Dict[str, Dict[str, Union[float, str, int]]], None
        ] = None,
        edges_supplementary_parameters: Union[
            Dict[
                Tuple[Union[str, float, int], Union[str, float, int]],
                Dict[str, Union[float, str, int]],
            ],
            None,
        ] = None,
        **kwargs,
    ):
        """

        Parameters
        ----------
        G : BipartiteGraph
            Nodes and edges are automatically converted to string for compatibility with `dash_cytoscape.Cytoscape`.
        align : str, optional
            Whether to align source and target in rows or in columns, by default "vertical".
        scale : int, optional
            Scale factor of networkx graph positions to Cytoscape position. Used for conversion.
            This parameter should be set according to the number of nodes displayed. The more nodes, the bigger the value should be.
            By default 100
        nodes_supplementary_parameters : Union[Dict[str,Dict[str, Union[float, str, int]]], None], optional
            dictionary with keys corresponding to `nx.Graph` nodes and values consisting of a dictionary
            of cytoscape elements properties. See Dash documentation for more information on values.
            Properties are automatically put in the right level of `cytoscape` node/edges element dictionary according to its key.
            For example passing `nodes_supplementary_parameters = {'0':{'label':"zero", classes=["foo", "bar"]}}` will modify the
            preinitialized element `{"data":{'id':"0"}} as : {"data":{'id':'0', "label":"zero"}, "classes":["foo", bar"]}`.

            All values can be overriden, be cautious not overriding `renderedPosition`.
            By default None
        edges_supplementary_parameters : Union[ Dict[ Tuple[Union[str, float, int], Union[str, float, int]], Dict[str, Union[float, str, int]], ], None, ], optional
            Dicionnary with keys corresponding to `nx.Graph` edges (tuple) and values consisting of a dictionary
            of cytoscape elements properties.
            Processing of the dictionary is similar to `nodes_supplementary_parameters` argument.
            By default None


        Raises
        ------
        ValueError
            G must be instance of bipartite.BipartiteGraph.

        Examples
        --------
            >>> df = pd.DataFrame({"A": [0, 1, 2, 3, 3], "B": [4, 5, 6, 7, 4]})
            >>> G = from_pandas_edgelist(df=df, source="A", target="B")
            >>> nodes_dict = {node: {"label": "node", "grabbable": False} for node in G.nodes}
            >>> edges_dict = {tuple_: {"selectable": False} for tuple_ in G.edges}
            >>> BipartiteCytoscape(G,
                    nodes_supplementary_parameters=nodes_dict,
                    edges_supplementary_parameters=edges_dict
                )
        """
        if isinstance(G, BipartiteGraph) is False:
            raise ValueError("`graph` must be instance of `BipartiteNetwork`")

        nx_coordinates = nx.bipartite_layout(G, nodes=set(G.sources), align=align)
        nx_coordinates = {str(key): value for key, value in nx_coordinates.items()}
        # this function convert numeric ids to str
        _ = nx.readwrite.json_graph.cytoscape_data(G)["elements"]

        nodes = _["nodes"]
        edges = _["edges"]
        for edge in edges:
            edge["data"]["source"] = str(edge["data"]["source"])
            edge["data"]["target"] = str(edge["data"]["target"])

        for node in nodes:
            node_id = node["data"]["id"]
            x, y = nx_coordinates[node_id].tolist()
            node.update({"renderedPosition": {"x": x * scale, "y": y * scale}})
            node["data"].update({"label": node["data"]["id"]})
            node["data"].pop("name")
            node["data"].pop("value")

            nodes_supplementary_parameters = {
                str(key): value for key, value in nodes_supplementary_parameters.items()
            }

            if nodes_supplementary_parameters is not None:
                items_to_add = nodes_supplementary_parameters[node_id].items()
                for key, value in items_to_add:
                    if key in ["id", "label", "parent", "source", "target"]:
                        node["data"].update({key: value})
                    else:
                        node.update({key: value})
        if edges_supplementary_parameters is not None:
            edges_supplementary_parameters = {
                (str(key1), str(key2)): value
                for (key1, key2), value in edges_supplementary_parameters.items()
            }

        for edge in edges:
            tuple_id = (edge["data"]["source"], edge["data"]["target"])
            if edges_supplementary_parameters is not None:
                items_to_add = edges_supplementary_parameters[tuple_id].items()
                for key, value in items_to_add:
                    if key in ["id", "label", "parent", "source", "target"]:
                        edge["data"].update({key: value})
                    else:
                        edge.update({key: value})

        elements = nodes + edges

        layout = {"name": "preset"}
        super().__init__(elements=elements, layout=layout, **kwargs)
