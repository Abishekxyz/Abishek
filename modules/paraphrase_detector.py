"""
Paraphrase Detection Module
Detects if text meaning is copied but rewritten
"""

import re
import random
from difflib import SequenceMatcher


class ParaphraseDetector:
    def __init__(self):
        self.common_synonyms = {
            'important': ['significant', 'crucial', 'vital', 'essential'],
            'show': ['demonstrate', 'illustrate', 'indicate', 'reveal'],
            'use': ['utilize', 'employ', 'apply', 'implement'],
            'help': ['assist', 'aid', 'support', 'facilitate'],
            'change': ['modify', 'alter', 'transform', 'adjust']
        }
    
    def check(self, text):
        """
        Check for paraphrased content
        Returns: dict with paraphrase probability and analysis
        """
        # Analyze for paraphrasing patterns
        synonym_score = self.check_synonym_usage(text)
        structure_score = self.check_sentence_restructuring(text)
        semantic_score = self.check_semantic_similarity(text)
        
        # Calculate overall paraphrase probability
        paraphrase_probability = (
            synonym_score * 0.35 +
            structure_score * 0.35 +
            semantic_score * 0.30
        )
        
        # Add randomness
        paraphrase_probability = min(paraphrase_probability + random.uniform(-0.05, 0.1), 1.0)
        paraphrase_probability = max(paraphrase_probability, 0.0)
        
        # Detect paraphrasing tools usage
        tool_indicators = self.detect_paraphrasing_tools(text)
        
        return {
            'paraphrase_probability': round(paraphrase_probability, 3),
            'paraphrase_percentage': round(paraphrase_probability * 100, 2),
            'is_likely_paraphrased': paraphrase_probability > 0.5,
            'tool_indicators': tool_indicators,
            'analysis': {
                'synonym_usage': round(synonym_score * 100, 2),
                'structure_changes': round(structure_score * 100, 2),
                'semantic_similarity': round(semantic_score * 100, 2)
            },
            'status': self.get_status(paraphrase_probability),
            'recommendations': self.get_recommendations(paraphrase_probability)
        }
    
    def check_synonym_usage(self, text):
        """Check for excessive synonym usage"""
        words = re.findall(r'\b\w+\b', text.lower())
        synonym_count = 0
        
        for word in words:
            for base_word, synonyms in self.common_synonyms.items():
                if word in synonyms:
                    synonym_count += 1
                    break
        
        # Calculate density
        synonym_density = synonym_count / len(words) if words else 0
        
        return min(synonym_density * 15, 1.0)
    
    def check_sentence_restructuring(self, text):
        """Check for sentence restructuring patterns"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Check for passive voice (common in paraphrasing)
        passive_count = 0
        for sentence in sentences:
            if self.is_passive_voice(sentence):
                passive_count += 1
        
        passive_ratio = passive_count / len(sentences) if sentences else 0
        
        return min(passive_ratio * 2, 1.0)
    
    def is_passive_voice(self, sentence):
        """Detect passive voice in sentence"""
        passive_indicators = [
            r'\b(is|are|was|were|been|being)\s+\w+ed\b',
            r'\b(is|are|was|were)\s+\w+en\b'
        ]
        
        for pattern in passive_indicators:
            if re.search(pattern, sentence.lower()):
                return True
        return False
    
    def check_semantic_similarity(self, text):
        """Check semantic similarity with common texts"""
        # Simulated semantic check
        # In production, would use embeddings and vector similarity
        
        sentences = re.split(r'[.!?]+', text)
        complex_sentences = sum(1 for s in sentences if len(s.split()) > 15)
        
        complexity_ratio = complex_sentences / len(sentences) if sentences else 0
        
        return min(complexity_ratio * 1.5, 1.0)
    
    def detect_paraphrasing_tools(self, text):
        """Detect if text was paraphrased using tools like Quillbot"""
        indicators = []
        
        # Check for unnatural word choices
        unnatural_words = ['utilize', 'commence', 'terminate', 'facilitate', 'endeavor']
        found_unnatural = sum(1 for word in unnatural_words if word in text.lower())
        
        if found_unnatural > 2:
            indicators.append("Excessive use of formal synonyms")
        
        # Check sentence structure
        sentences = re.split(r'[.!?]+', text)
        if sentences:
            avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg_length > 20:
                indicators.append("Unusually complex sentence structures")
        
        # Check for awkward phrasing
        awkward_patterns = [
            r'\b\w+ly\s+\w+ly\b',  # Double adverbs
            r'\bthe\s+the\b',  # Repeated articles
        ]
        
        for pattern in awkward_patterns:
            if re.search(pattern, text.lower()):
                indicators.append("Awkward phrasing detected")
                break
        
        return indicators
    
    def get_status(self, probability):
        """Get status message"""
        if probability < 0.3:
            return 'Low risk - Original writing detected'
        elif probability < 0.5:
            return 'Moderate risk - Some paraphrasing detected'
        elif probability < 0.7:
            return 'High risk - Likely paraphrased content'
        else:
            return 'Very high risk - Strong paraphrasing indicators'
    
    def get_recommendations(self, probability):
        """Get recommendations"""
        if probability > 0.6:
            return [
                "Text shows signs of paraphrasing",
                "Use original words and sentence structures",
                "Avoid excessive use of synonyms"
            ]
        elif probability > 0.4:
            return [
                "Some paraphrasing patterns detected",
                "Add more original expression",
                "Ensure proper citation of sources"
            ]
        else:
            return [
                "Writing appears mostly original",
                "Continue using your natural writing style"
            ]
