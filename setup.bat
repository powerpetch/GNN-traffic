@echo off
REM GNN Traffic Project Setup Script for Windows

echo 🚗 GNN Traffic Prediction Setup
echo ================================

REM Check Python version
py --version

REM Create virtual environment
echo 📦 Creating virtual environment...
py -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📚 Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Setup complete!
echo.
echo 🚀 Next steps:
echo 1. Activate environment: venv\Scripts\activate
echo 2. Launch dashboard: streamlit run app/streamlit_app.py
echo 3. Open browser to: http://localhost:8501
echo.
echo 📖 For detailed instructions, see README.md

pause
