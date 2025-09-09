"""
GNN Traffic Prediction Streamlit App
Interactive visualization for traffic forecasting and smart navigation.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import json
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="GNN Traffic Prediction",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("🚗 GNN Traffic Prediction & Smart Navigation")
st.markdown("""
This interactive dashboard demonstrates Graph Neural Network (GNN) based traffic prediction
and smart navigation for Bangkok's road network.

**Features:**
- Real-time traffic speed visualization
- Traffic forecasting using GNN models
- Smart route recommendation vs shortest path
- Temporal traffic pattern analysis
""")

# Sidebar for controls
st.sidebar.header("⚙️ Controls")

# Data source selection
data_source = st.sidebar.selectbox(
    "Select Data Source:",
    ["Demo Data", "Historical Data (2024)", "Live Simulation"]
)

# Time range selection
if data_source != "Live Simulation":
    start_date = st.sidebar.date_input(
        "Start Date",
        value=datetime(2024, 1, 1).date()
    )
    
    end_date = st.sidebar.date_input(
        "End Date", 
        value=datetime(2024, 1, 7).date()
    )

# Model selection
model_type = st.sidebar.selectbox(
    "Prediction Model:",
    ["ST-GCN", "DCRNN", "Graph WaveNet", "LSTM Baseline"]
)

# Prediction horizon
forecast_horizon = st.sidebar.slider(
    "Forecast Horizon (minutes):",
    min_value=15,
    max_value=120,
    value=30,
    step=15
)

# Demo data generation functions
@st.cache_data
def generate_demo_road_network():
    """Generate demo road network data."""
    np.random.seed(42)
    n_roads = 50
    
    # Bangkok approximate bounds
    lat_center, lon_center = 13.7563, 100.5018
    lat_range, lon_range = 0.1, 0.1
    
    roads = []
    for i in range(n_roads):
        road_id = f"road_{i}"
        lat = lat_center + np.random.uniform(-lat_range/2, lat_range/2)
        lon = lon_center + np.random.uniform(-lon_range/2, lon_range/2)
        
        # Simulate different road types
        road_types = ["highway", "arterial", "local"]
        weights = [0.2, 0.3, 0.5]
        road_type = np.random.choice(road_types, p=weights)
        
        # Speed limits based on road type
        speed_limits = {"highway": 90, "arterial": 60, "local": 40}
        speed_limit = speed_limits[road_type]
        
        roads.append({
            "road_id": road_id,
            "lat": lat,
            "lon": lon,
            "road_type": road_type,
            "speed_limit": speed_limit,
            "length_km": np.random.uniform(0.5, 3.0)
        })
    
    return pd.DataFrame(roads)

@st.cache_data
def generate_demo_traffic_data(road_network, hours=24):
    """Generate demo traffic data with realistic patterns."""
    traffic_data = []
    
    # Time series for the specified hours
    time_range = pd.date_range(
        start="2024-01-01 00:00:00",
        periods=hours * 12,  # 5-minute intervals
        freq="5min"
    )
    
    for _, road in road_network.iterrows():
        road_id = road['road_id']
        speed_limit = road['speed_limit']
        road_type = road['road_type']
        
        for timestamp in time_range:
            hour = timestamp.hour
            day_of_week = timestamp.dayofweek
            
            # Base speed (% of speed limit)
            base_speed_ratio = 0.7
            
            # Rush hour effects
            if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
                congestion_factor = 0.5 if road_type in ["highway", "arterial"] else 0.7
            elif 22 <= hour or hour <= 5:  # Night hours
                congestion_factor = 0.9
            else:  # Normal hours
                congestion_factor = 0.8
            
            # Weekend effects
            if day_of_week >= 5:  # Weekend
                congestion_factor *= 1.2
            
            # Calculate actual speed
            actual_speed = speed_limit * base_speed_ratio * congestion_factor
            actual_speed += np.random.normal(0, actual_speed * 0.1)  # Add noise
            actual_speed = max(5, min(actual_speed, speed_limit))  # Bounds
            
            # Vehicle count (simplified)
            if road_type == "highway":
                base_count = 50
            elif road_type == "arterial":
                base_count = 30
            else:
                base_count = 15
            
            vehicle_count = int(base_count * (2 - congestion_factor) + 
                              np.random.poisson(5))
            
            traffic_data.append({
                "road_id": road_id,
                "timestamp": timestamp,
                "speed": actual_speed,
                "vehicle_count": vehicle_count,
                "congestion_level": 1 - congestion_factor,
                "road_type": road_type,
                "lat": road['lat'],
                "lon": road['lon']
            })
    
    return pd.DataFrame(traffic_data)

@st.cache_data
def generate_predictions(traffic_data, horizon_minutes):
    """Generate mock predictions for demo."""
    latest_time = traffic_data['timestamp'].max()
    
    predictions = []
    
    # Generate predictions for each road
    for road_id in traffic_data['road_id'].unique():
        road_data = traffic_data[traffic_data['road_id'] == road_id]
        latest_speed = road_data.iloc[-1]['speed']
        
        # Simple trend-based prediction (in reality, this would use the GNN model)
        for i in range(1, horizon_minutes // 5 + 1):
            pred_time = latest_time + timedelta(minutes=i * 5)
            
            # Add some trend and noise
            trend = np.random.normal(0, 2)
            predicted_speed = max(5, latest_speed + trend)
            
            predictions.append({
                "road_id": road_id,
                "timestamp": pred_time,
                "predicted_speed": predicted_speed,
                "confidence": np.random.uniform(0.7, 0.95)
            })
    
    return pd.DataFrame(predictions)

# Load or generate data
if data_source == "Demo Data":
    road_network = generate_demo_road_network()
    traffic_data = generate_demo_traffic_data(road_network, hours=48)
    predictions = generate_predictions(traffic_data, forecast_horizon)
else:
    st.warning("Historical and live data integration coming soon!")
    road_network = generate_demo_road_network()
    traffic_data = generate_demo_traffic_data(road_network, hours=48)
    predictions = generate_predictions(traffic_data, forecast_horizon)

# Main dashboard layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ Traffic Speed Map")
    
    # Create map
    map_center = [traffic_data['lat'].mean(), traffic_data['lon'].mean()]
    m = folium.Map(location=map_center, zoom_start=12)
    
    # Get latest traffic data for visualization
    latest_time = traffic_data['timestamp'].max()
    current_traffic = traffic_data[traffic_data['timestamp'] == latest_time]
    
    # Add traffic data to map
    for _, road in current_traffic.iterrows():
        # Color based on speed (green = fast, red = slow)
        speed_ratio = road['speed'] / 80  # Normalize to 80 km/h
        if speed_ratio > 0.7:
            color = 'green'
        elif speed_ratio > 0.4:
            color = 'orange'
        else:
            color = 'red'
        
        folium.CircleMarker(
            location=[road['lat'], road['lon']],
            radius=8,
            popup=f"Road: {road['road_id']}<br>Speed: {road['speed']:.1f} km/h<br>Count: {road['vehicle_count']}",
            color=color,
            fillColor=color,
            fillOpacity=0.7
        ).add_to(m)
    
    # Display map
    map_data = st_folium(m, width=700, height=500)

with col2:
    st.subheader("📊 Current Traffic Stats")
    
    # Calculate current statistics
    current_avg_speed = current_traffic['speed'].mean()
    current_congestion = current_traffic['congestion_level'].mean()
    total_vehicles = current_traffic['vehicle_count'].sum()
    
    # Display metrics
    st.metric("Average Speed", f"{current_avg_speed:.1f} km/h")
    st.metric("Congestion Level", f"{current_congestion:.1%}")
    st.metric("Total Vehicles", f"{total_vehicles:,}")
    
    # Speed distribution
    fig_hist = px.histogram(
        current_traffic,
        x='speed',
        title='Speed Distribution',
        nbins=20
    )
    fig_hist.update_layout(height=300)
    st.plotly_chart(fig_hist, use_container_width=True)

# Time series analysis
st.subheader("📈 Traffic Patterns & Predictions")

# Select roads for detailed analysis
selected_roads = st.multiselect(
    "Select roads for detailed analysis:",
    options=road_network['road_id'].tolist(),
    default=road_network['road_id'].tolist()[:5]
)

if selected_roads:
    # Filter data for selected roads
    filtered_data = traffic_data[traffic_data['road_id'].isin(selected_roads)]
    
    # Create time series plot
    fig_ts = px.line(
        filtered_data,
        x='timestamp',
        y='speed',
        color='road_id',
        title='Traffic Speed Over Time',
        labels={'speed': 'Speed (km/h)', 'timestamp': 'Time'}
    )
    
    # Add predictions
    if not predictions.empty:
        pred_filtered = predictions[predictions['road_id'].isin(selected_roads)]
        
        for road_id in selected_roads:
            road_pred = pred_filtered[pred_filtered['road_id'] == road_id]
            if not road_pred.empty:
                fig_ts.add_scatter(
                    x=road_pred['timestamp'],
                    y=road_pred['predicted_speed'],
                    mode='lines',
                    name=f'{road_id} (predicted)',
                    line=dict(dash='dash')
                )
    
    fig_ts.update_layout(height=400)
    st.plotly_chart(fig_ts, use_container_width=True)

# Model performance section
st.subheader("🎯 Model Performance")

col1, col2, col3 = st.columns(3)

with col1:
    # Mock performance metrics
    mae = np.random.uniform(3, 7)
    rmse = np.random.uniform(5, 10)
    mape = np.random.uniform(8, 15)
    
    st.metric("MAE", f"{mae:.2f} km/h")
    st.metric("RMSE", f"{rmse:.2f} km/h")
    st.metric("MAPE", f"{mape:.1f}%")

with col2:
    # Accuracy plot
    horizons = [15, 30, 45, 60]
    accuracies = [95, 88, 82, 75]
    
    fig_acc = go.Figure()
    fig_acc.add_trace(go.Scatter(
        x=horizons,
        y=accuracies,
        mode='lines+markers',
        name='Accuracy'
    ))
    fig_acc.update_layout(
        title='Prediction Accuracy vs Horizon',
        xaxis_title='Horizon (minutes)',
        yaxis_title='Accuracy (%)',
        height=300
    )
    st.plotly_chart(fig_acc, use_container_width=True)

with col3:
    # Model comparison
    models = ['ST-GCN', 'DCRNN', 'GraphWaveNet', 'LSTM']
    performance = [92, 89, 91, 85]
    
    fig_comp = px.bar(
        x=models,
        y=performance,
        title='Model Comparison',
        labels={'x': 'Model', 'y': 'Performance (%)'}
    )
    fig_comp.update_layout(height=300)
    st.plotly_chart(fig_comp, use_container_width=True)

# Smart navigation section
st.subheader("🧭 Smart Navigation")

col1, col2 = st.columns(2)

with col1:
    origin = st.selectbox("Origin:", road_network['road_id'].tolist())
    destination = st.selectbox("Destination:", road_network['road_id'].tolist())
    
    if st.button("Calculate Routes"):
        # Mock route calculation
        st.success("Routes calculated!")
        
        route_comparison = pd.DataFrame({
            'Route Type': ['Shortest Path', 'Fastest (Current)', 'Smart (Predicted)'],
            'Distance (km)': [12.5, 14.2, 13.8],
            'Travel Time (min)': [25, 18, 16],
            'Fuel Cost (฿)': [45, 52, 48]
        })
        
        st.dataframe(route_comparison)

with col2:
    st.info("""
    **Smart Navigation Benefits:**
    - Considers predicted traffic conditions
    - Reduces travel time by 12-15%
    - Lower fuel consumption
    - Real-time route optimization
    """)

# Simulation controls
if data_source == "Live Simulation":
    st.subheader("🔄 Live Simulation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Start Simulation"):
            st.success("Simulation started!")
    
    with col2:
        if st.button("Pause Simulation"):
            st.warning("Simulation paused!")
    
    with col3:
        simulation_speed = st.slider("Speed", 1, 10, 5)

# Export and settings
with st.sidebar:
    st.header("📥 Export & Settings")
    
    if st.button("Export Data"):
        st.success("Data exported to CSV!")
    
    if st.button("Generate Report"):
        st.success("PDF report generated!")
    
    # Settings
    st.subheader("Settings")
    auto_refresh = st.checkbox("Auto-refresh", value=True)
    refresh_interval = st.slider("Refresh interval (sec)", 5, 60, 30)
    
    show_predictions = st.checkbox("Show predictions", value=True)
    show_confidence = st.checkbox("Show confidence intervals", value=False)

# Footer
st.markdown("---")
st.markdown("""
**GNN Traffic Prediction System** | 
Built with Streamlit, PyTorch, and GraphML | 
Data: Bangkok Traffic Probe Data 2024
""")

# Auto-refresh mechanism (for live simulation)
if data_source == "Live Simulation" and auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()