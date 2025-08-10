#!/bin/bash

# Bash script to set up DVC remote with HTTPS
# This script helps configure DVC to use HTTPS instead of SSH for cross-platform compatibility

echo "🔧 Setting up DVC remote with HTTPS for cross-platform compatibility..."

# Check if DVC is installed
if ! command -v dvc &> /dev/null; then
    echo "❌ DVC is not installed. Please install DVC first."
    echo "   pip install dvc"
    exit 1
fi

echo "✅ DVC is installed"

# Remove existing remote if it exists
echo "🔄 Removing existing DVC remote..."
dvc remote remove origin 2>/dev/null || true

# Add HTTPS remote
echo "🔗 Adding HTTPS remote..."
dvc remote add origin https://github.com/vignesh-bits-wilp/mlops-assignment-data.git

# Set as default
dvc remote default origin

# Verify configuration
echo "📋 Current DVC configuration:"
dvc remote list

echo ""
echo "✅ DVC remote configured with HTTPS!"
echo ""
echo "📝 Next steps:"
echo "1. Create the data repository: https://github.com/vignesh-bits-wilp/mlops-assignment-data"
echo "2. Generate data files: python scripts/download_data.py"
echo "3. Process data: python src/data/data_ingestion.py"
echo "4. Add to DVC: dvc add data/raw/california_housing.csv data/processed/cleaned.csv"
echo "5. Commit DVC files: git add data/*.dvc && git commit -m 'Add DVC tracking'"
echo "6. Push to remote: dvc push"
echo ""
echo "🔐 For CI/CD, make sure the data repository allows GitHub Actions access"
