#!/usr/bin/env python3
"""
Visualization of enhanced knowledge graph with neighbors of torch.nn.Linear.
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

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

def visualize_neighbors(G, linear_node_id):
    """Visualize the neighbors of torch.nn.Linear."""
    neighbors = get_neighbors(G, linear_node_id, 10)

    print("10 Neighbors of torch.nn.Linear:")
    print("=" * 50)
    for i, neighbor in enumerate(neighbors, 1):
        print(f"{i}. {neighbor['name']} ({neighbor['type']})")
        print(f"   Path: {neighbor['path']}")
        print()

    # Create a subgraph with Linear and its neighbors
    neighbor_ids = [n['id'] for n in neighbors]
    subgraph_nodes = [linear_node_id] + neighbor_ids

    # Get all edges involving these nodes
    subgraph_edges = []
    for u, v, data in G.edges(data=True):
        if u in subgraph_nodes and v in subgraph_nodes:
            subgraph_edges.append((u, v, data))

    # Create subgraph
    H = nx.DiGraph()
    for node_id in subgraph_nodes:
        H.add_node(node_id, **G.nodes[node_id])

    for u, v, data in subgraph_edges:
        H.add_edge(u, v, **data)

    # Visualize the subgraph
    plt.figure(figsize=(15, 12))

    # Position nodes using spring layout
    try:
        pos = nx.spring_layout(H, k=2, iterations=50)
    except Exception:
        pos = nx.circular_layout(H)

    # Draw edges with different colors based on type
    edge_types = set()
    for u, v, data in H.edges(data=True):
        edge_types.add(data.get('link_type', 'other'))

    # Create edge colors mapping
    edge_colors = {
        'inheritance': 'purple',
        'imports': 'blue',
        'uses': 'red',
        'other': 'gray'
    }

    # Draw edges grouped by type
    for edge_type in edge_types:
        edges = [(u, v) for u, v, d in H.edges(data=True) if d.get('link_type') == edge_type]
        if edges:
            color = edge_colors.get(edge_type, edge_colors['other'])
            width = 2 if edge_type == 'inheritance' else 1
            alpha = 0.7
            nx.draw_networkx_edges(
                H, pos,
                edgelist=edges,
                edge_color=color,
                width=width,
                alpha=alpha,
                arrows=True,
                arrowsize=15,
                connectionstyle='arc3,rad=0.1'
            )

    # Draw nodes
    node_colors = []
    for node_id in H.nodes():
        node_type = H.nodes[node_id].get('type', 'other')
        if node_type == 'class':
            node_colors.append('lightblue')
        elif node_type == 'function':
            node_colors.append('lightgreen')
        elif node_type == 'module':
            node_colors.append('lightyellow')
        else:
            node_colors.append('lightgray')

    nx.draw_networkx_nodes(H, pos, node_color=node_colors, alpha=0.8, node_size=1500)

    # Draw labels
    labels = {}
    for node_id in H.nodes():
        name = H.nodes[node_id].get('name', node_id)
        labels[node_id] = name

    nx.draw_networkx_labels(H, pos, labels, font_size=9)

    # Highlight the main Linear node
    linear_pos = pos.get(linear_node_id, None)
    if linear_pos is not None:
        plt.annotate('torch.nn.Linear',
                   xy=linear_pos,
                   xytext=(10, 10),
                   textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.9),
                   fontsize=12, fontweight='bold')

    plt.title('Neighbors of torch.nn.Linear in Enhanced Knowledge Graph', fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.show()

    return neighbors

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

    # Get and visualize neighbors
    neighbors = visualize_neighbors(G, linear_node_id)

    print("\nDetailed neighbor information:")
    for i, neighbor in enumerate(neighbors, 1):
        print(f"{i}. {neighbor['name']} ({neighbor['type']})")
        print(f"   Path: {neighbor['path']}")
        print()

    # Show some statistics
    print("Graph statistics:")
    print(f"  Total nodes: {G.number_of_nodes()}")
    print(f"  Total edges: {G.number_of_edges()}")

    # Show edge types
    edge_types = Counter(data.get('link_type', 'other') for _, _, data in G.edges(data=True))
    print("  Edge types:")
    for edge_type, count in edge_types.most_common():
        print(f"    {edge_type}: {count}")

if __name__ == "__main__":
    main()