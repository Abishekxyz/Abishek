#!/usr/bin/env python3
"""
Plagiarism Detection Module
Detects plagiarized content using multiple techniques
"""

import os
import re
import hashlib
import requests
from typing import Dict, List, Tuple, Optional
from collections import Counter
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from bs4 import BeautifulSoup
import json
from config import Config

class PlagiarismDetector:
    """Advanced plagiarism detection system"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            stop_words='english',
            min_df=1
        )

        # Common phrases and patterns to ignore
        self.common_phrases = {
            'the purpose of this', 'in this paper we', 'the results show that',
            'it is important to', 'the main objective', 'based on the findings',
            'the study reveals', 'the research indicates', 'it can be seen that',
            'the data suggests', 'the analysis shows', 'the experiment demonstrates'
        }

        # Load known academic sources (in production, this would be a database)
        self.known_sources = self._load_known_sources()

    def _load_known_sources(self) -> Dict[str, str]:
        """Load known academic sources for comparison"""
        # In a real implementation, this would load from a database
        # For demo purposes, we'll use a small sample
        return {
            'sample1': 'The impact of artificial intelligence on modern education has been significant.',
            'sample2': 'Machine learning algorithms have revolutionized data analysis techniques.',
            'sample3': 'The development of neural networks has advanced computer vision capabilities.',
        }

    def detect_plagiarism(self, text: str, threshold: float = 0.3) -> Dict:
        """
        Comprehensive plagiarism detection

        Args:
            text: Input text to analyze
            threshold: Similarity threshold for flagging plagiarism

        Returns:
            Dictionary containing plagiarism analysis results
        """
        results = {
            'overall_score': 100.0,  # Start with 100% integrity
            'plagiarism_percentage': 0.0,
            'matches': [],
            'sources': [],
            'risk_level': 'low',
            'details': {}
        }

        if not text or len(text.strip()) < 50:
            return results

        # Clean and preprocess text
        clean_text = self._preprocess_text(text)

        # 1. Check against known academic sources
        source_matches = self._check_known_sources(clean_text)
        results['matches'].extend(source_matches)

        # 2. Check for exact phrase matches
        phrase_matches = self._check_common_phrases(clean_text)
        results['matches'].extend(phrase_matches)

        # 3. Online plagiarism check (using web search)
        online_matches = self._check_online_sources(clean_text)
        results['matches'].extend(online_matches)

        # 4. Semantic similarity analysis
        semantic_matches = self._semantic_similarity_check(clean_text)
        results['matches'].extend(semantic_matches)

        # Calculate overall plagiarism score
        results['plagiarism_percentage'] = self._calculate_plagiarism_score(results['matches'])
        results['overall_score'] = max(0, 100 - results['plagiarism_percentage'])

        # Determine risk level
        results['risk_level'] = self._determine_risk_level(results['plagiarism_percentage'])

        # Store detailed information
        results['details'] = {
            'total_matches': len(results['matches']),
            'unique_sources': len(set(match.get('source', 'unknown') for match in results['matches'])),
            'text_length': len(clean_text),
            'threshold_used': threshold
        }

        return results

    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize text for analysis"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove citations and references (basic pattern)
        text = re.sub(r'\[\d+\]|\(\d{4}\)|\b[A-Z][a-z]+ et al\.,?\s*\d{4}', '', text)

        # Remove common academic phrases that are not plagiarism
        for phrase in self.common_phrases:
            text = text.replace(phrase, '')

        return text.strip().lower()

    def _check_known_sources(self, text: str) -> List[Dict]:
        """Check against known academic sources"""
        matches = []

        for source_id, source_text in self.known_sources.items():
            similarity = self._calculate_similarity(text, source_text)

            if similarity > 0.2:  # 20% similarity threshold
                matches.append({
                    'type': 'known_source',
                    'source': f'Academic Source {source_id}',
                    'similarity': similarity,
                    'matched_text': self._find_matching_segments(text, source_text),
                    'severity': 'medium' if similarity > 0.5 else 'low'
                })

        return matches

    def _check_common_phrases(self, text: str) -> List[Dict]:
        """Check for commonly used academic phrases"""
        matches = []

        for phrase in self.common_phrases:
            if phrase.lower() in text:
                matches.append({
                    'type': 'common_phrase',
                    'source': 'Academic Writing Pattern',
                    'similarity': 1.0,
                    'matched_text': phrase,
                    'severity': 'low'  # Common phrases are not serious plagiarism
                })

        return matches

    def _check_online_sources(self, text: str) -> List[Dict]:
        """Check against online sources using web search"""
        matches = []

        try:
            # Use SerpAPI for web search (requires API key)
            if hasattr(Config, 'SERPAPI_KEY') and Config.SERPAPI_KEY:
                search_results = self._search_web(text[:500])  # Search first 500 chars

                for result in search_results[:3]:  # Check top 3 results
                    if 'snippet' in result:
                        snippet = result['snippet']
                        similarity = self._calculate_similarity(text, snippet)

                        if similarity > 0.15:  # Lower threshold for online sources
                            matches.append({
                                'type': 'online_source',
                                'source': result.get('title', 'Web Source'),
                                'url': result.get('link', ''),
                                'similarity': similarity,
                                'matched_text': snippet[:200] + '...',
                                'severity': 'high' if similarity > 0.4 else 'medium'
                            })

        except Exception as e:
            print(f"Online search error: {e}")

        return matches

    def _search_web(self, query: str) -> List[Dict]:
        """Search web using SerpAPI"""
        try:
            params = {
                'engine': 'google',
                'q': query,
                'api_key': Config.SERPAPI_KEY,
                'num': 5
            }

            response = requests.get('https://serpapi.com/search.json', params=params)
            data = response.json()

            return data.get('organic_results', [])

        except Exception as e:
            print(f"Web search failed: {e}")
            return []

    def _semantic_similarity_check(self, text: str) -> List[Dict]:
        """Check semantic similarity using TF-IDF"""
        matches = []

        # Split text into chunks for comparison
        chunks = self._split_into_chunks(text, chunk_size=200)

        for i, chunk1 in enumerate(chunks):
            for j, chunk2 in enumerate(chunks[i+1:], i+1):
                similarity = self._calculate_similarity(chunk1, chunk2)

                if similarity > 0.6:  # High similarity between chunks
                    matches.append({
                        'type': 'internal_similarity',
                        'source': 'Document Section',
                        'similarity': similarity,
                        'matched_text': f'Section similarity detected',
                        'severity': 'medium'
                    })

        return matches

    def _split_into_chunks(self, text: str, chunk_size: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size // 2):  # 50% overlap
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.split()) > 10:  # Only include substantial chunks
                chunks.append(chunk)

        return chunks

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        if not text1 or not text2:
            return 0.0

        # Use SequenceMatcher for basic similarity
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def _find_matching_segments(self, text1: str, text2: str, min_length: int = 20) -> str:
        """Find specific matching segments between texts"""
        matcher = SequenceMatcher(None, text1.lower(), text2.lower())

        # Get the longest matching block
        match = matcher.find_longest_match(0, len(text1), 0, len(text2))

        if match.size >= min_length:
            return text1[match.a:match.a + match.size]

        return "No significant matches found"

    def _calculate_plagiarism_score(self, matches: List[Dict]) -> float:
        """Calculate overall plagiarism percentage"""
        if not matches:
            return 0.0

        # Weight matches by severity and similarity
        total_weight = 0.0
        weighted_score = 0.0

        for match in matches:
            severity = match.get('severity', 'low')
            similarity = match.get('similarity', 0.0)

            # Assign weights based on severity
            if severity == 'high':
                weight = 3.0
            elif severity == 'medium':
                weight = 2.0
            else:
                weight = 1.0

            weighted_score += similarity * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return min(100.0, (weighted_score / total_weight) * 100)

    def _determine_risk_level(self, plagiarism_percentage: float) -> str:
        """Determine risk level based on plagiarism percentage"""
        if plagiarism_percentage >= 70:
            return 'critical'
        elif plagiarism_percentage >= 40:
            return 'high'
        elif plagiarism_percentage >= 20:
            return 'medium'
        else:
            return 'low'

    def generate_report(self, text: str, matches: List[Dict]) -> str:
        """Generate detailed plagiarism report"""
        report = []
        report.append("=== PLAGIARISM DETECTION REPORT ===\n")
        report.append(f"Text Length: {len(text)} characters\n")
        report.append(f"Total Matches Found: {len(matches)}\n")

        if matches:
            report.append("\nDetailed Matches:")
            for i, match in enumerate(matches, 1):
                report.append(f"\n{i}. Type: {match.get('type', 'unknown')}")
                report.append(f"   Source: {match.get('source', 'unknown')}")
                report.append(f"   Similarity: {match.get('similarity', 0)".1%"}")
                report.append(f"   Severity: {match.get('severity', 'unknown')}")
                if 'matched_text' in match:
                    report.append(f"   Matched Text: {match['matched_text'][:100]}...")
        else:
            report.append("\nNo significant plagiarism detected.")

        return '\n'.join(report)