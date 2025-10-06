"""
AI-Powered Academic Integrity Checker
Main Flask Application
"""

from flask import Flask, render_template, request, jsonify, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import secrets
from functools import wraps
import sqlite3
import json

# Import custom modules
from modules.plagiarism_detector import PlagiarismDetector
from modules.ai_detector import AIContentDetector
from modules.paraphrase_detector import ParaphraseDetector
from modules.citation_validator import CitationValidator
from modules.readability_checker import ReadabilityChecker
from modules.writing_feedback import WritingFeedback
from modules.resume_analyzer import ResumeAnalyzer
from modules.report_generator import ReportGenerator
from database import init_db, get_db_connection
from utils.file_handler import extract_text_from_file

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'docx', 'doc'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
init_db()

# Initialize modules
plagiarism_detector = PlagiarismDetector()
ai_detector = AIContentDetector()
paraphrase_detector = ParaphraseDetector()
citation_validator = CitationValidator()
readability_checker = ReadabilityChecker()
writing_feedback = WritingFeedback()
resume_analyzer = ResumeAnalyzer()
report_generator = ReportGenerator()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ============================================
# ROUTES - Authentication
# ============================================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    """User registration"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE email = ? OR username = ?', (email, username))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'User already exists'}), 400
        
        # Create user
        hashed_password = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)',
            (username, email, hashed_password, datetime.now())
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {'id': user_id, 'username': username, 'email': email}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Email and password are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user or not check_password_hash(user[2], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        session['user_id'] = user[0]
        session['username'] = user[1]
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {'id': user[0], 'username': user[1]}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})


@app.route('/check-auth')
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {'id': session['user_id'], 'username': session['username']}
        })
    return jsonify({'authenticated': False})


# ============================================
# ROUTES - Dashboard
# ============================================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    return render_template('dashboard.html')


