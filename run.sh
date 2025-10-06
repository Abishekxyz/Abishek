#!/bin/bash

echo "🚀 AI-Powered Academic Integrity Checker"
echo "========================================"
echo ""

# Add local bin to PATH
export PATH=$PATH:$HOME/.local/bin

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "📦 Installing dependencies..."
python3 -m pip install --upgrade pip setuptools wheel --quiet
python3 -m pip install -r requirements.txt --quiet

echo ""
echo "🗄️ Initializing database..."
python3 database.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting application..."
echo "📊 Access the application at: http://localhost:5000"
echo ""

# Run the application
python3 app.py
