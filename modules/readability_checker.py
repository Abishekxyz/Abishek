"""
Readability Checker Module
Analyzes text readability using Flesch Reading Ease and other metrics
"""

import re
import math


class ReadabilityChecker:
    def analyze(self, text):
        """
        Analyze text readability
        Returns: dict with various readability scores
        """
        # Count basic text statistics
        stats = self.get_text_statistics(text)
        
        # Calculate readability scores
        flesch_score = self.flesch_reading_ease(stats)
        flesch_kincaid_grade = self.flesch_kincaid_grade(stats)
        gunning_fog = self.gunning_fog_index(stats)
        
        # Determine reading level
        reading_level = self.get_reading_level(flesch_score)
        
        # Get recommendations
        recommendations = self.get_readability_recommendations(flesch_score, stats)
        
        return {
            'statistics': {
                'total_words': stats['words'],
                'total_sentences': stats['sentences'],
                'total_syllables': stats['syllables'],
                'avg_words_per_sentence': round(stats['words'] / stats['sentences'], 2) if stats['sentences'] > 0 else 0,
                'avg_syllables_per_word': round(stats['syllables'] / stats['words'], 2) if stats['words'] > 0 else 0
            },
            'scores': {
                'flesch_reading_ease': round(flesch_score, 2),
                'flesch_kincaid_grade': round(flesch_kincaid_grade, 2),
                'gunning_fog_index': round(gunning_fog, 2)
            },
            'reading_level': reading_level,
            'interpretation': self.interpret_flesch_score(flesch_score),
            'recommendations': recommendations,
            'status': self.get_status(flesch_score)
        }
    
    def get_text_statistics(self, text):
        """Get basic text statistics"""
        # Count sentences
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Count words
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        # Count syllables
        syllable_count = sum(self.count_syllables(word) for word in words)
        
        return {
            'sentences': max(sentence_count, 1),
            'words': max(word_count, 1),
            'syllables': max(syllable_count, 1)
        }
    
    def count_syllables(self, word):
        """Count syllables in a word"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent e
        if word.endswith('e'):
            syllable_count -= 1
        
        # Every word has at least one syllable
        if syllable_count == 0:
            syllable_count = 1
        
        return syllable_count
    
    def flesch_reading_ease(self, stats):
        """
        Calculate Flesch Reading Ease score
        Formula: 206.835 - 1.015(total words/total sentences) - 84.6(total syllables/total words)
        """
        avg_sentence_length = stats['words'] / stats['sentences']
        avg_syllables_per_word = stats['syllables'] / stats['words']
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        return max(0, min(100, score))  # Clamp between 0-100
    
    def flesch_kincaid_grade(self, stats):
        """
        Calculate Flesch-Kincaid Grade Level
        Formula: 0.39(total words/total sentences) + 11.8(total syllables/total words) - 15.59
        """
        avg_sentence_length = stats['words'] / stats['sentences']
        avg_syllables_per_word = stats['syllables'] / stats['words']
        
        grade = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
        
        return max(0, grade)
    
    def gunning_fog_index(self, stats):
        """
        Calculate Gunning Fog Index
        Formula: 0.4[(words/sentences) + 100(complex words/words)]
        """
        avg_sentence_length = stats['words'] / stats['sentences']
        # Approximate complex words as words with 3+ syllables
        complex_words = stats['syllables'] / 3  # Rough approximation
        percent_complex = (complex_words / stats['words']) * 100
        
        fog = 0.4 * (avg_sentence_length + percent_complex)
        
        return max(0, fog)
    
    def get_reading_level(self, flesch_score):
        """Determine reading level from Flesch score"""
        if flesch_score >= 90:
            return "Very Easy (5th grade)"
        elif flesch_score >= 80:
            return "Easy (6th grade)"
        elif flesch_score >= 70:
            return "Fairly Easy (7th grade)"
        elif flesch_score >= 60:
            return "Standard (8th-9th grade)"
        elif flesch_score >= 50:
            return "Fairly Difficult (10th-12th grade)"
        elif flesch_score >= 30:
            return "Difficult (College level)"
        else:
            return "Very Difficult (College graduate)"
    
    def interpret_flesch_score(self, score):
        """Interpret Flesch Reading Ease score"""
        if score >= 80:
            return "Very easy to read. Easily understood by an average 11-year-old student."
        elif score >= 70:
            return "Easy to read. Conversational English for consumers."
        elif score >= 60:
            return "Plain English. Easily understood by 13- to 15-year-old students."
        elif score >= 50:
            return "Fairly difficult to read. Typical of high school students."
        elif score >= 30:
            return "Difficult to read. Best understood by college graduates."
        else:
            return "Very difficult to read. Best understood by university graduates."
    
    def get_readability_recommendations(self, score, stats):
        """Get recommendations to improve readability"""
        recommendations = []
        
        # Check sentence length
        avg_sentence_length = stats['words'] / stats['sentences']
        if avg_sentence_length > 25:
            recommendations.append("Reduce average sentence length (currently {:.1f} words)".format(avg_sentence_length))
        
        # Check word complexity
        avg_syllables = stats['syllables'] / stats['words']
        if avg_syllables > 2:
            recommendations.append("Use simpler words (average {:.1f} syllables per word)".format(avg_syllables))
        
        # Check overall readability
        if score < 50:
            recommendations.append("Overall text is difficult to read. Consider simplifying.")
        elif score > 80:
            recommendations.append("Text is very easy to read. May be too simple for academic writing.")
        
        if not recommendations:
            recommendations.append("Readability is good for the target audience.")
        
        return recommendations
    
    def get_status(self, score):
        """Get readability status"""
        if score >= 70:
            return "Excellent readability"
        elif score >= 60:
            return "Good readability"
        elif score >= 50:
            return "Moderate readability"
        elif score >= 30:
            return "Challenging readability"
        else:
            return "Very difficult to read"
