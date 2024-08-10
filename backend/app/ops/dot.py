from app.ops import Op, Computation
from app.ops.computation import FlatComputation, FlatComputations
from pydot import Node, Edge, Dot

def dot(computation: Computation) -> Dot:
    graph = Dot("computation", graph_type="digraph")
    flat_computations = FlatComputations.from_computation(computation)
    nodes(graph, flat_computations)
    edges(graph, flat_computations)
    return graph

def nodes(graph: Dot, flat_computations: FlatComputations):
    for fc in flat_computations.flat_computations:
        graph.add_node(Node(flat_computations.computation.encoder()[fc], label=str(fc.op)))

def edges(graph: Dot, flat_computations: FlatComputations):
    for fc in flat_computations.flat_computations:
        for arg in fc.args:
            graph.add_edge(Edge(flat_computations.computation.encoder()[fc], arg))
