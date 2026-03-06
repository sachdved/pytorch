// Main JavaScript for PyTorch Knowledge Graph Visualization
// This file contains all the logic for loading, visualizing, and interacting with knowledge graphs

// Global variables
let graphData = null;
let svg = null;
let g = null;
let simulation = null;
let zoom = null;
let currentZoom = 1;
let selectedNode = null;
let nodeTypes = new Set();
let nodeTypeColors = {};

// Node type colors mapping
const NODE_TYPE_COLORS = {
    'root_module': '#E74C3C',      // Red
    'submodule': '#3498DB',        // Blue
    'class': '#9B59B6',            // Purple
    'function': '#1ABC9C',         // Teal
    'method': '#F39C12',           // Orange
    'config': '#95A5A6',           // Gray
    'file': '#34495E',             // Dark Blue
    'directory': '#E67E22',        // Brown
    'other': '#7F8C8D'             // Light Gray
};

// Edge color mapping
const EDGE_COLOR_MAP = {
    'inheritance': '#9B59B6',      // Purple
    'imports': '#3498DB',          // Blue
    'calls': '#E74C3C',            // Red
    'test_of': '#F39C12',          // Orange
    'belongs_to': '#1ABC9C',       // Teal
    'uses': '#95A5A6',             // Gray
    'other': '#BDC3C7'             // Light gray
};

// Initialize the application
function init() {
    // Set up event listeners
    document.getElementById('file-input').addEventListener('change', handleFileSelect);
    document.getElementById('max-nodes').addEventListener('change', updateGraph);
    document.getElementById('hop-distance').addEventListener('change', updateGraph);
    document.getElementById('node-type-filter').addEventListener('change', updateGraph);
    document.getElementById('reset-view').addEventListener('click', resetView);
    document.getElementById('zoom-in').addEventListener('click', () => zoomBy(0.2));
    document.getElementById('zoom-out').addEventListener('click', () => zoomBy(-0.2));

    // Create SVG container
    createVisualization();

    // Initialize legend
    createLegend();
}

// Create the visualization area
function createVisualization() {
    const container = document.getElementById('graph-container');

    // Clear previous content
    container.innerHTML = '';

    // Create SVG
    svg = d3.select("#graph-container")
        .append("svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("id", "graph-svg");

    // Create zoom behavior
    zoom = d3.zoom()
        .scaleExtent([0.1, 10])
        .on("zoom", (event) => {
            g.attr("transform", event.transform);
            currentZoom = event.transform.k;
            document.getElementById('zoom-level').textContent = currentZoom.toFixed(2);
        });

    // Apply zoom to SVG
    svg.call(zoom);

    // Create group for all graph elements
    g = svg.append("g");

    // Add tooltip
    tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);
}

// Create legend for node types
function createLegend() {
    const legendContainer = document.getElementById('legend-container');
    legendContainer.innerHTML = '';

    Object.entries(NODE_TYPE_COLORS).forEach(([type, color]) => {
        const legendItem = document.createElement('div');
        legendItem.className = 'legend-item';

        const colorBox = document.createElement('div');
        colorBox.className = 'legend-color';
        colorBox.style.backgroundColor = color;

        const label = document.createElement('span');
        label.textContent = type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());

        legendItem.appendChild(colorBox);
        legendItem.appendChild(label);
        legendContainer.appendChild(legendItem);
    });
}

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            graphData = JSON.parse(e.target.result);
            updateGraph();
        } catch (error) {
            console.error('Error parsing JSON:', error);
            alert('Error parsing JSON file. Please ensure it is a valid knowledge graph JSON.');
        }
    };
    reader.readAsText(file);
}

