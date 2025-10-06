#!/usr/bin/env python3
"""
Database models for Academic Integrity Checker
"""

from app import db
from datetime import datetime
import json

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'is_admin': self.is_admin
        }

class Analysis(db.Model):
    """Analysis model for storing analysis results"""
    __tablename__ = 'analyses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255))
    file_type = db.Column(db.String(50))
    text_content = db.Column(db.Text)
    analysis_type = db.Column(db.String(50), default='document')  # document, resume, text

    # Status tracking
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime)

    # File metadata
    file_size = db.Column(db.Integer)  # bytes
    processing_time = db.Column(db.Float)  # seconds

    # Overall scores (0-100, higher is better for integrity)
    overall_integrity_score = db.Column(db.Float)
    plagiarism_score = db.Column(db.Float)
    paraphrase_score = db.Column(db.Float)
    ai_content_score = db.Column(db.Float)
    citation_score = db.Column(db.Float)
    readability_score = db.Column(db.Float)

    # Detailed results as JSON strings
    plagiarism_details = db.Column(db.Text)  # JSON
    paraphrase_details = db.Column(db.Text)  # JSON
    ai_content_details = db.Column(db.Text)  # JSON
    citation_details = db.Column(db.Text)  # JSON
    writing_feedback = db.Column(db.Text)  # JSON
    resume_analysis = db.Column(db.Text)  # JSON for resume analysis

    # Additional metadata
    word_count = db.Column(db.Integer)
    character_count = db.Column(db.Integer)
    language_detected = db.Column(db.String(10))

    def __repr__(self):
        return f'<Analysis {self.id} - {self.analysis_type}>'

    def to_dict(self):
        """Convert analysis to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'file_type': self.file_type,
            'analysis_type': self.analysis_type,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'file_size': self.file_size,
            'processing_time': self.processing_time,
            'overall_integrity_score': self.overall_integrity_score,
            'plagiarism_score': self.plagiarism_score,
            'paraphrase_score': self.paraphrase_score,
            'ai_content_score': self.ai_content_score,
            'citation_score': self.citation_score,
            'readability_score': self.readability_score,
            'word_count': self.word_count,
            'character_count': self.character_count,
            'language_detected': self.language_detected
        }

    def get_plagiarism_details(self):
        """Parse plagiarism details JSON"""
        return json.loads(self.plagiarism_details) if self.plagiarism_details else {}

    def get_paraphrase_details(self):
        """Parse paraphrase details JSON"""
        return json.loads(self.paraphrase_details) if self.paraphrase_details else {}

    def get_ai_content_details(self):
        """Parse AI content details JSON"""
        return json.loads(self.ai_content_details) if self.ai_content_details else {}

    def get_citation_details(self):
        """Parse citation details JSON"""
        return json.loads(self.citation_details) if self.citation_details else {}

    def get_writing_feedback(self):
        """Parse writing feedback JSON"""
        return json.loads(self.writing_feedback) if self.writing_feedback else {}

    def get_resume_analysis(self):
        """Parse resume analysis JSON"""
        return json.loads(self.resume_analysis) if self.resume_analysis else {}

class Citation(db.Model):
    """Citation model for storing citation data"""
    __tablename__ = 'citations'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    citation_text = db.Column(db.Text, nullable=False)
    citation_style = db.Column(db.String(20))  # apa, mla, ieee
    is_valid = db.Column(db.Boolean)
    suggested_correction = db.Column(db.Text)
    source_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Citation {self.id} - {self.citation_style}>'

class DocumentHistory(db.Model):
    """Document history for tracking changes"""
    __tablename__ = 'document_history'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    text_snapshot = db.Column(db.Text)
    changes_detected = db.Column(db.Text)  # JSON of changes
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DocumentHistory {self.analysis_id} v{self.version}>'

class UserPreferences(db.Model):
    """User preferences and settings"""
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    setting_key = db.Column(db.String(100), nullable=False)
    setting_value = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserPreferences {self.user_id} - {self.setting_key}>'