#!/usr/bin/env python3
"""
🔧 Project Structure Migration Script
Reorganizes the GNN Traffic project according to best practices
"""

import os
import shutil
from pathlib import Path

class ProjectReorganizer:
    def __init__(self, project_root):
        self.root = Path(project_root)
        self.backup_dir = self.root / "backup_old_structure"
        
    def create_backup(self):
        """Create backup of current structure"""
        print("📦 Creating backup of current structure...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # Backup key directories
        backup_items = ['src', 'app', 'configs', 'notebooks']
        
        for item in backup_items:
            src_path = self.root / item
            if src_path.exists():
                dst_path = self.backup_dir / item
                shutil.copytree(src_path, dst_path)
                print(f"  ✅ Backed up {item}/")
    
    def create_new_structure(self):
        """Create new directory structure"""
        print("\n🏗️ Creating new directory structure...")
        
        # Define new structure
        directories = [
            # Configuration
            "configs",
            
            # Source code organization
            "src/data",
            "src/graphs", 
            "src/models/layers",
            "src/models/baselines",
            "src/training",
            "src/evaluation",
            "src/deployment",
            "src/utils",
            
            # Applications
            "apps/streamlit_app/pages",
            "apps/streamlit_app/components",
            "apps/streamlit_app/assets/css",
            "apps/streamlit_app/assets/images",
            "apps/api_server/routes",
            "apps/api_server/middleware",
            "apps/api_server/schemas",
            "apps/cli/commands",
            
            # Notebooks organization
            "notebooks/exploratory",
            "notebooks/experiments", 
            "notebooks/colab",
            "notebooks/tutorials",
            
            # Testing
            "tests/test_data",
            "tests/test_models",
            "tests/test_training",
            "tests/test_utils",
            
            # Scripts
            "scripts/setup",
            "scripts/preprocessing",
            "scripts/training",
            "scripts/evaluation",
            "scripts/deployment",
            
            # Deployment
            "deployment/docker",
            "deployment/kubernetes",
            "deployment/aws",
            "deployment/heroku",
            
            # Documentation
            "docs",
            "papers",
            "presentations",
            
            # Models and results
            "models/checkpoints/stgcn",
            "models/checkpoints/dcrnn", 
            "models/checkpoints/graphwavenet",
            "models/artifacts",
            "models/experiments",
            
            # Results
            "results/figures/model_performance",
            "results/figures/data_analysis",
            "results/figures/predictions",
            "results/reports",
            "results/logs/training_logs",
            "results/logs/evaluation_logs",
            "results/logs/api_logs",
            
            # Environment
            "environments",
            "requirements"
        ]
        
        # Create directories
        for directory in directories:
            dir_path = self.root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py for Python packages
            if any(part in directory for part in ['src/', 'apps/', 'tests/']):
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    init_file.touch()
            
            print(f"  📁 Created {directory}/")
    
    def migrate_existing_files(self):
        """Migrate existing files to new structure"""
        print("\n🚚 Migrating existing files...")
        
        # File migration mapping
        migrations = [
            # Current app/ -> new apps/streamlit_app/
            ("app/streamlit_app.py", "apps/streamlit_app/main.py"),
            
            # Current src/ files
            ("src/train.py", "scripts/training/train.py"),
            ("src/evaluate.py", "scripts/evaluation/evaluate.py"),
            ("src/datasets.py", "src/training/dataset.py"),
            ("src/features.py", "src/data/feature_engineering.py"),
            ("src/graph.py", "src/graphs/road_network.py"),
            ("src/ingest.py", "src/data/ingestion.py"),
            ("src/mapmatch.py", "src/data/map_matching.py"),
            ("src/aggregate.py", "src/data/preprocessing.py"),
            
            # Configuration files
            ("configs", "configs"),  # Keep existing if good
            
            # Notebooks
            ("notebooks", "notebooks/exploratory"),  # Move existing to exploratory
        ]
        
        for src, dst in migrations:
            src_path = self.root / src
            dst_path = self.root / dst
            
            if src_path.exists():
                # Create destination directory if needed
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                
                if src_path.is_file():
                    shutil.copy2(src_path, dst_path)
                    print(f"  📄 Moved {src} → {dst}")
                elif src_path.is_dir():
                    if dst_path.exists():
                        shutil.rmtree(dst_path)
                    shutil.copytree(src_path, dst_path)
                    print(f"  📁 Moved {src}/ → {dst}/")
    
    def create_config_files(self):
        """Create configuration files"""
        print("\n⚙️ Creating configuration files...")
        
        # Model configuration
        model_config = """# Model Configuration
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
"""
        
        # Training configuration  
        training_config = """# Training Configuration
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
"""
        
        # Data configuration
        data_config = """# Data Configuration
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
"""
        
        configs = [
            ("configs/model_config.yaml", model_config),
            ("configs/training_config.yaml", training_config),
            ("configs/data_config.yaml", data_config)
        ]
        
        for path, content in configs:
            file_path = self.root / path
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"  📝 Created {path}")
    
    def create_requirements_files(self):
        """Create detailed requirements files"""
        print("\n📦 Creating requirements files...")
        
        # Base requirements
        base_reqs = """# Core dependencies
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
"""
        
        # Development requirements
        dev_reqs = """# Development tools
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
"""
        
        # Production requirements
        prod_reqs = """# Production dependencies
fastapi>=0.75.0
uvicorn>=0.17.0
streamlit>=1.8.0
redis>=4.2.0
celery>=5.2.0

# Monitoring
prometheus-client>=0.14.0
"""
        
        # Colab requirements
        colab_reqs = """# Google Colab optimized
torch>=1.12.0
torch-geometric>=2.1.0
numpy>=1.21.0
pandas>=1.4.0
matplotlib>=3.5.0
plotly>=5.8.0
geopandas>=0.11.0
networkx>=2.8.0
"""
        
        requirements = [
            ("requirements/base.txt", base_reqs),
            ("requirements/dev.txt", dev_reqs), 
            ("requirements/prod.txt", prod_reqs),
            ("requirements/colab.txt", colab_reqs)
        ]
        
        for path, content in requirements:
            file_path = self.root / path
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"  📄 Created {path}")
    
    def create_init_files(self):
        """Create __init__.py files for Python packages"""
        print("\n🐍 Creating __init__.py files...")
        
        # Main package init
        main_init = '''"""
GNN Traffic Prediction System
Bangkok Traffic Prediction using Graph Neural Networks
"""

__version__ = "1.0.0"
__author__ = "GNN Traffic Team"
__email__ = "contact@gnn-traffic.com"

from .src import models, data, training, evaluation
'''
        
        # Models package init
        models_init = '''"""
GNN Models Package
Contains ST-GCN, DCRNN, and GraphWaveNet implementations
"""

from .stgcn import STGCNModel
from .dcrnn import DCRNNModel  
from .graphwavenet import GraphWaveNet

__all__ = ["STGCNModel", "DCRNNModel", "GraphWaveNet"]
'''
        
        init_files = [
            ("src/__init__.py", '"""GNN Traffic Source Package"""'),
            ("src/models/__init__.py", models_init),
            ("src/data/__init__.py", '"""Data Processing Package"""'),
            ("src/training/__init__.py", '"""Training Package"""'),
            ("src/evaluation/__init__.py", '"""Evaluation Package"""'),
            ("tests/__init__.py", '"""Test Package"""'),
            ("apps/__init__.py", '"""Applications Package"""'),
        ]
        
        for path, content in init_files:
            file_path = self.root / path
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"  🐍 Created {path}")
    
    def update_gitignore(self):
        """Update .gitignore for new structure"""
        print("\n🙈 Updating .gitignore...")
        
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Data files
data/raw/
data/interim/
*.csv
*.parquet
*.h5

