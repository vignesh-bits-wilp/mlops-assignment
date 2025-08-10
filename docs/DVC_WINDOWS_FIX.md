# DVC Windows Compatibility Fix

## Problem

The original DVC setup used SSH URLs with special characters that are not supported by Windows filesystem:

```
git@github.com:vignesh-bits-wilp/mlops-assignment-data.git
```

This creates cache directories with `@` and `:` characters, which are invalid in Windows:
```
.dvc/git@github.com:vignesh-bits-wilp/mlops-assignment-data.git/files/md5/...
```

## Solution

Switched from SSH to HTTPS URLs for cross-platform compatibility:

```
https://github.com/vignesh-bits-wilp/mlops-assignment-data.git
```

This creates safe cache directories:
```
.dvc/github.com/vignesh-bits-wilp/mlops-assignment-data.git/files/md5/...
```

## Changes Made

### 1. Updated DVC Configuration

**File**: `.dvc/config`
```ini
[core]
    remote = origin
['remote "origin"']
    url = https://github.com/vignesh-bits-wilp/mlops-assignment-data.git
```

### 2. Updated CI/CD Pipeline

**File**: `.github/workflows/ci.yml`

**Removed**:
- SSH key setup
- SSH known_hosts configuration
- DVC cache actions

**Added**:
- DVC installation
- HTTPS configuration with GitHub token
- Simplified authentication

**Key Changes**:
```yaml
- name: Configure DVC for GitHub Actions
  run: |
    dvc remote modify origin url https://${{ secrets.GITHUB_TOKEN }}@github.com/vignesh-bits-wilp/mlops-assignment-data.git
```

### 3. Created Setup Scripts

**Windows**: `scripts/setup_dvc_remote.ps1`
**Linux/macOS**: `scripts/setup_dvc_remote.sh`

These scripts help configure DVC remote with HTTPS for local development.

### 4. Updated Documentation

- Updated `docs/DVC_CICD_SETUP.md` to reflect HTTPS approach
- Updated `README.md` with new setup instructions
- Created this documentation file

## Benefits

1. **✅ Windows Compatible**: No special characters in folder names
2. **✅ Cross-Platform**: Works on Windows, macOS, Linux
3. **✅ Simpler Setup**: No SSH key management needed
4. **✅ CI/CD Friendly**: Uses GitHub's built-in authentication
5. **✅ More Reliable**: No filesystem compatibility issues

## Setup Instructions

### For Local Development

**Windows**:
```powershell
.\scripts\setup_dvc_remote.ps1
```

**Linux/macOS**:
```bash
chmod +x scripts/setup_dvc_remote.sh
./scripts/setup_dvc_remote.sh
```

### For CI/CD

1. **Create Data Repository**: `vignesh-bits-wilp/mlops-assignment-data`
2. **Enable GitHub Actions**: Settings → Actions → General → Allow GitHub Actions
3. **Push Data**: The CI/CD pipeline will automatically handle data management

### Data Repository Setup

1. Create repository: `https://github.com/vignesh-bits-wilp/mlops-assignment-data`
2. Make it private (recommended)
3. Enable GitHub Actions access
4. No additional secrets needed (uses built-in `GITHUB_TOKEN`)

## Testing

### Local Testing
```bash
# Setup DVC remote
.\scripts\setup_dvc_remote.ps1  # Windows
# or
./scripts/setup_dvc_remote.sh   # Linux/macOS

# Generate and process data
python scripts/download_data.py
python src/data/data_ingestion.py

# Add to DVC tracking
dvc add data/raw/california_housing.csv data/processed/cleaned.csv

# Push to remote
dvc push

# Test pull
rm data/raw/california_housing.csv data/processed/cleaned.csv
dvc pull
```

### CI/CD Testing
The pipeline will automatically:
1. Configure DVC with HTTPS
2. Pull data from remote
3. Process data if needed
4. Train models
5. Push any data changes back to remote

## Troubleshooting

### Common Issues

1. **"Repository not found"**: Data repository doesn't exist
2. **"Permission denied"**: GitHub Actions not enabled on data repository
3. **"Cache files missing"**: Data hasn't been pushed to remote yet

### Solutions

1. **Create the data repository** if it doesn't exist
2. **Enable GitHub Actions** on the data repository
3. **Push data locally first** before running CI/CD

## Migration from SSH

If you were using SSH before:

1. **Remove SSH remote**:
   ```bash
   dvc remote remove origin
   ```

2. **Add HTTPS remote**:
   ```bash
   dvc remote add origin https://github.com/vignesh-bits-wilp/mlops-assignment-data.git
   dvc remote default origin
   ```

3. **Update CI/CD**: Already done in this fix

4. **Test the setup**: Use the provided scripts

This fix ensures that DVC works reliably across all platforms, especially Windows, while maintaining the assignment requirements for using DVC.
