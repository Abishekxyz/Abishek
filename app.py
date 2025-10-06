#!/usr/bin/env python3
"""
AI-Powered Academic Integrity Checker
Main Flask Application with Comprehensive Analysis Features
"""

import os
import json
import uuid
import secrets
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, SelectField, validators
import nltk
import spacy
from config import Config

# Import AI modules
from ai_modules.plagiarism_detector import PlagiarismDetector
from ai_modules.paraphrase_detector import ParaphraseDetector
from ai_modules.ai_content_detector import AIContentDetector
from ai_modules.citation_validator import CitationValidator
from ai_modules.writing_analyzer import WritingAnalyzer
from ai_modules.resume_analyzer import ResumeAnalyzer
from utils.text_processor import TextProcessor
from utils.file_handler import FileHandler
from utils.report_generator import ReportGenerator

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize AI modules
plagiarism_detector = PlagiarismDetector()
paraphrase_detector = ParaphraseDetector()
ai_detector = AIContentDetector()
citation_validator = CitationValidator()
writing_analyzer = WritingAnalyzer()
resume_analyzer = ResumeAnalyzer()
text_processor = TextProcessor()
file_handler = FileHandler()
report_generator = ReportGenerator()

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("Downloading spaCy model...")
    os.system('python -m spacy download en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationship with analyses
    analyses = db.relationship('Analysis', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255))
    file_type = db.Column(db.String(50))
    text_content = db.Column(db.Text)
    analysis_type = db.Column(db.String(50))  # 'document', 'resume', 'text'
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed

    # Analysis results
    plagiarism_score = db.Column(db.Float)
    paraphrase_score = db.Column(db.Float)
    ai_content_score = db.Column(db.Float)
    citation_score = db.Column(db.Float)
    readability_score = db.Column(db.Float)
    overall_integrity_score = db.Column(db.Float)

    # Detailed results (JSON)
    plagiarism_details = db.Column(db.Text)  # JSON string
    paraphrase_details = db.Column(db.Text)  # JSON string
    ai_content_details = db.Column(db.Text)  # JSON string
    citation_details = db.Column(db.Text)  # JSON string
    writing_feedback = db.Column(db.Text)  # JSON string
    resume_analysis = db.Column(db.Text)  # JSON string for resume analysis

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processing_time = db.Column(db.Float)  # seconds
    file_size = db.Column(db.Integer)  # bytes

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired(), validators.Length(min=4, max=80)])
    password = PasswordField('Password', [validators.DataRequired()])
    remember = False  # BooleanField('Remember me')

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired(), validators.Length(min=4, max=80)])
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=6)])
    confirm_password = PasswordField('Confirm Password', [validators.DataRequired(), validators.EqualTo('password')])

class UploadForm(FlaskForm):
    file = FileField('Document', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'docx', 'doc', 'txt'], 'Documents only!')
    ])
    analysis_type = SelectField('Analysis Type', choices=[
        ('document', 'Academic Document'),
        ('resume', 'Resume/CV Analysis')
    ])

class TextAnalysisForm(FlaskForm):
    text = TextAreaField('Text Content', [validators.DataRequired()], render_kw={"rows": 10})
    analysis_type = SelectField('Analysis Type', choices=[
        ('document', 'Academic Document'),
        ('resume', 'Resume/CV Analysis')
    ])

# Routes
@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'error')
        elif User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'error')
        else:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    # Get recent analyses
    recent_analyses = Analysis.query.filter_by(user_id=current_user.id)\
                                   .order_by(Analysis.created_at.desc())\
                                   .limit(10).all()

    # Calculate statistics
    total_analyses = Analysis.query.filter_by(user_id=current_user.id).count()
    completed_analyses = Analysis.query.filter_by(user_id=current_user.id, status='completed').count()

    return render_template('dashboard.html',
                         recent_analyses=recent_analyses,
                         total_analyses=total_analyses,
                         completed_analyses=completed_analyses)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """File upload for analysis"""
    form = UploadForm()

    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Determine file type
        file_type = filename.split('.')[-1].lower()

        # Extract text from file
        try:
            if file_type == 'pdf':
                text_content = file_handler.extract_text_from_pdf(file_path)
            elif file_type in ['docx', 'doc']:
                text_content = file_handler.extract_text_from_docx(file_path)
            elif file_type == 'txt':
                text_content = file_handler.extract_text_from_txt(file_path)
            else:
                flash('Unsupported file type', 'error')
                return redirect(url_for('upload'))

            # Create analysis record
            analysis = Analysis(
                user_id=current_user.id,
                filename=filename,
                file_type=file_type,
                text_content=text_content,
                analysis_type=form.analysis_type.data,
                status='pending',
                file_size=os.path.getsize(file_path)
            )
            db.session.add(analysis)
            db.session.commit()

            # Start analysis in background (simulate with direct call for now)
            analysis_id = analysis.id
            perform_analysis.delay(analysis_id)

            flash('File uploaded successfully! Analysis started.', 'success')
            return redirect(url_for('analysis_status', analysis_id=analysis_id))

        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
            return redirect(url_for('upload'))

    return render_template('upload.html', form=form)

