#!/usr/bin/env python3
"""
Simple analysis of torch.nn.Linear and its related components in the knowledge graph.
"""

import json
import re

def load_knowledge_graph(filepath='codebase_knowledge_graph_torch_enhanced.json'):
    """Load knowledge graph from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

def analyze_linear_class():
    """Analyze torch.nn.Linear and related components."""
    print("Analyzing torch.nn.Linear in the knowledge graph")
    print("=" * 60)

    # Load the knowledge graph
    knowledge_graph = load_knowledge_graph()

    print(f"Total nodes in knowledge graph: {len(knowledge_graph['nodes'])}")

    # Find torch.nn.Linear class
    linear_node = None
    for node in knowledge_graph['nodes']:
        if node.get('name') == 'Linear' and 'torch/nn/modules/linear.py' in node.get('path', ''):
            linear_node = node
            break

    if not linear_node:
        print("Could not find torch.nn.Linear class")
        return

    print(f"Found torch.nn.Linear class:")
    print(f"  ID: {linear_node['id']}")
    print(f"  Name: {linear_node['name']}")
    print(f"  Type: {linear_node['type']}")
    print(f"  Path: {linear_node['path']}")
    print(f"  Line: {linear_node.get('line', 'N/A')}")

    # Show description if available
    description = linear_node.get('description', '')
    if description:
        print("  Description:")
        # Show first few lines of description
        desc_lines = description.split('\n')[:10]
        for line in desc_lines:
            print(f"    {line}")

    print("\n" + "=" * 60)
    print("Related Linear classes found in the knowledge graph:")
    print("=" * 60)

    # Find all Linear-related classes
    linear_classes = []
    for node in knowledge_graph['nodes']:
        if node.get('name') == 'Linear' and node.get('type') == 'class':
            linear_classes.append(node)

    print(f"Total Linear classes found: {len(linear_classes)}")

    for i, node in enumerate(linear_classes):
        print(f"{i+1}. {node['name']} in {node['path']}")
        print(f"   ID: {node['id']}")
        print(f"   Type: {node['type']}")
        if i < 5:  # Only show first 5 for brevity
            print()

    if len(linear_classes) > 5:
        print(f"... and {len(linear_classes) - 5} more Linear classes")

    print("\n" + "=" * 60)
    print("Module hierarchy related to Linear:")
    print("=" * 60)

    # Find nn module related nodes
    nn_nodes = []
    for node in knowledge_graph['nodes']:
        if 'torch/nn' in node.get('path', '') and node.get('type') in ['class', 'module']:
            nn_nodes.append(node)

    print(f"Total nn module nodes: {len(nn_nodes)}")

    # Group by module path
    modules = {}
    for node in nn_nodes:
        path = node.get('path', '')
        if path:
            module_name = path.split('/')[-1]  # Get filename
            if module_name not in modules:
                modules[module_name] = []
            modules[module_name].append(node)

    # Show first few modules
    for i, (module_name, nodes) in enumerate(list(modules.items())[:10]):
        print(f"{i+1}. {module_name}:")
        for node in nodes[:3]:  # Show first 3 nodes from each module
            print(f"   - {node['name']} ({node['type']})")
        if len(nodes) > 3:
            print(f"   ... and {len(nodes) - 3} more")
        print()

    if len(modules) > 10:
        print(f"... and {len(modules) - 10} more modules")

if __name__ == "__main__":
    analyze_linear_class()