# 🔧 Manual Migration Guide for Windows

## Step-by-Step Migration Process

### 1. 📦 Create Backup First
```powershell
# Navigate to your project
cd "d:\user\Data_project\gnn-traffic"

# Create backup directory
mkdir backup_old_structure

# Backup current structure
Copy-Item -Path "src" -Destination "backup_old_structure\src" -Recurse
Copy-Item -Path "app" -Destination "backup_old_structure\app" -Recurse
Copy-Item -Path "configs" -Destination "backup_old_structure\configs" -Recurse -ErrorAction SilentlyContinue
Copy-Item -Path "notebooks" -Destination "backup_old_structure\notebooks" -Recurse -ErrorAction SilentlyContinue
```

### 2. 🏗️ Create New Directory Structure
```powershell
# Configuration
mkdir configs

# Source code organization
mkdir src\data, src\graphs, src\models\layers, src\models\baselines, src\training, src\evaluation, src\deployment, src\utils

# Applications
mkdir apps\streamlit_app\pages, apps\streamlit_app\components, apps\streamlit_app\assets\css, apps\streamlit_app\assets\images
mkdir apps\api_server\routes, apps\api_server\middleware, apps\api_server\schemas
mkdir apps\cli\commands

# Notebooks
mkdir notebooks\exploratory, notebooks\experiments, notebooks\colab, notebooks\tutorials

# Testing
mkdir tests\test_data, tests\test_models, tests\test_training, tests\test_utils

# Scripts
mkdir scripts\setup, scripts\preprocessing, scripts\training, scripts\evaluation, scripts\deployment

# Deployment
mkdir deployment\docker, deployment\kubernetes, deployment\aws, deployment\heroku

# Documentation
mkdir docs, papers, presentations

# Models and results
mkdir models\checkpoints\stgcn, models\checkpoints\dcrnn, models\checkpoints\graphwavenet, models\artifacts, models\experiments

# Results
mkdir results\figures\model_performance, results\figures\data_analysis, results\figures\predictions, results\reports
mkdir results\logs\training_logs, results\logs\evaluation_logs, results\logs\api_logs

# Environment
mkdir environments, requirements
```

### 3. 🚚 Migrate Existing Files

#### Move Streamlit App
```powershell
Copy-Item -Path "app\streamlit_app.py" -Destination "apps\streamlit_app\main.py"
```

#### Move Source Files
```powershell
# Training and evaluation scripts
Copy-Item -Path "src\train.py" -Destination "scripts\training\train.py"
Copy-Item -Path "src\evaluate.py" -Destination "scripts\evaluation\evaluate.py"

# Data processing files
Copy-Item -Path "src\datasets.py" -Destination "src\training\dataset.py"
Copy-Item -Path "src\aggregate.py" -Destination "src\data\preprocessing.py"

# Check if these files exist and move them
if (Test-Path "src\features.py") { Copy-Item -Path "src\features.py" -Destination "src\data\feature_engineering.py" }
if (Test-Path "src\graph.py") { Copy-Item -Path "src\graph.py" -Destination "src\graphs\road_network.py" }
if (Test-Path "src\ingest.py") { Copy-Item -Path "src\ingest.py" -Destination "src\data\ingestion.py" }
if (Test-Path "src\mapmatch.py") { Copy-Item -Path "src\mapmatch.py" -Destination "src\data\map_matching.py" }
```

#### Move Notebooks
```powershell
if (Test-Path "notebooks") {
    Copy-Item -Path "notebooks\*" -Destination "notebooks\exploratory\" -Recurse
}
```

### 4. 📝 Create Configuration Files

#### Model Configuration (configs\model_config.yaml)
```yaml
# Model Configuration
models:
  stgcn:
    hidden_channels: 64
    num_layers: 4
    dropout: 0.3
    
  dcrnn:
    hidden_size: 64
    num_layers: 2
    dropout: 0.3
    
  graphwavenet:
    residual_channels: 32
    dilation_channels: 32
    skip_channels: 256
    end_channels: 512
    
# Common settings
common:
  device: "cuda"
  random_seed: 42
  num_workers: 4
```

