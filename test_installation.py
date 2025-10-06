#!/usr/bin/env python3
"""
Installation and Setup Test Script
Tests the Academic Integrity Checker installation and basic functionality
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

def run_command(command, description):
    """Run a shell command and return success status"""
    print(f"\n🔍 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def test_python_modules():
    """Test if required Python modules are installed"""
    required_modules = [
        'flask', 'flask_cors', 'flask_sqlalchemy', 'flask_login',
        'werkzeug', 'transformers', 'torch', 'scikit_learn',
        'nltk', 'spacy', 'pandas', 'numpy', 'beautifulsoup4',
        'requests', 'python_docx', 'PyPDF2', 'reportlab'
    ]

    missing_modules = []

    for module in required_modules:
        try:
            importlib.import_module(module.replace('_', '.').replace('python_docx', 'docx').replace('PyPDF2', 'PyPDF2'))
            print(f"✅ {module} - INSTALLED")
        except ImportError:
            print(f"❌ {module} - MISSING")
            missing_modules.append(module)

    return len(missing_modules) == 0, missing_modules

def test_file_structure():
    """Test if all required files and directories exist"""
    required_files = [
        'app.py',
        'config.py',
        'models.py',
        'requirements.txt',
        'README.md',
        'static/css/style.css',
        'static/js/script.js',
        'templates/base.html',
        'templates/index.html',
        'templates/dashboard.html',
        'ai_modules/plagiarism_detector.py',
        'ai_modules/paraphrase_detector.py',
        'ai_modules/ai_content_detector.py',
        'ai_modules/citation_validator.py',
        'ai_modules/writing_analyzer.py',
        'ai_modules/resume_analyzer.py',
        'utils/text_processor.py',
        'utils/file_handler.py',
        'utils/report_generator.py'
    ]

    missing_files = []

    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - EXISTS")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)

    return len(missing_files) == 0, missing_files

def test_database_setup():
    """Test database setup"""
    print("
🔍 Testing database setup..."    try:
        # Try to import and create database
        from app import create_app, db

        app = create_app()
        with app.app_context():
            # Test database connection
            db.create_all()
            print("✅ Database setup - SUCCESS")

        return True
    except Exception as e:
        print(f"❌ Database setup - FAILED: {e}")
        return False

def test_ai_modules():
    """Test AI modules initialization"""
    print("
🔍 Testing AI modules..."    try:
        from ai_modules.plagiarism_detector import PlagiarismDetector
        from ai_modules.ai_content_detector import AIContentDetector
        from ai_modules.citation_validator import CitationValidator
        from ai_modules.writing_analyzer import WritingAnalyzer
        from ai_modules.resume_analyzer import ResumeAnalyzer

        # Initialize modules
        plagiarism_detector = PlagiarismDetector()
        ai_detector = AIContentDetector()
        citation_validator = CitationValidator()
        writing_analyzer = WritingAnalyzer()
        resume_analyzer = ResumeAnalyzer()

        print("✅ AI modules initialization - SUCCESS")
        return True

    except Exception as e:
        print(f"❌ AI modules initialization - FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Academic Integrity Checker - Installation Test")
    print("=" * 60)

    tests = [
        ("Python Modules", test_python_modules),
        ("File Structure", test_file_structure),
        ("Database Setup", test_database_setup),
        ("AI Modules", test_ai_modules),
    ]

    results = []

    for test_name, test_func in tests:
        success, details = test_func()
        results.append((test_name, success, details))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    all_passed = True

    for test_name, success, details in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name"20"} {status}")

        if not success and details:
            if isinstance(details, list):
                for detail in details:
                    print(f"                 - {detail}")

    print("\n" + "=" * 60)

    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your Academic Integrity Checker is ready to use!")
        print("\n🚀 To start the application:")
        print("   1. Run: pip install -r requirements.txt")
        print("   2. Run: python app.py")
        print("   3. Open: http://localhost:5000")
    else:
        print("⚠️  SOME TESTS FAILED!")
        print("❌ Please fix the issues above before running the application.")
        return 1

    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)