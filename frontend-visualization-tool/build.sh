#!/bin/bash

# Build script for PyTorch Knowledge Graph Explorer

echo "Building PyTorch Knowledge Graph Explorer..."

# Create distribution directory
mkdir -p dist

# Copy all necessary files
cp -r src/* dist/

# Remove the sample file for distribution
rm dist/sample-knowledge-graph.json

# Create a zip file for easy distribution
cd dist
zip -r pytorch-knowledge-graph-explorer.zip *

echo "Build complete! Distribution files created in dist/ directory"
echo "Files created:"
ls -la