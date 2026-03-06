# Running the Knowledge Graph Notebook

## Quick Start

### Activate Environment
```bash
conda activate torch_kg
```

### Run Tests First
```bash
python test_notebook.py
```
This verifies all components are working correctly.

### Run the Notebook
```bash
jupyter notebook knowledge_graph_demo.ipynb
```

### Or Run the Script
```bash
python visualize_knowledge_graph.py
```

## What the Notebook Shows

1. **Graph Visualization** - Shows the PyTorch codebase structure as a network graph
2. **Graph Statistics** - Displays node and edge counts by type
3. **Interactive Analysis** - Shows:
   - Most connected nodes (key components)
   - Nodes connected to Module
   - Subsystem breakdown (Inductor, Dynamo, FX)

## Expected Output

The notebook should show:
- **206 nodes** (modules, classes, functions, files)
- **115 edges** (imports, calls, inheritance)
- **4 node types** (module, other, class, function)
- **3 edge types** (imports, calls, inherits)

Key components to look for:
- `torch.nn.modules.module.Module` - Most connected (23 connections)
- `torch._inductor` - Inductor system
- `torch._dynamo` - Dynamo compilation
- `torch.fx` - FX graph system

## Troubleshooting

If you get errors:
1. Make sure you're in the `torch_kg` conda environment
2. Run `python test_notebook.py` to check the setup
3. Ensure `codebase_knowledge_graph.json` exists in the current directory

## Notebook Cells

- **Cell 1**: Runs the visualization script
- **Cell 2**: Creates the visualization graph
- **Cell 3**: Shows graph statistics
- **Cell 4**: Shows top connected nodes
- **Cell 5**: Shows nodes connected to Module
- **Cell 6**: Shows subsystem breakdown