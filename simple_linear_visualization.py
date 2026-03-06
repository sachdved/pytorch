#!/usr/bin/env python3
"""
Simple visualization of torch.nn.Linear neighbors from enhanced knowledge graph.
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

def find_linear_node(G):
    """Find the torch.nn.Linear node in the graph."""
    for node_id, node_data in G.nodes(data=True):
        if node_data.get('name') == 'Linear' and 'torch/nn/modules/linear.py' in node_data.get('path', ''):
            return node_id
    return None

def get_neighbors(G, node_id, num_neighbors=10):
    """Get the neighbors of a node."""
    # Get both predecessors (incoming edges) and successors (outgoing edges)
    predecessors = list(G.predecessors(node_id))
    successors = list(G.successors(node_id))

    # Combine them
    all_neighbors = predecessors + successors

    # Get the actual node data for neighbors
    neighbor_data = []
    for neighbor_id in all_neighbors:
        neighbor_data.append({
            'id': neighbor_id,
            'name': G.nodes[neighbor_id].get('name', neighbor_id),
            'type': G.nodes[neighbor_id].get('type', 'unknown'),
            'path': G.nodes[neighbor_id].get('path', '')
        })

    # Sort by name for consistent results
    neighbor_data.sort(key=lambda x: x['name'])

    return neighbor_data[:num_neighbors]

def main():
    """Main function."""
    # Load the enhanced knowledge graph
    print("Loading enhanced knowledge graph...")
    knowledge_graph = load_knowledge_graph()
    G = build_nx_graph(knowledge_graph)

    print(f"Enhanced graph loaded with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

    # Find torch.nn.Linear
    linear_node_id = find_linear_node(G)

    if not linear_node_id:
        print("Could not find torch.nn.Linear in the knowledge graph")
        return

    print(f"Found torch.nn.Linear with node ID: {linear_node_id}")

    # Get neighbors
    neighbors = get_neighbors(G, linear_node_id, 10)

    print("\n10 Neighbors of torch.nn.Linear:")
    print("=" * 50)
    for i, neighbor in enumerate(neighbors, 1):
        print(f"{i}. {neighbor['name']} ({neighbor['type']})")
        if neighbor['path']:
            print(f"   Path: {neighbor['path']}")
        print()

    # Show edge types
    edge_types = Counter(data.get('link_type', 'other') for _, _, data in G.edges(data=True))
    print("Edge types in the graph:")
    for edge_type, count in edge_types.most_common():
        print(f"  {edge_type}: {count}")

    # Show some specific relationships for Linear
    print(f"\nRelationships for torch.nn.Linear:")
    print("-" * 30)

    # Show incoming relationships (what imports/uses Linear)
    predecessors = list(G.predecessors(linear_node_id))
    print(f"Incoming relationships ({len(predecessors)}):")
    for pred in predecessors[:5]:  # Show first 5
        pred_data = G.nodes[pred]
        print(f"  {pred_data.get('name', pred)} ({pred_data.get('type', 'unknown')})")

    # Show outgoing relationships (what Linear imports/uses)
    successors = list(G.successors(linear_node_id))
    print(f"\nOutgoing relationships ({len(successors)}):")
    for succ in successors[:5]:  # Show first 5
        succ_data = G.nodes[succ]
        print(f"  {succ_data.get('name', succ)} ({succ_data.get('type', 'unknown')})")

if __name__ == "__main__":
    main()