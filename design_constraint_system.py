#!/usr/bin/env python3
"""
Design Constraint System for PyTorch Repository Enhancements
This system allows you to define design constraints for PyTorch enhancements
by specifying new entities and their relationships to the knowledge graph.
"""

import json
import networkx as nx
from collections import Counter, defaultdict
import re
from typing import Dict, List, Set, Tuple, Any

class DesignConstraintSystem:
    def __init__(self, knowledge_graph_path='comprehensive_knowledge_graph.json'):
        """Initialize the design constraint system with a knowledge graph."""
        self.knowledge_graph_path = knowledge_graph_path
        self.knowledge_graph = self.load_knowledge_graph()
        self.G = self.build_nx_graph()
        self.design_constraints = []

    def load_knowledge_graph(self) -> Dict:
        """Load the comprehensive knowledge graph."""
        with open(self.knowledge_graph_path, 'r') as f:
            return json.load(f)

    def build_nx_graph(self) -> nx.DiGraph:
        """Build NetworkX graph from knowledge graph data."""
        G = nx.DiGraph()

        # Add nodes
        for node in self.knowledge_graph['nodes']:
            G.add_node(
                node['id'],
                name=node['name'],
                type=node['type'],
                path=node.get('path', ''),
                description=node.get('description', ''),
                module=node.get('module', '')
            )

        # Add edges
        edges_data = self.knowledge_graph.get('edges', [])
        for link in edges_data:
            G.add_edge(
                link['source'],
                link['target'],
                link_type=link['type'],
                **link.get('properties', {})
            )

        return G

    def get_neighbors(self, node_id: str, depth: int = 1) -> Set[str]:
        """Get neighbors of a node up to specified depth."""
        if depth <= 0:
            return set()

        neighbors = set()
        current_level = {node_id}

        for _ in range(depth):
            next_level = set()
            for node in current_level:
                # Get successors (outgoing relationships)
                for successor in self.G.successors(node):
                    next_level.add(successor)
                # Get predecessors (incoming relationships)
                for predecessor in self.G.predecessors(node):
                    next_level.add(predecessor)
            neighbors.update(next_level)
            current_level = next_level

        return neighbors

    def find_similar_components(self, target_name: str, max_results: int = 10) -> List[Dict]:
        """Find components similar to target name."""
        similar = []
        target_lower = target_name.lower()

        for node_id, node_data in self.G.nodes(data=True):
            if target_lower in node_data.get('name', '').lower():
                similar.append({
                    'id': node_id,
                    'name': node_data.get('name'),
                    'type': node_data.get('type'),
                    'path': node_data.get('path'),
                    'module': node_data.get('module')
                })

        return sorted(similar, key=lambda x: x['name'])[:max_results]

    def analyze_component_context(self, node_id: str) -> Dict[str, Any]:
        """Analyze the context of a component for design guidance."""
        if node_id not in self.G.nodes():
            return {}

        node_data = self.G.nodes[node_id]

        # Get immediate neighbors
        neighbors = list(self.G.neighbors(node_id))

        # Get inheritance relationships
        inheritances = []
        for successor in self.G.successors(node_id):
            edge_data = self.G.get_edge_data(node_id, successor)
            if edge_data and edge_data.get('link_type') == 'inheritance':
                inheritances.append({
                    'target': successor,
                    'target_name': self.G.nodes[successor].get('name', successor)
                })

        # Get usage relationships (what this component uses)
        usages = []
        for successor in self.G.successors(node_id):
            edge_data = self.G.get_edge_data(node_id, successor)
            if edge_data:
                usages.append({
                    'target': successor,
                    'target_name': self.G.nodes[successor].get('name', successor),
                    'relationship': edge_data.get('link_type', 'unknown')
                })

        # Get module information
        module = node_data.get('module', 'unknown')

        return {
            'node_id': node_id,
            'name': node_data.get('name'),
            'type': node_data.get('type'),
            'path': node_data.get('path'),
            'module': module,
            'neighbors': len(neighbors),
            'inheritances': inheritances,
            'usages': usages,
            'context': f"Component {node_data.get('name')} in module {module}"
        }

    def validate_design_constraint(self, constraint: Dict) -> Dict[str, Any]:
        """Validate a design constraint against the knowledge graph."""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }

        # Validate entity name
        if 'name' not in constraint:
            validation['is_valid'] = False
            validation['errors'].append("Entity name is required")

        # Validate type
        if 'type' not in constraint:
            constraint['type'] = 'class'  # Default to class

        # Validate module
        if 'module' not in constraint:
            validation['warnings'].append("Module not specified, will use default")

        # Validate inheritance
        if 'inherits_from' in constraint:
            inherits_from = constraint['inherits_from']
            if isinstance(inherits_from, str):
                # Check if parent exists
                parent_exists = False
                for node_id, node_data in self.G.nodes(data=True):
                    if node_data.get('name') == inherits_from:
                        parent_exists = True
                        break
                if not parent_exists:
                    validation['warnings'].append(f"Parent class '{inherits_from}' not found in knowledge graph")
            elif isinstance(inherits_from, list):
                for parent in inherits_from:
                    parent_exists = False
                    for node_id, node_data in self.G.nodes(data=True):
                        if node_data.get('name') == parent:
                            parent_exists = True
                            break
                    if not parent_exists:
                        validation['warnings'].append(f"Parent class '{parent}' not found in knowledge graph")

        # Validate imports
        if 'imports' in constraint:
            for imported in constraint['imports']:
                if isinstance(imported, str):
                    # Check if imported component exists
                    imported_exists = False
                    for node_id, node_data in self.G.nodes(data=True):
                        if node_data.get('name') == imported or imported in node_data.get('path', ''):
                            imported_exists = True
                            break
                    if not imported_exists:
                        validation['warnings'].append(f"Imported component '{imported}' not found in knowledge graph")

        return validation

    def create_design_constraint(self, entity_name: str, entity_type: str = 'class',
                               inherits_from: str = None, module: str = None,
                               imports: List[str] = None, description: str = None,
                               context: str = None) -> Dict[str, Any]:
        """Create a design constraint for a new PyTorch entity."""
        constraint = {
            'name': entity_name,
            'type': entity_type,
            'module': module,
            'inherits_from': inherits_from,
            'imports': imports or [],
            'description': description,
            'context': context,
            'created_at': 'now'  # This would be timestamp in real system
        }

        # Validate the constraint
        validation = self.validate_design_constraint(constraint)
        constraint['validation'] = validation

        self.design_constraints.append(constraint)
        return constraint

    def get_relevant_neighbors(self, entity_name: str, depth: int = 2) -> Dict[str, Any]:
        """Get relevant neighbors for a new entity based on existing knowledge graph."""
        # Find existing components with similar names
        similar = self.find_similar_components(entity_name, 5)

        # Get context for each similar component
        contexts = []
        for comp in similar:
            if comp['id'] in self.G.nodes():
                context_info = self.analyze_component_context(comp['id'])
                contexts.append(context_info)

        # Get neighbors of the most similar component
        relevant_neighbors = set()
        if contexts:
            # Use the first similar component for neighbor analysis
            first_context = contexts[0]
            if 'node_id' in first_context:
                neighbors = self.get_neighbors(first_context['node_id'], depth)
                relevant_neighbors = neighbors

        return {
            'similar_components': similar,
            'contexts': contexts,
            'relevant_neighbors': list(relevant_neighbors),
            'neighbor_count': len(relevant_neighbors)
        }

    def generate_development_guidance(self, entity_name: str, constraint: Dict = None) -> Dict[str, Any]:
        """Generate development guidance based on design constraint and knowledge graph."""
        guidance = {
            'entity_name': entity_name,
            'suggested_inheritance': [],
            'suggested_imports': [],
            'suggested_module': None,
            'context_analysis': None,
            'neighbor_insights': [],
            'recommendations': []
        }

        # Get context analysis for the entity
        if constraint and 'module' in constraint and constraint['module']:
            # Find components in the same module
            module_components = []
            for node_id, node_data in self.G.nodes(data=True):
                if node_data.get('module') == constraint['module']:
                    module_components.append(node_data)

            guidance['context_analysis'] = {
                'module': constraint['module'],
                'related_components': len(module_components),
                'sample_components': [comp['name'] for comp in module_components[:5]]
            }

        # Get relevant neighbors for development
        neighbors_info = self.get_relevant_neighbors(entity_name, depth=2)
        guidance['neighbor_insights'] = neighbors_info

        # Suggest inheritance based on similar components
        similar = self.find_similar_components(entity_name, 3)
        if similar:
            guidance['suggested_inheritance'] = [comp['name'] for comp in similar[:2]]

        # Suggest imports based on module context
        if constraint and constraint.get('module'):
            # Find components that are commonly imported in the same module
            guidance['suggested_imports'] = [
                "torch.nn.Module",
                "torch.nn.functional as F",
                "torch.Tensor"
            ]

        # Generate recommendations
        guidance['recommendations'] = [
            f"Consider inheriting from {' or '.join(guidance['suggested_inheritance'])} for consistency",
            f"Import standard PyTorch components like torch.nn.Module and torch.Tensor",
            "Follow the existing naming conventions in the module",
            "Ensure proper docstring documentation following PyTorch conventions",
            "Test compatibility with existing PyTorch ecosystem components"
        ]

        return guidance

    def export_constraints(self, filepath: str = 'design_constraints.json'):
        """Export design constraints to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.design_constraints, f, indent=2)
        print(f"Design constraints exported to {filepath}")

    def load_constraints(self, filepath: str = 'design_constraints.json'):
        """Load design constraints from a JSON file."""
        try:
            with open(filepath, 'r') as f:
                self.design_constraints = json.load(f)
            print(f"Design constraints loaded from {filepath}")
        except FileNotFoundError:
            print(f"No constraints file found at {filepath}")

def main():
    """Main function to demonstrate the design constraint system."""
    print("PyTorch Design Constraint System")
    print("=" * 50)

    # Initialize the system
    system = DesignConstraintSystem()

    print("System initialized with knowledge graph")
    print(f"Knowledge graph has {system.G.number_of_nodes()} nodes and {system.G.number_of_edges()} edges")

    # Example 1: Create a design constraint for a new Linear variant
    print("\n1. Creating design constraint for new Linear variant:")
    constraint1 = system.create_design_constraint(
        entity_name="QuantizedLinear",
        entity_type="class",
        inherits_from="Linear",
        module="torch.nn.quantized.modules.linear",
        imports=["torch.nn.Module", "torch.nn.functional as F"],
        description="Quantized version of Linear module for efficient inference"
    )

    print(f"Created constraint for {constraint1['name']}")
    print(f"Validation: {'Valid' if constraint1['validation']['is_valid'] else 'Invalid'}")
    if constraint1['validation']['warnings']:
        print(f"Warnings: {constraint1['validation']['warnings']}")

    # Example 2: Generate development guidance
    print("\n2. Generating development guidance:")
    guidance = system.generate_development_guidance("QuantizedLinear", constraint1)

    print(f"Entity: {guidance['entity_name']}")
    print(f"Suggested inheritance: {guidance['suggested_inheritance']}")
    print(f"Suggested imports: {guidance['suggested_imports']}")
    print(f"Neighbor insights: {guidance['neighbor_insights']['neighbor_count']} neighbors found")
    print("\nRecommendations:")
    for rec in guidance['recommendations']:
        print(f"  • {rec}")

    # Example 3: Find similar components
    print("\n3. Finding similar components:")
    similar = system.find_similar_components("Linear", 5)
    for comp in similar:
        print(f"  {comp['name']} ({comp['type']}) in {comp['path']}")

    # Example 4: Get relevant neighbors
    print("\n4. Getting relevant neighbors:")
    neighbors = system.get_relevant_neighbors("Linear", depth=1)
    print(f"Found {neighbors['neighbor_count']} relevant neighbors")

    # Export constraints
    system.export_constraints('my_design_constraints.json')

    print("\n" + "=" * 50)
    print("Design constraint system demonstration complete!")

if __name__ == "__main__":
    main()