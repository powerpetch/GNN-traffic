# 🚀 Google Colab Upload Guide

## Method 1: GitHub Integration (Recommended) ⭐

### Step 1: Push Your Colab Files to GitHub
```bash
# Navigate to your project
cd "d:\user\Data_project\gnn-traffic"

# Add the colab directory to git
git add gnn-traffic-colab/
git commit -m "Add Google Colab version of GNN Traffic project"
git push origin main
```

### Step 2: Open in Colab Directly from GitHub
1. Go to [Google Colab](https://colab.research.google.com)
2. Click "GitHub" tab
3. Enter your repository: `powerpetch/GNN-traffic`
4. Select the notebook you want to open:
   - `gnn-traffic-colab/notebooks/01_data_preprocessing.ipynb`
   - `gnn-traffic-colab/notebooks/02_graph_construction.ipynb`
   - `gnn-traffic-colab/notebooks/03_model_training.ipynb`
   - `gnn-traffic-colab/notebooks/04_evaluation.ipynb`
   - `gnn-traffic-colab/notebooks/05_visualization.ipynb`

### Step 3: Clone Repository in Colab
Add this cell at the beginning of each notebook:
```python
# Clone the repository
!git clone https://github.com/powerpetch/GNN-traffic.git
%cd GNN-traffic/gnn-traffic-colab

# Install requirements
!pip install -r requirements_colab.txt

# Setup the project
!python setup_colab.py
```

---

## Method 2: Direct File Upload 📁

### Step 1: Create a Zip File
```powershell
# Create a zip file of your colab directory
Compress-Archive -Path "gnn-traffic-colab" -DestinationPath "gnn-traffic-colab.zip"
```

### Step 2: Upload to Colab
1. Open [Google Colab](https://colab.research.google.com)
2. Create a new notebook
3. Upload the zip file:
```python
from google.colab import files
uploaded = files.upload()  # Select your gnn-traffic-colab.zip

# Extract the files
!unzip gnn-traffic-colab.zip
%cd gnn-traffic-colab

# Install requirements
!pip install -r requirements_colab.txt
```

---

## Method 3: Google Drive Integration ☁️

### Step 1: Upload to Google Drive
1. Upload your `gnn-traffic-colab.zip` to Google Drive
2. Get the shareable link

### Step 2: Download in Colab
```python
# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Copy from Drive to Colab
!cp "/content/drive/MyDrive/gnn-traffic-colab.zip" .
!unzip gnn-traffic-colab.zip
%cd gnn-traffic-colab

# Install requirements
!pip install -r requirements_colab.txt
```

---

## Method 4: Direct GitHub Raw Files 🔗

### For Individual Notebooks:
You can open notebooks directly using this URL format:
```
https://colab.research.google.com/github/powerpetch/GNN-traffic/blob/main/gnn-traffic-colab/notebooks/01_data_preprocessing.ipynb
```

Just replace the notebook name for each file:
- [01_data_preprocessing.ipynb](https://colab.research.google.com/github/powerpetch/GNN-traffic/blob/main/gnn-traffic-colab/notebooks/01_data_preprocessing.ipynb)
- [02_graph_construction.ipynb](https://colab.research.google.com/github/powerpetch/GNN-traffic/blob/main/gnn-traffic-colab/notebooks/02_graph_construction.ipynb)
- [03_model_training.ipynb](https://colab.research.google.com/github/powerpetch/GNN-traffic/blob/main/gnn-traffic-colab/notebooks/03_model_training.ipynb)
- [04_evaluation.ipynb](https://colab.research.google.com/github/powerpetch/GNN-traffic/blob/main/gnn-traffic-colab/notebooks/04_evaluation.ipynb)
- [05_visualization.ipynb](https://colab.research.google.com/github/powerpetch/GNN-traffic/blob/main/gnn-traffic-colab/notebooks/05_visualization.ipynb)

---

## 🔧 Setting Up in Colab

### Standard Setup Cell (Add to beginning of each notebook):
```python
# 🚀 GNN Traffic Project Setup for Google Colab

import os
import sys

# Check if running in Colab
IN_COLAB = 'google.colab' in sys.modules

if IN_COLAB:
    print("🔍 Running in Google Colab")
    
    # Clone repository if not exists
    if not os.path.exists('GNN-traffic'):
        print("📥 Cloning repository...")
        !git clone https://github.com/powerpetch/GNN-traffic.git
    
    # Change to project directory
    %cd GNN-traffic/gnn-traffic-colab
    
    # Install requirements
    print("📦 Installing requirements...")
    !pip install -q -r requirements_colab.txt
    
    # Setup project
    print("⚙️ Setting up project...")
    !python setup_colab.py
    
    print("✅ Setup complete!")
else:
    print("🖥️ Running locally")
    # Add local setup if needed

# Add project to Python path
if 'src' not in sys.path:
    sys.path.append('src')

print("🎯 Ready to run GNN Traffic models!")
```

---

## 📊 Data Handling in Colab

### For Large Data Files:
Since your data files are large, consider these options:

#### Option 1: Sample Data
```python
# Use sample data for demonstration
!wget https://github.com/powerpetch/GNN-traffic/releases/download/v1.0/sample_data.zip
!unzip sample_data.zip
```

#### Option 2: Google Drive Storage
```python
# Mount Google Drive for large datasets
from google.colab import drive
drive.mount('/content/drive')

# Create symbolic link to your data
!ln -s "/content/drive/MyDrive/GNN_Traffic_Data" "./data"
```

#### Option 3: Download Subset
```python
# Download only necessary data files
import gdown

# Download specific PROBE data files
gdown.download('YOUR_GOOGLE_DRIVE_FILE_ID', 'data/probe_sample.csv', quiet=False)
```

---

## 🎯 Quick Start Commands

### Push to GitHub (Run in PowerShell):
```powershell
cd "d:\user\Data_project\gnn-traffic"
git add .
git commit -m "Add Colab-ready project structure"
git push origin main
```

### Open in Colab:
1. Go to: https://colab.research.google.com
2. Click "GitHub" tab
3. Enter: `powerpetch/GNN-traffic`
4. Select your notebook

### Direct Links (After pushing to GitHub):
- [Start with Data Preprocessing](https://colab.research.google.com/github/powerpetch/GNN-traffic/blob/main/gnn-traffic-colab/notebooks/01_data_preprocessing.ipynb)

---

## ⚠️ Important Notes

1. **GPU Runtime**: Enable GPU in Colab (Runtime → Change runtime type → GPU)
2. **Session Timeout**: Colab sessions timeout after inactivity
3. **File Persistence**: Files are lost when session ends (use Google Drive for persistence)
4. **Memory Limits**: Colab has memory limitations for large datasets
5. **Runtime Limits**: Free Colab has usage limits

---

## 🔧 Troubleshooting

### Common Issues:
1. **Import Errors**: Make sure `sys.path.append('src')` is included
2. **Data Not Found**: Check data paths and download commands
3. **Package Conflicts**: Use `requirements_colab.txt` for compatible versions
4. **Memory Issues**: Use smaller batch sizes or data samples

### Getting Help:
- Check the logs in each notebook cell
- Verify file paths with `!ls` commands
- Use `!pwd` to check current directory
