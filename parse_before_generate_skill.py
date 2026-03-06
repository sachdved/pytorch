#!/usr/bin/env python3
"""
Parse Before Generate Skill for Claude Code
This skill enables Claude Code to analyze the codebase structure before generating code,
ensuring better context awareness and code quality.
"""

import os
import json
import ast
import re
from typing import Dict, List, Set, Optional
from pathlib import Path

class ParseBeforeGenerateSkill:
    """
    A skill that teaches Claude Code to parse code trees and determine what to look at
    before generating code.
    """

    def __init__(self, knowledge_graph_path: str = 'comprehensive_knowledge_graph.json'):
        self.knowledge_graph_path = knowledge_graph_path
        self.knowledge_graph = None
        self.load_knowledge_graph()

    def load_knowledge_graph(self):
        """Load the knowledge graph if available."""
        try:
            with open(self.knowledge_graph_path, 'r') as f:
                self.knowledge_graph = json.load(f)
            print(f"Knowledge graph loaded with {len(self.knowledge_graph['nodes'])} nodes")
        except Exception as e:
            print(f"Warning: Could not load knowledge graph: {e}")
            self.knowledge_graph = None

    def analyze_file_structure(self, file_path: str) -> Dict:
        """Analyze the structure of a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            analysis = {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'line_count': len(content.split('\n')),
                'components': {
                    'classes': [],
                    'functions': [],
                    'imports': [],
                    'variables': []
                },
                'structure': {
                    'has_main': False,
                    'has_docstring': False,
                    'has_test': False
                }
            }

            # Analyze AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    analysis['components']['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'docstring': ast.get_docstring(node) or '',
                        'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                    })
                elif isinstance(node, ast.FunctionDef):
                    analysis['components']['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'docstring': ast.get_docstring(node) or '',
                        'args': [arg.arg for arg in node.args.args if hasattr(arg, 'arg')]
                    })
                elif isinstance(node, ast.Import):
                    analysis['components']['imports'].extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    analysis['components']['imports'].append(f"{node.module or ''}")
                elif isinstance(node, ast.Assign):
                    analysis['components']['variables'].append({
                        'name': node.targets[0].id if isinstance(node.targets[0], ast.Name) else str(node.targets[0]),
                        'line': node.lineno
                    })

            # Check for special markers
            analysis['structure']['has_main'] = '__main__' in content or 'if __name__' in content
            analysis['structure']['has_docstring'] = '"""' in content or "'''" in content
            analysis['structure']['has_test'] = 'test_' in content or 'unittest' in content or 'pytest' in content

            return analysis

        except Exception as e:
            return {
                'file_path': file_path,
                'error': str(e),
                'components': {'classes': [], 'functions': [], 'imports': [], 'variables': []}
            }

    def get_module_context(self, file_path: str) -> str:
        """Get the module context for a file."""
        # Extract module path from file path
        if file_path.startswith('torch/'):
            module_path = file_path.replace('torch/', '', 1)
            module_path = module_path.replace('.py', '')
            return module_path.replace('/', '.')
        return file_path

    def analyze_codebase_context(self, target_path: str = 'torch') -> Dict:
        """Analyze the broader codebase context."""
        context = {
            'target_path': target_path,
            'module': self.get_module_context(target_path),
            'file_count': 0,
            'component_stats': {
                'classes': 0,
                'functions': 0,
                'imports': 0,
                'variables': 0
            },
            'structure_analysis': []
        }

        if os.path.isfile(target_path):
            # Single file analysis
            analysis = self.analyze_file_structure(target_path)
            context['file_count'] = 1
            for comp_type, components in analysis['components'].items():
                context['component_stats'][comp_type] = len(components)
        elif os.path.isdir(target_path):
            # Directory analysis
            for root, dirs, files in os.walk(target_path):
                for file in files:
                    if file.endswith('.py'):
                        context['file_count'] += 1
                        file_path = os.path.join(root, file)
                        analysis = self.analyze_file_structure(file_path)
                        for comp_type, components in analysis['components'].items():
                            context['component_stats'][comp_type] += len(components)

        return context

    def generate_analysis_report(self, context: Dict) -> str:
        """Generate a human-readable analysis report."""
        report = f"""
Codebase Analysis Report
========================

Target: {context['target_path']}
Module: {context['module']}
Files Analyzed: {context['file_count']}

Component Statistics:
- Classes: {context['component_stats']['classes']}
- Functions: {context['component_stats']['functions']}
- Imports: {context['component_stats']['imports']}
- Variables: {context['component_stats']['variables']}

Structure Analysis:
"""

        # Add more detailed analysis
        if context['file_count'] == 1:
            # Single file analysis
            report += "  Single file analysis completed\n"
        else:
            # Directory analysis
            report += f"  Directory analysis of {context['file_count']} files\n"

        return report

    def get_relevant_context(self, entity_name: str, depth: int = 2) -> Dict:
        """Get relevant context for an entity from the knowledge graph."""
        if not self.knowledge_graph:
            return {"error": "Knowledge graph not available"}

        # Find entities matching the name
        matching_entities = []
        for node in self.knowledge_graph['nodes']:
            if entity_name.lower() in node.get('name', '').lower():
                matching_entities.append(node)

        return {
            "entity_name": entity_name,
            "matching_entities": matching_entities[:10],  # Top 10 matches
            "total_matches": len(matching_entities),
            "knowledge_graph_available": True
        }

    def parse_and_analyze(self, target_path: str, entity_name: str = None) -> str:
        """Parse and analyze the codebase structure."""
        print(f"Parsing codebase at: {target_path}")

        # Analyze the target
        context = self.analyze_codebase_context(target_path)

        # Generate report
        report = self.generate_analysis_report(context)

        # Get relevant context from knowledge graph if available
        if entity_name:
            kg_context = self.get_relevant_context(entity_name)
            report += f"\nKnowledge Graph Context for '{entity_name}':\n"
            if 'error' not in kg_context:
                report += f"  Found {kg_context['total_matches']} matching entities\n"
                if kg_context['matching_entities']:
                    report += "  First few matches:\n"
                    for i, entity in enumerate(kg_context['matching_entities'][:3]):
                        report += f"    {i+1}. {entity.get('name', 'unknown')} ({entity.get('type', 'unknown')})\n"
            else:
                report += f"  {kg_context['error']}\n"

        return report

def main():
    """Demonstrate the parse before generate skill."""
    print("Parse Before Generate Skill")
    print("=" * 40)

    # Initialize skill
    skill = ParseBeforeGenerateSkill()

    # Example usage
    print("1. Analyzing a single file:")
    report1 = skill.parse_and_analyze('torch/nn/modules/linear.py', 'Linear')
    print(report1)

    print("\n2. Analyzing a directory:")
    report2 = skill.parse_and_analyze('torch/nn/modules', 'Linear')
    print(report2)

    print("\n3. Analyzing a specific function:")
    report3 = skill.parse_and_analyze('torch/nn/modules/linear.py')
    print(report3)

    print("\nSkill demonstration complete!")

if __name__ == "__main__":
    main()