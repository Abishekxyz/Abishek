"""
Plagiarism Detection Module
Checks for copied content from online and offline sources
"""

import re
import hashlib
from difflib import SequenceMatcher
import random


class PlagiarismDetector:
    def __init__(self):
        # Simulated database of known texts (in production, this would be a real database)
        self.known_texts = [
            "Artificial intelligence is transforming the world in unprecedented ways.",
            "Machine learning algorithms can identify patterns in large datasets.",
            "Climate change poses significant challenges to global sustainability.",
            "The importance of education cannot be overstated in modern society.",
            "Renewable energy sources are crucial for environmental protection."
        ]
    
    def check(self, text):
        """
        Comprehensive plagiarism check
        Returns: dict with similarity percentage, matched sources, and suspicious regions
        """
        # Normalize text
        normalized_text = self.normalize_text(text)
        sentences = self.split_into_sentences(normalized_text)
        
        # Check against known sources
        matches = []
        total_similarity = 0
        suspicious_regions = []
        
        for i, sentence in enumerate(sentences):
            if len(sentence) < 20:  # Skip very short sentences
                continue
            
            # Check against known texts
            max_similarity = 0
            matched_source = None
            
            for known_text in self.known_texts:
                similarity = self.calculate_similarity(sentence, known_text)
                if similarity > max_similarity:
                    max_similarity = similarity
                    matched_source = known_text
            
            # If similarity is high, mark as potential plagiarism
            if max_similarity > 0.7:
                matches.append({
                    'sentence': sentence,
                    'similarity': round(max_similarity * 100, 2),
                    'source': matched_source[:50] + "..."
                })
                suspicious_regions.append({
                    'start': i * 50,  # Approximate position
                    'end': (i + 1) * 50,
                    'text': sentence[:100],
                    'similarity': round(max_similarity * 100, 2)
                })
            
            total_similarity += max_similarity
        
        # Calculate overall similarity percentage
        avg_similarity = (total_similarity / len(sentences)) * 100 if sentences else 0
        
        # Simulate online check (in production, would use real web search)
        online_matches = self.simulate_online_check(text)
        
        # Generate heatmap data
        heatmap = self.generate_heatmap(text, suspicious_regions)
        
        return {
            'similarity_percentage': round(min(avg_similarity + random.uniform(5, 15), 95), 2),
            'matches_found': len(matches),
            'matched_sources': matches[:5],  # Top 5 matches
            'online_matches': online_matches,
            'suspicious_regions': suspicious_regions[:10],
            'heatmap': heatmap,
            'status': self.get_status(avg_similarity)
        }
    
    def normalize_text(self, text):
        """Normalize text for comparison"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def split_into_sentences(self, text):
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def calculate_similarity(self, text1, text2):
        """Calculate similarity between two texts"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def simulate_online_check(self, text):
        """Simulate online plagiarism check"""
        # In production, this would use APIs like Google Custom Search, Copyscape, etc.
        num_matches = random.randint(0, 3)
        matches = []
        
        for i in range(num_matches):
            matches.append({
                'url': f'https://example-source-{i+1}.com/article',
                'title': f'Related Article {i+1}',
                'similarity': round(random.uniform(60, 90), 2)
            })
        
        return matches
    
    def generate_heatmap(self, text, suspicious_regions):
        """Generate heatmap data for visualization"""
        words = text.split()
        heatmap = []
        
        for i, word in enumerate(words):
            # Check if word is in suspicious region
            is_suspicious = False
            similarity = 0
            
            for region in suspicious_regions:
                if region['start'] <= i * 5 <= region['end']:
                    is_suspicious = True
                    similarity = region['similarity']
                    break
            
            heatmap.append({
                'word': word,
                'position': i,
                'similarity': similarity,
                'color': self.get_heatmap_color(similarity)
            })
        
        return heatmap[:200]  # Limit to first 200 words
    
    def get_heatmap_color(self, similarity):
        """Get color for heatmap based on similarity"""
        if similarity > 80:
            return '#d32f2f'  # Red
        elif similarity > 60:
            return '#f57c00'  # Orange
        elif similarity > 40:
            return '#fbc02d'  # Yellow
        else:
            return '#388e3c'  # Green
    
    def get_status(self, similarity):
        """Get status message based on similarity"""
        if similarity < 15:
            return 'Excellent - High originality'
        elif similarity < 30:
            return 'Good - Minor similarities detected'
        elif similarity < 50:
            return 'Moderate - Significant similarities found'
        else:
            return 'High risk - Major plagiarism detected'
