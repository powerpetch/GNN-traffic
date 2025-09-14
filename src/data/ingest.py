"""
Data ingestion module for GNN Traffic project.
Handles loading and initial processing of probe data, traffic incidents, and road network data.
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
import logging
from typing import Dict, List, Optional

class DataIngester:
    """Data ingestion class for handling various traffic data sources."""
    
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
        
    def load_probe_data(self, date_range: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Load probe data from CSV files.
        
        Args:
            date_range: List of dates in YYYYMMDD format to load
            
        Returns:
            Combined DataFrame with probe data
        """
        probe_dirs = list(self.data_dir.glob("PROBE-*"))
        all_data = []
        
        for probe_dir in probe_dirs:
            csv_files = list(probe_dir.glob("*.csv.out"))
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file)
                    df['date'] = csv_file.stem.split('.')[0]
                    all_data.append(df)
                except Exception as e:
                    self.logger.warning(f"Error loading {csv_file}: {e}")
                    
        return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
    
    def load_road_network(self) -> gpd.GeoDataFrame:
        """
        Load road network data from HOTOSM files.
        
        Returns:
            GeoDataFrame with road network
        """
        # Try to load from GeoPackage first, then GeoJSON
        gpkg_path = self.data_dir / "hotosm_tha_roads_lines_gpkg"
        geojson_path = self.data_dir / "hotosm_tha_roads_lines_geojson"
        
        if gpkg_path.exists():
            gpkg_files = list(gpkg_path.glob("*.gpkg"))
            if gpkg_files:
                return gpd.read_file(gpkg_files[0])
        
        if geojson_path.exists():
            geojson_files = list(geojson_path.glob("*.geojson"))
            if geojson_files:
                return gpd.read_file(geojson_files[0])
                
        raise FileNotFoundError("No road network data found")
    
    def load_traffic_incidents(self) -> pd.DataFrame:
        """
        Load traffic incident data from iTIC-Longdo files.
        
        Returns:
            DataFrame with traffic incidents
        """
        incident_dir = self.data_dir / "iTIC-Longdo-Traffic-events-2022"
        all_incidents = []
        
        for month_dir in incident_dir.glob("*"):
            if month_dir.is_dir():
                for file in month_dir.glob("*.csv"):
                    try:
                        df = pd.read_csv(file)
                        df['month'] = month_dir.name
                        all_incidents.append(df)
                    except Exception as e:
                        self.logger.warning(f"Error loading {file}: {e}")
                        
        return pd.concat(all_incidents, ignore_index=True) if all_incidents else pd.DataFrame()

if __name__ == "__main__":
    ingester = DataIngester()
    
    # Example usage
    print("Loading probe data...")
    probe_df = ingester.load_probe_data()
    print(f"Loaded {len(probe_df)} probe records")
    
    print("Loading road network...")
    roads_gdf = ingester.load_road_network()
    print(f"Loaded {len(roads_gdf)} road segments")
    
    print("Loading traffic incidents...")
    incidents_df = ingester.load_traffic_incidents()
    print(f"Loaded {len(incidents_df)} incident records")
