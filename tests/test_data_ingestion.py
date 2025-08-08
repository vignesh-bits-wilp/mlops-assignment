import pandas as pd
import os
import tempfile
from src.data.data_ingestion import ingest_and_clean_data


class TestDataIngestion:
    """Test cases for data ingestion functionality."""

    def test_ingest_and_clean_data_creates_output_file(self):
        """Test that data ingestion creates the expected output file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a minimal test CSV file
            test_data = pd.DataFrame({
                'MedInc': [8.3252, 8.3014],
                'HouseAge': [41.0, 21.0],
                'AveRooms': [6.984127, 6.238137],
                'AveBedrms': [1.023810, 0.970880],
                'Population': [322.0, 2401.0],
                'AveOccup': [2.555556, 2.109842],
                'Latitude': [37.88, 37.86],
                'Longitude': [-122.23, -122.22],
                'target': [4.526, 3.585]
            })

            # Create test directories
            raw_dir = os.path.join(temp_dir, 'data', 'raw')
            processed_dir = os.path.join(temp_dir, 'data', 'processed')
            os.makedirs(raw_dir, exist_ok=True)
            os.makedirs(processed_dir, exist_ok=True)

            # Save test data
            raw_path = os.path.join(raw_dir, 'california_housing.csv')
            processed_path = os.path.join(processed_dir, 'cleaned.csv')
            test_data.to_csv(raw_path, index=False)

            # Run ingestion
            ingest_and_clean_data(raw_path, processed_path)

            # Check that output file exists
            assert os.path.exists(processed_path)

            # Check that output file has the same data (no missing values in test data)
            output_data = pd.read_csv(processed_path)
            assert len(output_data) == len(test_data)
            assert list(output_data.columns) == list(test_data.columns)

    def test_ingest_and_clean_data_handles_missing_values(self):
        """Test that data ingestion handles missing values correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data with missing values
            test_data = pd.DataFrame({
                'MedInc': [8.3252, None, 8.3014],
                'HouseAge': [41.0, 21.0, None],
                'AveRooms': [6.984127, 6.238137, 7.0],
                'AveBedrms': [1.023810, 0.970880, 1.0],
                'Population': [322.0, 2401.0, 500.0],
                'AveOccup': [2.555556, 2.109842, 2.5],
                'Latitude': [37.88, 37.86, 37.85],
                'Longitude': [-122.23, -122.22, -122.21],
                'target': [4.526, 3.585, 4.0]
            })

            # Create test directories
            raw_dir = os.path.join(temp_dir, 'data', 'raw')
            processed_dir = os.path.join(temp_dir, 'data', 'processed')
            os.makedirs(raw_dir, exist_ok=True)
            os.makedirs(processed_dir, exist_ok=True)

            # Save test data
            raw_path = os.path.join(raw_dir, 'california_housing.csv')
            processed_path = os.path.join(processed_dir, 'cleaned.csv')
            test_data.to_csv(raw_path, index=False)

            # Run ingestion
            ingest_and_clean_data(raw_path, processed_path)

            # Check that output file exists and has fewer rows (missing values removed)
            assert os.path.exists(processed_path)
            output_data = pd.read_csv(processed_path)
            assert len(output_data) < len(test_data)  # Should have fewer rows due to missing values
            assert len(output_data) > 0  # Should still have some data
