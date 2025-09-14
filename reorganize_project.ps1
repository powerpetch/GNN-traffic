# 🚀 GNN Traffic Project Reorganization Script (PowerShell)
# Automatically reorganizes your project structure according to best practices

param(
    [switch]$DryRun = $false,
    [switch]$SkipBackup = $false
)

Write-Host "🚀 GNN Traffic Project Reorganization" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Get current directory
$ProjectRoot = Get-Location
Write-Host "📂 Project root: $ProjectRoot" -ForegroundColor Yellow

# Dry run check
if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No files will be modified" -ForegroundColor Magenta
}

function Write-Step {
    param([string]$Message, [string]$Color = "Green")
    Write-Host "  ✅ $Message" -ForegroundColor $Color
}

function Write-Error {
    param([string]$Message)
    Write-Host "  ❌ $Message" -ForegroundColor Red
}

function Create-Directory {
    param([string]$Path)
    
    if ($DryRun) {
        Write-Host "  [DRY RUN] Would create: $Path" -ForegroundColor DarkGray
        return
    }
    
    if (!(Test-Path $Path)) {
        New-Item -Path $Path -ItemType Directory -Force | Out-Null
        Write-Step "Created $Path"
    }
}

function Copy-FileIfExists {
    param([string]$Source, [string]$Destination)
    
    if ($DryRun) {
        if (Test-Path $Source) {
            Write-Host "  [DRY RUN] Would copy: $Source → $Destination" -ForegroundColor DarkGray
        }
        return
    }
    
    if (Test-Path $Source) {
        # Create destination directory if it doesn't exist
        $DestDir = Split-Path $Destination -Parent
        if (!(Test-Path $DestDir)) {
            New-Item -Path $DestDir -ItemType Directory -Force | Out-Null
        }
        
        Copy-Item -Path $Source -Destination $Destination -Force
        Write-Step "Moved $Source → $Destination"
    }
}

function Create-FileWithContent {
    param([string]$Path, [string]$Content)
    
    if ($DryRun) {
        Write-Host "  [DRY RUN] Would create: $Path" -ForegroundColor DarkGray
        return
    }
    
    $Dir = Split-Path $Path -Parent
    if (!(Test-Path $Dir)) {
        New-Item -Path $Dir -ItemType Directory -Force | Out-Null
    }
    
    Set-Content -Path $Path -Value $Content -Encoding UTF8
    Write-Step "Created $Path"
}

# Step 1: Create Backup
if (!$SkipBackup) {
    Write-Host "`n📦 Creating backup..." -ForegroundColor Yellow
    
    $BackupDir = Join-Path $ProjectRoot "backup_old_structure"
    
    if (!$DryRun) {
        if (Test-Path $BackupDir) {
            Remove-Item -Path $BackupDir -Recurse -Force
        }
        New-Item -Path $BackupDir -ItemType Directory | Out-Null
    }
    
    $BackupItems = @("src", "app", "configs", "notebooks")
    
    foreach ($Item in $BackupItems) {
        if (Test-Path $Item) {
            if (!$DryRun) {
                Copy-Item -Path $Item -Destination (Join-Path $BackupDir $Item) -Recurse
            }
            Write-Step "Backed up $Item/"
        }
    }
}

# Step 2: Create New Directory Structure
Write-Host "`n🏗️ Creating new directory structure..." -ForegroundColor Yellow

$Directories = @(
    "configs",
    "src/data", "src/graphs", "src/models/layers", "src/models/baselines", 
    "src/training", "src/evaluation", "src/deployment", "src/utils",
    "apps/streamlit_app/pages", "apps/streamlit_app/components", 
    "apps/streamlit_app/assets/css", "apps/streamlit_app/assets/images",
    "apps/api_server/routes", "apps/api_server/middleware", "apps/api_server/schemas",
    "apps/cli/commands",
    "notebooks/exploratory", "notebooks/experiments", "notebooks/colab", "notebooks/tutorials",
    "tests/test_data", "tests/test_models", "tests/test_training", "tests/test_utils",
    "scripts/setup", "scripts/preprocessing", "scripts/training", "scripts/evaluation", "scripts/deployment",
    "deployment/docker", "deployment/kubernetes", "deployment/aws", "deployment/heroku",
    "docs", "papers", "presentations",
    "models/checkpoints/stgcn", "models/checkpoints/dcrnn", "models/checkpoints/graphwavenet",
    "models/artifacts", "models/experiments",
    "results/figures/model_performance", "results/figures/data_analysis", "results/figures/predictions",
    "results/reports", "results/logs/training_logs", "results/logs/evaluation_logs", "results/logs/api_logs",
    "environments", "requirements"
)

