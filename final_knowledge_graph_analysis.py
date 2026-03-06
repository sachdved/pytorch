#!/usr/bin/env python3
"""
Final analysis of the comprehensive PyTorch knowledge graph.
"""

import json
import networkx as nx
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

def load_knowledge_graph(filepath='comprehensive_knowledge_graph.json'):
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
            description=node.get('description', ''),
            module=node.get('module', '')
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

def analyze_linear_components():
    """Analyze torch.nn.Linear and its components."""
    print("Analyzing torch.nn.Linear and its components")
    print("=" * 60)

    # Load the knowledge graph
    knowledge_graph = load_knowledge_graph()
    G = build_nx_graph(knowledge_graph)

    print(f"Graph loaded with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

    # Find torch.nn.Linear
    linear_node_id = None
    for node_id, node_data in G.nodes(data=True):
        if node_data.get('name') == 'Linear' and 'torch/nn/modules/linear.py' in node_data.get('path', ''):
            linear_node_id = node_id
            break

    if not linear_node_id:
        print("Could not find torch.nn.Linear in the knowledge graph")
        # Try to find any Linear class
        linear_nodes = [node_id for node_id, node_data in G.nodes(data=True)
                       if node_data.get('name') == 'Linear']
        if linear_nodes:
            print("Found Linear classes:")
            for node_id in linear_nodes[:5]:
                print(f"  {G.nodes[node_id].get('name')} in {G.nodes[node_id].get('path')}")
        return

    print(f"Found torch.nn.Linear with node ID: {linear_node_id}")

    # Get neighbors (predecessors and successors)
    predecessors = list(G.predecessors(linear_node_id))
    successors = list(G.successors(linear_node_id))

    print(f"\nLinear has {len(predecessors)} incoming relationships and {len(successors)} outgoing relationships")

    # Show inheritance relationships
    inheritance_edges = [(u, v, data) for u, v, data in G.edges(data=True)
                        if data.get('link_type') == 'inheritance' and u == linear_node_id]

    print(f"\nInheritance relationships:")
    for u, v, data in inheritance_edges[:5]:
        v_data = G.nodes[v]
        print(f"  {v_data.get('name', v)} ({v_data.get('type', 'unknown')})")

    # Show module relationships
    module_edges = [(u, v, data) for u, v, data in G.edges(data=True)
                   if data.get('link_type') == 'module_internal' and u == linear_node_id]

    print(f"\nModule internal relationships:")
    for u, v, data in module_edges[:5]:
        v_data = G.nodes[v]
        print(f"  {v_data.get('name', v)} ({v_data.get('type', 'unknown')})")

    # Show node type distribution
    print(f"\nNode type distribution:")
    node_types = Counter(node_data.get('type', 'other') for _, node_data in G.nodes(data=True))
    for node_type, count in node_types.most_common():
        print(f"  {node_type}: {count}")

    # Show edge type distribution
    print(f"\nEdge type distribution:")
    edge_types = Counter(data.get('link_type', 'other') for _, _, data in G.edges(data=True))
    for edge_type, count in edge_types.most_common():
        print(f"  {edge_type}: {count}")

    # Show the most connected nodes
    print(f"\nMost connected nodes:")
    degrees = dict(G.degree())
    sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
    for node_id, degree in sorted_nodes:
        name = G.nodes[node_id].get('name', node_id)
        node_type = G.nodes[node_id].get('type', 'unknown')
        print(f"  {name} ({node_type}): {degree} connections")

    # Show key subsystems
    print(f"\nKey subsystems found:")

    # Find nn module components
    nn_components = [node_id for node_id, node_data in G.nodes(data=True)
                    if 'nn' in node_data.get('module', '') and node_data.get('type') == 'class']
    print(f"  torch.nn classes: {len(nn_components)}")

    # Find quantization components
    quant_components = [node_id for node_id, node_data in G.nodes(data=True)
                       if 'quantized' in node_data.get('module', '') and node_data.get('type') == 'class']
    print(f"  quantized classes: {len(quant_components)}")

    # Find inductive components
    inductor_components = [node_id for node_id, node_data in G.nodes(data=True)
                          if 'inductor' in node_data.get('module', '') and node_data.get('type') == 'class']
    print(f"  inductor classes: {len(inductor_components)}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

def main():
    """Main function."""
    analyze_linear_components()

if __name__ == "__main__":
    main()