#### Training Configuration (configs\training_config.yaml)
```yaml
# Training Configuration
training:
  batch_size: 32
  learning_rate: 0.001
  num_epochs: 200
  early_stopping_patience: 20
  
optimizer:
  type: "adam"
  weight_decay: 1e-4
  
scheduler:
  type: "step"
  step_size: 50
  gamma: 0.5
  
loss:
  type: "mse"
  weights:
    mse: 1.0
    mae: 0.5
    mape: 0.3
```

#### Data Configuration (configs\data_config.yaml)
```yaml
# Data Configuration
data:
  sequence_length: 12
  prediction_horizon: 12
  train_ratio: 0.7
  val_ratio: 0.15
  test_ratio: 0.15
  
paths:
  raw_data: "data/raw"
  processed_data: "data/processed" 
  probe_data: "data/raw/PROBE-*"
  road_network: "data/raw/hotosm_tha_roads_lines_geojson"
  
preprocessing:
  min_speed: 5.0
  max_speed: 120.0
  outlier_threshold: 3.0
```

### 5. 📦 Create Requirements Files

#### Base Requirements (requirements\base.txt)
```
# Core dependencies
torch>=1.12.0
torch-geometric>=2.1.0
numpy>=1.21.0
pandas>=1.4.0
scikit-learn>=1.1.0
scipy>=1.8.0

# Data processing
geopandas>=0.11.0
networkx>=2.8.0
pyproj>=3.3.0

# Visualization
matplotlib>=3.5.0
plotly>=5.8.0
seaborn>=0.11.0

# Configuration
pyyaml>=6.0
python-dotenv>=0.19.0
```

#### Development Requirements (requirements\dev.txt)
```
# Development tools
pytest>=7.0.0
pytest-cov>=3.0.0
black>=22.0.0
flake8>=4.0.0
mypy>=0.910
jupyter>=1.0.0
ipykernel>=6.0.0

# Documentation
sphinx>=4.5.0
sphinx-rtd-theme>=1.0.0
```

#### Colab Requirements (requirements\colab.txt)
```
# Google Colab optimized
torch>=1.12.0
torch-geometric>=2.1.0
numpy>=1.21.0
pandas>=1.4.0
matplotlib>=3.5.0
plotly>=5.8.0
geopandas>=0.11.0
networkx>=2.8.0
```

### 6. 🐍 Create __init__.py Files

Create empty `__init__.py` files in all Python package directories:
```powershell
# Main packages
New-Item -Path "src\__init__.py" -ItemType File -Force
New-Item -Path "src\models\__init__.py" -ItemType File -Force
New-Item -Path "src\data\__init__.py" -ItemType File -Force
New-Item -Path "src\training\__init__.py" -ItemType File -Force
New-Item -Path "src\evaluation\__init__.py" -ItemType File -Force
New-Item -Path "tests\__init__.py" -ItemType File -Force
New-Item -Path "apps\__init__.py" -ItemType File -Force
```

### 7. 🔧 Update Import Statements

After migration, you'll need to update import statements in your Python files:

#### Before:
```python
from models.stgcn import STGCNModel
from datasets import TrafficDataset
```

#### After:
```python
from src.models.stgcn import STGCNModel
from src.training.dataset import TrafficDataset
```

### 8. ✅ Verification Steps

1. **Test the structure:**
   ```powershell
   python -c "import src.models; print('Models package working')"
   ```

2. **Run a simple test:**
   ```powershell
   cd scripts\training
   python train.py --help
   ```

3. **Check Streamlit app:**
   ```powershell
   cd apps\streamlit_app
   streamlit run main.py
   ```

### 9. 🧹 Cleanup (Only after verification)

```powershell
# Remove old directories (ONLY after confirming everything works)
Remove-Item -Path "backup_old_structure" -Recurse -Force
```

## 🎯 Benefits of New Structure

- **Separation of Concerns**: Clear separation between data processing, models, applications
- **Scalability**: Easy to add new models, applications, or experiments
- **Testing**: Dedicated test structure for better coverage
- **Deployment**: Organized deployment configurations
- **Documentation**: Centralized documentation and papers
- **Google Colab**: Simplified structure for Colab notebooks

## 📋 Next Steps

1. Update all import statements in Python files
2. Create proper model implementations in `src/models/`
3. Set up CI/CD pipelines using the new structure
4. Create Colab notebooks in `notebooks/colab/`
5. Add comprehensive tests in `tests/`
