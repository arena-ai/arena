from app.ops import Computation
from app.ops.computation import FlatComputations
from pydot import Node, Edge, Dot


def dot(computation: Computation) -> Dot:
    graph = Dot("computation", graph_type="digraph")
    flat_computations = FlatComputations.from_computation(computation)
    nodes(graph, flat_computations)
    edges(graph, flat_computations)
    return graph


def nodes(graph: Dot, flat_computations: FlatComputations):
    for fc in flat_computations.flat_computation_list:
        graph.add_node(Node(fc.index, label=str(fc.op)))


def edges(graph: Dot, flat_computations: FlatComputations):
    for fc in flat_computations.flat_computation_list:
        for arg in fc.args:
            graph.add_edge(Edge(fc.index, arg))
