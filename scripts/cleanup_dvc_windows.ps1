# PowerShell script to clean up DVC cache for Windows compatibility
Write-Host "Cleaning up DVC cache for Windows compatibility..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Remove DVC cache directories that cause Windows filename issues
$dvcDirs = @(".dvc\cache", ".dvc\tmp", ".dvc\state", ".dvc\state-journal")

foreach ($dir in $dvcDirs) {
    if (Test-Path $dir) {
        Write-Host "Removing $dir directory..." -ForegroundColor Yellow
        Remove-Item -Path $dir -Recurse -Force
    }
}

# Remove any temporary DVC files
$tempFiles = Get-ChildItem -Path . -Recurse -Include "*.dvc-tmp", "*.dvc-cache" -ErrorAction SilentlyContinue
foreach ($file in $tempFiles) {
    Write-Host "Removing temporary file: $($file.FullName)" -ForegroundColor Yellow
    Remove-Item -Path $file.FullName -Force
}

Write-Host ""
Write-Host "DVC cache cleanup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run: git add ." -ForegroundColor White
Write-Host "2. Run: git commit -m 'Clean up DVC cache for Windows compatibility'" -ForegroundColor White
Write-Host "3. Run: dvc pull (to re-download data if needed)" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue" 