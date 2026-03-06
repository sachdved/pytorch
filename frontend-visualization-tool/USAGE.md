# PyTorch Knowledge Graph Explorer - Usage Guide

This tool provides an interactive visualization of PyTorch codebase knowledge graphs. It allows developers to explore the relationships between different components in the PyTorch codebase.

## Getting Started

1. **Open the tool**:
   - Open `index.html` in a modern web browser
   - Or run `npm start` from the project directory to start a local server

2. **Load a knowledge graph**:
   - Click "Load Knowledge Graph JSON" and select a JSON file from your system
   - Sample files are available in the project directory

## Control Panel

The left panel contains controls for customizing the visualization:

- **Load Knowledge Graph JSON**: Upload a knowledge graph file in JSON format
- **Max Nodes to Display**: Set the maximum number of nodes to show (default: 200)
- **Hop Distance**: Control how many hops away from a selected node to show (1-5)
- **Filter by Node Type**: Show only nodes of a specific type (class, function, method, etc.)
- **Reset View**: Reset the zoom and pan to the default view
- **Zoom In/Zoom Out**: Adjust the zoom level manually

## Interacting with the Graph

- **Click on nodes**: Highlights the selected node and shows information
- **Hover over nodes**: Shows a tooltip with node details
- **Drag nodes**: Reposition nodes manually
- **Zoom**: Use mouse wheel or zoom buttons to zoom in/out
- **Pan**: Click and drag the background to move around the graph

## Data Format

The tool expects JSON files with the following structure:

```json
{
  "nodes": [
    {
      "id": "unique-id",
      "name": "Node Name",
      "type": "node-type",
      "path": "path/to/file",
      "description": "Node description"
    }
  ],
  "edges": [
    {
      "source": "source-node-id",
      "target": "target-node-id",
      "type": "edge-type"
    }
  ]
}
```

## Node Types and Colors

- **Root Module**: Red
- **Submodule**: Blue
- **Class**: Purple
- **Function**: Teal
- **Method**: Orange
- **Config**: Gray
- **File**: Dark Blue
- **Directory**: Brown
- **Other**: Light Gray

## Edge Types and Colors

- **Inheritance**: Purple
- **Imports**: Blue
- **Calls**: Red
- **Test Of**: Orange
- **Belongs To**: Teal
- **Uses**: Gray
- **Other**: Light Gray

## Performance Considerations

- For large graphs, use the "Max Nodes to Display" setting to limit the visualization
- The tool is optimized to handle up to 200 nodes by default
- Very large graphs may be automatically reduced to maintain performance

## Troubleshooting

If you encounter issues:

1. Ensure your JSON file is valid
2. Check that the file has the correct structure
3. Try reducing the "Max Nodes to Display" setting
4. Clear browser cache if visualization appears corrupted

## Customization

The visualization can be extended by:

1. Adding new node types to `NODE_TYPE_COLORS`
2. Adding new edge types to `EDGE_COLOR_MAP`
3. Modifying the filtering and display logic
4. Adding more interactive features