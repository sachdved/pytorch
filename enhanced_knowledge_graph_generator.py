#!/usr/bin/env python3
"""
Enhanced Knowledge Graph Generator for PyTorch
This script demonstrates how to enhance the knowledge graph generation
to capture edges between nodes.
"""

import ast
import os
import json
from collections import defaultdict
import networkx as nx

def parse_python_file(file_path):
    """
    Parse a Python file and extract AST nodes with relationships.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)
        relationships = []

        # Track imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    relationships.append({
                        'type': 'imports',
                        'source': file_path,
                        'target': alias.name,
                        'properties': {'import_type': 'import'}
                    })
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    relationships.append({
                        'type': 'imports',
                        'source': file_path,
                        'target': node.module,
                        'properties': {'import_type': 'from_import', 'level': node.level}
                    })
            elif isinstance(node, ast.ClassDef):
                # Track inheritance relationships
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        relationships.append({
                            'type': 'inheritance',
                            'source': file_path + ':' + node.name,
                            'target': base.id,
                            'properties': {'class_name': node.name}
                        })
            elif isinstance(node, ast.Call):
                # Track function calls
                if isinstance(node.func, ast.Name):
                    relationships.append({
                        'type': 'uses',
                        'source': file_path,
                        'target': node.func.id,
                        'properties': {'call_type': 'function_call'}
                    })
                elif isinstance(node.func, ast.Attribute):
                    relationships.append({
                        'type': 'uses',
                        'source': file_path,
                        'target': node.func.attr,
                        'properties': {'call_type': 'method_call'}
                    })

        return relationships
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def build_enhanced_knowledge_graph(root_dir='torch'):
    """
    Build an enhanced knowledge graph with edges between nodes.
    """
    print("Building enhanced knowledge graph...")

    # Initialize graph
    graph = {
        'nodes': [],
        'edges': [],
        'metadata': {
            'description': 'Enhanced knowledge graph with edges',
            'source': 'AST parsing of PyTorch source code',
            'version': '1.0'
        }
    }

    # Track node IDs to avoid duplicates
    node_ids = set()

    # Parse all Python files in the directory
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)

                # Parse the file for nodes and relationships
                try:
                    # Extract node information
                    node_id = file_path

                    # Create node
                    node = {
                        'id': node_id,
                        'name': file,
                        'type': 'file',
                        'path': file_path,
                        'description': f'Python file: {file_path}'
                    }

                    if node_id not in node_ids:
                        graph['nodes'].append(node)
                        node_ids.add(node_id)

                    # Parse relationships in the file
                    relationships = parse_python_file(file_path)

                    # Add relationships to edges
                    for rel in relationships:
                        # Ensure source and target nodes exist
                        source_id = rel['source']
                        target_id = rel['target']

                        # Add source node if it doesn't exist
                        if source_id not in node_ids:
                            source_node = {
                                'id': source_id,
                                'name': source_id.split(':')[-1] if ':' in source_id else source_id,
                                'type': 'unknown',
                                'path': source_id,
                                'description': f'Node: {source_id}'
                            }
                            graph['nodes'].append(source_node)
                            node_ids.add(source_id)

                        # Add target node if it doesn't exist
                        if target_id not in node_ids:
                            target_node = {
                                'id': target_id,
                                'name': target_id,
                                'type': 'unknown',
                                'path': target_id,
                                'description': f'Node: {target_id}'
                            }
                            graph['nodes'].append(target_node)
                            node_ids.add(target_id)

                        # Add edge
                        edge = {
                            'source': source_id,
                            'target': target_id,
                            'type': rel['type'],
                            'properties': rel['properties']
                        }
                        graph['edges'].append(edge)

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    return graph

def save_knowledge_graph(graph, filepath):
    """Save the knowledge graph to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(graph, f, indent=2)
    print(f"Knowledge graph saved to {filepath}")

def main():
    """Main function to demonstrate enhanced knowledge graph generation."""
    print("Enhanced Knowledge Graph Generator")
    print("=" * 50)

    # Build enhanced knowledge graph
    enhanced_graph = build_enhanced_knowledge_graph()

    print(f"Generated graph with:")
    print(f"  - {len(enhanced_graph['nodes'])} nodes")
    print(f"  - {len(enhanced_graph['edges'])} edges")

    # Save the enhanced graph
    save_knowledge_graph(enhanced_graph, 'enhanced_knowledge_graph.json')

    # Show sample edges
    if enhanced_graph['edges']:
        print("\nSample edges:")
        for i, edge in enumerate(enhanced_graph['edges'][:5]):
            print(f"  {i+1}. {edge['source']} -> {edge['target']} ({edge['type']})")

if __name__ == "__main__":
    main()