foreach ($Dir in $Directories) {
    Create-Directory $Dir
}

# Step 3: Migrate Existing Files
Write-Host "`n🚚 Migrating existing files..." -ForegroundColor Yellow

$Migrations = @{
    "app/streamlit_app.py" = "apps/streamlit_app/main.py"
    "src/train.py" = "scripts/training/train.py"
    "src/evaluate.py" = "scripts/evaluation/evaluate.py"
    "src/datasets.py" = "src/training/dataset.py"
    "src/aggregate.py" = "src/data/preprocessing.py"
    "src/features.py" = "src/data/feature_engineering.py"
    "src/graph.py" = "src/graphs/road_network.py"
    "src/ingest.py" = "src/data/ingestion.py"
    "src/mapmatch.py" = "src/data/map_matching.py"
}

foreach ($Migration in $Migrations.GetEnumerator()) {
    Copy-FileIfExists $Migration.Key $Migration.Value
}

# Migrate notebooks directory
if (Test-Path "notebooks") {
    if (!$DryRun) {
        Copy-Item -Path "notebooks/*" -Destination "notebooks/exploratory/" -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Step "Moved notebooks/ → notebooks/exploratory/"
}

# Step 4: Create Configuration Files
Write-Host "`n⚙️ Creating configuration files..." -ForegroundColor Yellow

$ModelConfig = @"
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
"@

$TrainingConfig = @"
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
"@

$DataConfig = @"
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
"@

Create-FileWithContent "configs/model_config.yaml" $ModelConfig
Create-FileWithContent "configs/training_config.yaml" $TrainingConfig
Create-FileWithContent "configs/data_config.yaml" $DataConfig

# Step 5: Create Requirements Files
Write-Host "`n📦 Creating requirements files..." -ForegroundColor Yellow

$BaseRequirements = @"
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
"@

$DevRequirements = @"
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
"@

$ColabRequirements = @"
# Google Colab optimized
torch>=1.12.0
torch-geometric>=2.1.0
numpy>=1.21.0
pandas>=1.4.0
matplotlib>=3.5.0
plotly>=5.8.0
geopandas>=0.11.0
networkx>=2.8.0
"@

Create-FileWithContent "requirements/base.txt" $BaseRequirements
Create-FileWithContent "requirements/dev.txt" $DevRequirements
Create-FileWithContent "requirements/colab.txt" $ColabRequirements

# Step 6: Create __init__.py Files
Write-Host "`n🐍 Creating __init__.py files..." -ForegroundColor Yellow

$InitFiles = @(
    "src/__init__.py",
    "src/models/__init__.py", 
    "src/data/__init__.py",
    "src/training/__init__.py",
    "src/evaluation/__init__.py",
    "tests/__init__.py",
    "apps/__init__.py"
)

foreach ($InitFile in $InitFiles) {
    Create-FileWithContent $InitFile '"""Package initialization file"""'
}

# Step 7: Update .gitignore
Write-Host "`n🙈 Updating .gitignore..." -ForegroundColor Yellow

$GitignoreContent = @"
# Python
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
"@

Create-FileWithContent ".gitignore" $GitignoreContent

# Final Summary
Write-Host "`n" + "=" * 50 -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "🔍 DRY RUN COMPLETED - No changes were made" -ForegroundColor Magenta
    Write-Host "💡 Run without -DryRun to perform actual migration" -ForegroundColor Yellow
} else {
    Write-Host "✅ Project reorganization completed successfully!" -ForegroundColor Green
    
    Write-Host "`n📋 Next steps:" -ForegroundColor Yellow
    Write-Host "1. Review migrated files in new locations" -ForegroundColor White
    Write-Host "2. Update import statements in Python files" -ForegroundColor White
    Write-Host "3. Test the new structure" -ForegroundColor White
    Write-Host "4. Remove backup if everything works" -ForegroundColor White
    
    Write-Host "`n🎯 Documentation:" -ForegroundColor Yellow
    Write-Host "- PROJECT_STRUCTURE.md - Detailed structure documentation" -ForegroundColor White
    Write-Host "- MIGRATION_GUIDE.md - Manual migration guide" -ForegroundColor White
}

Write-Host "`n🚀 Happy coding with your organized project!" -ForegroundColor Cyan
