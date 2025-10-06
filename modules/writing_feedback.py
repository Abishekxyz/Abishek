"""
Writing Style Feedback Module
Provides feedback on writing style, grammar, passive voice, word repetition
"""

import re
from collections import Counter


class WritingFeedback:
    def __init__(self):
        self.passive_patterns = [
            r'\b(is|are|was|were|been|being)\s+\w+ed\b',
            r'\b(is|are|was|were)\s+\w+en\b'
        ]
        
        self.weak_words = ['very', 'really', 'just', 'quite', 'rather', 'somewhat']
        
        self.filler_words = ['actually', 'basically', 'literally', 'honestly']
    
    def analyze(self, text):
        """
        Analyze writing style and provide feedback
        Returns: dict with style analysis and suggestions
        """
        # Analyze various aspects
        passive_voice = self.check_passive_voice(text)
        word_repetition = self.check_word_repetition(text)
        weak_words_found = self.check_weak_words(text)
        filler_words_found = self.check_filler_words(text)
        sentence_variety = self.check_sentence_variety(text)
        paragraph_structure = self.check_paragraph_structure(text)
        
        # Generate suggestions
        suggestions = self.generate_suggestions(
            passive_voice, word_repetition, weak_words_found, 
            filler_words_found, sentence_variety
        )
        
        # Calculate overall writing score
        writing_score = self.calculate_writing_score(
            passive_voice, word_repetition, weak_words_found, 
            filler_words_found, sentence_variety
        )
        
        return {
            'writing_score': writing_score,
            'passive_voice': passive_voice,
            'word_repetition': word_repetition,
            'weak_words': weak_words_found,
            'filler_words': filler_words_found,
            'sentence_variety': sentence_variety,
            'paragraph_structure': paragraph_structure,
            'suggestions': suggestions,
            'status': self.get_status(writing_score)
        }
    
    def check_passive_voice(self, text):
        """Check for passive voice usage"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        passive_count = 0
        passive_examples = []
        
        for sentence in sentences:
            for pattern in self.passive_patterns:
                if re.search(pattern, sentence.lower()):
                    passive_count += 1
                    if len(passive_examples) < 3:
                        passive_examples.append(sentence[:100])
                    break
        
        passive_percentage = (passive_count / len(sentences)) * 100 if sentences else 0
        
        return {
            'count': passive_count,
            'percentage': round(passive_percentage, 2),
            'examples': passive_examples,
            'recommendation': 'Good' if passive_percentage < 15 else 'Reduce passive voice'
        }
    
    def check_word_repetition(self, text):
        """Check for repeated words"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        filtered_words = [w for w in words if w not in common_words and len(w) > 3]
        
        # Count word frequency
        word_freq = Counter(filtered_words)
        
        # Find most repeated words
        most_repeated = word_freq.most_common(5)
        
        # Calculate repetition score
        total_words = len(filtered_words)
        unique_words = len(set(filtered_words))
        diversity_ratio = unique_words / total_words if total_words > 0 else 1
        
        return {
            'diversity_ratio': round(diversity_ratio, 3),
            'most_repeated': [
                {'word': word, 'count': count} 
                for word, count in most_repeated if count > 3
            ],
            'recommendation': 'Good variety' if diversity_ratio > 0.6 else 'Use more varied vocabulary'
        }
    
    def check_weak_words(self, text):
        """Check for weak/filler words"""
        text_lower = text.lower()
        found_weak_words = []
        
        for word in self.weak_words:
            count = len(re.findall(r'\b' + word + r'\b', text_lower))
            if count > 0:
                found_weak_words.append({'word': word, 'count': count})
        
        total_weak = sum(w['count'] for w in found_weak_words)
        
        return {
            'total_count': total_weak,
            'words': found_weak_words,
            'recommendation': 'Good' if total_weak < 5 else 'Reduce weak modifiers'
        }
    
    def check_filler_words(self, text):
        """Check for filler words"""
        text_lower = text.lower()
        found_filler_words = []
        
        for word in self.filler_words:
            count = len(re.findall(r'\b' + word + r'\b', text_lower))
            if count > 0:
                found_filler_words.append({'word': word, 'count': count})
        
        total_filler = sum(w['count'] for w in found_filler_words)
        
        return {
            'total_count': total_filler,
            'words': found_filler_words,
            'recommendation': 'Good' if total_filler < 3 else 'Remove unnecessary filler words'
        }
    
    def check_sentence_variety(self, text):
        """Check sentence length variety"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 3:
            return {
                'variety_score': 50,
                'recommendation': 'Text too short to analyze variety'
            }
        
        # Calculate sentence lengths
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        
        # Calculate variance
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        std_dev = variance ** 0.5
        
        # Higher standard deviation = more variety
        variety_score = min(std_dev * 10, 100)
        
        return {
            'variety_score': round(variety_score, 2),
            'avg_length': round(avg_length, 2),
            'shortest': min(lengths),
            'longest': max(lengths),
            'recommendation': 'Good variety' if variety_score > 30 else 'Vary sentence lengths more'
        }
    
    def check_paragraph_structure(self, text):
        """Check paragraph structure"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if not paragraphs:
            paragraphs = [text]
        
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
        
        return {
            'paragraph_count': len(paragraphs),
            'avg_words_per_paragraph': round(avg_paragraph_length, 2),
            'recommendation': self.get_paragraph_recommendation(avg_paragraph_length)
        }
    
    def get_paragraph_recommendation(self, avg_length):
        """Get paragraph structure recommendation"""
        if avg_length < 50:
            return "Consider developing paragraphs more fully"
        elif avg_length > 150:
            return "Consider breaking long paragraphs into smaller ones"
        else:
            return "Good paragraph length"
    
    def generate_suggestions(self, passive, repetition, weak, filler, variety):
        """Generate writing improvement suggestions"""
        suggestions = []
        
        # Passive voice suggestions
        if passive['percentage'] > 20:
            suggestions.append({
                'category': 'Passive Voice',
                'issue': f"{passive['percentage']:.1f}% of sentences use passive voice",
                'suggestion': "Convert passive constructions to active voice for stronger writing",
                'priority': 'High'
            })
        
        # Word repetition suggestions
        if repetition['diversity_ratio'] < 0.5:
            suggestions.append({
                'category': 'Word Choice',
                'issue': "Limited vocabulary diversity",
                'suggestion': "Use synonyms and vary word choice",
                'priority': 'Medium'
            })
        
        # Weak words suggestions
        if weak['total_count'] > 5:
            suggestions.append({
                'category': 'Word Strength',
                'issue': f"Found {weak['total_count']} weak modifiers",
                'suggestion': "Replace weak words with stronger alternatives",
                'priority': 'Medium'
            })
        
        # Filler words suggestions
        if filler['total_count'] > 3:
            suggestions.append({
                'category': 'Conciseness',
                'issue': f"Found {filler['total_count']} filler words",
                'suggestion': "Remove unnecessary filler words for clearer writing",
                'priority': 'Medium'
            })
        
        # Sentence variety suggestions
        if variety['variety_score'] < 30:
            suggestions.append({
                'category': 'Sentence Structure',
                'issue': "Low sentence variety",
                'suggestion': "Vary sentence length and structure for better flow",
                'priority': 'High'
            })
        
        if not suggestions:
            suggestions.append({
                'category': 'Overall',
                'issue': 'No major issues detected',
                'suggestion': 'Writing style is generally good',
                'priority': 'Info'
            })
        
        return suggestions
    
    def calculate_writing_score(self, passive, repetition, weak, filler, variety):
        """Calculate overall writing quality score"""
        score = 100
        
        # Deduct for passive voice
        if passive['percentage'] > 15:
            score -= (passive['percentage'] - 15) * 0.5
        
        # Deduct for low diversity
        if repetition['diversity_ratio'] < 0.6:
            score -= (0.6 - repetition['diversity_ratio']) * 50
        
        # Deduct for weak words
        score -= min(weak['total_count'] * 2, 10)
        
        # Deduct for filler words
        score -= min(filler['total_count'] * 3, 15)
        
        # Deduct for low variety
        if variety['variety_score'] < 30:
            score -= (30 - variety['variety_score']) * 0.5
        
        return max(round(score, 2), 0)
    
    def get_status(self, score):
        """Get writing quality status"""
        if score >= 85:
            return "Excellent writing quality"
        elif score >= 70:
            return "Good writing quality"
        elif score >= 55:
            return "Fair writing quality"
        else:
            return "Needs improvement"