@app.route('/text_analysis', methods=['GET', 'POST'])
@login_required
def text_analysis():
    """Text input for analysis"""
    form = TextAnalysisForm()

    if form.validate_on_submit():
        text_content = form.text.data

        # Create analysis record
        analysis = Analysis(
            user_id=current_user.id,
            filename=None,
            file_type='text',
            text_content=text_content,
            analysis_type=form.analysis_type.data,
            status='pending'
        )
        db.session.add(analysis)
        db.session.commit()

        # Start analysis
        analysis_id = analysis.id
        perform_analysis.delay(analysis_id)

        flash('Text submitted for analysis!', 'success')
        return redirect(url_for('analysis_status', analysis_id=analysis_id))

    return render_template('text_analysis.html', form=form)

@app.route('/analysis/<int:analysis_id>')
@login_required
def analysis_status(analysis_id):
    """Show analysis status and results"""
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()

    if analysis.status == 'completed':
        return redirect(url_for('analysis_report', analysis_id=analysis_id))

    return render_template('analysis_status.html', analysis=analysis)

@app.route('/report/<int:analysis_id>')
@login_required
def analysis_report(analysis_id):
    """Show complete analysis report"""
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()

    if analysis.status != 'completed':
        flash('Analysis not completed yet', 'warning')
        return redirect(url_for('analysis_status', analysis_id=analysis_id))

    # Parse JSON results
    plagiarism_details = json.loads(analysis.plagiarism_details) if analysis.plagiarism_details else {}
    paraphrase_details = json.loads(analysis.paraphrase_details) if analysis.paraphrase_details else {}
    ai_content_details = json.loads(analysis.ai_content_details) if analysis.ai_content_details else {}
    citation_details = json.loads(analysis.citation_details) if analysis.citation_details else {}
    writing_feedback = json.loads(analysis.writing_feedback) if analysis.writing_feedback else {}
    resume_analysis = json.loads(analysis.resume_analysis) if analysis.resume_analysis else {}

    return render_template('report.html',
                         analysis=analysis,
                         plagiarism_details=plagiarism_details,
                         paraphrase_details=paraphrase_details,
                         ai_content_details=ai_content_details,
                         citation_details=citation_details,
                         writing_feedback=writing_feedback,
                         resume_analysis=resume_analysis)

@app.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    """API endpoint for text analysis"""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Text content required'}), 400

    text_content = data['text']
    analysis_type = data.get('analysis_type', 'document')

    # Create analysis record
    analysis = Analysis(
        user_id=current_user.id,
        text_content=text_content,
        analysis_type=analysis_type,
        status='pending'
    )
    db.session.add(analysis)
    db.session.commit()

    # Start analysis
    analysis_id = analysis.id
    perform_analysis.delay(analysis_id)

    return jsonify({'analysis_id': analysis_id, 'message': 'Analysis started'}), 202

@app.route('/api/report/<int:analysis_id>')
@login_required
def api_report(analysis_id):
    """API endpoint to get analysis report"""
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()

    if analysis.status != 'completed':
        return jsonify({'error': 'Analysis not completed'}), 404

    # Return formatted results
    results = {
        'id': analysis.id,
        'filename': analysis.filename,
        'analysis_type': analysis.analysis_type,
        'created_at': analysis.created_at.isoformat(),
        'overall_score': analysis.overall_integrity_score,
        'scores': {
            'plagiarism': analysis.plagiarism_score,
            'paraphrase': analysis.paraphrase_score,
            'ai_content': analysis.ai_content_score,
            'citation': analysis.citation_score,
            'readability': analysis.readability_score
        },
        'details': {
            'plagiarism': json.loads(analysis.plagiarism_details) if analysis.plagiarism_details else {},
            'paraphrase': json.loads(analysis.paraphrase_details) if analysis.paraphrase_details else {},
            'ai_content': json.loads(analysis.ai_content_details) if analysis.ai_content_details else {},
            'citations': json.loads(analysis.citation_details) if analysis.citation_details else {},
            'writing_feedback': json.loads(analysis.writing_feedback) if analysis.writing_feedback else {}
        }
    }

    if analysis.analysis_type == 'resume':
        results['resume_analysis'] = json.loads(analysis.resume_analysis) if analysis.resume_analysis else {}

    return jsonify(results)