@app.route('/api/stats')
@login_required
def get_stats():
    """Get user statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = session['user_id']
        
        # Get submission count
        cursor.execute('SELECT COUNT(*) FROM submissions WHERE user_id = ?', (user_id,))
        total_submissions = cursor.fetchone()[0]
        
        # Get recent submissions
        cursor.execute('''
            SELECT id, title, submission_type, created_at, originality_score 
            FROM submissions 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 5
        ''', (user_id,))
        recent_submissions = [
            {
                'id': row[0],
                'title': row[1],
                'type': row[2],
                'date': row[3],
                'score': row[4]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return jsonify({
            'total_submissions': total_submissions,
            'recent_submissions': recent_submissions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# ROUTES - Text Analysis
# ============================================

@app.route('/analyze')
@login_required
def analyze_page():
    """Analysis page"""
    return render_template('analyze.html')


@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze_text():
    """Comprehensive text analysis"""
    try:
        text = None
        title = "Untitled Document"
        
        # Get text from file or direct input
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                text = extract_text_from_file(filepath)
                title = filename
                os.remove(filepath)  # Clean up
        else:
            data = request.get_json()
            text = data.get('text', '')
            title = data.get('title', 'Untitled Document')
        
        if not text or len(text.strip()) < 50:
            return jsonify({'error': 'Text must be at least 50 characters'}), 400
        
        # Run all analyses
        plagiarism_result = plagiarism_detector.check(text)
        ai_detection_result = ai_detector.detect(text)
        paraphrase_result = paraphrase_detector.check(text)
        citation_result = citation_validator.validate(text)
        readability_result = readability_checker.analyze(text)
        writing_result = writing_feedback.analyze(text)
        
        # Calculate overall originality score
        originality_score = calculate_originality_score(
            plagiarism_result,
            ai_detection_result,
            paraphrase_result
        )
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO submissions 
            (user_id, title, content, submission_type, originality_score, created_at, analysis_results)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session['user_id'],
            title,
            text[:1000],  # Store first 1000 chars
            'document',
            originality_score,
            datetime.now(),
            json.dumps({
                'plagiarism': plagiarism_result,
                'ai_detection': ai_detection_result,
                'paraphrase': paraphrase_result,
                'citations': citation_result,
                'readability': readability_result,
                'writing': writing_result
            })
        ))
        submission_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'submission_id': submission_id,
            'originality_score': originality_score,
            'plagiarism': plagiarism_result,
            'ai_detection': ai_detection_result,
            'paraphrase': paraphrase_result,
            'citations': citation_result,
            'readability': readability_result,
            'writing': writing_result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# ROUTES - Resume Analyzer (Module 8)
# ============================================

@app.route('/resume-analyzer')
@login_required
def resume_analyzer_page():
    """Resume analyzer page"""
    return render_template('resume_analyzer.html')


@app.route('/api/analyze-resume', methods=['POST'])
@login_required
def analyze_resume():
    """Analyze resume for quality, keywords, ATS compatibility"""
    try:
        text = None
        filename = "Resume"
        
        # Get resume from file or text
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                text = extract_text_from_file(filepath)
                os.remove(filepath)
        else:
            data = request.get_json()
            text = data.get('text', '')
        
        if not text or len(text.strip()) < 100:
            return jsonify({'error': 'Resume must be at least 100 characters'}), 400
        
        # Analyze resume
        resume_result = resume_analyzer.analyze(text)
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO submissions 
            (user_id, title, content, submission_type, originality_score, created_at, analysis_results)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session['user_id'],
            filename,
            text[:1000],
            'resume',
            resume_result['overall_score'],
            datetime.now(),
            json.dumps(resume_result)
        ))
        submission_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'submission_id': submission_id,
            'result': resume_result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# ROUTES - Report Generation
# ============================================

@app.route('/api/generate-report/<int:submission_id>')
@login_required
def generate_report(submission_id):
    """Generate downloadable PDF report"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, content, submission_type, originality_score, created_at, analysis_results
            FROM submissions 
            WHERE id = ? AND user_id = ?
        ''', (submission_id, session['user_id']))
        
        submission = cursor.fetchone()
        conn.close()
        
        if not submission:
            return jsonify({'error': 'Submission not found'}), 404
        
        # Generate PDF report
        report_path = report_generator.generate(
            title=submission[0],
            content=submission[1],
            submission_type=submission[2],
            originality_score=submission[3],
            created_at=submission[4],
            analysis_results=json.loads(submission[5]),
            username=session['username']
        )
        
        return send_file(report_path, as_attachment=True, download_name=f'report_{submission_id}.pdf')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# ROUTES - History
# ============================================

@app.route('/history')
@login_required
def history_page():
    """History page"""
    return render_template('history.html')


@app.route('/api/submissions')
@login_required
def get_submissions():
    """Get user submission history"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, submission_type, originality_score, created_at
            FROM submissions 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (session['user_id'],))
        
        submissions = [
            {
                'id': row[0],
                'title': row[1],
                'type': row[2],
                'score': row[3],
                'date': row[4]
            }
            for row in cursor.fetchall()
        ]
        conn.close()
        
        return jsonify({'submissions': submissions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/submission/<int:submission_id>')
@login_required
def get_submission_details(submission_id):
    """Get detailed submission information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, content, submission_type, originality_score, created_at, analysis_results
            FROM submissions 
            WHERE id = ? AND user_id = ?
        ''', (submission_id, session['user_id']))
        
        submission = cursor.fetchone()
        conn.close()
        
        if not submission:
            return jsonify({'error': 'Submission not found'}), 404
        
        return jsonify({
            'title': submission[0],
            'content': submission[1],
            'type': submission[2],
            'score': submission[3],
            'date': submission[4],
            'analysis': json.loads(submission[5])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# Helper Functions
# ============================================

def calculate_originality_score(plagiarism, ai_detection, paraphrase):
    """Calculate overall originality score"""
    plagiarism_score = 100 - plagiarism['similarity_percentage']
    ai_score = 100 - ai_detection['ai_probability'] * 100
    paraphrase_score = 100 - paraphrase['paraphrase_probability'] * 100
    
    # Weighted average
    overall = (plagiarism_score * 0.4 + ai_score * 0.35 + paraphrase_score * 0.25)
    return round(overall, 2)


# ============================================
# Error Handlers
# ============================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("🚀 AI-Powered Academic Integrity Checker Starting...")
    print("📊 Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
