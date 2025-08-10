# PowerShell script to set up DVC remote with HTTPS
# This script helps configure DVC to use HTTPS instead of SSH for Windows compatibility

Write-Host "🔧 Setting up DVC remote with HTTPS for Windows compatibility..." -ForegroundColor Green

# Check if DVC is installed
try {
    dvc --version | Out-Null
    Write-Host "✅ DVC is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ DVC is not installed. Please install DVC first." -ForegroundColor Red
    Write-Host "   pip install dvc" -ForegroundColor Yellow
    exit 1
}

# Remove existing remote if it exists
Write-Host "🔄 Removing existing DVC remote..." -ForegroundColor Yellow
dvc remote remove origin 2>$null

# Add HTTPS remote
Write-Host "🔗 Adding HTTPS remote..." -ForegroundColor Yellow
dvc remote add origin https://github.com/vignesh-bits-wilp/mlops-assignment-data.git

# Set as default
dvc remote default origin

# Verify configuration
Write-Host "📋 Current DVC configuration:" -ForegroundColor Cyan
dvc remote list

Write-Host ""
Write-Host "✅ DVC remote configured with HTTPS!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Yellow
Write-Host "1. Create the data repository: https://github.com/vignesh-bits-wilp/mlops-assignment-data" -ForegroundColor White
Write-Host "2. Generate data files: python scripts/download_data.py" -ForegroundColor White
Write-Host "3. Process data: python src/data/data_ingestion.py" -ForegroundColor White
Write-Host "4. Add to DVC: dvc add data/raw/california_housing.csv data/processed/cleaned.csv" -ForegroundColor White
Write-Host "5. Commit DVC files: git add data/*.dvc && git commit -m 'Add DVC tracking'" -ForegroundColor White
Write-Host "6. Push to remote: dvc push" -ForegroundColor White
Write-Host ""
Write-Host "🔐 For CI/CD, make sure the data repository allows GitHub Actions access" -ForegroundColor Cyan