@app.route('/api/citations', methods=['POST'])
@login_required
def api_citations():
    """API endpoint for citation generation"""
    data = request.get_json()
    if not data or 'text' not in data or 'style' not in data:
        return jsonify({'error': 'Text and citation style required'}), 400

    text = data['text']
    style = data['style']  # 'apa', 'mla', 'ieee'

    citations = citation_validator.generate_citations(text, style)
    return jsonify({'citations': citations})

@app.route('/download_report/<int:analysis_id>')
@login_required
def download_report(analysis_id):
    """Download analysis report as PDF"""
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()

    if analysis.status != 'completed':
        flash('Analysis not completed yet', 'warning')
        return redirect(url_for('analysis_status', analysis_id=analysis_id))

    # Generate PDF report
    pdf_path = report_generator.generate_pdf_report(analysis)

    return send_file(pdf_path, as_attachment=True,
                    download_name=f'integrity_report_{analysis_id}.pdf')

# Background task for analysis (using threading for demo)
import threading
from celery import Celery

# Celery configuration for background tasks
celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task
def perform_analysis(analysis_id):
    """Perform comprehensive analysis on text content"""
    with app.app_context():
        analysis = Analysis.query.get(analysis_id)
        if not analysis:
            return

        try:
            analysis.status = 'processing'
            db.session.commit()

            start_time = datetime.utcnow()
            text_content = analysis.text_content

            # Preprocess text
            processed_text = text_processor.preprocess_text(text_content)

            # Perform all analyses
            results = {}

            # 1. Plagiarism Detection
            plagiarism_results = plagiarism_detector.detect_plagiarism(processed_text)
            results['plagiarism'] = plagiarism_results

            # 2. Paraphrase Detection
            paraphrase_results = paraphrase_detector.detect_paraphrasing(processed_text)
            results['paraphrase'] = paraphrase_results

            # 3. AI Content Detection
            ai_results = ai_detector.detect_ai_content(processed_text)
            results['ai_content'] = ai_results

            # 4. Citation Analysis
            citation_results = citation_validator.validate_citations(processed_text)
            results['citations'] = citation_results

            # 5. Writing Analysis
            writing_results = writing_analyzer.analyze_writing(processed_text)
            results['writing_feedback'] = writing_results

            # 6. Resume Analysis (if applicable)
            resume_results = {}
            if analysis.analysis_type == 'resume':
                resume_results = resume_analyzer.analyze_resume(processed_text)
                results['resume_analysis'] = resume_results

            # Calculate overall scores
            overall_score = calculate_overall_score(results)

            # Update analysis record
            analysis.plagiarism_score = results['plagiarism']['overall_score']
            analysis.paraphrase_score = results['paraphrase']['overall_score']
            analysis.ai_content_score = results['ai_content']['overall_score']
            analysis.citation_score = results['citations']['overall_score']
            analysis.readability_score = results['writing_feedback']['readability_score']
            analysis.overall_integrity_score = overall_score

            # Store detailed results as JSON
            analysis.plagiarism_details = json.dumps(results['plagiarism'])
            analysis.paraphrase_details = json.dumps(results['paraphrase'])
            analysis.ai_content_details = json.dumps(results['ai_content'])
            analysis.citation_details = json.dumps(results['citations'])
            analysis.writing_feedback = json.dumps(results['writing_feedback'])
            analysis.resume_analysis = json.dumps(results['resume_analysis']) if resume_results else None

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            analysis.processing_time = processing_time

            analysis.status = 'completed'
            db.session.commit()

        except Exception as e:
            app.logger.error(f'Analysis failed for ID {analysis_id}: {str(e)}')
            analysis.status = 'failed'
            db.session.commit()

def calculate_overall_score(results):
    """Calculate overall integrity score"""
    weights = {
        'plagiarism': 0.25,
        'paraphrase': 0.20,
        'ai_content': 0.25,
        'citations': 0.15,
        'writing_feedback': 0.15
    }

    overall_score = (
        results['plagiarism']['overall_score'] * weights['plagiarism'] +
        results['paraphrase']['overall_score'] * weights['paraphrase'] +
        results['ai_content']['overall_score'] * weights['ai_content'] +
        results['citations']['overall_score'] * weights['citations'] +
        results['writing_feedback']['readability_score'] * weights['writing_feedback']
    )

    return round(overall_score, 2)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)