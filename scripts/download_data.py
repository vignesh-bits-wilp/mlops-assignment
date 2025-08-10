"""
Script to download the California Housing dataset.
"""

import pandas as pd
from sklearn.datasets import fetch_california_housing
import os

def download_california_housing():
    """Download California Housing dataset and save to data/raw/"""
    
    # Create directory if it doesn't exist
    os.makedirs('data/raw', exist_ok=True)
    
    # Fetch the dataset
    print("Downloading California Housing dataset...")
    california_housing = fetch_california_housing()
    
    # Convert to DataFrame
    df = pd.DataFrame(california_housing.data, columns=california_housing.feature_names)
    df['target'] = california_housing.target
    
    # Save to CSV
    output_path = 'data/raw/california_housing.csv'
    df.to_csv(output_path, index=False)
    
    print(f"Dataset saved to: {output_path}")
    print(f"Dataset shape: {df.shape}")
    print(f"Features: {list(df.columns)}")

if __name__ == "__main__":
    download_california_housing()
