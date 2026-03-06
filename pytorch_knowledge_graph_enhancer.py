#!/usr/bin/env python3
"""
PyTorch Knowledge Graph Enhancer
Enhances existing knowledge graphs to add meaningful edges between nodes.
"""

import ast
import os
import json
from collections import defaultdict, Counter
import re

class PyTorchKnowledgeGraphEnhancer:
    def __init__(self):
        self.edges = []
        self.node_types = {}
        self.node_paths = {}

    def extract_nodes_from_file(self, file_path):
        """Extract node information from a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            nodes = []

            # Extract class definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_node = {
                        'id': f"{file_path}:{node.name}",
                        'name': node.name,
                        'type': 'class',
                        'path': file_path,
                        'line': node.lineno,
                        'description': f"Class {node.name} defined in {file_path}"
                    }
                    nodes.append(class_node)

                    # Track inheritance
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            self.edges.append({
                                'source': f"{file_path}:{node.name}",
                                'target': base.id,
                                'type': 'inheritance',
                                'properties': {
                                    'class_name': node.name,
                                    'base_class': base.id
                                }
                            })

            # Extract function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_node = {
                        'id': f"{file_path}:{node.name}",
                        'name': node.name,
                        'type': 'function',
                        'path': file_path,
                        'line': node.lineno,
                        'description': f"Function {node.name} defined in {file_path}"
                    }
                    nodes.append(func_node)

            return nodes

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return []

    def extract_imports_and_relationships(self, file_path):
        """Extract import relationships from a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Create edge from current file to imported module
                        self.edges.append({
                            'source': file_path,
                            'target': alias.name,
                            'type': 'imports',
                            'properties': {
                                'import_type': 'import',
                                'alias': alias.asname if alias.asname else None
                            }
                        })
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Create edge from current file to imported module
                        self.edges.append({
                            'source': file_path,
                            'target': node.module,
                            'type': 'imports',
                            'properties': {
                                'import_type': 'from_import',
                                'level': node.level,
                                'module': node.module
                            }
                        })

        except Exception as e:
            print(f"Error extracting imports from {file_path}: {e}")

    def enhance_knowledge_graph(self, existing_graph, pytorch_root='torch'):
        """
        Enhance an existing knowledge graph with edges.
        """
        print("Enhancing knowledge graph with edges...")

        # First, let's process all Python files to extract nodes and relationships
        node_id_to_info = {node['id']: node for node in existing_graph['nodes']}

        # Process files to find import relationships
        print("Processing Python files for import relationships...")
        for root, dirs, files in os.walk(pytorch_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.extract_imports_and_relationships(file_path)

        # Process files to find class relationships
        print("Processing Python files for class relationships...")
        for root, dirs, files in os.walk(pytorch_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    nodes = self.extract_nodes_from_file(file_path)
                    # Add new nodes to the graph if they don't exist
                    for node in nodes:
                        if node['id'] not in node_id_to_info:
                            existing_graph['nodes'].append(node)
                            node_id_to_info[node['id']] = node

        # Add the new edges to the existing graph
        existing_graph['edges'] = existing_graph.get('edges', []) + self.edges

        # Add metadata about the enhancement
        if 'metadata' not in existing_graph:
            existing_graph['metadata'] = {}
        existing_graph['metadata']['enhanced_with_edges'] = True
        existing_graph['metadata']['edge_count'] = len(self.edges)

        print(f"Added {len(self.edges)} edges to the knowledge graph")
        return existing_graph

    def analyze_edge_types(self):
        """Analyze the types of edges that were added."""
        edge_types = Counter(edge['type'] for edge in self.edges)
        print("Edge type distribution:")
        for edge_type, count in edge_types.most_common():
            print(f"  {edge_type}: {count}")

def main():
    """Main function to demonstrate the enhancement."""
    print("PyTorch Knowledge Graph Enhancer")
    print("=" * 50)

    # Load existing knowledge graph
    try:
        with open('codebase_knowledge_graph.json', 'r') as f:
            existing_graph = json.load(f)

        print(f"Loaded existing graph with {len(existing_graph['nodes'])} nodes")
        print(f"Original graph has {len(existing_graph.get('edges', []))} edges")

        # Enhance the graph
        enhancer = PyTorchKnowledgeGraphEnhancer()
        enhanced_graph = enhancer.enhance_knowledge_graph(existing_graph)

        # Save the enhanced graph
        with open('enhanced_knowledge_graph_with_edges.json', 'w') as f:
            json.dump(enhanced_graph, f, indent=2)

        print(f"Enhanced graph saved with {len(enhanced_graph['edges'])} edges")

        # Analyze edge types
        enhancer.analyze_edge_types()

    except FileNotFoundError:
        print("Error: Could not find the existing knowledge graph file")
        print("Please ensure 'codebase_knowledge_graph.json' exists in the directory")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()