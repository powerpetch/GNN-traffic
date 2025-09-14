# 📁 GNN Traffic Project Structure

## 🎯 **Current vs Recommended Structure**

### **📂 Recommended Project Organization**

```
gnn-traffic/
├── 📋 PROJECT FILES
│   ├── README.md                    # Main project documentation
│   ├── PROJECT_EXPLANATION_TH.md     # Detailed Thai explanation
│   ├── requirements.txt             # Python dependencies
│   ├── setup.py                    # Package installation
│   ├── .gitignore                  # Git ignore rules
│   └── LICENSE                     # Project license
│
├── 🔧 CONFIGURATION
│   ├── configs/
│   │   ├── __init__.py
│   │   ├── model_config.yaml       # Model configurations
│   │   ├── data_config.yaml        # Data processing configs
│   │   ├── training_config.yaml    # Training parameters
│   │   └── deployment_config.yaml  # Deployment settings
│   │
│   └── .env.example                # Environment variables template
│
├── 📊 DATA MANAGEMENT
│   ├── data/
│   │   ├── raw/                    # Original PROBE/HOTOSM data
│   │   │   ├── PROBE-202401/
│   │   │   ├── PROBE-202402/
│   │   │   ├── hotosm_tha_roads_lines_geojson/
│   │   │   └── iTIC-Longdo-Traffic-events-2022/
│   │   │
│   │   ├── interim/                # Intermediate processing
│   │   │   ├── cleaned_probe/
│   │   │   ├── processed_roads/
│   │   │   └── matched_data/
│   │   │
│   │   ├── processed/              # Final processed data
│   │   │   ├── features/
│   │   │   ├── graphs/
│   │   │   └── datasets/
│   │   │
│   │   └── external/               # External APIs/sources
│   │       ├── weather/
│   │       └── traffic_events/
│
├── 💻 SOURCE CODE
│   ├── src/
│   │   ├── __init__.py
│   │   │
│   │   ├── data/                   # Data processing modules
│   │   │   ├── __init__.py
│   │   │   ├── ingestion.py        # Data loading/ingestion
│   │   │   ├── preprocessing.py    # Data cleaning
│   │   │   ├── feature_engineering.py
│   │   │   ├── map_matching.py     # GPS to road matching
│   │   │   └── validation.py       # Data quality checks
│   │   │
│   │   ├── graphs/                 # Graph construction
│   │   │   ├── __init__.py
│   │   │   ├── road_network.py     # Road graph builder
│   │   │   ├── adjacency.py        # Adjacency matrix creation
│   │   │   └── graph_utils.py      # Graph utilities
│   │   │
│   │   ├── models/                 # GNN model implementations
│   │   │   ├── __init__.py
│   │   │   ├── base_model.py       # Base model class
│   │   │   ├── stgcn.py           # ST-GCN implementation
│   │   │   ├── dcrnn.py           # DCRNN implementation
│   │   │   ├── graphwavenet.py    # GraphWaveNet implementation
│   │   │   ├── layers/            # Custom layers
│   │   │   │   ├── __init__.py
│   │   │   │   ├── graph_conv.py
│   │   │   │   ├── temporal_conv.py
│   │   │   │   └── attention.py
│   │   │   └── baselines/         # Baseline models
│   │   │       ├── __init__.py
│   │   │       ├── lstm.py
│   │   │       └── arima.py
│   │   │
│   │   ├── training/              # Training pipeline
│   │   │   ├── __init__.py
│   │   │   ├── trainer.py         # Main trainer class
│   │   │   ├── dataset.py         # PyTorch datasets
│   │   │   ├── losses.py          # Loss functions
│   │   │   ├── metrics.py         # Evaluation metrics
│   │   │   └── callbacks.py       # Training callbacks
│   │   │
│   │   ├── evaluation/            # Model evaluation
│   │   │   ├── __init__.py
│   │   │   ├── evaluator.py       # Main evaluator
│   │   │   ├── comparisons.py     # Model comparisons
│   │   │   └── visualizations.py  # Evaluation plots
│   │   │
│   │   ├── deployment/            # Deployment utilities
│   │   │   ├── __init__.py
│   │   │   ├── model_server.py    # Model serving
│   │   │   ├── api.py             # REST API
│   │   │   └── inference.py       # Real-time inference
│   │   │
│   │   └── utils/                 # Utility functions
│   │       ├── __init__.py
│   │       ├── io.py              # File I/O utilities
│   │       ├── logging_config.py  # Logging setup
│   │       ├── visualization.py   # Plotting utilities
│   │       └── helpers.py         # General helpers
│
├── 📱 APPLICATIONS
│   ├── streamlit_app/             # Streamlit dashboard
│   │   ├── __init__.py
│   │   ├── main.py                # Main dashboard
│   │   ├── pages/                 # Multi-page app
│   │   │   ├── __init__.py
│   │   │   ├── predictions.py
│   │   │   ├── analytics.py
│   │   │   ├── model_comparison.py
│   │   │   └── settings.py
│   │   ├── components/            # Reusable components
│   │   │   ├── __init__.py
│   │   │   ├── charts.py
│   │   │   ├── maps.py
│   │   │   └── widgets.py
│   │   └── assets/                # Static assets
│   │       ├── css/
│   │       ├── images/
│   │       └── data/
│   │
│   ├── api_server/                # FastAPI/Flask server
│   │   ├── __init__.py
│   │   ├── app.py                 # Main API app
│   │   ├── routes/                # API routes
│   │   │   ├── __init__.py
│   │   │   ├── predictions.py
│   │   │   ├── models.py
│   │   │   └── health.py
│   │   ├── middleware/            # API middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── cors.py
│   │   └── schemas/               # Pydantic schemas
│   │       ├── __init__.py
│   │       ├── requests.py
│   │       └── responses.py
│   │
│   └── cli/                       # Command line interface
│       ├── __init__.py
│       ├── main.py                # CLI entry point
│       ├── commands/              # CLI commands
│       │   ├── __init__.py
│       │   ├── train.py
│       │   ├── evaluate.py
│       │   ├── predict.py
│       │   └── serve.py
│       └── utils.py
│
├── 📓 NOTEBOOKS
│   ├── exploratory/               # Data exploration
│   │   ├── 01_data_overview.ipynb
│   │   ├── 02_probe_analysis.ipynb
│   │   ├── 03_road_network_viz.ipynb
│   │   └── 04_traffic_patterns.ipynb
│   │
│   ├── experiments/               # Model experiments
│   │   ├── 01_baseline_models.ipynb
│   │   ├── 02_stgcn_experiments.ipynb
│   │   ├── 03_dcrnn_experiments.ipynb
│   │   ├── 04_graphwavenet_experiments.ipynb
│   │   └── 05_model_comparison.ipynb
│   │
│   ├── colab/                     # Google Colab versions
│   │   ├── GNN_Traffic_Colab_Setup.ipynb
│   │   ├── GNN_Traffic_Training.ipynb
│   │   └── GNN_Traffic_Demo.ipynb
│   │
│   └── tutorials/                 # Educational notebooks
│       ├── GNN_Introduction.ipynb
│       ├── Traffic_Data_Processing.ipynb
│       └── Model_Deployment.ipynb
│
├── 🧪 TESTS
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration
│   ├── test_data/                 # Test data processing
│   │   ├── __init__.py
│   │   ├── test_preprocessing.py
│   │   ├── test_feature_engineering.py
│   │   └── test_graph_construction.py
│   ├── test_models/               # Test models
│   │   ├── __init__.py
│   │   ├── test_stgcn.py
│   │   ├── test_dcrnn.py
│   │   └── test_graphwavenet.py
│   ├── test_training/             # Test training
│   │   ├── __init__.py
│   │   ├── test_trainer.py
│   │   └── test_metrics.py
│   └── test_utils/                # Test utilities
│       ├── __init__.py
│       └── test_helpers.py
│
├── 📋 SCRIPTS
│   ├── setup/                     # Setup scripts
│   │   ├── install_dependencies.sh
│   │   ├── setup_environment.py
│   │   └── download_data.sh
│   ├── preprocessing/             # Data preprocessing scripts
│   │   ├── process_probe_data.py
│   │   ├── build_road_graph.py
│   │   └── create_features.py
│   ├── training/                  # Training scripts
│   │   ├── train_stgcn.py
│   │   ├── train_dcrnn.py
│   │   ├── train_graphwavenet.py
│   │   └── hyperparameter_search.py
│   ├── evaluation/                # Evaluation scripts
│   │   ├── evaluate_models.py
│   │   ├── generate_reports.py
│   │   └── performance_analysis.py
│   └── deployment/                # Deployment scripts
│       ├── deploy_model.py
│       ├── start_api_server.sh
│       └── docker_build.sh
│
├── 🐳 DEPLOYMENT
│   ├── docker/                    # Docker configurations
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.streamlit
│   │   ├── docker-compose.yml
│   │   └── .dockerignore
│   ├── kubernetes/                # K8s configurations
│   │   ├── api-deployment.yaml
│   │   ├── streamlit-deployment.yaml
│   │   └── service.yaml
│   ├── aws/                       # AWS deployment
│   │   ├── lambda_function.py
│   │   ├── cloudformation.yaml
│   │   └── ecs_task_definition.json
│   └── heroku/                    # Heroku deployment
│       ├── Procfile
│       ├── app.json
│       └── runtime.txt
│
├── 📚 DOCUMENTATION
│   ├── docs/                      # Detailed documentation
│   │   ├── index.md
│   │   ├── getting_started.md
│   │   ├── data_guide.md
│   │   ├── model_guide.md
│   │   ├── api_reference.md
│   │   └── deployment_guide.md
│   ├── papers/                    # Research papers
│   │   ├── methodology.pdf
│   │   └── results.pdf
│   └── presentations/             # Slides and presentations
│       ├── project_overview.pptx
│       └── technical_deep_dive.pdf
│
├── 💾 MODELS
│   ├── checkpoints/               # Training checkpoints
│   │   ├── stgcn/
│   │   ├── dcrnn/
│   │   └── graphwavenet/
│   ├── artifacts/                 # Model artifacts
│   │   ├── model_weights.pth
│   │   ├── scaler.pkl
│   │   ├── adjacency_matrix.npy
│   │   └── config.json
│   └── experiments/               # Experiment results
│       ├── experiment_1/
│       ├── experiment_2/
│       └── best_models/
│
├── 📊 RESULTS
│   ├── figures/                   # Generated plots
│   │   ├── model_performance/
│   │   ├── data_analysis/
│   │   └── predictions/
│   ├── reports/                   # Analysis reports
│   │   ├── data_quality_report.html
│   │   ├── model_comparison_report.html
│   │   └── performance_analysis.pdf
│   └── logs/                      # Training logs
│       ├── training_logs/
│       ├── evaluation_logs/
│       └── api_logs/
│
└── 🔄 ENVIRONMENT
    ├── environments/              # Conda environments
    │   ├── environment.yml
    │   ├── environment-dev.yml
    │   └── environment-prod.yml
    ├── .env                       # Environment variables
    ├── .env.example              # Environment template
    └── requirements/              # Detailed requirements
        ├── base.txt
        ├── dev.txt
        ├── prod.txt
        └── colab.txt
```

## 🎯 **Key Organization Principles**

### **1. Separation of Concerns**
- **Data**: Raw → Interim → Processed
- **Code**: Modular with clear responsibilities
- **Applications**: Separate UI, API, and CLI
- **Tests**: Mirror source structure

### **2. Environment Management**
- Development vs Production configs
- Docker for containerization
- Multiple deployment options

### **3. Scalability**
- Plugin architecture for models
- Configurable components
- Easy to add new features

### **4. Documentation**
- Code documentation
- User guides
- API references
- Deployment instructions

## 🚀 **Migration Steps**

1. **Create new structure** (see scripts below)
2. **Move existing files** to appropriate locations
3. **Update import paths** in Python files
4. **Create configuration files**
5. **Set up testing framework**
6. **Update documentation**

## 📝 **File Naming Conventions**

- **Python files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case()`
- **Constants**: `UPPER_CASE`
- **Config files**: `lowercase.yaml`
- **Scripts**: `descriptive_name.py`

## 🔧 **Development Workflow**

1. **Feature development**: Create in `src/`
2. **Experimentation**: Use `notebooks/experiments/`
3. **Testing**: Write tests in `tests/`
4. **Documentation**: Update in `docs/`
5. **Deployment**: Use `deployment/` configs
