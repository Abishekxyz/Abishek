#!/usr/bin/env python3
"""
Text Processing Utilities
Common text processing functions for the academic integrity checker
"""

import re
import unicodedata
from typing import List, Dict, Tuple, Optional
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
import spacy
from config import Config

class TextProcessor:
    """Text processing utilities"""

    def __init__(self):
        # Initialize NLTK components
        try:
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
            self.stemmer = PorterStemmer()
        except LookupError:
            nltk.download('stopwords')
            nltk.download('wordnet')
            nltk.download('punkt')
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
            self.stemmer = PorterStemmer()

        # Initialize spaCy
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            print("Downloading spaCy model...")
            import subprocess
            subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'], check=True)
            self.nlp = spacy.load('en_core_web_sm')

    def preprocess_text(self, text: str) -> str:
        """
        Comprehensive text preprocessing

        Args:
            text: Raw text to preprocess

        Returns:
            Cleaned and normalized text
        """
        if not text:
            return ""

        # 1. Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)

        # 2. Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # 3. Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.,!?\-:;()[\]{}]', '', text)

        # 4. Convert to lowercase for analysis
        text = text.lower()

        # 5. Remove common academic stop words but keep important ones
        words = word_tokenize(text)
        filtered_words = []

        for word in words:
            # Keep academic terms that might be important for plagiarism detection
            academic_terms = {
                'methodology', 'hypothesis', 'analysis', 'research', 'study',
                'data', 'results', 'conclusion', 'introduction', 'literature'
            }

            if word in academic_terms or word not in self.stop_words or len(word) <= 2:
                filtered_words.append(word)

        # 6. Rejoin words
        processed_text = ' '.join(filtered_words)

        # 7. Remove very short words (except academic terms)
        words = processed_text.split()
        filtered_words = []

        for word in words:
            if len(word) > 2 or word in academic_terms:
                filtered_words.append(word)

        return ' '.join(filtered_words)

    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text"""
        try:
            return sent_tokenize(text)
        except:
            # Fallback if sent_tokenize fails
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]

    def extract_words(self, text: str) -> List[str]:
        """Extract words from text"""
        try:
            return word_tokenize(text.lower())
        except:
            # Fallback tokenization
            words = re.findall(r'\b\w+\b', text.lower())
            return words

    def remove_citations(self, text: str) -> str:
        """Remove citations from text for cleaner analysis"""
        # Remove various citation formats
        patterns = [
            # APA: (Author, Year)
            r'\([A-Z][a-z]+(?:\s+[A-Z]\.)?(?:\s*&\s*[A-Z][a-z]+)?,\s*\d{4}\)',
            # MLA: (Author Page)
            r'\([A-Z][a-z]+(?:\s+[A-Z]\.)?(?:\s*&\s*[A-Z][a-z]+)?\s+\d+\)',
            # IEEE: [1]
            r'\[\d+(?:\s*,\s*\d+)*\]',
            # Footnotes: 1., (1), etc.
            r'\b\d+\.\s*',
            r'\(\d+\)',
            # DOI links
            r'doi:\s*\d+\.\d{4,9}/[^\s]+',
            # URLs
            r'https?://[^\s]+',
        ]

        clean_text = text
        for pattern in patterns:
            clean_text = re.sub(pattern, '', clean_text)

        return clean_text.strip()

    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases from text"""
        # Use spaCy for noun phrase extraction
        doc = self.nlp(text)

        # Extract noun chunks
        noun_chunks = [chunk.text for chunk in doc.noun_chunks]

        # Filter and rank phrases
        phrases = []
        for chunk in noun_chunks:
            # Filter out very short or very long phrases
            if 3 <= len(chunk.split()) <= 6:
                phrases.append(chunk)

        # Remove duplicates and return top phrases
        unique_phrases = list(set(phrases))
        return unique_phrases[:max_phrases]

    def calculate_text_stats(self, text: str) -> Dict:
        """Calculate basic text statistics"""
        sentences = self.extract_sentences(text)
        words = self.extract_words(text)

        stats = {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_words_per_sentence': len(words) / len(sentences) if sentences else 0,
            'avg_characters_per_word': sum(len(word) for word in words) / len(words) if words else 0,
            'unique_words': len(set(words)),
            'lexical_diversity': len(set(words)) / len(words) if words else 0,
        }

        return stats

    def detect_language(self, text: str) -> str:
        """Detect text language (simplified)"""
        # Simple language detection based on common words
        english_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'
        }

        words = set(self.extract_words(text.lower()))
        english_overlap = len(words & english_words)

        if english_overlap > 5:
            return 'en'
        else:
            return 'unknown'

    def find_similar_sections(self, text1: str, text2: str, min_length: int = 50) -> List[Dict]:
        """Find similar sections between two texts"""
        sentences1 = self.extract_sentences(text1)
        sentences2 = self.extract_sentences(text2)

        similar_sections = []

        for i, sent1 in enumerate(sentences1):
            for j, sent2 in enumerate(sentences2):
                # Simple similarity check
                words1 = set(self.extract_words(sent1))
                words2 = set(self.extract_words(sent2))

                if words1 and words2:
                    similarity = len(words1 & words2) / len(words1 | words2)

                    if similarity > 0.3 and len(sent1) > min_length:  # 30% similarity
                        similar_sections.append({
                            'text1': sent1,
                            'text2': sent2,
                            'similarity': similarity,
                            'position1': i,
                            'position2': j
                        })

        # Sort by similarity
        similar_sections.sort(key=lambda x: x['similarity'], reverse=True)

        return similar_sections[:10]  # Return top 10

    def clean_filename(self, filename: str) -> str:
        """Clean filename for safe storage"""
        # Remove path separators and dangerous characters
        clean_name = re.sub(r'[<>:"/\\|?*]', '', filename)

        # Ensure it's not too long
        if len(clean_name) > 100:
            name_part, ext = os.path.splitext(clean_name)
            clean_name = name_part[:96] + ext

        return clean_name

    def extract_metadata(self, text: str) -> Dict:
        """Extract metadata from document text"""
        metadata = {
            'title': None,
            'author': None,
            'date': None,
            'keywords': [],
            'abstract': None
        }

        lines = text.split('\n')[:20]  # Check first 20 lines

        # Look for title (first non-empty line)
        for line in lines:
            if line.strip() and not metadata['title']:
                metadata['title'] = line.strip()
                break

        # Look for author
        author_patterns = [
            r'author:\s*(.+)',
            r'by:\s*(.+)',
            r'written by:\s*(.+)'
        ]

        for line in lines:
            for pattern in author_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    metadata['author'] = match.group(1).strip()
                    break

        # Look for date
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{4}-\d{1,2}-\d{1,2}\b',
            r'\b\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}\b'
        ]

        for line in lines:
            for pattern in date_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    metadata['date'] = match.group(0)
                    break

        return metadata

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.split()) > 50:  # Only include substantial chunks
                chunks.append(chunk)

        return chunks

    def highlight_similarities(self, original_text: str, similar_text: str) -> Dict:
        """Highlight similarities between two texts"""
        # Simple word-level highlighting
        words1 = set(self.extract_words(original_text.lower()))
        words2 = set(self.extract_words(similar_text.lower()))

        common_words = words1 & words2
        unique_words1 = words1 - words2
        unique_words2 = words2 - words1

        return {
            'common_words': list(common_words),
            'unique_to_original': list(unique_words1),
            'unique_to_similar': list(unique_words2),
            'common_count': len(common_words),
            'unique_count': len(unique_words1) + len(unique_words2)
        }

    def normalize_text(self, text: str) -> str:
        """Normalize text for consistent processing"""
        # Remove accents and diacritics
        text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('ascii')

        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        return text.strip()