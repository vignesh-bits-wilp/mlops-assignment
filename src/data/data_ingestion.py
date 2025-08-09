"""
Data ingestion and preprocessing for California Housing dataset.
Handles downloading, cleaning, and DVC tracking.
"""

import pandas as pd
import numpy as np
from sklearn.datasets import fetch_california_housing
import os
import subprocess


def download_california_housing_data(output_path="data/raw/california_housing.csv"):
    """
    Download California Housing dataset from sklearn and save as CSV.
    """
    print("📥 Downloading California Housing dataset...")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Fetch the dataset
    housing = fetch_california_housing(as_frame=True)
    
    # Combine features and target
    data = housing.data
    data['target'] = housing.target
    
    # Save to CSV
    data.to_csv(output_path, index=False)
    print(f"✅ Raw data saved to {output_path}")
    print(f"   Shape: {data.shape}")
    
    return output_path


def clean_and_preprocess_data(
    input_path="data/raw/california_housing.csv",
    output_path="data/processed/cleaned.csv"
):
    """
    Clean and preprocess the housing data.
    Basic cleaning - the sklearn dataset is already pretty clean.
    """
    print("🧹 Cleaning and preprocessing data...")
    
    # Load data
    df = pd.read_csv(input_path)
    print(f"Loaded data shape: {df.shape}")
    
    # Check for missing values (shouldn't be any in this dataset)
    missing_values = df.isnull().sum()
    if missing_values.sum() > 0:
        print("⚠️  Found missing values:")
        print(missing_values[missing_values > 0])
    else:
        print("✅ No missing values found")
    
    # Basic data validation
    print("\nData summary:")
    print(df.describe())
    
    # Check for obvious outliers or data issues
    # (In a real project we'd do more thorough analysis)
    if (df['HouseAge'] < 0).any():
        print("⚠️  Found negative house ages, fixing...")
        df['HouseAge'] = df['HouseAge'].abs()
    
    if (df['Population'] <= 0).any():
        print("⚠️  Found zero or negative population, fixing...")
        df = df[df['Population'] > 0]
    
    # Ensure target column exists and is named correctly
    if 'MedHouseVal' in df.columns and 'target' not in df.columns:
        df['target'] = df['MedHouseVal']
        df = df.drop('MedHouseVal', axis=1)
    
    # Create output directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save cleaned data
    df.to_csv(output_path, index=False)
    print(f"✅ Cleaned data saved to {output_path}")
    print(f"   Final shape: {df.shape}")
    
    return output_path


def ingest_and_clean_data(
    raw_path="data/raw/california_housing.csv",
    cleaned_path="data/processed/cleaned.csv"
):
    """
    Full data ingestion pipeline: download, clean, and track with DVC.
    """
    print("🚀 Starting data ingestion pipeline...")
    
    # Download raw data if it doesn't exist
    if not os.path.exists(raw_path):
        download_california_housing_data(raw_path)
    else:
        print(f"Raw data already exists at {raw_path}")
    
    # Clean and preprocess
    clean_and_preprocess_data(raw_path, cleaned_path)
    
    # Try to add both files to DVC tracking
    # (This might fail if DVC isn't set up, which is fine)
    for file in [raw_path, cleaned_path]:
        print(f"Adding {file} to DVC tracking...")
        try:
            result = subprocess.run(["dvc", "add", file], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {file} added to DVC")
            else:
                print(f"⚠️  DVC add failed for {file}: {result.stderr}")
        except FileNotFoundError:
            print("⚠️  DVC not found - skipping version control")
            print("This is normal if DVC is not installed or configured")
            break
    
    print("✅ Data ingestion pipeline complete!")


if __name__ == "__main__":
    ingest_and_clean_data()
