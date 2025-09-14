#!/usr/bin/env python3
"""
🚀 Google Colab Setup Script for GNN Traffic Project
Automatically configures the environment for running in Google Colab
"""

import os
import sys
import subprocess
import urllib.request
from pathlib import Path

class ColabSetup:
    def __init__(self):
        self.in_colab = 'google.colab' in sys.modules
        self.project_root = Path.cwd()
        
    def print_step(self, message, emoji="✅"):
        print(f"{emoji} {message}")
    
    def check_environment(self):
        """Check if running in Colab"""
        if self.in_colab:
            self.print_step("Running in Google Colab", "🔍")
        else:
            self.print_step("Running locally", "🖥️")
        
        # Print system info
        print(f"📂 Working directory: {self.project_root}")
        print(f"🐍 Python version: {sys.version}")
        
    def setup_directories(self):
        """Create necessary directories"""
        self.print_step("Setting up directories...")
        
        directories = [
            "data/raw",
            "data/processed", 
            "data/interim",
            "models/checkpoints",
            "results/figures",
            "logs"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
        self.print_step("Directories created")
    
    def install_packages(self):
        """Install required packages"""
        self.print_step("Installing packages...", "📦")
        
        # Install from requirements
        requirements_file = self.project_root / "requirements_colab.txt"
        if requirements_file.exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                         check=True, capture_output=True)
            self.print_step("Packages installed from requirements")
        else:
            # Install essential packages manually
            essential_packages = [
                "torch>=1.12.0",
                "torch-geometric>=2.1.0", 
                "pandas>=1.4.0",
                "numpy>=1.21.0",
                "matplotlib>=3.5.0",
                "plotly>=5.8.0",
                "networkx>=2.8.0",
                "scikit-learn>=1.1.0"
            ]
            
            for package in essential_packages:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True)
            
            self.print_step("Essential packages installed")
    
    def setup_python_path(self):
        """Add project directories to Python path"""
        self.print_step("Configuring Python path...")
        
        paths_to_add = [
            str(self.project_root),
            str(self.project_root / "src"),
            str(self.project_root / "notebooks")
        ]
        
        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)
        
        self.print_step("Python path configured")
    
    def download_sample_data(self):
        """Download sample data for demonstration"""
        self.print_step("Setting up sample data...", "📊")
        
        data_dir = self.project_root / "data" / "raw"
        
        # Create sample PROBE data
        sample_probe_data = """timestamp,lat,lon,speed,heading,vehicle_id
2024-01-01 08:00:00,13.7563,100.5018,45.2,90,V001
2024-01-01 08:01:00,13.7565,100.5020,42.1,85,V001
2024-01-01 08:02:00,13.7567,100.5022,38.5,80,V001
2024-01-01 08:00:00,13.7460,100.5340,52.3,180,V002
2024-01-01 08:01:00,13.7458,100.5340,48.7,175,V002
2024-01-01 08:02:00,13.7456,100.5340,44.2,170,V002
"""
        
        sample_file = data_dir / "sample_probe_data.csv"
        with open(sample_file, 'w') as f:
            f.write(sample_probe_data)
        
        self.print_step("Sample data created")
    
    def create_config_file(self):
        """Create configuration file for Colab"""
        self.print_step("Creating configuration...", "⚙️")
        
        config_content = """# GNN Traffic Configuration for Google Colab

# Model settings
model:
  type: "stgcn"  # stgcn, dcrnn, graphwavenet
  hidden_channels: 32  # Reduced for Colab
  num_layers: 2  # Reduced for Colab
  dropout: 0.3

# Training settings  
training:
  batch_size: 16  # Reduced for Colab memory
  learning_rate: 0.001
  num_epochs: 10  # Reduced for quick testing
  device: "cuda"  # Will auto-detect in Colab

# Data settings
data:
  sequence_length: 12
  prediction_horizon: 6  # Reduced for faster processing
  sample_size: 1000  # Use sample data in Colab
  
# Paths (relative to project root)
paths:
  data_dir: "data"
  model_dir: "models" 
  results_dir: "results"
"""
        
        config_file = self.project_root / "config_colab.yaml"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        self.print_step("Configuration file created")
    
    def test_imports(self):
        """Test if key imports work"""
        self.print_step("Testing imports...", "🧪")
        
        try:
            import torch
            import torch_geometric
            import pandas as pd
            import numpy as np
            import matplotlib.pyplot as plt
            import networkx as nx
            
            # Check CUDA availability
            if torch.cuda.is_available():
                self.print_step(f"CUDA available: {torch.cuda.get_device_name()}", "🚀")
            else:
                self.print_step("CUDA not available - using CPU", "⚠️")
            
            self.print_step("All imports successful")
            
        except ImportError as e:
            self.print_step(f"Import error: {e}", "❌")
            return False
        
        return True
    
    def run_setup(self):
        """Run complete setup process"""
        print("🚀 GNN Traffic Project - Google Colab Setup")
        print("=" * 50)
        
        try:
            self.check_environment()
            self.setup_directories()
            self.install_packages()
            self.setup_python_path()
            self.download_sample_data()
            self.create_config_file()
            
            if self.test_imports():
                print("\n" + "=" * 50)
                self.print_step("Setup completed successfully!", "🎉")
                print("\n📋 Next steps:")
                print("1. Open any notebook in the notebooks/ directory")
                print("2. Run the cells to start experimenting")
                print("3. Use sample data or upload your own datasets")
                print("\n🎯 Happy modeling in Google Colab!")
            else:
                self.print_step("Setup completed with some issues", "⚠️")
                
        except Exception as e:
            self.print_step(f"Setup failed: {e}", "❌")
            raise

def main():
    """Main setup function"""
    setup = ColabSetup()
    setup.run_setup()

if __name__ == "__main__":
    main()