"""
Detailed Knowledge Graph Visualization for PyTorch Codebase

This script loads and visualizes the detailed knowledge graph from codebase_knowledge_graph.json
using NetworkX and Matplotlib.

Usage in Jupyter Notebook:
    %run visualize_knowledge_graph.py
    visualize_pytorch_knowledge_graph()
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import rcParams
from collections import Counter
import numpy as np

# Configure matplotlib for Jupyter
rcParams['figure.figsize'] = (20, 16)
rcParams['font.size'] = 8
plt.style.use('seaborn-v0_8-darkgrid')

# Node type colors for legend
NODE_TYPE_COLORS = {
    'root_module': '#E74C3C',      # Red
    'submodule': '#3498DB',        # Blue
    'class': '#9B59B6',            # Purple
    'function': '#1ABC9C',         # Teal
    'method': '#F39C12',           # Orange
    'config': '#95A5A6',           # Gray
    'file': '#34495E',             # Dark Blue
    'directory': '#E67E22',        # Brown
    'other': '#7F8C8D'             # Light Gray
}

# Edge color mapping
EDGE_COLOR_MAP = {
    'inheritance': '#9B59B6',      # Purple
    'imports': '#3498DB',          # Blue
    'calls': '#E74C3C',            # Red
    'test_of': '#F39C12',          # Orange
    'belongs_to': '#1ABC9C',       # Teal
    'uses': '#95A5A6',             # Gray
    'other': '#BDC3C7'             # Light gray
}


def load_knowledge_graph(filepath='codebase_knowledge_graph.json'):
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
    edges_data = knowledge_graph.get('edges', knowledge_graph.get('links', []))
    for link in edges_data:
        G.add_edge(
            link['source'],
            link['target'],
            link_type=link['type'],
            **link.get('properties', {})
        )

    return G


def color_by_type(G):
    """Assign colors based on node type."""
    node_colors = {}

    for node_id, node_data in G.nodes(data=True):
        node_type = node_data.get('type', 'other')
        node_colors[node_id] = NODE_TYPE_COLORS.get(node_type, NODE_TYPE_COLORS['other'])

    return node_colors


def get_edge_width(G, edge_type='default'):
    """Assign edge widths based on type."""
    if edge_type == 'default':
        return 1
    return 2


def visualize_pytorch_knowledge_graph(filepath='codebase_knowledge_graph.json', max_nodes=100):
    """
    Main visualization function for detailed knowledge graph.

    Parameters:
        filepath: Path to the knowledge graph JSON file
        max_nodes: Maximum number of nodes to display (for better layout)
    """
    # Load and build graph
    knowledge_graph = load_knowledge_graph(filepath)
    G = build_nx_graph(knowledge_graph)

    print("=" * 60)
    print("PYTORCH CODEBASE KNOWLEDGE GRAPH")
    print("=" * 60)
    print(f"\nGraph Statistics:")
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")
    print(f"\nNode Types:")
    node_type_counts = Counter(node_data.get('type', 'other') for _, node_data in G.nodes(data=True))
    for node_type, count in sorted(node_type_counts.items(), key=lambda x: -x[1]):
        print(f"  {node_type}: {count}")
    print(f"\nEdge Types:")
    edge_type_counts = Counter(data.get('link_type', 'other') for _, _, data in G.edges(data=True))
    for edge_type, count in sorted(edge_type_counts.items(), key=lambda x: -x[1]):
        print(f"  {edge_type}: {count}")

    # Component analysis
    all_components = list(nx.connected_components(G.to_undirected()))
    largest_cc = max(all_components, key=len)
    print(f"\nConnected Components Analysis:")
    print(f"  Largest component: {len(largest_cc)} nodes")
    print(f"  Total components: {len(all_components)}")

    # Get top N components to show (if graph is larger than max_nodes)
    all_nodes = set(G.nodes())
    sub_nodes = set()

    if G.number_of_nodes() > max_nodes:
        # Get top components that fit within max_nodes
        for i, component in enumerate(sorted(all_components, key=len, reverse=True)):
            if len(sub_nodes) + len(component) <= max_nodes:
                sub_nodes.update(component)
            else:
                # Take as many as possible from this component
                remaining = max_nodes - len(sub_nodes)
                sub_nodes.update(list(component)[:remaining])
            if len(sub_nodes) >= max_nodes:
                break

        G = G.subgraph(sub_nodes).copy()
        print(f"Showing top components: {len(sub_nodes)} nodes")

    # Color nodes by type
    node_colors = color_by_type(G)

    # Edge color mapping
    edge_colors = EDGE_COLOR_MAP

    # Layout - use spring layout for better visualization
    try:
        pos = nx.spring_layout(G, k=0.5, iterations=50)
    except Exception:
        pos = nx.circular_layout(G)

    # Create figure
    fig, ax = plt.subplots(figsize=(20, 16))

    # Draw edges grouped by type
    for edge_type in set(d.get('link_type', 'other') for _, _, d in G.edges(data=True)):
        edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('link_type') == edge_type]
        if not edges:
            continue
        color = edge_colors.get(edge_type, edge_colors['other'])
        width = 1 if edge_type == 'imports' or edge_type == 'calls' else 2
        alpha = 0.4 if edge_type in ['imports', 'calls'] else 0.6
        nx.draw_networkx_edges(
            G, pos,
            edgelist=edges,
            edge_color=color,
            width=width,
            alpha=alpha,
            arrows=True,
            arrowsize=15,
            connectionstyle='arc3,rad=0.1',
            label=edge_type
        )

    # Draw nodes with size based on degree
    degrees = dict(G.degree())
    nx.set_node_attributes(G, degrees, 'degree')
    max_degree = max(degrees.values()) if degrees else 1

    # Normalize node sizes
    node_sizes = [300 + (degrees.get(n, 0) / max_degree) * 400 for n in G.nodes()]

    nx.draw_networkx_nodes(
        G, pos,
        node_color=list(node_colors.values()),
        node_size=node_sizes,
        alpha=0.85,
        ax=ax
    )

    # Draw labels - show important nodes
    important_nodes = set()
    # All classes and root modules
    important_nodes.update([n for n, d in G.nodes(data=True) if d.get('type') == 'class'])
    # Root modules
    important_nodes.update([n for n, d in G.nodes(data=True) if d.get('type') == 'root_module'])
    # All modules (excluding other)
    important_nodes.update([n for n, d in G.nodes(data=True) if d.get('type') == 'module'])
    # All classes with "Module" in name
    important_nodes.update([n for n, d in G.nodes(data=True) if 'Module' in d.get('name', '')])

    # Limit important nodes to avoid overcrowding
    if len(important_nodes) > 30:
        important_nodes = list(important_nodes)[:30]

    labels = {}
    for n, data in G.nodes(data=True):
        if n in important_nodes:
            name = data.get('name', n)
            # Shorten module paths for clarity
            if '/' in name and name.count('/') > 1:
                parts = name.split('/')
                name = '/'.join(parts[-3:]) if len(parts) > 3 else parts[-1]
            labels[n] = name

    nx.draw_networkx_labels(
        G, pos,
        labels,
        font_size=6,
        font_weight='bold',
        ax=ax
    )

    # Create legend for node types
    legend_elements = []
    for node_type, color in NODE_TYPE_COLORS.items():
        if node_type != 'other':
            legend_elements.append(
                plt.Line2D([0], [0], marker='o', color='w',
                          markerfacecolor=color, markersize=6,
                          label=f"{node_type.replace('_', ' ').title()}")
            )

    ax.legend(handles=legend_elements, loc='upper right', fontsize=6, framealpha=0.9)

    # Add edge legend
    edge_legend = []
    for edge_type, color in edge_colors.items():
        edge_legend.append(
            plt.Line2D([0], [0], color=color, linewidth=2,
                      label=f"{edge_type.replace('_', ' ').title()}")
        )

    ax.legend(handles=edge_legend, loc='lower left', fontsize=6, framealpha=0.9)

    # Title and labels
    ax.set_title('PyTorch Codebase Knowledge Graph\n(Detailed - Classes, Functions, Methods)',
                 fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')

    plt.tight_layout()
    plt.show()

    return G, pos


def explore_graph(G):
    """Interactive exploration of the knowledge graph."""
    print("\n" + "=" * 60)
    print("INTERACTIVE GRAPH EXPLORATION")
    print("=" * 60)

    # 1. Find most connected nodes
    degrees = dict(G.degree())
    sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:15]

    print("\n1. Most Connected Nodes (Top 15):")
    print("   Node ID (Name) - Connections")
    for node_id, degree in sorted_nodes:
        name = G.nodes[node_id].get('name', node_id)
        print(f"   {name[:30]:<30} - {degree}")

    # 2. Find classes by module
    print("\n2. Classes by Module:")
    module_classes = {}
    for node_id, data in G.nodes(data=True):
        if data.get('type') == 'class':
            module = data.get('path', '').split('/')[-2] if '/' in data.get('path', '') else 'unknown'
            module_classes.setdefault(module, []).append(data.get('name', node_id))

    for module, classes in sorted(module_classes.items()):
        print(f"\n   {module}:")
        for cls in classes[:10]:  # Show top 10
            print(f"     - {cls}")
        if len(classes) > 10:
            print(f"     ... and {len(classes) - 10} more")

    # 3. Find specific subsystems
    print("\n3. Key Subsystems:")

    # Inductor
    inductor_nodes = [n for n, d in G.nodes(data=True)
                     if 'inductor' in d.get('name', '').lower()]
    print(f"\n   TorchInductor ({len(inductor_nodes)} components):")
    for node in sorted(inductor_nodes, key=lambda x: G.nodes[x].get('name', ''))[:10]:
        print(f"     - {G.nodes[node].get('name', node)}")

    # Dynamo
    dynamo_nodes = [n for n, d in G.nodes(data=True)
                   if 'dynamo' in d.get('name', '').lower()]
    print(f"\n   TorchDynamo ({len(dynamo_nodes)} components):")
    for node in sorted(dynamo_nodes, key=lambda x: G.nodes[x].get('name', ''))[:10]:
        print(f"     - {G.nodes[node].get('name', node)}")

    # FX
    fx_nodes = [n for n, d in G.nodes(data=True)
               if 'fx' in d.get('name', '').lower()]
    print(f"\n   TorchFX ({len(fx_nodes)} components):")
    for node in sorted(fx_nodes, key=lambda x: G.nodes[x].get('name', ''))[:10]:
        print(f"     - {G.nodes[node].get('name', node)}")

    # NN
    nn_nodes = [n for n, d in G.nodes(data=True)
               if 'nn' in d.get('path', '').lower() and d.get('type') == 'class']
    print(f"\n   torch.nn Classes ({len(nn_nodes)}):")
    for node in sorted(nn_nodes, key=lambda x: G.nodes[x].get('name', ''))[:10]:
        print(f"     - {G.nodes[node].get('name', node)}")

    # 4. Find inheritance chains
    print("\n4. Key Inheritance Chains:")
    for node_id, data in G.nodes(data=True):
        if data.get('type') == 'class' and 'Module' in data.get('name', ''):
            superclasses = list(G.predecessors(node_id))
            if superclasses:
                print(f"\n   {data.get('name', node_id)}:")
                for sup in superclasses:
                    print(f"     inherits from: {G.nodes[sup].get('name', sup)}")

    # 5. Module dependencies
    print("\n5. Module Import Dependencies:")
    module_imports = {}
    for node_id, data in G.nodes(data=True):
        if data.get('type') in ['file', 'module']:
            module = data.get('path', '').split('/')[-2] if '/' in data.get('path', '') else 'unknown'
            imports = list(G.successors(node_id))
            if imports:
                module_imports[module] = imports[:5]  # Top 5 imports

    for module, imports in sorted(module_imports.items())[:10]:
        print(f"\n   {module}:")
        for imp in imports:
            print(f"     imports: {G.nodes[imp].get('name', imp)}")

    print("\n" + "=" * 60)


# Convenience function for Jupyter
def kg():
    """Quick access to knowledge graph visualization."""
    return visualize_pytorch_knowledge_graph()


# Interactive exploration
def explore():
    """Interactive exploration."""
    filepath = 'codebase_knowledge_graph.json'
    knowledge_graph = load_knowledge_graph(filepath)
    G = build_nx_graph(knowledge_graph)
    explore_graph(G)


if __name__ == '__main__':
    # Run in script mode
    G, pos = visualize_pytorch_knowledge_graph()
    explore_graph(G)