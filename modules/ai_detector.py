"""
AI-Generated Text Detection Module
Detects if text is written by AI (ChatGPT, GPT-3, etc.)
"""

import re
import random
from collections import Counter


class AIContentDetector:
    def __init__(self):
        # AI writing patterns and characteristics
        self.ai_patterns = [
            r'\b(furthermore|moreover|additionally|consequently|nevertheless)\b',
            r'\b(it is important to note|it should be noted|it is worth mentioning)\b',
            r'\b(in conclusion|to summarize|in summary|overall)\b',
            r'\b(various|numerous|several|multiple)\b',
            r'\b(significant|substantial|considerable|noteworthy)\b',
        ]
        
        # Common AI transition words
        self.ai_transitions = {
            'furthermore', 'moreover', 'additionally', 'consequently', 
            'nevertheless', 'therefore', 'thus', 'hence'
        }
    
    def detect(self, text):
        """
        Detect AI-generated content
        Returns: dict with probability, indicators, and detailed analysis
        """
        # Analyze various features
        pattern_score = self.check_ai_patterns(text)
        repetition_score = self.check_repetition(text)
        uniformity_score = self.check_uniformity(text)
        vocabulary_score = self.check_vocabulary_diversity(text)
        sentence_structure_score = self.check_sentence_structure(text)
        
        # Calculate overall AI probability
        ai_probability = (
            pattern_score * 0.25 +
            repetition_score * 0.20 +
            uniformity_score * 0.20 +
            vocabulary_score * 0.20 +
            sentence_structure_score * 0.15
        )
        
        # Add some randomness to simulate ML model
        ai_probability = min(ai_probability + random.uniform(-0.1, 0.1), 1.0)
        ai_probability = max(ai_probability, 0.0)
        
        # Detect specific indicators
        indicators = self.get_indicators(text)
        
        # Generate confidence breakdown
        confidence_breakdown = {
            'pattern_matching': round(pattern_score * 100, 2),
            'repetition_analysis': round(repetition_score * 100, 2),
            'text_uniformity': round(uniformity_score * 100, 2),
            'vocabulary_diversity': round(vocabulary_score * 100, 2),
            'sentence_structure': round(sentence_structure_score * 100, 2)
        }
        
        return {
            'ai_probability': round(ai_probability, 3),
            'ai_percentage': round(ai_probability * 100, 2),
            'is_likely_ai': ai_probability > 0.6,
            'confidence_level': self.get_confidence_level(ai_probability),
            'indicators': indicators,
            'confidence_breakdown': confidence_breakdown,
            'status': self.get_status(ai_probability),
            'recommendations': self.get_recommendations(ai_probability)
        }
    
    def check_ai_patterns(self, text):
        """Check for common AI writing patterns"""
        text_lower = text.lower()
        pattern_count = 0
        
        for pattern in self.ai_patterns:
            matches = re.findall(pattern, text_lower)
            pattern_count += len(matches)
        
        # Normalize by text length
        words = text.split()
        pattern_density = pattern_count / len(words) if words else 0
        
        return min(pattern_density * 20, 1.0)  # Scale to 0-1
    
    def check_repetition(self, text):
        """Check for repetitive sentence structures"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 3:
            return 0.3
        
        # Check sentence length consistency (AI tends to be more uniform)
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        
        # Low variance indicates high uniformity (AI trait)
        uniformity = 1.0 - min(variance / 100, 1.0)
        
        return uniformity * 0.7
    
    def check_uniformity(self, text):
        """Check text uniformity (AI text tends to be more uniform)"""
        paragraphs = text.split('\n\n')
        if len(paragraphs) < 2:
            paragraphs = text.split('\n')
        
        paragraph_lengths = [len(p.split()) for p in paragraphs if p.strip()]
        
        if len(paragraph_lengths) < 2:
            return 0.5
        
        avg_length = sum(paragraph_lengths) / len(paragraph_lengths)
        variance = sum((l - avg_length) ** 2 for l in paragraph_lengths) / len(paragraph_lengths)
        
        # Low variance = high uniformity = likely AI
        uniformity = 1.0 - min(variance / 500, 1.0)
        
        return uniformity
    
    def check_vocabulary_diversity(self, text):
        """Check vocabulary diversity (AI tends to use more formal vocabulary)"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        if len(words) < 10:
            return 0.5
        
        # Calculate type-token ratio
        unique_words = set(words)
        diversity = len(unique_words) / len(words)
        
        # AI text often has moderate diversity (not too low, not too high)
        if 0.4 <= diversity <= 0.7:
            return 0.7  # Typical AI range
        else:
            return 0.3  # More human-like
    
    def check_sentence_structure(self, text):
        """Analyze sentence structure patterns"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Check for consistent sentence beginnings (AI pattern)
        first_words = [s.split()[0].lower() for s in sentences if s.split()]
        first_word_freq = Counter(first_words)
        
        # High repetition of first words indicates AI
        max_freq = max(first_word_freq.values()) if first_word_freq else 1
        repetition_ratio = max_freq / len(sentences) if sentences else 0
        
        return min(repetition_ratio * 2, 1.0)
    
    def get_indicators(self, text):
        """Get specific AI indicators found in text"""
        indicators = []
        text_lower = text.lower()
        
        # Check for AI phrases
        ai_phrases = [
            'it is important to note',
            'it should be noted',
            'in conclusion',
            'to summarize',
            'furthermore',
            'moreover',
            'consequently'
        ]
        
        for phrase in ai_phrases:
            if phrase in text_lower:
                indicators.append(f"Common AI phrase: '{phrase}'")
        
        # Check sentence length consistency
        sentences = re.split(r'[.!?]+', text)
        lengths = [len(s.split()) for s in sentences if s.strip()]
        if lengths:
            avg_length = sum(lengths) / len(lengths)
            if 15 <= avg_length <= 25:
                indicators.append(f"Consistent sentence length (avg: {int(avg_length)} words)")
        
        # Check for formal language
        formal_words = sum(1 for word in ['significant', 'substantial', 'numerous', 'various'] 
                          if word in text_lower)
        if formal_words > 3:
            indicators.append("High frequency of formal vocabulary")
        
        return indicators[:5]  # Return top 5 indicators
    
    def get_confidence_level(self, probability):
        """Get confidence level description"""
        if probability < 0.3:
            return 'High confidence - Likely human-written'
        elif probability < 0.5:
            return 'Moderate confidence - Mostly human-written'
        elif probability < 0.7:
            return 'Moderate confidence - Possibly AI-assisted'
        else:
            return 'High confidence - Likely AI-generated'
    
    def get_status(self, probability):
        """Get status message"""
        if probability < 0.3:
            return 'Human-written'
        elif probability < 0.5:
            return 'Mostly human-written'
        elif probability < 0.7:
            return 'Possibly AI-assisted'
        else:
            return 'Likely AI-generated'
    
    def get_recommendations(self, probability):
        """Get recommendations based on detection"""
        if probability > 0.7:
            return [
                "Text shows strong AI characteristics",
                "Consider adding more personal voice and varied sentence structure",
                "Review for overly formal or repetitive patterns"
            ]
        elif probability > 0.5:
            return [
                "Some AI patterns detected",
                "Add more personal examples and unique insights",
                "Vary sentence structure and vocabulary"
            ]
        else:
            return [
                "Text appears mostly original",
                "Continue writing in your natural style",
                "Maintain current level of authenticity"
            ]
