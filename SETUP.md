# GNN Traffic Prediction Project Setup

## Quick Start Guide

### 1. Python Environment Setup

```bash
# Navigate to project directory
cd gnn-traffic

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Installation

```python
# Test script to verify installation
import torch
import pandas as pd
import numpy as np
import networkx as nx
import geopandas as gpd

print("✅ All core dependencies installed successfully!")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
```

### 3. Data Processing Pipeline

```bash
# Step 1: Data ingestion
python src/ingest.py

# Step 2: Map matching (GPS to roads)
python src/mapmatch.py

# Step 3: Temporal aggregation (5-min intervals)
python src/aggregate.py

# Step 4: Feature engineering
python src/features.py

# Step 5: Graph construction
python src/graph.py
```

### 4. Model Training

```bash
# Quick training with default config
python src/train.py --data-dir data/processed --epochs 10

# Training with specific model
python src/train.py --config configs/stgcn_config.json

# Custom training parameters
python src/train.py \
  --data-dir data/processed \
  --epochs 50 \
  --batch-size 64 \
  --lr 0.001 \
  --output-dir models/my_experiment
```

### 5. Model Evaluation

```bash
# Evaluate trained model
python src/evaluate.py \
  --model models/experiments/[timestamp]/final_model.pth \
  --data-dir data/processed \
  --output-dir evaluation_results

# Compare multiple models
python src/evaluate.py \
  --compare models/model1.pth models/model2.pth \
  --data-dir data/processed
```

### 6. Launch Interactive Dashboard

```bash
# Start Streamlit app
streamlit run app/streamlit_app.py

# App will open at: http://localhost:8501
```

## Project Directory Structure

After setup, your directory should look like:

```
gnn-traffic/
├── data/
│   ├── raw/              # Original data files
│   ├── interim/          # Processed intermediate files
│   └── processed/        # Final model-ready data
├── notebooks/            # Jupyter notebooks
├── src/                  # Source code
├── app/                  # Streamlit dashboard
├── models/              # Saved model checkpoints
├── configs/             # Configuration files
└── evaluation_results/  # Model evaluation outputs
```

## Common Issues and Solutions

### 1. CUDA/GPU Issues
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# If CUDA issues, install CPU-only version:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 2. Geospatial Library Issues
```bash
# On Windows, install via conda if pip fails:
conda install geopandas

# On Linux, install system dependencies:
sudo apt-get install gdal-bin libgdal-dev
pip install GDAL==$(gdal-config --version)
```

### 3. Memory Issues
```bash
# Reduce batch size in config files
# Or use gradient accumulation:
python src/train.py --batch-size 16 --accumulate-grads 2
```

## Development Workflow

### 1. Data Exploration
```bash
# Start Jupyter notebook
jupyter notebook notebooks/

# Key notebooks:
# - 01_data_exploration.ipynb
# - 02_traffic_patterns.ipynb
# - 03_model_comparison.ipynb
```

### 2. Model Development
```bash
# Create new model configuration
cp configs/stgcn_config.json configs/my_model_config.json

# Edit configuration
# Train with new config
python src/train.py --config configs/my_model_config.json
```

### 3. Experiment Tracking
```bash
# Each training run creates timestamped directory:
models/experiments/20241201_120000/
├── config.json
├── final_model.pth
├── checkpoint_epoch_10.pth
├── training_history.json
└── logs/training.log
```

## Performance Optimization

### 1. Data Loading
- Use `num_workers > 0` for faster data loading
- Enable `pin_memory=True` for GPU training
- Preprocess data to reduce runtime overhead

### 2. Model Training
- Use mixed precision training: `--mixed-precision`
- Gradient accumulation for larger effective batch sizes
- Learning rate scheduling for better convergence

### 3. Memory Management
- Reduce sequence length for memory-constrained systems
- Use gradient checkpointing for large models
- Clear CUDA cache between experiments

## Next Steps

1. **Explore the data**: Start with `notebooks/01_data_exploration.ipynb`
2. **Run baseline**: Train a simple model with default settings
3. **Dashboard tour**: Launch Streamlit app and explore features
4. **Custom experiments**: Modify configs and train your own models
5. **Evaluation**: Compare different models and analyze results

## Getting Help

- **Documentation**: Check README.md for detailed information
- **Code comments**: All modules are well-documented
- **Configuration**: Example configs in `configs/` directory
- **Issues**: Create GitHub issues for bugs or questions

---

Happy experimenting with GNN traffic prediction! 🚗📊
