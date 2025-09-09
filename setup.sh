#!/bin/bash
# GNN Traffic Project Setup Script

echo "🚗 GNN Traffic Prediction Setup"
echo "================================"

# Check Python version
python --version

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install requirements
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Activate environment: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
echo "2. Launch dashboard: streamlit run app/streamlit_app.py"
echo "3. Open browser to: http://localhost:8501"
echo ""
echo "📖 For detailed instructions, see README.md"
