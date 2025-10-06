"""
Database configuration and initialization
"""

import sqlite3
import os


def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect('academic_integrity.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Submissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            submission_type TEXT NOT NULL,
            originality_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            analysis_results TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Document history table (for tracking edits)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS document_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL,
            content TEXT,
            edit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            changes_detected TEXT,
            FOREIGN KEY (submission_id) REFERENCES submissions (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")


if __name__ == '__main__':
    init_db()
