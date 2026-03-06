#!/usr/bin/env python3
"""
Final analysis of torch.nn.Linear neighbors from enhanced knowledge graph.
"""

import json
import networkx as nx
from collections import Counter

def load_knowledge_graph(filepath='enhanced_knowledge_graph_with_edges.json'):
    """Load knowledge graph from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

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
    """Main function."""
    # Load the enhanced knowledge graph
    print("Loading enhanced knowledge graph...")
    knowledge_graph = load_knowledge_graph()
    G = build_nx_graph(knowledge_graph)

    print(f"Enhanced graph loaded with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

    # Find torch.nn.Linear
    linear_node_id = 'torch/nn/modules/linear.py:Linear'

    if not linear_node_id in G.nodes():
        print("Could not find torch.nn.Linear in the knowledge graph")
        return

    print(f"Found torch.nn.Linear with node ID: {linear_node_id}")

    # Get detailed information about Linear
    linear_node_data = G.nodes[linear_node_id]
    print(f"Linear node details:")
    print(f"  Name: {linear_node_data.get('name')}")
    print(f"  Type: {linear_node_data.get('type')}")
    print(f"  Path: {linear_node_data.get('path')}")

    # Show neighbors (predecessors and successors)
    print("\n" + "="*60)
    print("NEIGHBORS OF torch.nn.Linear")
    print("="*60)

    # Get all neighbors (both incoming and outgoing edges)
    predecessors = list(G.predecessors(linear_node_id))
    successors = list(G.successors(linear_node_id))

    all_neighbors = predecessors + successors

    print(f"Total neighbors: {len(all_neighbors)}")

    # Show first 10 neighbors with details
    print("\nFirst 10 neighbors:")
    print("-" * 40)

    for i, neighbor_id in enumerate(all_neighbors[:10]):
        neighbor_data = G.nodes[neighbor_id]
        print(f"{i+1}. {neighbor_data.get('name', neighbor_id)} ({neighbor_data.get('type', 'unknown')})")
        if neighbor_data.get('path'):
            print(f"   Path: {neighbor_data.get('path')}")
        print()

    # Show relationships
    print("\n" + "="*60)
    print("RELATIONSHIPS FOR torch.nn.Linear")
    print("="*60)

    # Show incoming relationships (what imports/uses Linear)
    print("Incoming relationships (what uses/imports Linear):")
    for pred in predecessors:
        pred_data = G.nodes[pred]
        edge_data = G.get_edge_data(pred, linear_node_id)
        edge_type = edge_data.get('link_type', 'unknown') if edge_data else 'unknown'
        print(f"  {pred_data.get('name', pred)} ({edge_type})")

    # Show outgoing relationships (what Linear imports/uses)
    print("\nOutgoing relationships (what Linear uses/imports):")
    for succ in successors:
        succ_data = G.nodes[succ]
        edge_data = G.get_edge_data(linear_node_id, succ)
        edge_type = edge_data.get('link_type', 'unknown') if edge_data else 'unknown'
        print(f"  {succ_data.get('name', succ)} ({edge_type})")

    # Show edge type statistics
    print("\n" + "="*60)
    print("EDGE TYPE STATISTICS")
    print("="*60)

    edge_types = Counter(data.get('link_type', 'other') for _, _, data in G.edges(data=True))
    for edge_type, count in edge_types.most_common():
        print(f"  {edge_type}: {count}")

    # Show the most important relationship for Linear
    print("\n" + "="*60)
    print("PRIMARY RELATIONSHIP")
    print("="*60)

    # Show the inheritance relationship
    if successors:
        for succ in successors:
            edge_data = G.get_edge_data(linear_node_id, succ)
            if edge_data and edge_data.get('link_type') == 'inheritance':
                succ_data = G.nodes[succ]
                print(f"torch.nn.Linear inherits from {succ_data.get('name')}")
                print(f"  Path: {succ_data.get('path')}")
                print(f"  Type: {succ_data.get('type')}")

if __name__ == "__main__":
    main()