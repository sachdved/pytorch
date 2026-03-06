# PyTorch Knowledge Graph Explorer

An interactive visualization tool for exploring PyTorch codebase knowledge graphs.

## Features

- Interactive graph visualization using D3.js
- Load knowledge graph JSON files
- Filter by node type
- Adjust maximum nodes to display
- Zoom and pan functionality
- Node highlighting and tooltips
- Hop-based navigation
- Responsive design

## Usage

1. Open `index.html` in a web browser
2. Select a knowledge graph JSON file using the file input
3. Adjust settings in the control panel:
   - Max Nodes to Display: Limit the number of nodes shown
   - Hop Distance: Control the distance for related nodes
   - Node Type Filter: Show only nodes of a specific type
4. Interact with the graph:
   - Click on nodes to highlight them
   - Hover over nodes to see tooltips
   - Zoom in/out using buttons or mouse wheel
   - Drag nodes to reposition them

## Data Format

The tool expects knowledge graph JSON files with the following structure:

```json
{
  "nodes": [
    {
      "id": "node-id",
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

## Technical Details

- Built with vanilla JavaScript and D3.js
- Responsive design using CSS
- Drag-and-drop node interaction
- Zoom and pan functionality
- Node filtering and highlighting
- Real-time statistics display

## Requirements

- Modern web browser with JavaScript enabled
- No external dependencies beyond D3.js (included via CDN)

## License

MIT License