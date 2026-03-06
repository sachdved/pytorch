#!/usr/bin/env python3
"""
Knowledge Graph Converter
Converts knowledge graph files to be compatible with frontend visualization tool
"""

import json
import sys
import os

def convert_knowledge_graph(input_file, output_file):
    """
    Convert knowledge graph file to frontend-compatible format
    """
    try:
        # Read the input file
        with open(input_file, 'r') as f:
            data = json.load(f)

        # Normalize the structure to match frontend expectations
        converted_data = {
            "nodes": [],
            "edges": []
        }

        # Convert nodes to expected format
        if "nodes" in data:
            for node in data["nodes"]:
                converted_node = {
                    "id": node.get("id", node.get("name", "")),
                    "name": node.get("name", ""),
                    "type": node.get("type", "unknown"),
                    "path": node.get("path", ""),
                    "description": node.get("description", "")
                }
                converted_data["nodes"].append(converted_node)
        else:
            # If nodes are in a different structure, try to extract them
            for node in data:
                converted_node = {
                    "id": node.get("id", node.get("name", "")),
                    "name": node.get("name", ""),
                    "type": node.get("type", "unknown"),
                    "path": node.get("path", ""),
                    "description": node.get("description", "")
                }
                converted_data["nodes"].append(converted_node)

        # Convert edges to expected format
        if "edges" in data:
            for edge in data["edges"]:
                converted_edge = {
                    "source": edge.get("source", ""),
                    "target": edge.get("target", ""),
                    "type": edge.get("type", "dependency")
                }
                converted_data["edges"].append(converted_edge)
        else:
            # If edges are in a different structure, try to extract them
            for edge in data:
                converted_edge = {
                    "source": edge.get("source", ""),
                    "target": edge.get("target", ""),
                    "type": edge.get("type", "dependency")
                }
                converted_data["edges"].append(converted_edge)

        # Write the converted data
        with open(output_file, 'w') as f:
            json.dump(converted_data, f, indent=2)

        print(f"Successfully converted {input_file} to {output_file}")
        print(f"Nodes: {len(converted_data['nodes'])}")
        print(f"Edges: {len(converted_data['edges'])}")

    except Exception as e:
        print(f"Error converting {input_file}: {str(e)}")
        return False

    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: python knowledge_graph_converter.py <input_file> <output_file>")
        print("Example: python knowledge_graph_converter.py codebase_knowledge_graph.json frontend_compatible.json")
        return

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist")
        return

    convert_knowledge_graph(input_file, output_file)

if __name__ == "__main__":
    main()