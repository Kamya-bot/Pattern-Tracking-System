"""
Data Preprocessing Pipeline
Handles data cleaning, transformation, and feature engineering
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler
from sklearn.impute import SimpleImputer


class DataPreprocessor:
    """
    Comprehensive data preprocessing pipeline for health symptom data
    """
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.imputers = {}
        self.feature_names = []
        self.is_fitted = False
    
    def fit(self, data: pd.DataFrame, target_column: Optional[str] = None) -> 'DataPreprocessor':
        """
        Fit preprocessing pipeline to training data
        
        Args:
            data: Training DataFrame
            target_column: Name of target column (excluded from scaling)
            
        Returns:
            Self for method chaining
        """
        self.feature_names = [col for col in data.columns if col != target_column]
        
        # Identify column types
        self.numeric_features = data[self.feature_names].select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_features = data[self.feature_names].select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Fit imputers for missing values
        if self.numeric_features:
            self.imputers['numeric'] = SimpleImputer(strategy='mean')
            self.imputers['numeric'].fit(data[self.numeric_features])
        
        if self.categorical_features:
            self.imputers['categorical'] = SimpleImputer(strategy='most_frequent')
            self.imputers['categorical'].fit(data[self.categorical_features])
        
        # Fit scalers for numeric features
        if self.numeric_features:
            self.scalers['standard'] = StandardScaler()
            self.scalers['standard'].fit(data[self.numeric_features])
            
            self.scalers['minmax'] = MinMaxScaler()
            self.scalers['minmax'].fit(data[self.numeric_features])
        
        # Fit encoders for categorical features
        for col in self.categorical_features:
            self.encoders[col] = LabelEncoder()
            self.encoders[col].fit(data[col].fillna('Unknown'))
        
        self.is_fitted = True
        print(f"✅ Preprocessing pipeline fitted")
        print(f"   Numeric features: {len(self.numeric_features)}")
        print(f"   Categorical features: {len(self.categorical_features)}")
        
        return self
    
    def transform(self, data: pd.DataFrame, scale_method: str = 'standard') -> pd.DataFrame:
        """
        Transform data using fitted pipeline
        
        Args:
            data: DataFrame to transform
            scale_method: 'standard' or 'minmax' scaling
            
        Returns:
            Transformed DataFrame
        """
        if not self.is_fitted:
            raise RuntimeError("Pipeline not fitted. Call fit() first.")
        
        data_transformed = data.copy()
        
        # Handle missing values
        if self.numeric_features:
            data_transformed[self.numeric_features] = self.imputers['numeric'].transform(
                data_transformed[self.numeric_features]
            )
        
        if self.categorical_features:
            data_transformed[self.categorical_features] = self.imputers['categorical'].transform(
                data_transformed[self.categorical_features]
            )
        
        # Scale numeric features
        if self.numeric_features and scale_method in self.scalers:
            data_transformed[self.numeric_features] = self.scalers[scale_method].transform(
                data_transformed[self.numeric_features]
            )
        
        # Encode categorical features
        for col in self.categorical_features:
            data_transformed[col] = self.encoders[col].transform(
                data_transformed[col].fillna('Unknown')
            )
        
        return data_transformed
    
    def fit_transform(self, data: pd.DataFrame, target_column: Optional[str] = None,
                     scale_method: str = 'standard') -> pd.DataFrame:
        """
        Fit pipeline and transform data in one step
        
        Args:
            data: DataFrame to fit and transform
            target_column: Name of target column
            scale_method: Scaling method
            
        Returns:
            Transformed DataFrame
        """
        self.fit(data, target_column)
        return self.transform(data, scale_method)
    
    def inverse_transform(self, data: pd.DataFrame, scale_method: str = 'standard') -> pd.DataFrame:
        """
        Reverse scaling transformation (numeric features only)
        
        Args:
            data: Scaled DataFrame
            scale_method: Method used for scaling
            
        Returns:
            Unscaled DataFrame
        """
        data_inverse = data.copy()
        
        if self.numeric_features and scale_method in self.scalers:
            data_inverse[self.numeric_features] = self.scalers[scale_method].inverse_transform(
                data_inverse[self.numeric_features]
            )
        
        return data_inverse


def preprocess_symptom_data(data: Dict[str, any]) -> np.ndarray:
    """
    Preprocess raw symptom report data for ML models
    
    Args:
        data: Dict with symptom flags (fever, cough, etc.)
        
    Returns:
        Feature vector as numpy array
    """
    # Define symptom order (must match training data)
    symptom_order = [
        'fever', 'cold_cough', 'headache', 'stomach_pain',
        'nausea', 'skin_allergy', 'fatigue', 'body_pain'
    ]
    
    # Extract binary features
    features = [int(data.get(symptom, 0)) for symptom in symptom_order]
    
    return np.array(features)


def engineer_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Create engineered features for better ML performance
    
    Args:
        data: Raw symptom DataFrame
        
    Returns:
        DataFrame with additional engineered features
    """
    data_eng = data.copy()
    
    # Symptom count
    symptom_columns = ['fever', 'cold_cough', 'headache', 'stomach_pain',
                      'nausea', 'skin_allergy', 'fatigue', 'body_pain']
    
    if all(col in data.columns for col in symptom_columns):
        data_eng['symptom_count'] = data[symptom_columns].sum(axis=1)
        
        # Symptom severity score (weighted)
        severity_weights = {
            'fever': 2.0,
            'cold_cough': 1.5,
            'headache': 1.0,
            'stomach_pain': 1.5,
            'nausea': 1.5,
            'skin_allergy': 1.0,
            'fatigue': 1.5,
            'body_pain': 1.5
        }
        
        data_eng['severity_score'] = sum(
            data[col] * severity_weights[col] for col in symptom_columns
        )
        
        # Respiratory flag (fever + cough)
        if 'fever' in data.columns and 'cold_cough' in data.columns:
            data_eng['respiratory_flag'] = ((data['fever'] == 1) & 
                                           (data['cold_cough'] == 1)).astype(int)
        
        # Digestive flag (stomach pain + nausea)
        if 'stomach_pain' in data.columns and 'nausea' in data.columns:
            data_eng['digestive_flag'] = ((data['stomach_pain'] == 1) & 
                                         (data['nausea'] == 1)).astype(int)
    
    # Temporal features (if timestamp available)
    if 'timestamp' in data.columns:
        data_eng['hour_of_day'] = pd.to_datetime(data['timestamp']).dt.hour
        data_eng['day_of_week'] = pd.to_datetime(data['timestamp']).dt.dayofweek
        data_eng['is_weekend'] = (data_eng['day_of_week'] >= 5).astype(int)
    
    print(f"✅ Engineered {len(data_eng.columns) - len(data.columns)} new features")
    
    return data_eng


