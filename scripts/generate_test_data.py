#!/usr/bin/env python3
"""
Generate test data for monitoring dashboard
"""

import requests
import time
import random

def generate_test_predictions():
    """Generate multiple test predictions to populate the dashboard."""
    
    # Test data samples
    test_samples = [
        {'MedInc': 8.3252, 'HouseAge': 41.0, 'AveRooms': 6.984, 'AveBedrms': 1.024, 'Population': 322.0, 'AveOccup': 2.556, 'Latitude': 37.88, 'Longitude': -122.23},
        {'MedInc': 5.0, 'HouseAge': 35.0, 'AveRooms': 5.5, 'AveBedrms': 1.0, 'Population': 500.0, 'AveOccup': 2.0, 'Latitude': 37.5, 'Longitude': -122.0},
        {'MedInc': 12.0, 'HouseAge': 50.0, 'AveRooms': 8.0, 'AveBedrms': 1.5, 'Population': 200.0, 'AveOccup': 3.0, 'Latitude': 38.0, 'Longitude': -122.5},
        {'MedInc': 3.0, 'HouseAge': 25.0, 'AveRooms': 4.0, 'AveBedrms': 0.8, 'Population': 800.0, 'AveOccup': 1.5, 'Latitude': 37.0, 'Longitude': -121.5},
        {'MedInc': 15.0, 'HouseAge': 60.0, 'AveRooms': 10.0, 'AveBedrms': 2.0, 'Population': 100.0, 'AveOccup': 4.0, 'Latitude': 38.5, 'Longitude': -123.0}
    ]
    
    print("Generating test predictions...")
    
    for i in range(20):
        # Randomly select a test sample
        sample = random.choice(test_samples)
        
        # Add some randomness
        sample = {k: v + random.uniform(-0.5, 0.5) if isinstance(v, float) else v for k, v in sample.items()}
        
        try:
            response = requests.post('http://localhost:8000/predict', json=sample)
            if response.status_code == 200:
                result = response.json()
                print(f"Prediction {i+1}: {result['prediction']:.2f} (Response time: {result['response_time_ms']:.2f}ms)")
            else:
                print(f"Error {i+1}: {response.status_code}")
        except Exception as e:
            print(f"Request {i+1} failed: {e}")
        
        # Small delay between requests
        time.sleep(0.1)
    
    print("Test data generation complete!")

if __name__ == "__main__":
    generate_test_predictions() 