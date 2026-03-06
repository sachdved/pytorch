#!/usr/bin/env python3
"""
Simple command-line tool to explore the enhanced PyTorch knowledge graph.
"""

import json
import sys
import os
from collections import Counter

def load_knowledge_graph(file_path="codebase_knowledge_graph_torch_enhanced.json"):
    """Load the enhanced knowledge graph from JSON file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Knowledge graph file {file_path} not found. Please ensure the file exists.")

    with open(file_path, 'r') as f:
        graph = json.load(f)

    print(f"Loaded knowledge graph with {len(graph['nodes'])} nodes")
    print(f"Metadata: {graph['metadata']}")

    return graph

def show_statistics(graph):
    """Show basic statistics about the knowledge graph."""
    nodes = graph['nodes']

    print("\n=== Knowledge Graph Statistics ===")
    print(f"Total nodes: {len(nodes)}")

    # Node type distribution
    type_counts = Counter(node['type'] for node in nodes)
    print("\nNode type distribution:")
    for node_type, count in type_counts.items():
        print(f"  {node_type}: {count}")

    # Top files by node count
    file_counts = Counter(node['path'] for node in nodes)
    print("\nTop 5 files by node count:")
    for file, count in file_counts.most_common(5):
        print(f"  {file}: {count}")

def search_nodes(graph, search_term, column='name'):
    """Search for nodes containing a term."""
    nodes = graph['nodes']
    results = [node for node in nodes if search_term.lower() in node[column].lower()]
    return results

def show_search_results(results, max_results=10):
    """Display search results."""
    print(f"\nFound {len(results)} matching nodes:")

    for i, node in enumerate(results[:max_results]):
        print(f"  {i+1}. {node['name']} ({node['type']}) in {node['path']}")

def show_node_details(graph, node_id):
    """Show detailed information about a specific node."""
    nodes = graph['nodes']
    matching_nodes = [node for node in nodes if node['id'] == node_id]

    if matching_nodes:
        node = matching_nodes[0]
        print(f"\n=== Node Details ===")
        for key, value in node.items():
            print(f"  {key}: {value}")
    else:
        print(f"\nNode with ID '{node_id}' not found.")

def main():
    """Main function to handle command-line arguments."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python explore_knowledge_graph.py stats          # Show statistics")
        print("  python explore_knowledge_graph.py search <term>  # Search for term")
        print("  python explore_knowledge_graph.py show <id>      # Show node details")
        return

    try:
        graph = load_knowledge_graph()

        command = sys.argv[1]

        if command == "stats":
            show_statistics(graph)
        elif command == "search" and len(sys.argv) > 2:
            term = sys.argv[2]
            results = search_nodes(graph, term)
            show_search_results(results)
        elif command == "show" and len(sys.argv) > 2:
            node_id = sys.argv[2]
            show_node_details(graph, node_id)
        else:
            print("Unknown command or missing arguments")
            print("Usage:")
            print("  python explore_knowledge_graph.py stats")
            print("  python explore_knowledge_graph.py search <term>")
            print("  python explore_knowledge_graph.py show <id>")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()