"""
Feature engineering module for creating model-ready features from traffic data.
Creates spatial-temporal features for GNN training.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta

class FeatureEngineer:
    """Feature engineering for traffic prediction models."""
    
    def __init__(self, sequence_length: int = 12, prediction_horizon: int = 6):
        """
        Initialize feature engineer.
        
        Args:
            sequence_length: Number of historical time steps (default: 12 = 1 hour)
            prediction_horizon: Number of future time steps to predict (default: 6 = 30 min)
        """
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
        self.logger = logging.getLogger(__name__)
        
    def create_sequences(self, time_series_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create input-output sequences for model training.
        
        Args:
            time_series_df: Time series data with 'road_id', 'time_bin' columns
            
        Returns:
            Tuple of (X, y) arrays where X is input sequences, y is target sequences
        """
        # Sort by road_id and time
        df_sorted = time_series_df.sort_values(['road_id', 'time_bin'])
        
        # Get feature columns (exclude identifiers and target)
        feature_cols = [col for col in df_sorted.columns 
                       if col not in ['road_id', 'time_bin']]
        
        X_sequences = []
        y_sequences = []
        road_ids = []
        
        # Group by road segment
        for road_id, group in df_sorted.groupby('road_id'):
            if len(group) < self.sequence_length + self.prediction_horizon:
                continue
                
            features = group[feature_cols].values
            
            # Create sliding windows
            for i in range(len(features) - self.sequence_length - self.prediction_horizon + 1):
                X_seq = features[i:i + self.sequence_length]
                y_seq = features[i + self.sequence_length:i + self.sequence_length + self.prediction_horizon]
                
                X_sequences.append(X_seq)
                y_sequences.append(y_seq)
                road_ids.append(road_id)
        
        return np.array(X_sequences), np.array(y_sequences), road_ids
    
    def create_spatial_features(self, time_series_df: pd.DataFrame, 
                               road_network_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add spatial features based on road network topology.
        
        Args:
            time_series_df: Time series traffic data
            road_network_df: Road network with connectivity information
            
        Returns:
            DataFrame with spatial features added
        """
        # Create road connectivity matrix (simplified)
        road_connections = self._build_connectivity_matrix(road_network_df)
        
        # Add neighbor features
        enriched_df = time_series_df.copy()
        
        for road_id in time_series_df['road_id'].unique():
            neighbors = road_connections.get(road_id, [])
            
            if neighbors:
                # Calculate neighbor statistics
                neighbor_mask = time_series_df['road_id'].isin(neighbors)
                neighbor_data = time_series_df[neighbor_mask]
                
                if not neighbor_data.empty:
                    # Group by time_bin and calculate neighbor stats
                    neighbor_stats = neighbor_data.groupby('time_bin').agg({
                        'avg_speed': ['mean', 'std'],
                        'vehicle_count': 'sum',
                        'traffic_density': 'mean'
                    }).reset_index()
                    
                    # Flatten column names
                    neighbor_stats.columns = [
                        f"neighbor_{col[0]}_{col[1]}" if col[1] != '' else col[0]
                        for col in neighbor_stats.columns
                    ]
                    
                    # Merge back to main dataframe
                    road_mask = enriched_df['road_id'] == road_id
                    enriched_df.loc[road_mask] = enriched_df.loc[road_mask].merge(
                        neighbor_stats, on='time_bin', how='left'
                    )
        
        return enriched_df
    
    def _build_connectivity_matrix(self, road_network_df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Build road connectivity matrix from road network data.
        
        Args:
            road_network_df: Road network GeoDataFrame
            
        Returns:
            Dictionary mapping road_id to list of connected road_ids
        """
        # Simplified connectivity based on spatial proximity
        # In practice, this would use actual topology from OSM data
        connectivity = {}
        
        # For now, create dummy connections (would need actual geometric analysis)
        road_ids = road_network_df['osm_id'].unique() if 'osm_id' in road_network_df.columns else []
        
        for i, road_id in enumerate(road_ids):
            # Connect to nearby roads (simplified approach)
            start_idx = max(0, i - 2)
            end_idx = min(len(road_ids), i + 3)
            neighbors = [rid for rid in road_ids[start_idx:end_idx] if rid != road_id]
            connectivity[road_id] = neighbors
            
        return connectivity
    
    def add_lag_features(self, time_series_df: pd.DataFrame, 
                        lag_periods: List[int] = [1, 2, 3, 6, 12]) -> pd.DataFrame:
        """
        Add lagged features for time series modeling.
        
        Args:
            time_series_df: Time series data
            lag_periods: List of lag periods to create
            
        Returns:
            DataFrame with lag features
        """
        enriched_df = time_series_df.copy()
        
        # Sort by road_id and time
        enriched_df = enriched_df.sort_values(['road_id', 'time_bin'])
        
        feature_cols = ['avg_speed', 'vehicle_count', 'traffic_density']
        
        for road_id, group in enriched_df.groupby('road_id'):
            for lag in lag_periods:
                for col in feature_cols:
                    lag_col_name = f"{col}_lag_{lag}"
                    enriched_df.loc[group.index, lag_col_name] = group[col].shift(lag)
                    
        return enriched_df
    
    def add_rolling_features(self, time_series_df: pd.DataFrame,
                           windows: List[int] = [3, 6, 12]) -> pd.DataFrame:
        """
        Add rolling window statistics.
        
        Args:
            time_series_df: Time series data
            windows: List of window sizes
            
        Returns:
            DataFrame with rolling features
        """
        enriched_df = time_series_df.copy()
        enriched_df = enriched_df.sort_values(['road_id', 'time_bin'])
        
        feature_cols = ['avg_speed', 'vehicle_count', 'traffic_density']
        
        for road_id, group in enriched_df.groupby('road_id'):
            for window in windows:
                for col in feature_cols:
                    # Rolling mean
                    mean_col = f"{col}_rolling_mean_{window}"
                    enriched_df.loc[group.index, mean_col] = group[col].rolling(window).mean()
                    
                    # Rolling std
                    std_col = f"{col}_rolling_std_{window}"
                    enriched_df.loc[group.index, std_col] = group[col].rolling(window).std()
                    
        return enriched_df
    
    def create_cyclical_features(self, time_series_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create cyclical encoding for temporal features.
        
        Args:
            time_series_df: Time series data
            
        Returns:
            DataFrame with cyclical features
        """
        enriched_df = time_series_df.copy()
        
        # Hour cyclical features
        enriched_df['hour_sin'] = np.sin(2 * np.pi * enriched_df['hour'] / 24)
        enriched_df['hour_cos'] = np.cos(2 * np.pi * enriched_df['hour'] / 24)
        
        # Day of week cyclical features
        enriched_df['dow_sin'] = np.sin(2 * np.pi * enriched_df['day_of_week'] / 7)
        enriched_df['dow_cos'] = np.cos(2 * np.pi * enriched_df['day_of_week'] / 7)
        
        # Month cyclical features
        enriched_df['month_sin'] = np.sin(2 * np.pi * enriched_df['month'] / 12)
        enriched_df['month_cos'] = np.cos(2 * np.pi * enriched_df['month'] / 12)
        
        return enriched_df
    
    def normalize_features(self, train_df: pd.DataFrame, 
                          test_df: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, Dict]:
        """
        Normalize features using training data statistics.
        
        Args:
            train_df: Training data
            test_df: Test data (optional)
            
        Returns:
            Tuple of (normalized_data, normalization_stats)
        """
        # Identify numeric columns to normalize
        numeric_cols = train_df.select_dtypes(include=[np.number]).columns
        exclude_cols = ['road_id', 'time_bin', 'hour', 'day_of_week', 'month', 'is_weekend']
        normalize_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        # Calculate normalization statistics from training data
        normalization_stats = {}
        normalized_train = train_df.copy()
        
        for col in normalize_cols:
            mean_val = train_df[col].mean()
            std_val = train_df[col].std()
            normalization_stats[col] = {'mean': mean_val, 'std': std_val}
            
            # Apply normalization
            normalized_train[col] = (train_df[col] - mean_val) / (std_val + 1e-8)
        
        if test_df is not None:
            normalized_test = test_df.copy()
            for col in normalize_cols:
                if col in test_df.columns:
                    mean_val = normalization_stats[col]['mean']
                    std_val = normalization_stats[col]['std']
                    normalized_test[col] = (test_df[col] - mean_val) / (std_val + 1e-8)
            return normalized_train, normalized_test, normalization_stats
        
        return normalized_train, normalization_stats

def create_model_ready_features(input_file: str, output_dir: str, 
                               road_network_file: Optional[str] = None):
    """
    Complete feature engineering pipeline.
    
    Args:
        input_file: Path to aggregated time series data
        output_dir: Output directory for processed features
        road_network_file: Optional road network file for spatial features
    """
    engineer = FeatureEngineer()
    
    # Load data
    time_series_df = pd.read_csv(input_file)
    time_series_df['time_bin'] = pd.to_datetime(time_series_df['time_bin'])
    
    print(f"Loaded {len(time_series_df)} time series records")
    
    # Add temporal features
    enriched_df = engineer.add_lag_features(time_series_df)
    enriched_df = engineer.add_rolling_features(enriched_df)
    enriched_df = engineer.create_cyclical_features(enriched_df)
    
    # Add spatial features if road network is available
    if road_network_file:
        try:
            road_network_df = pd.read_csv(road_network_file)  # Simplified
            enriched_df = engineer.create_spatial_features(enriched_df, road_network_df)
        except Exception as e:
            print(f"Warning: Could not add spatial features: {e}")
    
    # Split train/test (80/20)
    split_date = enriched_df['time_bin'].quantile(0.8)
    train_df = enriched_df[enriched_df['time_bin'] <= split_date]
    test_df = enriched_df[enriched_df['time_bin'] > split_date]
    
    # Normalize features
    train_normalized, test_normalized, norm_stats = engineer.normalize_features(train_df, test_df)
    
    # Create sequences
    X_train, y_train, train_road_ids = engineer.create_sequences(train_normalized)
    X_test, y_test, test_road_ids = engineer.create_sequences(test_normalized)
    
    # Save processed data
    np.save(f"{output_dir}/X_train.npy", X_train)
    np.save(f"{output_dir}/y_train.npy", y_train)
    np.save(f"{output_dir}/X_test.npy", X_test)
    np.save(f"{output_dir}/y_test.npy", y_test)
    
    # Save metadata
    metadata = {
        'train_road_ids': train_road_ids,
        'test_road_ids': test_road_ids,
        'normalization_stats': norm_stats,
        'sequence_length': engineer.sequence_length,
        'prediction_horizon': engineer.prediction_horizon,
        'feature_names': [col for col in train_normalized.columns 
                         if col not in ['road_id', 'time_bin']]
    }
    
    import json
    with open(f"{output_dir}/metadata.json", 'w') as f:
        json.dump(metadata, f, default=str, indent=2)
    
    print(f"Feature engineering complete:")
    print(f"  Training sequences: {X_train.shape}")
    print(f"  Test sequences: {X_test.shape}")
    print(f"  Features saved to {output_dir}")

if __name__ == "__main__":
    # Example usage with sample data
    engineer = FeatureEngineer()
    
    # Create sample time series data
    dates = pd.date_range('2024-01-01', periods=1000, freq='5min')
    sample_data = pd.DataFrame({
        'road_id': ['road_1'] * 500 + ['road_2'] * 500,
        'time_bin': list(dates[:500]) + list(dates[:500]),
        'avg_speed': np.random.normal(50, 10, 1000),
        'vehicle_count': np.random.poisson(10, 1000),
        'traffic_density': np.random.gamma(2, 2, 1000),
        'hour': [d.hour for d in dates[:500]] * 2,
        'day_of_week': [d.dayofweek for d in dates[:500]] * 2,
        'month': [d.month for d in dates[:500]] * 2
    })
    
    # Test feature engineering
    enriched = engineer.add_lag_features(sample_data)
    enriched = engineer.add_rolling_features(enriched)
    enriched = engineer.create_cyclical_features(enriched)
    
    # Create sequences
    X, y, road_ids = engineer.create_sequences(enriched.dropna())
    print(f"Sample sequences created: X={X.shape}, y={y.shape}")