// Update the graph visualization
function updateGraph() {
    if (!graphData) return;

    // Get current settings
    const maxNodes = parseInt(document.getElementById('max-nodes').value) || 200;
    const hopDistance = parseInt(document.getElementById('hop-distance').value) || 1;
    const nodeTypeFilter = document.getElementById('node-type-filter').value;

    // Clear existing visualization
    g.selectAll("*").remove();

    // Process data and create filtered graph
    const filteredData = filterGraphData(graphData, maxNodes, hopDistance, nodeTypeFilter);

    // Update statistics
    document.getElementById('node-count').textContent = filteredData.nodes.length;
    document.getElementById('edge-count').textContent = filteredData.edges.length;

    // Create simulation
    simulation = d3.forceSimulation(filteredData.nodes)
        .force("link", d3.forceLink(filteredData.edges).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(svg.attr("width") / 2, svg.attr("height") / 2))
        .force("collision", d3.forceCollide().radius(20));

    // Create edges
    const link = g.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(filteredData.edges)
        .enter()
        .append("line")
        .attr("class", "edge")
        .attr("stroke", d => EDGE_COLOR_MAP[d.type] || EDGE_COLOR_MAP['other'])
        .attr("stroke-width", 1);

    // Create nodes
    const node = g.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(filteredData.nodes)
        .enter()
        .append("circle")
        .attr("class", "node")
        .attr("r", 8)
        .attr("fill", d => NODE_TYPE_COLORS[d.type] || NODE_TYPE_COLORS['other'])
        .call(d3.drag()
            .on("start", dragStarted)
            .on("drag", dragged)
            .on("end", dragEnded))
        .on("click", nodeClicked)
        .on("mouseover", nodeMouseOver)
        .on("mouseout", nodeMouseOut);

    // Create labels
    const text = g.append("g")
        .attr("class", "labels")
        .selectAll("text")
        .data(filteredData.nodes)
        .enter()
        .append("text")
        .attr("class", "node-label")
        .text(d => d.name)
        .attr("font-size", "10px")
        .attr("dx", 10)
        .attr("dy", 4);

    // Update simulation
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);

        text
            .attr("x", d => d.x)
            .attr("y", d => d.y);
    });
}

// Filter graph data based on parameters
function filterGraphData(data, maxNodes, hopDistance, nodeTypeFilter) {
    // Create a copy of nodes and edges to avoid modifying original data
    let nodes = [...data.nodes];
    let edges = [...data.edges];

    // Filter by node type if specified
    if (nodeTypeFilter !== 'all') {
        nodes = nodes.filter(node => node.type === nodeTypeFilter);
    }

    // If we have more nodes than maxNodes, reduce the graph
    if (nodes.length > maxNodes) {
        // For simplicity, we'll just take the first N nodes
        // In a real implementation, this would be more sophisticated
        nodes = nodes.slice(0, maxNodes);

        // Filter edges to only include those between the selected nodes
        const nodeIds = new Set(nodes.map(n => n.id));
        edges = edges.filter(edge =>
            nodeIds.has(edge.source) && nodeIds.has(edge.target)
        );
    }

    // For hop distance, we'll simplify by just returning the filtered data
    // In a full implementation, this would compute the connected component

    return { nodes, edges };
}

// Drag functions
function dragStarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragEnded(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

// Node click handler
function nodeClicked(event, d) {
    // Clear previous selection
    g.selectAll(".node")
        .classed("highlighted", false);

    // Highlight clicked node
    d3.select(this).classed("highlighted", true);

    // Update selected node info
    selectedNode = d;
    document.getElementById('selected-node').textContent = d.name;

    // Show tooltip with node information
    tooltip.transition()
        .duration(200)
        .style("opacity", 0.9);

    tooltip.html(`<strong>${d.name}</strong><br/>
        Type: ${d.type}<br/>
        Path: ${d.path || 'N/A'}<br/>
        Description: ${d.description || 'N/A'}`)
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 28) + "px");
}

// Node mouse over handler
function nodeMouseOver(event, d) {
    tooltip.transition()
        .duration(200)
        .style("opacity", 0.9);

    tooltip.html(`<strong>${d.name}</strong><br/>
        Type: ${d.type}<br/>
        Path: ${d.path || 'N/A'}`)
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 28) + "px");
}

// Node mouse out handler
function nodeMouseOut() {
    tooltip.transition()
        .duration(500)
        .style("opacity", 0);
}

// Reset view
function resetView() {
    svg.transition()
        .duration(750)
        .call(zoom.transform, d3.zoomIdentity);
    currentZoom = 1;
    document.getElementById('zoom-level').textContent = '1.0';
}

// Zoom in/out
function zoomBy(amount) {
    const newZoom = Math.min(Math.max(currentZoom + amount, 0.1), 10);
    svg.transition()
        .duration(750)
        .call(zoom.scaleTo, newZoom);
    currentZoom = newZoom;
    document.getElementById('zoom-level').textContent = newZoom.toFixed(2);
}

// Initialize the application when the page loads
window.addEventListener('load', init);