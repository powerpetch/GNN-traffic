# 🚀 How to Run GNN Traffic Prediction Project

## ⚡ Quick Start (5 minutes)

### Windows Users
```bash
# 1. Double-click setup.bat OR run in PowerShell:
.\setup.bat

# 2. Activate environment
venv\Scripts\activate

# 3. Launch dashboard
streamlit run app/streamlit_app.py
```

### Linux/Mac Users
```bash
# 1. Run setup script
chmod +x setup.sh
./setup.sh

# 2. Activate environment
source venv/bin/activate

# 3. Launch dashboard
streamlit run app/streamlit_app.py
```

### Manual Setup
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate (Windows)
venv\Scripts\activate
# OR Activate (Linux/Mac)
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch dashboard
streamlit run app/streamlit_app.py
```

## 🎯 What You'll See

1. **Browser opens** to `http://localhost:8501`
2. **Interactive dashboard** with Bangkok traffic map
3. **Demo data** showing traffic patterns and predictions
4. **Smart navigation** route comparison tool

## 📊 Project Workflow

### Phase 1: Data Exploration (Start Here!)
```bash
# Launch Jupyter notebooks
jupyter notebook

# Open these notebooks in order:
# 1. data_exploration.ipynb
# 2. traffic_patterns.ipynb  
# 3. model_comparison.ipynb
```

### Phase 2: Data Processing Pipeline
```bash
# Process your real data step by step
python src/ingest.py      # Load PROBE and road data
python src/mapmatch.py    # Match GPS to roads
python src/aggregate.py   # Create time series
python src/features.py    # Engineer features
python src/graph.py       # Build road graph
```

### Phase 3: Model Training
```bash
# Quick test (10 epochs)
python src/train.py --epochs 10 --batch-size 16

# Full training
python src/train.py --config configs/stgcn_config.json

# Custom experiment
python src/train.py \
  --epochs 50 \
  --batch-size 32 \
  --lr 0.001 \
  --output-dir models/my_experiment
```

### Phase 4: Model Evaluation
```bash
# Evaluate trained model
python src/evaluate.py \
  --model models/experiments/[timestamp]/final_model.pth \
  --data-dir data/processed

# Compare models
python src/evaluate.py \
  --compare models/model1.pth models/model2.pth
```

## 🔧 Configuration Options

### Model Types
- `stgcn` - Spatial-Temporal Graph CNN (recommended)
- `temporal_gcn` - GCN + LSTM hybrid
- `simple_gcn` - Basic graph neural network

### Key Parameters
```json
{
  "sequence_length": 12,     # Input window (1 hour)
  "prediction_horizon": 6,   # Forecast ahead (30 min)
  "batch_size": 32,
  "learning_rate": 0.001,
  "num_epochs": 100
}
```

## 📁 Your Data Structure

Your data is already organized in:
```
data/raw/
├── PROBE-202401/          # January 2024 traffic data
├── PROBE-202402/          # February 2024 traffic data
├── ...                    # More months
├── hotosm_tha_roads_lines_geojson/  # Bangkok road network
└── iTIC-Longdo-Traffic-events-2022/ # Traffic incidents
```

## 🎮 Dashboard Features

### Traffic Map
- **Color-coded speeds**: Green (fast) → Red (slow)
- **Real-time updates**: Live traffic simulation
- **Interactive**: Click roads for details

### Predictions
- **15/30/60 minute forecasts**
- **Confidence intervals**
- **Actual vs Predicted comparison**

### Smart Navigation
- **Route comparison**: Shortest vs Smart path
- **Travel time estimates**
- **Fuel cost calculations**

### Analytics
- **Model performance metrics**
- **Traffic pattern analysis**
- **Historical trends**

## 🐛 Common Issues & Solutions

### Installation Issues
```bash
# CUDA not available (use CPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Geopandas install fails (Windows)
conda install geopandas

# Permission denied
# Run terminal as administrator (Windows)
# Use sudo on Linux/Mac
```

### Memory Issues
```bash
# Reduce batch size
python src/train.py --batch-size 8

# Use gradient accumulation
python src/train.py --batch-size 16 --accumulate-grads 2
```

### Data Issues
```bash
# Check data files exist
ls data/raw/PROBE-*/

# Verify CSV format
head data/raw/PROBE-202401/20240101.csv.out
```

## 🎯 Expected Outputs

### Training Results
```
models/experiments/20241201_120000/
├── config.json              # Training configuration
├── final_model.pth          # Trained model weights
├── training_history.json    # Loss curves and metrics
└── logs/training.log        # Detailed training logs
```

### Evaluation Results
```
evaluation_results/
├── evaluation_results.json  # Performance metrics
├── predictions.npy         # Model predictions
├── targets.npy            # Ground truth
└── plots/                 # Visualization charts
    ├── predicted_vs_actual.png
    ├── time_series_samples.png
    └── error_distribution.png
```

### Performance Expectations
- **MAE**: 3-7 km/h (Mean Absolute Error)
- **RMSE**: 5-10 km/h (Root Mean Square Error)  
- **MAPE**: 8-15% (Mean Absolute Percentage Error)
- **R²**: 0.85-0.92 (Correlation coefficient)

## 🎓 Academic Use Cases

### 1. Jupyter Notebook Analysis
```bash
# Create analysis notebook
jupyter notebook notebooks/
# Use provided templates for:
# - Data exploration
# - Model comparison
# - Result visualization
```

### 2. Research Paper Figures
```bash
# Generate publication-ready plots
python src/evaluate.py --model [path] --output-dir paper_figures/
# High-quality PNG/PDF outputs
```

### 3. Conference Demo
```bash
# Live interactive demo
streamlit run app/streamlit_app.py
# Show real-time predictions and routing
```

### 4. Video Creation
```bash
# Export time series animations
# Use dashboard's live simulation mode
# Screen record for video presentations
```

## 🔄 Development Cycle

1. **Start Dashboard**: `streamlit run app/streamlit_app.py`
2. **Explore Data**: Use Jupyter notebooks
3. **Train Models**: Experiment with different configs
4. **Evaluate**: Compare model performance
5. **Iterate**: Refine and improve

## 📞 Getting Help

1. **Check logs**: `models/experiments/[timestamp]/logs/training.log`
2. **Verify installation**: `python test_install.py`
3. **Read error messages**: Most errors have clear solutions
4. **Start simple**: Use demo data first, then real data

---

## 🎉 You're Ready!

Your project is perfectly structured for:
- ✅ **GNN Traffic Forecasting**
- ✅ **Smart Navigation System**  
- ✅ **Interactive Demonstrations**
- ✅ **Academic Presentations**

**Just run `streamlit run app/streamlit_app.py` and start exploring!** 🚗📊
