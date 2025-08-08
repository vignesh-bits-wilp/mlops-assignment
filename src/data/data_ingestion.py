import pandas as pd
import subprocess


def ingest_and_clean_data(
    raw_path="data/raw/california_housing.csv",
    cleaned_path="data/processed/cleaned.csv"
):
    """
    Loads the raw California Housing CSV, cleans it, saves the cleaned data,
    and uses DVC to track both the raw and cleaned CSVs.
    """
    # Ensure processed directory exists
    import os
    os.makedirs(os.path.dirname(cleaned_path), exist_ok=True)

    # Load raw data
    print(f"Loading raw data from {raw_path}...")
    df = pd.read_csv(raw_path)
    print(f"Raw data shape: {df.shape}")

    # Basic cleaning: drop missing values
    df_clean = df.dropna()
    print(f"Cleaned data shape (after dropna): {df_clean.shape}")

    # Save cleaned data
    df_clean.to_csv(cleaned_path, index=False)
    print(f"Cleaned data saved to {cleaned_path}")

    # DVC track both files
    for file in [raw_path, cleaned_path]:
        print(f"Adding {file} to DVC tracking...")
        try:
            subprocess.run(["dvc", "add", file], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"Warning: DVC tracking failed for {file}")
            print("This is normal if the file is already tracked by Git or DVC is not configured.")
    print("Data ingestion complete.")


if __name__ == "__main__":
    ingest_and_clean_data()
