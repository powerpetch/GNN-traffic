"""
Installation Test Script
Run this to verify your environment is set up correctly.
"""

def test_imports():
    """Test if all required packages can be imported."""
    print("🔍 Testing package imports...")
    
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
    except ImportError:
        print("❌ PyTorch not installed")
        return False
    
    try:
        import pandas as pd
        print(f"✅ Pandas: {pd.__version__}")
    except ImportError:
        print("❌ Pandas not installed")
        return False
    
    try:
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
    except ImportError:
        print("❌ NumPy not installed")
        return False
    
    try:
        import streamlit as st
        print(f"✅ Streamlit: {st.__version__}")
    except ImportError:
        print("❌ Streamlit not installed")
        return False
    
    try:
        import plotly
        print(f"✅ Plotly: {plotly.__version__}")
    except ImportError:
        print("❌ Plotly not installed")
        return False
    
    optional_packages = {
        'geopandas': 'Geographic data processing',
        'networkx': 'Graph analysis',
        'folium': 'Interactive maps',
        'sklearn': 'Machine learning metrics'
    }
    
    print("\n🔍 Testing optional packages...")
    for package, description in optional_packages.items():
        try:
            __import__(package)
            print(f"✅ {package}: {description}")
        except ImportError:
            print(f"⚠️  {package}: Not installed ({description})")
    
    return True

def test_data_structure():
    """Test if data directories exist."""
    print("\n🔍 Testing data structure...")
    
    from pathlib import Path
    
    required_dirs = [
        'data/raw',
        'data/interim', 
        'data/processed',
        'src',
        'app',
        'models',
        'notebooks'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ (missing)")
            all_exist = False
    
    return all_exist

def test_data_files():
    """Test if sample data files exist."""
    print("\n🔍 Testing data files...")
    
    from pathlib import Path
    
    data_dir = Path('data/raw')
    if not data_dir.exists():
        print("❌ data/raw directory not found")
        return False
    
    # Check for PROBE data
    probe_dirs = list(data_dir.glob('PROBE-*'))
    if probe_dirs:
        print(f"✅ Found {len(probe_dirs)} PROBE data directories")
        
        # Check for CSV files in first PROBE directory
        sample_dir = probe_dirs[0]
        csv_files = list(sample_dir.glob('*.csv.out'))
        if csv_files:
            print(f"✅ Found {len(csv_files)} CSV files in {sample_dir.name}")
        else:
            print(f"⚠️  No CSV files found in {sample_dir.name}")
    else:
        print("⚠️  No PROBE data directories found")
    
    # Check for road network data
    road_dirs = list(data_dir.glob('hotosm_*'))
    if road_dirs:
        print(f"✅ Found {len(road_dirs)} road network directories")
    else:
        print("⚠️  No road network data found")
    
    return True

def test_torch_functionality():
    """Test basic PyTorch functionality."""
    print("\n🔍 Testing PyTorch functionality...")
    
    try:
        import torch
        import torch.nn as nn
        
        # Test tensor creation
        x = torch.randn(10, 5)
        print(f"✅ Tensor creation: {x.shape}")
        
        # Test simple neural network
        model = nn.Linear(5, 1)
        output = model(x)
        print(f"✅ Neural network: {output.shape}")
        
        # Test GPU if available
        if torch.cuda.is_available():
            x_gpu = x.cuda()
            model_gpu = model.cuda()
            output_gpu = model_gpu(x_gpu)
            print(f"✅ GPU computation: {output_gpu.shape}")
        else:
            print("ℹ️  GPU not available (CPU only)")
        
        return True
    except Exception as e:
        print(f"❌ PyTorch test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚗 GNN Traffic Prediction - Installation Test")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("Data Structure", test_data_structure), 
        ("Data Files", test_data_files),
        ("PyTorch Functionality", test_torch_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print(f"\n🎉 All tests passed! Your environment is ready.")
        print(f"\n🚀 Next steps:")
        print(f"   1. streamlit run app/streamlit_app.py")
        print(f"   2. Open browser to http://localhost:8501")
        print(f"   3. Explore the interactive dashboard!")
    else:
        print(f"\n⚠️  Some tests failed. Please check the installation.")
        print(f"   Run: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
