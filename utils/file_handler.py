#!/usr/bin/env python3
"""
File Handling Utilities
Handles various file types (PDF, DOCX, TXT) for text extraction
"""

import os
import io
from typing import Dict, List, Tuple, Optional, BinaryIO
import PyPDF2
from docx import Document
import pandas as pd
import json
import re
from werkzeug.utils import secure_filename
from config import Config

class FileHandler:
    """File handling utilities for document processing"""

    def __init__(self):
        self.supported_extensions = {'.pdf', '.docx', '.doc', '.txt', '.rtf'}
        self.max_file_size = 50 * 1024 * 1024  # 50MB

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"

                return text.strip()

        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""

            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + " "

            return text.strip()

        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")

    def extract_text_from_txt(self, file_path: str, encoding: str = 'utf-8') -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read().strip()

        except UnicodeDecodeError:
            # Try different encodings
            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            for enc in encodings:
                try:
                    with open(file_path, 'r', encoding=enc) as file:
                        return file.read().strip()
                except UnicodeDecodeError:
                    continue

            raise Exception("Could not decode text file with any supported encoding")

        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")

    def extract_text_from_rtf(self, file_path: str) -> str:
        """Extract text from RTF file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                rtf_content = file.read()

            # Simple RTF text extraction (remove RTF formatting codes)
            # This is a basic implementation - for production, consider using a dedicated RTF parser
            text = re.sub(r'\\[a-z]+\d*', '', rtf_content)  # Remove RTF commands
            text = re.sub(r'[{}]', '', text)  # Remove braces
            text = re.sub(r'\\\*.*?;', '', text)  # Remove control words with parameters

            return text.strip()

        except Exception as e:
            raise Exception(f"Error extracting text from RTF: {str(e)}")

    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from any supported file type"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            raise ValueError(f"File too large: {file_size} bytes (max: {self.max_file_size})")

        # Get file extension
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()

        if extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif extension in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        elif extension == '.txt':
            return self.extract_text_from_txt(file_path)
        elif extension == '.rtf':
            return self.extract_text_from_rtf(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")

    def save_uploaded_file(self, file: BinaryIO, upload_folder: str, filename: str) -> str:
        """Save uploaded file to disk"""
        # Secure the filename
        secure_name = secure_filename(filename)

        # Create unique filename if file exists
        file_path = os.path.join(upload_folder, secure_name)
        counter = 1

        while os.path.exists(file_path):
            name, ext = os.path.splitext(secure_name)
            secure_name = f"{name}_{counter}{ext}"
            file_path = os.path.join(upload_folder, secure_name)
            counter += 1

        # Save file
        file.seek(0)
        with open(file_path, 'wb') as f:
            f.write(file.read())

        return file_path

    def get_file_metadata(self, file_path: str) -> Dict:
        """Get metadata about a file"""
        try:
            stat = os.stat(file_path)

            metadata = {
                'filename': os.path.basename(file_path),
                'size': stat.st_size,
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'extension': os.path.splitext(file_path)[1].lower(),
                'is_supported': os.path.splitext(file_path)[1].lower() in self.supported_extensions
            }

            # Try to detect MIME type
            import mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            metadata['mime_type'] = mime_type or 'application/octet-stream'

            return metadata

        except Exception as e:
            return {
                'error': str(e),
                'filename': os.path.basename(file_path),
                'is_supported': False
            }

    def validate_file(self, file_path: str) -> Dict:
        """Validate file for processing"""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        # Check if file exists
        if not os.path.exists(file_path):
            validation['is_valid'] = False
            validation['errors'].append('File does not exist')
            return validation

        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            validation['errors'].append('File is empty')
            validation['is_valid'] = False
        elif file_size > self.max_file_size:
            validation['errors'].append(f'File too large: {file_size} bytes')
            validation['is_valid'] = False

        # Check extension
        extension = os.path.splitext(file_path)[1].lower()
        if extension not in self.supported_extensions:
            validation['warnings'].append(f'Unsupported file type: {extension}')

        # Try to read file
        try:
            with open(file_path, 'rb') as f:
                header = f.read(1024)  # Read first 1KB

            # Basic file type detection
            if extension == '.pdf' and not header.startswith(b'%PDF'):
                validation['warnings'].append('File may not be a valid PDF')
            elif extension == '.docx' and not header.startswith(b'PK'):
                validation['warnings'].append('File may not be a valid DOCX')

        except Exception as e:
            validation['errors'].append(f'Cannot read file: {str(e)}')
            validation['is_valid'] = False

        return validation

    def create_text_preview(self, text: str, max_length: int = 500) -> str:
        """Create a preview of extracted text"""
        if len(text) <= max_length:
            return text

        # Try to break at sentence boundary
        preview = text[:max_length]
        last_sentence_end = max(
            preview.rfind('.'),
            preview.rfind('!'),
            preview.rfind('?')
        )

        if last_sentence_end > max_length * 0.7:  # If we can break at a reasonable sentence
            preview = preview[:last_sentence_end + 1]

        return preview + "..."

    def estimate_processing_time(self, file_path: str) -> int:
        """Estimate processing time in seconds"""
        file_size = os.path.getsize(file_path)

        # Rough estimation based on file size
        # PDF: ~1 second per 100KB
        # DOCX: ~0.5 seconds per 100KB
        # TXT: ~0.1 seconds per 100KB

        extension = os.path.splitext(file_path)[1].lower()

        if extension == '.pdf':
            base_time = file_size / (100 * 1024)  # 100KB chunks
        elif extension in ['.docx', '.doc']:
            base_time = file_size / (200 * 1024)  # 200KB chunks
        else:
            base_time = file_size / (1000 * 1024)  # 1MB chunks

        # Add base processing time
        return max(5, int(base_time + 2))

    def cleanup_old_files(self, upload_folder: str, max_age_hours: int = 24) -> int:
        """Clean up old uploaded files"""
        import time

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        cleaned_count = 0

        try:
            for filename in os.listdir(upload_folder):
                file_path = os.path.join(upload_folder, filename)

                # Check if file is old enough
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)

                    if file_age > max_age_seconds:
                        try:
                            os.remove(file_path)
                            cleaned_count += 1
                        except Exception as e:
                            print(f"Could not remove old file {file_path}: {e}")

        except Exception as e:
            print(f"Error during cleanup: {e}")

        return cleaned_count

    def get_file_info(self, file_path: str) -> Dict:
        """Get comprehensive file information"""
        metadata = self.get_file_metadata(file_path)
        validation = self.validate_file(file_path)

        # Try to extract text for preview
        preview = ""
        if validation['is_valid']:
            try:
                text = self.extract_text_from_file(file_path)
                preview = self.create_text_preview(text, 300)
            except Exception as e:
                preview = f"Error extracting text: {str(e)}"

        info = {
            'metadata': metadata,
            'validation': validation,
            'preview': preview,
            'estimated_processing_time': self.estimate_processing_time(file_path) if validation['is_valid'] else 0
        }

        return info