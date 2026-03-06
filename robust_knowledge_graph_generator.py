#!/usr/bin/env python3
"""
Robust PyTorch Knowledge Graph Generator
This script builds a knowledge graph of the PyTorch codebase with error handling
for complex syntax and comprehensive component extraction.
"""

import ast
import os
import json
import re
from collections import defaultdict, Counter
import sys
from typing import Dict, List, Set, Tuple, Any

class RobustPyTorchKnowledgeGraphGenerator:
    def __init__(self, root_dir='torch'):
        self.root_dir = root_dir
        self.nodes = []
        self.edges = []
        self.node_id_to_info = {}
        self.processed_files = 0

    def safe_extract_docstring(self, node) -> str:
        """Safely extract docstring from AST node."""
        try:
            if hasattr(node, 'docstring') and node.docstring:
                return str(node.docstring)
            elif hasattr(node, 'body') and node.body:
                # Look for string literal in first position of body
                if len(node.body) > 0 and isinstance(node.body[0], ast.Expr):
                    expr = node.body[0]
                    if hasattr(expr.value, 's'):
                        return str(expr.value.s)
                    elif hasattr(expr.value, 'value') and isinstance(expr.value.value, str):
                        return str(expr.value.value)
        except Exception:
            pass
        return ""

    def extract_module_name_from_path(self, file_path: str) -> str:
        """Extract module name from file path."""
        try:
            # Remove torch/ prefix and .py extension
            module_path = file_path.replace(self.root_dir + '/', '', 1)
            module_path = module_path.replace('.py', '')
            # Convert to dotted module name
            module_name = module_path.replace('/', '.')
            return module_name
        except Exception:
            return file_path

    def get_node_name(self, node) -> str:
        """Get name from AST node safely."""
        try:
            if hasattr(node, 'name'):
                return node.name
            elif hasattr(node, 'id'):
                return node.id
        except Exception:
            return "unknown"

    def parse_file_components(self, file_path: str) -> List[Dict]:
        """Parse a Python file and extract all components with error handling."""
        components = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Skip files that are too large or problematic
            if len(content) > 1000000:  # 1MB limit
                return components

            tree = ast.parse(content)

            # Parse all components in the file
            for node in ast.walk(tree):
                try:
                    if isinstance(node, ast.ClassDef):
                        # Extract class information
                        class_info = {
                            'id': f"{file_path}:{self.get_node_name(node)}",
                            'name': self.get_node_name(node),
                            'type': 'class',
                            'path': file_path,
                            'module': self.extract_module_name_from_path(file_path),
                            'line': getattr(node, 'lineno', 0),
                            'docstring': self.safe_extract_docstring(node),
                            'bases': [],
                            'methods': [],
                            'decorators': [],
                            'attributes': []
                        }

                        # Extract bases (parent classes)
                        try:
                            for base in node.bases:
                                if isinstance(base, ast.Name):
                                    class_info['bases'].append(base.id)
                                elif isinstance(base, ast.Attribute):
                                    class_info['bases'].append(f"{base.value.id}.{base.attr}")
                        except Exception:
                            pass

                        # Extract decorators
                        try:
                            for decorator in node.decorator_list:
                                if isinstance(decorator, ast.Name):
                                    class_info['decorators'].append(decorator.id)
                                elif isinstance(decorator, ast.Attribute):
                                    class_info['decorators'].append(f"{decorator.value.id}.{decorator.attr}")
                                elif hasattr(decorator, 'func') and hasattr(decorator.func, 'attr'):
                                    class_info['decorators'].append(f"{decorator.func.value.id}.{decorator.func.attr}")
                        except Exception:
                            pass

                        # Parse methods within the class
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                try:
                                    method_info = {
                                        'id': f"{file_path}:{self.get_node_name(node)}.{self.get_node_name(item)}",
                                        'name': self.get_node_name(item),
                                        'type': 'method',
                                        'path': file_path,
                                        'module': self.extract_module_name_from_path(file_path),
                                        'line': getattr(item, 'lineno', 0),
                                        'docstring': self.safe_extract_docstring(item),
                                        'decorators': [],
                                        'args': []
                                    }

                                    # Extract method arguments
                                    try:
                                        if hasattr(item, 'args'):
                                            for arg in item.args.args:
                                                if hasattr(arg, 'arg'):
                                                    method_info['args'].append(arg.arg)
                                    except Exception:
                                        pass

                                    # Extract decorators
                                    try:
                                        for decorator in item.decorator_list:
                                            if isinstance(decorator, ast.Name):
                                                method_info['decorators'].append(decorator.id)
                                            elif isinstance(decorator, ast.Attribute):
                                                method_info['decorators'].append(f"{decorator.value.id}.{decorator.attr}")
                                            elif hasattr(decorator, 'func') and hasattr(decorator.func, 'attr'):
                                                method_info['decorators'].append(f"{decorator.func.value.id}.{decorator.func.attr}")
                                    except Exception:
                                        pass

                                    class_info['methods'].append(method_info)
                                except Exception:
                                    continue  # Skip problematic methods

                        components.append(class_info)

                    elif isinstance(node, ast.FunctionDef):
                        # Extract function information
                        func_info = {
                            'id': f"{file_path}:{self.get_node_name(node)}",
                            'name': self.get_node_name(node),
                            'type': 'function',
                            'path': file_path,
                            'module': self.extract_module_name_from_path(file_path),
                            'line': getattr(node, 'lineno', 0),
                            'docstring': self.safe_extract_docstring(node),
                            'decorators': [],
                            'args': []
                        }

                        # Extract function arguments
                        try:
                            if hasattr(node, 'args'):
                                for arg in node.args.args:
                                    if hasattr(arg, 'arg'):
                                        func_info['args'].append(arg.arg)
                        except Exception:
                            pass

                        # Extract decorators
                        try:
                            for decorator in node.decorator_list:
                                if isinstance(decorator, ast.Name):
                                    func_info['decorators'].append(decorator.id)
                                elif isinstance(decorator, ast.Attribute):
                                    func_info['decorators'].append(f"{decorator.value.id}.{decorator.attr}")
                                elif hasattr(decorator, 'func') and hasattr(decorator.func, 'attr'):
                                    func_info['decorators'].append(f"{decorator.func.value.id}.{decorator.func.attr}")
                        except Exception:
                            pass

                        components.append(func_info)

                    elif isinstance(node, ast.Assign):
                        # Extract variable information
                        try:
                            for target in node.targets:
                                if isinstance(target, ast.Name):
                                    var_info = {
                                        'id': f"{file_path}:{target.id}",
                                        'name': target.id,
                                        'type': 'variable',
                                        'path': file_path,
                                        'module': self.extract_module_name_from_path(file_path),
                                        'line': getattr(node, 'lineno', 0),
                                        'docstring': '',
                                        'value': str(node.value) if hasattr(node, 'value') else ''
                                    }
                                    components.append(var_info)
                        except Exception:
                            continue  # Skip problematic assignments

                except Exception:
                    continue  # Skip problematic nodes in file

        except Exception as e:
            # Skip files that can't be parsed
            pass

        return components

    def build_graph_from_files(self):
        """Build the complete knowledge graph from all files with error handling."""
        print("Building knowledge graph from files...")

        processed_files = 0
        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        # Parse components in the file
                        components = self.parse_file_components(file_path)

                        # Add file node
                        file_node = {
                            'id': file_path,
                            'name': file,
                            'type': 'file',
                            'path': file_path,
                            'module': self.extract_module_name_from_path(file_path),
                            'description': f"Python file: {file}",
                            'line_count': 0
                        }

                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                file_node['line_count'] = len(content.split('\n'))
                        except Exception:
                            pass

                        self.nodes.append(file_node)

                        # Add component nodes
                        for component in components:
                            self.nodes.append(component)
                            self.node_id_to_info[component['id']] = component

                        processed_files += 1

                        if processed_files % 100 == 0:
                            print(f"Processed {processed_files} files...")

                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
                        continue

        print(f"Successfully processed {processed_files} files")
        print(f"Total nodes: {len(self.nodes)}")

    def add_inheritance_relationships(self):
        """Add inheritance relationships based on class hierarchy."""
        print("Adding inheritance relationships...")

        # Create a mapping of class names to their full IDs
        class_name_to_id = {}
        for node in self.nodes:
            if node['type'] == 'class':
                class_name_to_id[node['name']] = node['id']

        # Add inheritance edges based on class bases
        inheritance_count = 0
        for node in self.nodes:
            if node['type'] == 'class' and 'bases' in node:
                for base_name in node['bases']:
                    # If base exists in our graph, create inheritance edge
                    if base_name in class_name_to_id:
                        base_id = class_name_to_id[base_name]
                        self.edges.append({
                            'source': node['id'],
                            'target': base_id,
                            'type': 'inheritance',
                            'properties': {
                                'source_class': node['name'],
                                'target_class': base_name,
                                'relationship': 'inherits'
                            }
                        })
                        inheritance_count += 1

        print(f"Added {inheritance_count} inheritance relationships")

    def add_module_relationships(self):
        """Add relationships between components in the same module."""
        print("Adding module relationships...")

        # Group components by module
        module_components = defaultdict(list)
        for node in self.nodes:
            if 'module' in node and node['module']:
                module_components[node['module']].append(node['id'])

        # Add relationships between components in the same module
        module_edge_count = 0
        for module, component_ids in module_components.items():
            if len(component_ids) > 1:
                # Add relationships between all pairs in the same module
                for i in range(len(component_ids)):
                    for j in range(i+1, len(component_ids)):
                        self.edges.append({
                            'source': component_ids[i],
                            'target': component_ids[j],
                            'type': 'module_internal',
                            'properties': {
                                'relationship': 'module_internal_usage',
                                'module': module
                            }
                        })
                        module_edge_count += 1

        print(f"Added {module_edge_count} module internal relationships")

    def build_comprehensive_graph(self):
        """Build the complete comprehensive knowledge graph."""
        print("Building comprehensive knowledge graph...")

        # Parse all files
        self.build_graph_from_files()

        # Add inheritance relationships
        self.add_inheritance_relationships()

        # Add module relationships
        self.add_module_relationships()

        # Create graph structure
        graph = {
            'nodes': self.nodes,
            'edges': self.edges,
            'metadata': {
                'description': 'Comprehensive PyTorch knowledge graph',
                'source': 'AST parsing of PyTorch source code',
                'version': '1.0',
                'total_nodes': len(self.nodes),
                'total_edges': len(self.edges),
                'root_directory': self.root_dir,
                'status': 'completed'
            }
        }

        return graph

    def save_graph(self, graph, filepath='comprehensive_knowledge_graph.json'):
        """Save the knowledge graph to a JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(graph, f, indent=2, ensure_ascii=False)
            print(f"Knowledge graph saved to {filepath}")
            print(f"Total nodes: {len(graph['nodes'])}")
            print(f"Total edges: {len(graph['edges'])}")
        except Exception as e:
            print(f"Error saving graph: {e}")

def main():
    """Main function to generate comprehensive knowledge graph."""
    print("Robust PyTorch Knowledge Graph Generator")
    print("=" * 60)

    # Create generator
    generator = RobustPyTorchKnowledgeGraphGenerator(root_dir='torch')

    # Build comprehensive graph
    try:
        graph = generator.build_comprehensive_graph()

        # Save the graph
        generator.save_graph(graph, 'comprehensive_knowledge_graph.json')

        # Show statistics
        print("\n" + "=" * 60)
        print("GENERATION COMPLETE")
        print("=" * 60)
        print(f"Total nodes: {len(graph['nodes'])}")
        print(f"Total edges: {len(graph['edges'])}")

        # Show sample nodes and edges
        print("\nSample nodes:")
        sample_nodes = graph['nodes'][:10] if len(graph['nodes']) >= 10 else graph['nodes']
        for i, node in enumerate(sample_nodes):
            print(f"  {i+1}. {node['name']} ({node['type']}) in {node.get('path', 'no path')}")

        print("\nSample edges:")
        sample_edges = graph['edges'][:10] if len(graph['edges']) >= 10 else graph['edges']
        for i, edge in enumerate(sample_edges):
            print(f"  {i+1}. {edge['source']} -> {edge['target']} ({edge['type']})")

    except Exception as e:
        print(f"Error during generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()