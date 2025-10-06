@echo off
echo 🚀 AI-Powered Academic Integrity Checker
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo 📦 Installing dependencies...
pip install -r requirements.txt

echo.
echo 🗄️ Initializing database...
python database.py

echo.
echo ✅ Setup complete!
echo.
echo 🌐 Starting application...
echo 📊 Access the application at: http://localhost:5000
echo.

REM Run the application
python app.py
