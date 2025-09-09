# Bangkok GNN Traffic Prediction - Enhanced Version

## 🚀 New Features

### ✅ Real Road Names
- **Authentic Bangkok street names** in both English and Thai
- **HOTOSM OpenStreetMap data** integration for accurate road information
- **Multi-language support** - choose English, Thai, or both

### ✅ Longdo Maps Integration
- **Thailand-specific mapping** with high-quality local data
- **Traffic overlay** from Longdo's real-time data
- **Enhanced navigation** with local road knowledge

### ✅ Enhanced Data Sources
- **iTIC Foundation data** compatibility
- **Historical traffic incidents** from iTIC archives
- **Thailand Location Table** (TIS Standard 2604) support
- **Real traffic patterns** based on Bangkok data

## 🔧 Setup Instructions

### 1. Get Your Longdo Maps API Key

1. Visit [Longdo Maps API](https://map.longdo.com/)
2. Register for a free account
3. Generate your API key
4. Copy the API key for the next step

### 2. Configure API Key

#### Option A: Using Streamlit Secrets (Recommended)
1. Edit `.streamlit/secrets.toml` in your project directory
2. Replace `YOUR_LONGDO_API_KEY_HERE` with your actual API key:
```toml
LONGDO_API_KEY = "your_actual_api_key_here"
```

#### Option B: Using the Web Interface
1. Run the application
2. Enter your API key in the sidebar under "🔑 Longdo Maps API"
3. The key will be used for the current session

### 3. Run the Enhanced Application

```bash
# Navigate to project directory
cd d:\user\Data_project\gnn-traffic

# Run the enhanced version
py -m streamlit run app/streamlit_app_enhanced.py
```

## 📊 Data Sources Integration

### Available Data Sources

1. **HOTOSM Thailand Roads** ✅
   - Location: `data/raw/hotosm_tha_roads_lines_geojson/`
   - Contains: Real Bangkok road names, types, and coordinates
   - Usage: Automatic road name detection

2. **Thailand Location Table** ✅
   - Location: `data/raw/Thailand_T19_v3.2_flat_Thai.xlsx`
   - Contains: Official location referencing (TIS Standard 2604)
   - Usage: Precise location mapping

3. **iTIC Traffic Events** ✅
   - Location: `data/raw/iTIC-Longdo-Traffic-events-2022/`
   - Contains: Historical traffic incidents
   - Usage: Incident pattern analysis

4. **PROBE Traffic Data** ✅
   - Location: `data/raw/PROBE-202401/` through `data/raw/PROBE-202412/`
   - Contains: 13 months of real Bangkok traffic data
   - Usage: Training GNN models

### Recommended Additional Downloads

Based on the iTIC Open Data Archives, consider downloading:

1. **Historical traffic incidents** - CC-BY license
   - Improves incident prediction accuracy
   - Helps understand traffic event patterns

2. **Historical traffic information status of Thailand** - CC-BY license
   - Provides traffic status patterns
   - Enhances prediction models

3. **Historical raw vehicles and mobile probes data in Thailand** - CC-BY license
   - Rich dataset for model training
   - Real vehicle movement patterns

## 🎛️ Application Features

### Road Name Display Options
- **English**: Display road names in English
- **Thai**: Display road names in Thai script
- **Both**: Show both English and Thai names

### Map Options
- **Longdo Maps**: High-quality Thailand-specific mapping (requires API key)
- **Folium Fallback**: OpenStreetMap-based mapping (no API key required)

### Prediction Models
- **ST-GCN (Enhanced)**: Spatio-temporal graph convolution
- **DCRNN (Thai Roads)**: Diffusion convolution RNN optimized for Thai road network
- **Graph WaveNet**: WaveNet architecture for graph data
- **LSTM Baseline**: Traditional LSTM for comparison

### Data Visualization
- **Real-time traffic speeds** with color-coded congestion levels
- **Prediction overlays** with confidence intervals
- **Road type filtering** (motorway, trunk, primary, secondary, tertiary)
- **Multi-language road information**

## 🗺️ Longdo Maps Features

When API key is configured, you get:

1. **High-Quality Thailand Maps**
   - Detailed local road networks
   - Accurate Thai place names
   - Local points of interest

2. **Real-Time Traffic Layer**
   - Live traffic conditions
   - Incident reporting
   - Construction updates

3. **Enhanced Navigation**
   - Local route optimization
   - Thailand-specific routing logic
   - Motorcycle lane awareness

## 🔧 Troubleshooting

### Common Issues

1. **"Please configure your Longdo Maps API key"**
   - Ensure your API key is correctly set in `.streamlit/secrets.toml`
   - Or enter it manually in the sidebar

2. **"Real road data loader not available"**
   - This is normal - the app will use enhanced fallback data
   - The fallback includes real Bangkok road names

3. **Map not loading**
   - Check your internet connection
   - Verify your Longdo API key is valid
   - The app will fallback to Folium maps if needed

### Performance Tips

1. **Limit road data for better performance**
   - The app loads up to 500 roads by default
   - Adjust `max_roads` parameter in code if needed

2. **API rate limits**
   - Longdo Maps has usage limits for free accounts
   - Consider upgrading for high-volume usage

## 📈 Usage Examples

### Viewing Traffic by Road Type
1. Use the "Filter by Road Type" multiselect
2. Choose specific types: motorway, trunk, primary, etc.
3. See filtered results in both map and table

### Prediction Analysis
1. Select a specific road from the prediction dropdown
2. View speed predictions with confidence intervals
3. Analyze how confidence decreases with time horizon

### Multi-Language Road Names
1. Change "Road Name Language" in sidebar
2. See immediate updates in map popups and tables
3. Compare English and Thai road names

## 🛠️ Development

### Adding New Data Sources

To integrate additional iTIC data:

1. Add loader functions in `src/data/real_road_loader.py`
2. Update the data source selection in the main app
3. Add appropriate data processing in the traffic generation functions

### Customizing Road Data

To modify the fallback road data:

1. Edit the `real_roads` list in `load_real_road_network()`
2. Add new roads with proper coordinates and attributes
3. Ensure proper English and Thai names are included

## 📄 License

This project uses open data from:
- **HOTOSM**: OpenStreetMap data under ODbL license
- **iTIC Foundation**: Traffic data under CC-BY license
- **Longdo Maps**: Commercial API (requires registration)

## 🤝 Contributing

To contribute:
1. Add more real Bangkok road data
2. Improve prediction algorithms
3. Enhance Longdo Maps integration
4. Add more iTIC data source integrations
