# PyTorch Knowledge Graph Visualization Setup

## Setup Instructions

### Step 1: Activate the Environment
```bash
conda activate torch_kg
```

### Step 2: Run in Jupyter Notebook
```bash
jupyter notebook
```

### Step 3: In Your Notebook
```python
%run visualize_knowledge_graph.py
G, pos = visualize_pytorch_knowledge_graph()
```

## Alternative: Use Python Script
```bash
conda activate torch_kg
python visualize_knowledge_graph.py
```

## Usage Examples

### Basic Visualization
```python
from visualize_knowledge_graph import visualize_pytorch_knowledge_graph

# Default visualization
G, pos = visualize_pytorch_knowledge_graph()

# Custom max nodes
G, pos = visualize_pytorch_knowledge_graph(max_nodes=30)
```

### Access Graph Data
```python
# Get node names
node_names = [data['name'] for _, data in G.nodes(data=True)]

# Get connections
connections = list(G.edges())

# Get specific node info
tensor_node = 'torch_tensor'
tensor_info = G.nodes[tensor_node]
print(f"Tensor class path: {tensor_info['path']}")
```

### Interactive Analysis
```python
# Degree of each node
degrees = dict(G.degree())
sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
print("Most connected nodes:", sorted_nodes)

# Find modules that use Tensor
tensor_importers = list(G.predecessors('torch_tensor'))
print("Modules importing Tensor:", tensor_importers)
```

## Graph Components

### Node Types
- **root_module**: Root containers like `torch`, `c10`
- **submodule**: Subpackages like `torch.nn`, `torch.cuda`
- **class**: Python classes like `Tensor`, `nn.Module`
- **library**: C++ libraries like `ATen::native`
- **config**: Configuration files like `native_functions.yaml`
- **root_directory**: Top-level directories like `test`, `tools`

### Edge Types
- **imports**: Python import statements
- **inherits**: Class inheritance relationships
- **depends**: Low-level dependencies
- **uses**: Usage relationships
- **configures**: Configuration file relationships
- **other**: Miscellaneous relationships

## Notes
- The visualization automatically focuses on the largest connected component
- Node colors indicate the node type
- Edge thickness varies by type
- The graph uses spring layout for natural clustering