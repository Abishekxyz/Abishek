"""
File handling utilities for extracting text from various file formats
"""

import os
import re


def extract_text_from_file(filepath):
    """Extract text from uploaded files (txt, pdf, docx)"""
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.txt':
        return extract_from_txt(filepath)
    elif ext == '.pdf':
        return extract_from_pdf(filepath)
    elif ext in ['.docx', '.doc']:
        return extract_from_docx(filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def extract_from_txt(filepath):
    """Extract text from TXT file"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def extract_from_pdf(filepath):
    """Extract text from PDF file"""
    try:
        import PyPDF2
        text = []
        with open(filepath, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        return '\n'.join(text)
    except ImportError:
        # Fallback if PyPDF2 not installed
        return "PDF extraction requires PyPDF2. Please install it."


def extract_from_docx(filepath):
    """Extract text from DOCX file"""
    try:
        import docx
        doc = docx.Document(filepath)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    except ImportError:
        # Fallback if python-docx not installed
        return "DOCX extraction requires python-docx. Please install it."


def clean_text(text):
    """Clean and normalize text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s.,!?;:()\[\]{}"\'-]', '', text)
    return text.strip()
