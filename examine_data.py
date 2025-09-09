#!/usr/bin/env python3
"""
Script to examine the available data for real road names
"""

import json
import pandas as pd
import os

def examine_hotosm_data():
    """Examine HOTOSM road data for real road names"""
    print("=== Examining HOTOSM Road Data ===")
    
    geojson_path = "data/raw/hotosm_tha_roads_lines_geojson/hotosm_tha_roads_lines_geojson.geojson"
    
    if not os.path.exists(geojson_path):
        print(f"File not found: {geojson_path}")
        return None
    
    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Total road features: {len(data['features'])}")
        
        # Sample some features to see what data is available
        sample_features = data['features'][:10]
        
        print("\nSample road data:")
        for i, feature in enumerate(sample_features):
            props = feature['properties']
            print(f"\nRoad {i+1}:")
            print(f"  Name: {props.get('name', 'No name')}")
            print(f"  Name (EN): {props.get('name:en', 'No English name')}")
            print(f"  Name (TH): {props.get('name:th', 'No Thai name')}")
            print(f"  Highway type: {props.get('highway', 'No highway type')}")
            print(f"  Surface: {props.get('surface', 'No surface info')}")
            
        return data
        
    except Exception as e:
        print(f"Error reading GeoJSON: {e}")
        return None

def examine_thailand_location_table():
    """Examine Thailand location table"""
    print("\n=== Examining Thailand Location Table ===")
    
    excel_path = "data/raw/Thailand_T19_v3.2_flat_Thai.xlsx"
    
    if not os.path.exists(excel_path):
        print(f"File not found: {excel_path}")
        return None
    
    try:
        df = pd.read_excel(excel_path)
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"\nFirst 5 rows:")
        print(df.head())
        
        return df
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def examine_itic_traffic_events():
    """Examine iTIC traffic events data"""
    print("\n=== Examining iTIC Traffic Events Data ===")
    
    events_dir = "data/raw/iTIC-Longdo-Traffic-events-2022"
    
    if not os.path.exists(events_dir):
        print(f"Directory not found: {events_dir}")
        return None
    
    # Check what's in the directory
    subdirs = os.listdir(events_dir)
    print(f"Available months: {subdirs}")
    
    # Sample one month
    if subdirs:
        sample_month = subdirs[0]
        sample_path = os.path.join(events_dir, sample_month)
        files = os.listdir(sample_path)
        print(f"\nFiles in {sample_month}: {files[:5]}...")  # Show first 5 files
        
        # Try to read one file
        if files:
            sample_file = os.path.join(sample_path, files[0])
            try:
                if sample_file.endswith('.json'):
                    with open(sample_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"\nSample event data structure:")
                    if isinstance(data, list) and data:
                        print(json.dumps(data[0], indent=2, ensure_ascii=False))
                    elif isinstance(data, dict):
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                else:
                    print(f"File type: {sample_file.split('.')[-1]}")
            except Exception as e:
                print(f"Error reading sample file: {e}")

if __name__ == "__main__":
    hotosm_data = examine_hotosm_data()
    thailand_table = examine_thailand_location_table()
    examine_itic_traffic_events()
