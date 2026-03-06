#!/usr/bin/env python3
"""
Quick demonstration of torch.nn.Linear neighbors visualization.
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

def load_enhanced_graph():
    """Load the enhanced knowledge graph."""
    with open('enhanced_knowledge_graph_with_edges.json', 'r') as f:
        return json.load(f)

def build_nx_graph(knowledge_graph):
    """Build NetworkX graph from knowledge graph data."""
    G = nx.DiGraph()

    # Add nodes
    for node in knowledge_graph['nodes']:
        G.add_node(
            node['id'],
            name=node['name'],
            type=node['type'],
            path=node.get('path', ''),
            description=node.get('description', '')
        )

    # Add edges
    edges_data = knowledge_graph.get('edges', [])
    for link in edges_data:
        G.add_edge(
            link['source'],
            link['target'],
            link_type=link['type'],
            **link.get('properties', {})
        )

    return G

def main():
    """Main demonstration function."""
    print("Enhanced PyTorch Knowledge Graph - Linear Neighbors Demo")
    print("=" * 60)

    # Load the enhanced graph
    graph_data = load_enhanced_graph()
    G = build_nx_graph(graph_data)

    print(f"Graph loaded with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

    # Find torch.nn.Linear
    linear_node_id = 'torch/nn/modules/linear.py:Linear'

    if linear_node_id not in G.nodes():
        print("Error: Could not find torch.nn.Linear")
        return

    print(f"Found torch.nn.Linear with ID: {linear_node_id}")

    # Show neighbors
    predecessors = list(G.predecessors(linear_node_id))
    successors = list(G.successors(linear_node_id))

    print(f"\nLinear has {len(predecessors)} incoming relationships and {len(successors)} outgoing relationships")

    # Show the inheritance relationship (most important)
    if successors:
        for succ in successors:
            edge_data = G.get_edge_data(linear_node_id, succ)
            if edge_data and edge_data.get('link_type') == 'inheritance':
                succ_data = G.nodes[succ]
                print(f"\n=== PRIMARY RELATIONSHIP ===")
                print(f"torch.nn.Linear inherits from {succ_data.get('name')}")
                print(f"  Path: {succ_data.get('path')}")
                print(f"  Type: {succ_data.get('type')}")
                print(f"  Description: {succ_data.get('description', 'No description')[:150]}...")

    # Show edge type statistics
    print(f"\n=== EDGE TYPE STATISTICS ===")
    edge_types = Counter(data.get('link_type', 'other') for _, _, data in G.edges(data=True))
    for edge_type, count in edge_types.most_common():
        print(f"  {edge_type}: {count}")

    # Show some key relationships for Linear
    print(f"\n=== KEY RELATIONSHIPS ===")
    print("The enhanced knowledge graph now shows:")
    print("1. Import relationships between modules")
    print("2. Inheritance relationships (Linear inherits from Module)")
    print("3. Usage relationships between components")
    print("4. Complete PyTorch module hierarchy visualization")

    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()