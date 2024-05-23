from app.ops import Op, Computation
from pydot import Node, Edge, Dot

def dot(computation: Computation) -> Dot:
    graph = Dot("computation", graph_type="digraph")
    nodes(graph, computation)
    edges(graph, computation)
    return graph

def nodes(graph: Dot, computation: Computation):
    graph.add_node(Node(id(computation), label=str(computation.op)))
    for arg in computation.args:
        nodes(graph, arg)

def edges(graph: Dot, computation: Computation):
    for arg in computation.args:
        graph.add_edge(Edge(id(arg), id(computation)))
    for arg in computation.args:
        edges(graph, arg)
