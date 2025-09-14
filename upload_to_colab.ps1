# 🚀 Upload GNN Traffic Project to Google Colab
# PowerShell script to prepare and upload your project

Write-Host "🚀 GNN Traffic - Google Colab Upload Script" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Get current directory
$ProjectRoot = Get-Location
Write-Host "📂 Project root: $ProjectRoot" -ForegroundColor Yellow

function Write-Step {
    param([string]$Message, [string]$Color = "Green")
    Write-Host "  ✅ $Message" -ForegroundColor $Color
}

function Write-Info {
    param([string]$Message)
    Write-Host "  ℹ️ $Message" -ForegroundColor Blue
}

# Step 1: Prepare files for GitHub
Write-Host "`n📦 Preparing files for GitHub..." -ForegroundColor Yellow

# Replace the problematic setup file
if (Test-Path "gnn-traffic-colab\setup_colab.py") {
    Copy-Item "gnn-traffic-colab\setup_colab_clean.py" "gnn-traffic-colab\setup_colab.py" -Force
    Write-Step "Updated setup_colab.py"
}

# Add all files to git
Write-Host "`n📤 Adding files to Git..." -ForegroundColor Yellow
try {
    git add .
    Write-Step "Files added to git staging"
} catch {
    Write-Host "  ❌ Error adding files to git" -ForegroundColor Red
    Write-Host "  💡 Make sure you're in a git repository" -ForegroundColor Yellow
    exit 1
}

# Commit changes
Write-Host "`n💾 Committing changes..." -ForegroundColor Yellow
try {
    git commit -m "Add Google Colab support with notebooks and setup scripts"
    Write-Step "Changes committed"
} catch {
    Write-Host "  ⚠️ Nothing to commit or commit failed" -ForegroundColor Yellow
}

# Push to GitHub
Write-Host "`n🌐 Pushing to GitHub..." -ForegroundColor Yellow
try {
    git push origin main
    Write-Step "Pushed to GitHub successfully"
} catch {
    Write-Host "  ❌ Error pushing to GitHub" -ForegroundColor Red
    Write-Host "  💡 Check your GitHub authentication" -ForegroundColor Yellow
    exit 1
}

# Step 2: Provide Colab links
Write-Host "`n🎯 Google Colab Links" -ForegroundColor Yellow
Write-Host "=====================" -ForegroundColor Yellow

$GitHubRepo = "powerpetch/GNN-traffic"
$ColabBase = "https://colab.research.google.com/github"

Write-Info "Your project is now available in Google Colab!"
Write-Host ""

Write-Host "📚 Direct Notebook Links:" -ForegroundColor Cyan
Write-Host "1. Data Preprocessing:" -ForegroundColor White
Write-Host "   $ColabBase/$GitHubRepo/blob/main/gnn-traffic-colab/notebooks/01_data_preprocessing.ipynb" -ForegroundColor Blue

Write-Host "2. Graph Construction:" -ForegroundColor White  
Write-Host "   $ColabBase/$GitHubRepo/blob/main/gnn-traffic-colab/notebooks/02_graph_construction.ipynb" -ForegroundColor Blue

Write-Host "3. Model Training:" -ForegroundColor White
Write-Host "   $ColabBase/$GitHubRepo/blob/main/gnn-traffic-colab/notebooks/03_model_training.ipynb" -ForegroundColor Blue

Write-Host "4. Evaluation:" -ForegroundColor White
Write-Host "   $ColabBase/$GitHubRepo/blob/main/gnn-traffic-colab/notebooks/04_evaluation.ipynb" -ForegroundColor Blue

Write-Host "5. Visualization:" -ForegroundColor White
Write-Host "   $ColabBase/$GitHubRepo/blob/main/gnn-traffic-colab/notebooks/05_visualization.ipynb" -ForegroundColor Blue

# Step 3: Create quick setup instructions
Write-Host "`n⚡ Quick Setup in Colab" -ForegroundColor Yellow
Write-Host "=======================" -ForegroundColor Yellow

$SetupCode = @"
# 🚀 Quick Setup Code (Copy to first cell in any notebook)
import os
import sys

# Clone repository
!git clone https://github.com/$GitHubRepo.git
%cd GNN-traffic/gnn-traffic-colab

# Install requirements
!pip install -q -r requirements_colab.txt

# Setup project
!python setup_colab.py

# Add to Python path
sys.path.append('src')

print("✅ Setup complete! Ready to run GNN Traffic models!")
"@

Write-Host $SetupCode -ForegroundColor Gray

# Step 4: Create a summary file
Write-Host "`n📋 Creating Colab instructions..." -ForegroundColor Yellow

$Instructions = @"
# 🚀 GNN Traffic Project - Google Colab Instructions

## Quick Start

1. **Open any notebook directly from GitHub:**
   - Click on any of the Colab links above
   - Or go to [Google Colab](https://colab.research.google.com)
   - Choose "GitHub" tab and enter: `$GitHubRepo`

2. **Setup in first cell:**
   Copy this code to the first cell of any notebook:

``````python
# 🚀 GNN Traffic Setup
import os
import sys

# Clone repository
!git clone https://github.com/$GitHubRepo.git
%cd GNN-traffic/gnn-traffic-colab

# Install requirements
!pip install -q -r requirements_colab.txt

# Setup project  
!python setup_colab.py

# Add to Python path
sys.path.append('src')

print("✅ Ready to run!")
``````

3. **Enable GPU (Recommended):**
   - Runtime → Change runtime type → GPU

4. **Start with any notebook:**
   - 01_data_preprocessing.ipynb - Data loading and preprocessing
   - 02_graph_construction.ipynb - Build road network graphs
   - 03_model_training.ipynb - Train GNN models
   - 04_evaluation.ipynb - Evaluate model performance
   - 05_visualization.ipynb - Visualize results

## Features Available in Colab

✅ All three GNN models (ST-GCN, DCRNN, GraphWaveNet)
✅ Sample data for quick testing
✅ Interactive visualizations
✅ Model training and evaluation
✅ Bangkok road network analysis
✅ Traffic pattern visualization

## Tips for Colab

- Sessions timeout after inactivity - save your work frequently
- Free Colab has memory and time limitations
- Use sample data or smaller datasets for testing
- Save important results to Google Drive

## Need Help?

- Check the notebook cells for detailed explanations
- Each notebook is self-contained with setup instructions
- Use the sample data to get started quickly
"@

$Instructions | Out-File -FilePath "COLAB_INSTRUCTIONS.md" -Encoding UTF8
Write-Step "Created COLAB_INSTRUCTIONS.md"

# Final summary
Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "✅ SUCCESS! Your project is now available in Google Colab!" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Click any of the Colab links above" -ForegroundColor White
Write-Host "2. Copy the setup code to the first cell" -ForegroundColor White  
Write-Host "3. Enable GPU runtime if needed" -ForegroundColor White
Write-Host "4. Start experimenting with GNN models!" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation created:" -ForegroundColor Cyan
Write-Host "- COLAB_UPLOAD_GUIDE.md - Complete upload guide" -ForegroundColor White
Write-Host "- COLAB_INSTRUCTIONS.md - Quick start instructions" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Happy modeling in Google Colab!" -ForegroundColor Green
