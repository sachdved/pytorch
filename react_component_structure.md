# React Component Structure for Knowledge Graph Visualization

## Main Components

### 1. App Component
- Main application container
- File upload handler for JSON knowledge graph files
- State management for graph data and visualization settings

### 2. GraphVisualization Component
- Core graph rendering using D3.js or similar library
- Node and edge rendering with appropriate styling
- Zoom and pan functionality
- Node selection and highlighting

### 3. ControlsPanel Component
- Hop distance controls (0-5 hops)
- Node type filtering
- Search functionality
- Node expansion/collapse controls
- Performance settings (max nodes limit)

### 4. NodeDetailsPanel Component
- Detailed information display for selected nodes
- Node properties and relationships
- Path and description information

### 5. StatisticsPanel Component
- Graph statistics display
- Node type distribution
- Edge type distribution
- Connection metrics

## Data Flow

### State Management
- `graphData`: The loaded knowledge graph JSON data
- `selectedNode`: Currently selected node ID
- `hopDistance`: Current hop distance for neighbor visualization
- `nodeFilters`: Applied filters for node types
- `maxNodes`: Maximum nodes to display
- `isLoading`: Loading state indicator

### Props
- `graphData`: Passed down to visualization component
- `selectedNode`: Passed to details panel
- `onNodeSelect`: Callback for node selection
- `onHopChange`: Callback for hop distance changes
- `onFilterChange`: Callback for filter changes

## File Structure
```
/src
  /components
    App.js
    GraphVisualization.js
    ControlsPanel.js
    NodeDetailsPanel.js
    StatisticsPanel.js
  /utils
    graphUtils.js
    dataParser.js
  /styles
    app.css
    visualization.css
  /data
    sample-graph.json (example data file)
```

## API Endpoints
- `/api/load-graph` - Load and parse knowledge graph JSON file
- `/api/get-neighbors` - Get neighbors of a selected node up to specified hops
- `/api/search-nodes` - Search for nodes by name or properties