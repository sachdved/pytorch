# PyTorch Codebase Knowledge Graph - Detailed Version

## Overview

A comprehensive, fine-grained knowledge graph representation of the PyTorch codebase containing **206 nodes** and **115 edges** capturing classes, functions, methods, and their relationships.

## Graph Structure

### Node Types (4 categories)
1. **Module (90 nodes)** - Python modules and packages
2. **Other (78 nodes)** - Files, directories, and other entities
3. **Class (25 nodes)** - Python classes including:
   - `torch.nn.Module` - Base class
   - `torch.autograd.Function` - Custom functions
   - `torch.fx.Graph` - Graph representation
   - `torch._dynamo.OptimizedModule` - Compiled module
   - `torch._inductor.*` - Inductor components
4. **Function (13 nodes)** - Module-level and utility functions

### Edge Types (3 categories)
1. **Imports (57 edges)** - Module and file import relationships
2. **Calls (35 edges)** - Method and function call relationships
3. **Inherits (23 edges)** - Class inheritance hierarchies

## Key Components Identified

### Neural Network Layer (30+ nodes)
- **Container modules**: Sequential, ModuleList, ModuleDict
- **Convolutional layers**: Conv1d/2d/3d, ConvTranspose1d/2d/3d
- **Normalization**: LayerNorm, GroupNorm, RMSNorm
- **Activations**: ReLU, GELU, etc.
- **Pooling**: MaxPool, AvgPool, etc.
- **RNN**: RNN, LSTM, GRU and cells
- **Transformer**: Transformer, Encoder, Decoder
- **Embedding**: Embedding, EmbeddingBag
- **Loss functions**: MSELoss, CrossEntropyLoss, etc.

### TorchInductor (15+ nodes)
- `torch._inductor.compile_fx` - Main compilation function
- `torch._inductor.graph` - Graph representation
- `torch._inductor.ir` - Intermediate representation (TensorBox, StorageBox)
- `torch._inductor.lowering` - Operator lowering
- `torch._inductor.codecache` - Code generation
- Scheduler, memory, comm_analysis, cudagraph_trees modules

### TorchDynamo (10+ nodes)
- `torch._dynamo.OptimizedModule` - Compiled module wrapper
- `torch._dynamo.eval_frame` - Frame evaluation
- `torch._dynamo.convert_frame` - Graph conversion
- `torch._dynamo.config` - Configuration
- `torch._dynamo.decorators` - @compile, @no_grad

### TorchFX (8+ nodes)
- `torch.fx.Graph` - Graph representation
- `torch.fx.GraphModule` - GraphModule extending Module
- `torch.fx.Node` - Node types (placeholder, call_method, etc.)
- `torch.fx.Tracer` - Symbolic tracer
- `torch.fx.Proxy` - Proxy class

### Autograd System (7+ nodes)
- `torch.autograd.Function` - Custom function base
- `torch.autograd.backward` - Gradient computation
- `torch.autograd.grad` - Gradient retrieval

### Optimizer (15+ nodes)
- SGD, Adam, AdamW, RMSprop, etc.
- Base optimizer and scheduler classes
- LR schedulers and SWA utilities

## Visualization Usage

### In Jupyter Notebook
```python
%run visualize_knowledge_graph.py
G, pos = visualize_pytorch_knowledge_graph(max_nodes=60)
```

### Python Script
```bash
conda activate torch_kg
python visualize_knowledge_graph.py
```

### Interactive Exploration
```python
from visualize_knowledge_graph import load_knowledge_graph, build_nx_graph, explore_graph

kg = load_knowledge_graph('codebase_knowledge_graph.json')
G = build_nx_graph(kg)
explore_graph(G)
```

## Graph Statistics

```
Nodes: 206
Edges: 115
Node Types:
  module: 90
  other: 78
  class: 25
  function: 13
Edge Types:
  imports: 57
  calls: 35
  inherits: 23
Largest Connected Component: 40 nodes
```

## Key Insights

### Most Connected Nodes
1. `torch.nn.modules.module.Module` - 23 connections (base class)
2. `torch._inductor` - 15 connections (inductor system)
3. `eval_frame` - 13 connections (dynamo evaluation)
4. `compile_fx` - 13 connections (inductor compilation)
5. `torch._dynamo` - 13 connections (dynamo system)

### Module Import Dependencies
- Shows cross-module dependencies
- Critical for understanding compilation pipeline
- Reveals core components used by subsystems

### Inheritance Chains
- `torch.nn.Module` is the base for most nn layers
- Shows architectural patterns
- Identifies inheritance relationships between classes

## Visual Features

### Node Coloring
- **Module**: Blue
- **Class**: Purple
- **Function**: Teal
- **File**: Dark Blue
- **Directory**: Brown
- **Other**: Light Gray

### Edge Coloring
- **Inheritance**: Purple
- **Imports**: Blue
- **Calls**: Red
- **Other**: Gray

### Node Sizing
- Size represents node degree (number of connections)
- Important nodes are labeled
- High-degree nodes are emphasized

## Files

1. **`codebase_knowledge_graph.json`** - Knowledge graph data (206 nodes, 115 edges)
2. **`visualize_knowledge_graph.py`** - Main visualization script
3. **`knowledge_graph_demo.ipynb`** - Jupyter notebook template
4. **`knowledge_graph_setup.md`** - Setup instructions
5. **`DETAILED_KNOWLEDGE_GRAPH.md`** - This document

## Next Steps

You can expand the knowledge graph further by:
1. Adding more method-level details
2. Capturing test coverage relationships
3. Adding parameter and return type information
4. Including documentation strings
5. Tracking usage patterns and hotspots

The current graph provides a solid foundation for understanding PyTorch's architecture at the class and function level.