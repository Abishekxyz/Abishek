#!/usr/bin/env python3
"""
Setup script for Academic Integrity Checker
Handles installation, configuration, and initial setup
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description, critical=True):
    """Run a shell command with error handling"""
    print(f"\n🔍 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            if critical:
                print(f"Error: {result.stderr}")
                print("Setup cannot continue. Please fix the error above.")
                sys.exit(1)
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        if critical:
            sys.exit(1)
        return False

def check_python_version():
    """Check Python version compatibility"""
    print("🔍 Checking Python version...")

    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - COMPATIBLE")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - NOT COMPATIBLE")
        print("❌ This project requires Python 3.8 or higher")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")

    # Upgrade pip first
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip")

    # Install requirements
    if os.path.exists('requirements.txt'):
        run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing project dependencies")
    else:
        print("❌ requirements.txt not found!")
        return False

    return True

def download_nltk_data():
    """Download required NLTK data"""
    print("\n📚 Downloading NLTK data...")

    try:
        import nltk

        data_to_download = [
            'punkt',
            'stopwords',
            'wordnet',
            'averaged_perceptron_tagger'
        ]

        for data in data_to_download:
            try:
                nltk.data.find(f'tokenizers/{data}' if data != 'punkt' else f'tokenizers/punkt')
                print(f"✅ NLTK {data} - ALREADY DOWNLOADED")
            except LookupError:
                print(f"📥 Downloading NLTK {data}...")
                nltk.download(data)
                print(f"✅ NLTK {data} - DOWNLOADED")

        return True

    except ImportError:
        print("❌ NLTK not installed. Please install requirements first.")
        return False

def download_spacy_model():
    """Download spaCy language model"""
    print("\n🤖 Downloading spaCy model...")

    try:
        import spacy

        try:
            spacy.load('en_core_web_sm')
            print("✅ spaCy en_core_web_sm - ALREADY DOWNLOADED")
        except OSError:
            print("📥 Downloading spaCy en_core_web_sm model...")
            run_command(f"{sys.executable} -m spacy download en_core_web_sm", "Downloading spaCy model", critical=False)
            print("✅ spaCy en_core_web_sm - DOWNLOADED")

        return True

    except ImportError:
        print("❌ spaCy not installed. Please install requirements first.")
        return False

def setup_database():
    """Set up the database"""
    print("\n💾 Setting up database...")

    try:
        from app import create_app, db

        app = create_app()
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")

            # Add sample data if needed
            from models import User

            # Check if admin user exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', email='admin@example.com', is_admin=True)
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✅ Default admin user created (username: admin, password: admin123)")

        return True

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")

    directories = [
        'uploads',
        'static',
        'static/css',
        'static/js',
        'static/images',
        'static/fonts',
        'templates',
        'ai_modules',
        'utils',
        'chrome_extension',
        'chrome_extension/icons',
        'tests'
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}/ - CREATED")

    return True

def test_installation():
    """Run installation tests"""
    print("\n🧪 Running installation tests...")

    try:
        # Import test function
        from test_installation import main as run_tests

        # Run tests
        result = run_tests()

        if result == 0:
            print("✅ All installation tests passed!")
            return True
        else:
            print("❌ Some installation tests failed!")
            return False

    except ImportError as e:
        print(f"❌ Could not run tests: {e}")
        return False

def create_startup_scripts():
    """Create startup scripts for different platforms"""
    print("\n🚀 Creating startup scripts...")

    # Windows batch script
    windows_script = '''@echo off
echo Starting Academic Integrity Checker...
python app.py
pause
'''

    # Unix shell script
    unix_script = '''#!/bin/bash
echo "Starting Academic Integrity Checker..."
python3 app.py
'''

    # macOS script
    macos_script = unix_script

    try:
        # Windows
        with open('start_windows.bat', 'w') as f:
            f.write(windows_script)
        print("✅ start_windows.bat - CREATED")

        # Unix/Linux
        with open('start_unix.sh', 'w') as f:
            f.write(unix_script)
        os.chmod('start_unix.sh', 0o755)
        print("✅ start_unix.sh - CREATED")

        # macOS
        with open('start_macos.sh', 'w') as f:
            f.write(macos_script)
        os.chmod('start_macos.sh', 0o755)
        print("✅ start_macos.sh - CREATED")

    except Exception as e:
        print(f"❌ Error creating startup scripts: {e}")
        return False

    return True

def print_success_message():
    """Print final success message with instructions"""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("✅ Academic Integrity Checker has been successfully installed!")
    print()
    print("🚀 To start the application:")
    print("   1. Navigate to the project directory")
    print("   2. Run one of the following commands:")
    print()
    print("      Windows: start_windows.bat")
    print("      macOS:   ./start_macos.sh")
    print("      Linux:   ./start_unix.sh")
    print("      Manual:  python app.py")
    print()
    print("   3. Open your browser and go to: http://localhost:5000")
    print()
    print("📋 Default login credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print()
    print("📚 Documentation and help:")
    print("   - README.md contains detailed setup instructions")
    print("   - Check the /dashboard endpoint for API documentation")
    print()
    print("🔧 Configuration:")
    print("   - Edit config.py for database and API settings")
    print("   - Update requirements.txt if you need different versions")
    print()
    print("🎯 Next steps:")
    print("   1. Start the application")
    print("   2. Register your account or login with admin/admin123")
    print("   3. Upload a document or paste text for analysis")
    print("   4. Install the Chrome extension for Google Docs integration")
    print("=" * 60)

def main():
    """Main setup function"""
    print("🚀 Academic Integrity Checker - Setup Script")
    print("=" * 60)
    print("This script will set up your Academic Integrity Checker installation.")
    print("Make sure you have Python 3.8+ and pip installed.")
    print()

    # Check Python version
    if not check_python_version():
        return 1

    # Create directories
    create_directories()

    # Install Python dependencies
    if not install_python_dependencies():
        return 1

    # Download NLTK data
    if not download_nltk_data():
        print("⚠️  NLTK data download failed, but continuing...")

    # Download spaCy model
    if not download_spacy_model():
        print("⚠️  spaCy model download failed, but continuing...")

    # Setup database
    if not setup_database():
        print("⚠️  Database setup failed, but continuing...")

    # Create startup scripts
    create_startup_scripts()

    # Run installation tests
    test_installation()

    # Success message
    print_success_message()

    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)