def handle_missing_values(data: pd.DataFrame, strategy: str = 'auto') -> pd.DataFrame:
    """
    Handle missing values in DataFrame
    
    Args:
        data: DataFrame with potential missing values
        strategy: 'auto', 'mean', 'median', 'mode', or 'drop'
        
    Returns:
        DataFrame with missing values handled
    """
    data_clean = data.copy()
    
    if strategy == 'drop':
        data_clean = data_clean.dropna()
        print(f"✅ Dropped {len(data) - len(data_clean)} rows with missing values")
    
    elif strategy == 'auto':
        # Numeric: fill with median
        numeric_cols = data_clean.select_dtypes(include=[np.number]).columns
        data_clean[numeric_cols] = data_clean[numeric_cols].fillna(data_clean[numeric_cols].median())
        
        # Categorical: fill with mode
        categorical_cols = data_clean.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            data_clean[col] = data_clean[col].fillna(data_clean[col].mode()[0] if not data_clean[col].mode().empty else 'Unknown')
        
        print(f"✅ Filled missing values (numeric: median, categorical: mode)")
    
    elif strategy in ['mean', 'median']:
        numeric_cols = data_clean.select_dtypes(include=[np.number]).columns
        if strategy == 'mean':
            data_clean[numeric_cols] = data_clean[numeric_cols].fillna(data_clean[numeric_cols].mean())
        else:
            data_clean[numeric_cols] = data_clean[numeric_cols].fillna(data_clean[numeric_cols].median())
        
        print(f"✅ Filled numeric missing values with {strategy}")
    
    elif strategy == 'mode':
        for col in data_clean.columns:
            data_clean[col] = data_clean[col].fillna(data_clean[col].mode()[0] if not data_clean[col].mode().empty else 0)
        
        print(f"✅ Filled missing values with mode")
    
    return data_clean


def normalize_features(data: pd.DataFrame, method: str = 'standard') -> Tuple[pd.DataFrame, object]:
    """
    Normalize numeric features
    
    Args:
        data: DataFrame to normalize
        method: 'standard' (z-score) or 'minmax' (0-1 scaling)
        
    Returns:
        Tuple of (normalized DataFrame, fitted scaler)
    """
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    
    if method == 'standard':
        scaler = StandardScaler()
    elif method == 'minmax':
        scaler = MinMaxScaler()
    else:
        raise ValueError(f"Unknown method: {method}")
    
    data_normalized = data.copy()
    data_normalized[numeric_cols] = scaler.fit_transform(data[numeric_cols])
    
    print(f"✅ Normalized {len(numeric_cols)} numeric features using {method} scaling")
    
    return data_normalized, scaler


# Example usage
if __name__ == '__main__':
    print("="*70)
    print("DATA PREPROCESSING PIPELINE DEMO")
    print("="*70)
    
    # Create sample data
    sample_data = pd.DataFrame({
        'fever': [1, 0, 1, 0, 1, np.nan],
        'cold_cough': [1, 1, 0, 1, 1, 0],
        'headache': [0, 1, 1, 0, 1, 1],
        'stomach_pain': [0, 0, 1, 0, 0, 1],
        'nausea': [0, 0, 1, 0, 0, 1],
        'skin_allergy': [0, 0, 0, 0, 0, 0],
        'fatigue': [1, 1, 1, 0, 1, 1],
        'body_pain': [1, 0, 1, 0, 1, 0],
        'location': ['Hostel A', 'Hostel B', 'Hostel A', 'Library', 'Hostel A', 'Hostel B'],
        'severity': ['Mild', 'Moderate', 'Severe', 'Mild', 'Moderate', 'Severe']
    })
    
    print("\n📊 Original data shape:", sample_data.shape)
    print("\n📋 First few rows:")
    print(sample_data.head())
    
    # Handle missing values
    print("\n" + "─"*70)
    data_clean = handle_missing_values(sample_data, strategy='auto')
    
    # Feature engineering
    print("\n" + "─"*70)
    data_engineered = engineer_features(data_clean)
    print("\n📋 Engineered features:")
    print(data_engineered[['symptom_count', 'severity_score', 'respiratory_flag']].head())
    
    # Fit preprocessor
    print("\n" + "─"*70)
    preprocessor = DataPreprocessor()
    data_transformed = preprocessor.fit_transform(data_engineered, target_column='severity')
    
    print("\n📊 Transformed data shape:", data_transformed.shape)
    print("\n✅ Pipeline ready for production use!")
