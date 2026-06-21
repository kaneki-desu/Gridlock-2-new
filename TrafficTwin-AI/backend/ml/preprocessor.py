import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
import os
from datetime import datetime

class DataPreprocessor:
    """
    Preprocesses raw traffic incident data for ML training
    """
    
    def __init__(self):
        self.label_encoders = {}
        self.categorical_columns = [
            'event_type', 'event_cause', 'corridor', 'priority', 
            'requires_road_closure', 'veh_type', 'junction'
        ]
    
    def extract_peak_hour(self, datetime_obj):
        """Extract peak hour from datetime - True if 7-9 AM or 4-7 PM"""
        if pd.isna(datetime_obj):
            return 0
        hour = pd.to_datetime(datetime_obj).hour
        return 1 if (hour >= 7 and hour <= 9) or (hour >= 16 and hour <= 19) else 0
    
    def calculate_clearance_time(self, row):
        """Calculate clearance time in minutes"""
        try:
            if pd.notna(row['closed_datetime']) and pd.notna(row['start_datetime']):
                start = pd.to_datetime(row['start_datetime'])
                closed = pd.to_datetime(row['closed_datetime'])
                return (closed - start).total_seconds() / 60
        except:
            pass
        return None
    
    def preprocess(self, df, target_column='closed_datetime', is_training=True):
        """
        Preprocess the dataframe
        
        Args:
            df: Input dataframe
            target_column: Column to calculate target variable from
            is_training: If True, fits encoders; if False, uses existing encoders
        
        Returns:
            Processed dataframe ready for ML
        """
        df = df.copy()
        
        # Calculate clearance time as target variable
        df['clearance_time'] = df.apply(self.calculate_clearance_time, axis=1)
        
        # Extract peak hour
        df['peak_hour'] = df['start_datetime'].apply(self.extract_peak_hour)
        
        # Handle missing values
        df['corridor'] = df['corridor'].fillna('Unknown')
        df['veh_type'] = df['veh_type'].fillna('unknown')
        df['junction'] = df['junction'].fillna('Unknown')
        
        # Encode categorical variables
        for col in self.categorical_columns:
            if col in df.columns:
                if is_training:
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col].astype(str))
                    self.label_encoders[col] = le
                else:
                    le = self.label_encoders.get(col)
                    if le:
                        df[col] = le.transform(df[col].astype(str))
        
        # Select features for training
        feature_columns = [
            'event_type', 'event_cause', 'latitude', 'longitude', 'corridor',
            'priority', 'requires_road_closure', 'veh_type', 'junction',
            'peak_hour'
        ]
        
        # Filter for existing columns
        available_features = [col for col in feature_columns if col in df.columns]
        
        return df, available_features
    
    def save_encoders(self, feature_columns, path='models/encoders.pkl'):
        with open(path, 'wb') as f:
            pickle.dump({
                "label_encoders": self.label_encoders,
                "feature_columns": feature_columns
            }, f)
    
    def load_encoders(self, path='models/encoders.pkl'):
        with open(path, 'rb') as f:
            data = pickle.load(f)

        self.label_encoders = data["label_encoders"]
        return data["feature_columns"]


class ClearanceTimePredictor:
    """
    XGBoost model for predicting incident clearance time
    """
    
    def __init__(self):
        self.model = None
        self.preprocessor = DataPreprocessor()
        self.feature_columns = None
    
    def train(self, df, test_size=0.2, save_path='models/xgboost_model.pkl'):
        """
        Train XGBoost model on incident data
        
        Args:
            df: Dataframe with incident data
            test_size: Proportion for test set
            save_path: Path to save trained model
        """
        # Preprocess data
        df_processed, feature_columns = self.preprocessor.preprocess(df, is_training=True)
        self.feature_columns = feature_columns
        
        # Remove rows with no clearance time
        df_processed = df_processed[df_processed['clearance_time'].notna()].copy()
        
        # Prepare features and target
        X = df_processed[feature_columns].astype(float)
        y = df_processed['clearance_time'].astype(float)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Train XGBoost
        self.model = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            verbosity=0
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print(f"Training R² Score: {train_score:.4f}")
        print(f"Testing R² Score: {test_score:.4f}")
        
        # Save model
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        self.preprocessor.save_encoders(feature_columns,'models/encoders.pkl')
    
    def predict(self, features_dict):
        if not self.model:
            raise ValueError("Model not trained. Call train() first.")
    
        processed_features = {}
    
        # Fix vehicle_type mismatch
        if "vehicle_type" in features_dict:
            features_dict["veh_type"] = features_dict.pop("vehicle_type")
    
        for col in self.feature_columns:
            value = features_dict.get(col, "Unknown")
    
            # Encode categorical columns
            if col in self.preprocessor.label_encoders:
                le = self.preprocessor.label_encoders[col]
    
                if str(value) not in le.classes_:
                    value = le.classes_[0]
    
                value = le.transform([str(value)])[0]
    
            processed_features[col] = value
    
        feature_vector = [processed_features[col] for col in self.feature_columns]
    
        # Actual prediction happens here
        prediction = self.model.predict([feature_vector])[0]
    
        return max(0, float(prediction))
          
    def load_model(self, model_path='models/xgboost_model.pkl'):
        """Load pre-trained model"""
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        self.feature_columns=self.preprocessor.load_encoders('models/encoders.pkl')
