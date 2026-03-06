# PyTorch Knowledge Graph Explorer

Interactive visualization tool for exploring PyTorch codebase knowledge graphs.

## Overview

This project provides a web-based visualization tool for exploring PyTorch codebase knowledge graphs. It allows developers to understand the relationships between different components in the PyTorch codebase through an interactive graph interface.

## Features

- Interactive graph visualization using D3.js
- Load and visualize knowledge graph JSON files
- Filter by node type
- Adjust maximum nodes to display
- Zoom and pan functionality
- Node highlighting and tooltips
- Hop-based navigation
- Responsive design
- Performance optimization for large graphs

## Project Structure

```
frontend-visualization-tool/
├── src/
│   ├── index.html          # Main HTML file with UI
│   ├── app.js              # Main JavaScript logic
│   ├── sample-knowledge-graph.json  # Sample knowledge graph for testing
│   └── README.md           # This file
├── test-visualizer.html    # Test page with simple visualization
├── USAGE.md                # Usage instructions
└── package.json            # Project dependencies
```

## Getting Started

1. **Prerequisites**:
   - Modern web browser (Chrome, Firefox, Safari, Edge)
   - No server required (runs entirely in browser)

2. **Usage**:
   - Open `src/index.html` in a web browser
   - Select a knowledge graph JSON file using the file input
   - Adjust settings in the control panel
   - Interact with the graph using mouse controls

## Technical Details

### Data Format
The tool expects JSON files with nodes and edges:
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

### Visualization Features
- **Node Types**: Color-coded by type (class, function, method, etc.)
- **Edge Types**: Color-coded by relationship type (inheritance, imports, calls, etc.)
- **Interactive Controls**: Click, drag, zoom, and pan
- **Tooltips**: Show node information on hover
- **Filtering**: By node type or max node count
- **Performance**: Automatically limits nodes to prevent overload (default 200)

## Dependencies

- [D3.js v7](https://d3js.org/) - For graph visualization
- Vanilla JavaScript - No additional frameworks required

## Browser Compatibility

- Chrome 80+
- Firefox 70+
- Safari 13+
- Edge 80+

## License

MIT License

## Contributing

This is a tool for visualizing PyTorch knowledge graphs. Contributions to improve visualization quality, performance, or add new features are welcome.

## Contact

For questions or issues, please open an issue in the repository.