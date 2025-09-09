"""
Data aggregation module for creating time-based features from probe data.
Aggregates probe data into 5-minute intervals for model training.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

class TrafficAggregator:
    """Aggregates probe data into time intervals for analysis."""
    
    def __init__(self, interval_minutes: int = 5):
        """
        Initialize aggregator.
        
        Args:
            interval_minutes: Time interval for aggregation (default: 5 minutes)
        """
        self.interval_minutes = interval_minutes
        self.logger = logging.getLogger(__name__)
        
    def aggregate_probe_data(self, probe_df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate probe data by road segment and time interval.
        
        Args:
            probe_df: DataFrame with matched probe data
            
        Returns:
            Aggregated DataFrame with traffic metrics
        """
        # Ensure timestamp is datetime
        probe_df['timestamp'] = pd.to_datetime(probe_df['timestamp'])
        
        # Create time bins
        probe_df['time_bin'] = probe_df['timestamp'].dt.floor(f'{self.interval_minutes}min')
        
        # Group by road segment and time bin
        agg_funcs = {
            'speed': ['mean', 'std', 'count'],
            'heading': ['mean', 'std'],
            'lat': ['mean'],
            'lon': ['mean'],
            'match_distance': ['mean']
        }
        
        aggregated = probe_df.groupby(['road_id', 'time_bin']).agg(agg_funcs).reset_index()
        
        # Flatten column names
        aggregated.columns = [
            f"{col[0]}_{col[1]}" if col[1] != '' else col[0] 
            for col in aggregated.columns
        ]
        
        # Rename columns for clarity
        column_mapping = {
            'speed_mean': 'avg_speed',
            'speed_std': 'speed_variance',
            'speed_count': 'vehicle_count',
            'heading_mean': 'avg_heading',
            'heading_std': 'heading_variance',
            'lat_mean': 'avg_lat',
            'lon_mean': 'avg_lon',
            'match_distance_mean': 'avg_match_distance'
        }
        
        aggregated = aggregated.rename(columns=column_mapping)
        
        # Add derived features
        aggregated = self._add_temporal_features(aggregated)
        aggregated = self._add_traffic_features(aggregated)
        
        return aggregated
    
    def _add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features."""
        df['hour'] = df['time_bin'].dt.hour
        df['day_of_week'] = df['time_bin'].dt.dayofweek
        df['month'] = df['time_bin'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Rush hour indicators
        df['is_morning_rush'] = ((df['hour'] >= 7) & (df['hour'] <= 9)).astype(int)
        df['is_evening_rush'] = ((df['hour'] >= 17) & (df['hour'] <= 19)).astype(int)
        
        return df
    
    def _add_traffic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add traffic-specific features."""
        # Traffic density (vehicles per minute)
        df['traffic_density'] = df['vehicle_count'] / self.interval_minutes
        
        # Speed categories
        df['speed_category'] = pd.cut(
            df['avg_speed'], 
            bins=[0, 20, 40, 60, 100], 
            labels=['congested', 'slow', 'normal', 'fast']
        )
        
        # Traffic flow (simplified as speed * density)
        df['traffic_flow'] = df['avg_speed'] * df['traffic_density']
        
        # Fill NaN values
        df['speed_variance'] = df['speed_variance'].fillna(0)
        df['heading_variance'] = df['heading_variance'].fillna(0)
        
        return df
    
    def create_time_series(self, aggregated_df: pd.DataFrame, 
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> pd.DataFrame:
        """
        Create complete time series with missing intervals filled.
        
        Args:
            aggregated_df: Aggregated traffic data
            start_time: Start time for the series
            end_time: End time for the series
            
        Returns:
            Complete time series DataFrame
        """
        if start_time is None:
            start_time = aggregated_df['time_bin'].min()
        if end_time is None:
            end_time = aggregated_df['time_bin'].max()
            
        # Create complete time range
        time_range = pd.date_range(
            start=start_time,
            end=end_time,
            freq=f'{self.interval_minutes}min'
        )
        
        # Get unique road segments
        road_ids = aggregated_df['road_id'].unique()
        
        # Create complete index
        complete_index = pd.MultiIndex.from_product(
            [road_ids, time_range],
            names=['road_id', 'time_bin']
        )
        
        # Reindex and fill missing values
        complete_df = aggregated_df.set_index(['road_id', 'time_bin']).reindex(complete_index)
        
        # Forward fill for basic features, zero fill for counts
        fill_methods = {
            'avg_speed': 'ffill',
            'vehicle_count': 0,
            'traffic_density': 0,
            'traffic_flow': 0
        }
        
        for col, method in fill_methods.items():
            if col in complete_df.columns:
                if method == 'ffill':
                    complete_df[col] = complete_df[col].fillna(method='ffill')
                else:
                    complete_df[col] = complete_df[col].fillna(method)
                    
        return complete_df.reset_index()
    
    def calculate_historical_stats(self, time_series_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate historical statistics for each road segment.
        
        Args:
            time_series_df: Complete time series data
            
        Returns:
            DataFrame with historical statistics
        """
        # Group by road_id and hour/day patterns
        stats = time_series_df.groupby(['road_id', 'hour', 'day_of_week']).agg({
            'avg_speed': ['mean', 'std', 'min', 'max'],
            'vehicle_count': ['mean', 'std'],
            'traffic_density': ['mean', 'std']
        }).reset_index()
        
        # Flatten column names
        stats.columns = [
            f"{col[0]}_{col[1]}" if col[1] != '' else col[0] 
            for col in stats.columns
        ]
        
        # Add seasonal patterns
        monthly_stats = time_series_df.groupby(['road_id', 'month']).agg({
            'avg_speed': 'mean',
            'vehicle_count': 'mean'
        }).reset_index()
        
        monthly_stats.columns = ['road_id', 'month', 'monthly_avg_speed', 'monthly_avg_count']
        
        return stats, monthly_stats

def process_aggregation_pipeline(input_dir: str, output_dir: str, interval_minutes: int = 5):
    """
    Complete aggregation pipeline for processing matched data.
    
    Args:
        input_dir: Directory with matched probe data
        output_dir: Output directory for aggregated data
        interval_minutes: Aggregation interval
    """
    aggregator = TrafficAggregator(interval_minutes)
    
    # Process all matched files
    import glob
    matched_files = glob.glob(f"{input_dir}/*_matched.csv")
    
    all_aggregated = []
    
    for file_path in matched_files:
        try:
            probe_df = pd.read_csv(file_path)
            aggregated = aggregator.aggregate_probe_data(probe_df)
            all_aggregated.append(aggregated)
            
            print(f"Aggregated {file_path}: {len(aggregated)} time-road segments")
            
        except Exception as e:
            logging.error(f"Error aggregating {file_path}: {e}")
    
    if all_aggregated:
        # Combine all aggregated data
        combined_df = pd.concat(all_aggregated, ignore_index=True)
        
        # Create complete time series
        complete_series = aggregator.create_time_series(combined_df)
        
        # Save results
        combined_df.to_csv(f"{output_dir}/aggregated_traffic.csv", index=False)
        complete_series.to_csv(f"{output_dir}/time_series_traffic.csv", index=False)
        
        # Calculate and save historical statistics
        stats, monthly_stats = aggregator.calculate_historical_stats(complete_series)
        stats.to_csv(f"{output_dir}/historical_stats.csv", index=False)
        monthly_stats.to_csv(f"{output_dir}/monthly_stats.csv", index=False)
        
        print(f"Aggregation complete: {len(complete_series)} time series records")

if __name__ == "__main__":
    # Example usage
    aggregator = TrafficAggregator()
    
    # Process sample data (would normally come from mapmatch.py output)
    sample_data = pd.DataFrame({
        'road_id': ['road_1'] * 100,
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='1min'),
        'speed': np.random.normal(50, 10, 100),
        'heading': np.random.normal(90, 20, 100),
        'lat': [13.7563] * 100,
        'lon': [100.5018] * 100,
        'match_distance': np.random.uniform(0, 50, 100)
    })
    
    aggregated = aggregator.aggregate_probe_data(sample_data)
    print(f"Sample aggregation: {len(aggregated)} records")
