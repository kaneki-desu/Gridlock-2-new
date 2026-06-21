"""
Script to train XGBoost model on traffic incident data
Run this before starting the backend server

Usage:
    python train_model.py --data-path data.csv
"""

import pandas as pd
import argparse
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml.preprocessor import ClearanceTimePredictor

def train_xgboost_model(data_path: str, output_dir: str = "models"):
    """
    Train XGBoost model on incident data
    
    Args:
        data_path: Path to CSV file with incident data
        output_dir: Directory to save models
    """
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize predictor
    predictor = ClearanceTimePredictor()
    
    # Train model
    print("Training XGBoost model...")
    predictor.train(df, test_size=0.2, save_path=f'{output_dir}/xgboost_model.pkl')
    
    print(f"\nModel trained successfully!")
    print(f"Saved to: {output_dir}/xgboost_model.pkl")
    print(f"Encoders saved to: {output_dir}/encoders.pkl")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train XGBoost model")
    parser.add_argument(
        "--data-path",
        required=True,
        help="Path to incident CSV file"
    )
    parser.add_argument(
        "--output-dir",
        default="models",
        help="Directory to save models"
    )
    
    args = parser.parse_args()
    
    train_xgboost_model(args.data_path, args.output_dir)