# Model files
models/checkpoints/
models/artifacts/*.pth
models/artifacts/*.pkl
*.ckpt

# Logs
results/logs/
*.log

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Jupyter
.ipynb_checkpoints/

# Backup
backup_old_structure/

# Temporary
tmp/
temp/
"""
        
        gitignore_path = self.root / ".gitignore"
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        print("  ✅ Updated .gitignore")
    
    def create_setup_py(self):
        """Create setup.py for package installation"""
        print("\n📦 Creating setup.py...")
        
        setup_content = '''"""
Setup script for GNN Traffic Prediction System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements/base.txt", "r") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gnn-traffic",
    version="1.0.0",
    author="GNN Traffic Team",
    author_email="contact@gnn-traffic.com",
    description="Bangkok Traffic Prediction using Graph Neural Networks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/powerpetch/GNN-traffic",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest", "black", "flake8", "mypy"],
        "docs": ["sphinx", "sphinx-rtd-theme"],
    },
    entry_points={
        "console_scripts": [
            "gnn-traffic=apps.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
'''
        
        setup_path = self.root / "setup.py"
        with open(setup_path, 'w') as f:
            f.write(setup_content)
        print("  ✅ Created setup.py")
    
    def run_migration(self):
        """Run complete migration process"""
        print("🚀 Starting GNN Traffic Project Reorganization")
        print("=" * 50)
        
        try:
            self.create_backup()
            self.create_new_structure() 
            self.migrate_existing_files()
            self.create_config_files()
            self.create_requirements_files()
            self.create_init_files()
            self.update_gitignore()
            self.create_setup_py()
            
            print("\n" + "=" * 50)
            print("✅ Project reorganization completed successfully!")
            print("\n📋 Next steps:")
            print("1. Review migrated files in new locations")
            print("2. Update import statements in Python files")
            print("3. Test the new structure")
            print("4. Remove backup if everything works")
            print("\n🎯 New structure documented in PROJECT_STRUCTURE.md")
            
        except Exception as e:
            print(f"\n❌ Error during migration: {e}")
            print("💡 Check backup_old_structure/ to restore if needed")

if __name__ == "__main__":
    # Get project root (assume script is in project root)
    project_root = Path(__file__).parent
    
    reorganizer = ProjectReorganizer(project_root)
    reorganizer.run_migration()
