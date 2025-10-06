#!/usr/bin/env python3
"""
Test script to verify all modules are working
"""

import sys
print("=" * 60)
print("Testing AI-Powered Academic Integrity Checker")
print("=" * 60)

# Test imports
try:
    print("\n✓ Testing Flask import...")
    import flask
    print(f"  Flask version: {flask.__version__}")
except ImportError as e:
    print(f"  ✗ Flask import failed: {e}")
    sys.exit(1)

try:
    print("\n✓ Testing database module...")
    from database import init_db
    print("  Database module OK")
except ImportError as e:
    print(f"  ✗ Database import failed: {e}")
    sys.exit(1)

try:
    print("\n✓ Testing detection modules...")
    from modules.plagiarism_detector import PlagiarismDetector
    from modules.ai_detector import AIContentDetector
    from modules.paraphrase_detector import ParaphraseDetector
    from modules.citation_validator import CitationValidator
    from modules.readability_checker import ReadabilityChecker
    from modules.writing_feedback import WritingFeedback
    from modules.resume_analyzer import ResumeAnalyzer
    from modules.report_generator import ReportGenerator
    print("  All detection modules OK")
except ImportError as e:
    print(f"  ✗ Module import failed: {e}")
    sys.exit(1)

try:
    print("\n✓ Testing utility modules...")
    from utils.file_handler import extract_text_from_file
    print("  Utility modules OK")
except ImportError as e:
    print(f"  ✗ Utility import failed: {e}")
    sys.exit(1)

# Test module functionality
print("\n✓ Testing module functionality...")
try:
    # Test plagiarism detector
    plagiarism = PlagiarismDetector()
    result = plagiarism.check("This is a test document for plagiarism detection.")
    print(f"  Plagiarism Detector: OK (found {result['matches_found']} matches)")
    
    # Test AI detector
    ai_detector = AIContentDetector()
    result = ai_detector.detect("This is a test document for AI detection.")
    print(f"  AI Detector: OK (probability: {result['ai_percentage']}%)")
    
    # Test paraphrase detector
    paraphrase = ParaphraseDetector()
    result = paraphrase.check("This is a test document for paraphrase detection.")
    print(f"  Paraphrase Detector: OK (probability: {result['paraphrase_percentage']}%)")
    
    # Test citation validator
    citation = CitationValidator()
    result = citation.validate("This is a test document with citation (Author, 2024).")
    print(f"  Citation Validator: OK (found {result['citations_found']} citations)")
    
    # Test readability checker
    readability = ReadabilityChecker()
    result = readability.analyze("This is a simple test sentence for readability analysis.")
    print(f"  Readability Checker: OK (Flesch score: {result['scores']['flesch_reading_ease']})")
    
    # Test writing feedback
    writing = WritingFeedback()
    result = writing.analyze("This is a test document for writing feedback analysis.")
    print(f"  Writing Feedback: OK (score: {result['writing_score']})")
    
    # Test resume analyzer
    resume = ResumeAnalyzer()
    result = resume.analyze("John Doe\nExperience: Software Engineer\nEducation: BS Computer Science\nSkills: Python, Java")
    print(f"  Resume Analyzer: OK (score: {result['overall_score']})")
    
except Exception as e:
    print(f"  ✗ Functionality test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\n🚀 Application is ready to run!")
print("   Start with: python3 app.py")
print("   Access at: http://localhost:5000")
print("=" * 60)
