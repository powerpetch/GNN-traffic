"""
Map matching module for aligning probe data to road network.
Uses spatial operations to match GPS coordinates to road segments.
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points
from typing import Tuple, Dict, Optional
import logging

class MapMatcher:
    """Map matching class for aligning probe data to road network."""
    
    def __init__(self, road_network: gpd.GeoDataFrame, max_distance: float = 100.0):
        """
        Initialize map matcher.
        
        Args:
            road_network: GeoDataFrame containing road segments
            max_distance: Maximum distance (meters) for matching
        """
        self.road_network = road_network.to_crs(epsg=3857)  # Web Mercator for distance calc
        self.max_distance = max_distance
        self.logger = logging.getLogger(__name__)
        
        # Create spatial index for efficient matching
        self.road_sindex = self.road_network.sindex
        
    def match_points_to_roads(self, probe_df: pd.DataFrame) -> pd.DataFrame:
        """
        Match probe points to nearest road segments.
        
        Args:
            probe_df: DataFrame with 'lat', 'lon' columns
            
        Returns:
            DataFrame with matched road segment IDs and distances
        """
        # Convert probe points to GeoDataFrame
        geometry = [Point(xy) for xy in zip(probe_df['lon'], probe_df['lat'])]
        probe_gdf = gpd.GeoDataFrame(probe_df, geometry=geometry, crs=4326)
        probe_gdf = probe_gdf.to_crs(epsg=3857)  # Convert to Web Mercator
        
        matched_data = []
        
        for idx, point in probe_gdf.iterrows():
            road_id, distance = self._find_nearest_road(point.geometry)
            matched_data.append({
                'original_index': idx,
                'road_id': road_id,
                'match_distance': distance,
                'matched': distance <= self.max_distance
            })
            
        matched_df = pd.DataFrame(matched_data)
        return probe_df.merge(matched_df, left_index=True, right_on='original_index')
    
    def _find_nearest_road(self, point: Point) -> Tuple[Optional[str], float]:
        """
        Find the nearest road segment to a point.
        
        Args:
            point: Shapely Point geometry
            
        Returns:
            Tuple of (road_id, distance)
        """
        # Use spatial index to find potential candidates
        possible_matches_index = list(self.road_sindex.nearest(point.bounds, 1))
        
        if not possible_matches_index:
            return None, float('inf')
        
        min_distance = float('inf')
        nearest_road_id = None
        
        for idx in possible_matches_index:
            road_geom = self.road_network.iloc[idx].geometry
            distance = point.distance(road_geom)
            
            if distance < min_distance:
                min_distance = distance
                nearest_road_id = self.road_network.iloc[idx].get('osm_id', idx)
                
        return nearest_road_id, min_distance
    
    def clean_matched_data(self, matched_df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and filter matched data.
        
        Args:
            matched_df: DataFrame with matched probe data
            
        Returns:
            Cleaned DataFrame
        """
        # Filter out unmatched points
        cleaned_df = matched_df[matched_df['matched']].copy()
        
        # Remove duplicates and outliers
        cleaned_df = cleaned_df.drop_duplicates(subset=['lat', 'lon', 'timestamp'])
        
        # Add derived features
        cleaned_df['hour'] = pd.to_datetime(cleaned_df['timestamp']).dt.hour
        cleaned_df['day_of_week'] = pd.to_datetime(cleaned_df['timestamp']).dt.dayofweek
        
        self.logger.info(f"Cleaned data: {len(cleaned_df)} points from {len(matched_df)} original")
        
        return cleaned_df

def process_batch(probe_files: list, road_network: gpd.GeoDataFrame, output_dir: str):
    """
    Process a batch of probe files through map matching.
    
    Args:
        probe_files: List of probe data file paths
        road_network: Road network GeoDataFrame
        output_dir: Output directory for processed files
    """
    matcher = MapMatcher(road_network)
    
    for file_path in probe_files:
        try:
            probe_df = pd.read_csv(file_path)
            matched_df = matcher.match_points_to_roads(probe_df)
            cleaned_df = matcher.clean_matched_data(matched_df)
            
            # Save to interim directory
            output_file = f"{output_dir}/{Path(file_path).stem}_matched.csv"
            cleaned_df.to_csv(output_file, index=False)
            
            print(f"Processed {file_path}: {len(cleaned_df)} matched points")
            
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    from ingest import DataIngester
    from pathlib import Path
    
    # Example usage
    ingester = DataIngester()
    road_network = ingester.load_road_network()
    
    # Process sample data
    probe_df = ingester.load_probe_data()
    if not probe_df.empty:
        matcher = MapMatcher(road_network)
        matched_df = matcher.match_points_to_roads(probe_df.head(1000))  # Sample
        cleaned_df = matcher.clean_matched_data(matched_df)
        
        print(f"Map matching complete: {len(cleaned_df)} points matched")
