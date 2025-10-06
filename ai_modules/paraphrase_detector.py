#!/usr/bin/env python3
"""
Paraphrase Detection Module
Detects text that has been rewritten while maintaining original meaning
"""

import re
import nltk
from typing import Dict, List, Tuple, Set
from collections import Counter
from nltk.corpus import wordnet, stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from difflib import SequenceMatcher
import spacy
from config import Config

class ParaphraseDetector:
    """Advanced paraphrase detection system"""

    def __init__(self):
        # Initialize NLTK components
        try:
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
            self.nlp = spacy.load('en_core_web_sm')
        except LookupError:
            nltk.download('stopwords')
            nltk.download('wordnet')
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
            self.nlp = spacy.load('en_core_web_sm')

        # Common paraphrasing patterns
        self.paraphrasing_indicators = {
            'synonym_replacement': self._check_synonym_replacement,
            'structure_change': self._check_structure_change,
            'voice_change': self._check_voice_change,
            'tense_change': self._check_tense_change,
            'word_order_change': self._check_word_order_change
        }

        # Load common academic phrase patterns
        self.academic_patterns = self._load_academic_patterns()

    def _load_academic_patterns(self) -> Dict[str, List[str]]:
        """Load common academic writing patterns"""
        return {
            'introduction_patterns': [
                'this paper examines', 'this study investigates', 'the purpose of this research',
                'the main objective', 'the primary focus', 'the central question'
            ],
            'methodology_patterns': [
                'the study employed', 'the research utilized', 'the methodology involved',
                'data was collected', 'participants were recruited', 'the sample consisted'
            ],
            'results_patterns': [
                'the findings indicate', 'the results suggest', 'the data shows',
                'the analysis revealed', 'the experiment demonstrated', 'the study found'
            ],
            'conclusion_patterns': [
                'in conclusion', 'to summarize', 'the study concludes', 'the research suggests',
                'the findings imply', 'the results indicate'
            ]
        }

    def detect_paraphrasing(self, text: str, original_sources: List[str] = None) -> Dict:
        """
        Detect paraphrased content in text

        Args:
            text: Text to analyze
            original_sources: List of original source texts for comparison

        Returns:
            Dictionary containing paraphrase analysis results
        """
        results = {
            'overall_score': 100.0,  # Start with 100% integrity
            'paraphrase_percentage': 0.0,
            'paraphrasing_indicators': {},
            'suspicious_sections': [],
            'risk_level': 'low',
            'details': {}
        }

        if not text or len(text.strip()) < 100:
            return results

        # Preprocess text
        sentences = sent_tokenize(text)
        clean_text = self._preprocess_text(text)

        # Check for various paraphrasing indicators
        indicators = {}

        for indicator_type, check_function in self.paraphrasing_indicators.items():
            indicator_result = check_function(sentences, clean_text)
            if indicator_result['detected']:
                indicators[indicator_type] = indicator_result

        results['paraphrasing_indicators'] = indicators

        # Check against original sources if provided
        if original_sources:
            source_comparison = self._compare_with_sources(clean_text, original_sources)
            results['suspicious_sections'].extend(source_comparison)

        # Check for academic pattern overuse
        pattern_analysis = self._analyze_academic_patterns(sentences)
        results['suspicious_sections'].extend(pattern_analysis)

        # Calculate paraphrase score
        results['paraphrase_percentage'] = self._calculate_paraphrase_score(indicators, results['suspicious_sections'])
        results['overall_score'] = max(0, 100 - results['paraphrase_percentage'])

        # Determine risk level
        results['risk_level'] = self._determine_risk_level(results['paraphrase_percentage'])

        # Store detailed information
        results['details'] = {
            'total_indicators': len(indicators),
            'suspicious_sections_count': len(results['suspicious_sections']),
            'sentence_count': len(sentences),
            'indicators_detected': list(indicators.keys())
        }

        return results

    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove citations
        text = re.sub(r'\[\d+\]|\(\w+,\s*\d{4}\)|\b\w+\s+et\s+al\.', '', text)

        return text.strip().lower()

    def _check_synonym_replacement(self, sentences: List[str], text: str) -> Dict:
        """Check for synonym replacement patterns"""
        suspicious_sentences = []

        for sentence in sentences:
            # Get synonyms for content words
            words = word_tokenize(sentence.lower())
            content_words = [word for word in words if word not in self.stop_words and len(word) > 3]

            synonym_count = 0
            for word in content_words:
                synonyms = self._get_synonyms(word)
                if len(synonyms) > 3:  # Word has many synonyms - might be replaced
                    synonym_count += 1

            if synonym_count > len(content_words) * 0.4:  # 40% of words have many synonyms
                suspicious_sentences.append({
                    'sentence': sentence,
                    'indicator': 'high_synonym_usage',
                    'confidence': min(0.9, synonym_count / len(content_words))
                })

        return {
            'detected': len(suspicious_sentences) > 0,
            'count': len(suspicious_sentences),
            'examples': suspicious_sentences[:3]
        }

    def _check_structure_change(self, sentences: List[str], text: str) -> Dict:
        """Check for sentence structure changes"""
        suspicious_sentences = []

        for sentence in sentences:
            # Check for passive voice overuse (common in paraphrasing)
            doc = self.nlp(sentence)
            passive_count = 0
            total_verbs = 0

            for token in doc:
                if token.pos_ == 'VERB':
                    total_verbs += 1
                    # Check if verb is passive
                    if token.dep_ == 'aux:pass' or (token.head.pos_ == 'AUX' and 'pass' in token.head.tag_):
                        passive_count += 1

            if total_verbs > 0 and (passive_count / total_verbs) > 0.6:  # 60% passive
                suspicious_sentences.append({
                    'sentence': sentence,
                    'indicator': 'passive_voice_overuse',
                    'confidence': passive_count / total_verbs
                })

        return {
            'detected': len(suspicious_sentences) > 0,
            'count': len(suspicious_sentences),
            'examples': suspicious_sentences[:3]
        }

    def _check_voice_change(self, sentences: List[str], text: str) -> Dict:
        """Check for systematic voice changes"""
        active_count = 0
        passive_count = 0

        for sentence in sentences:
            doc = self.nlp(sentence)
            has_passive = False

            for token in doc:
                if token.dep_ == 'nsubj:pass' or (token.pos_ == 'AUX' and 'pass' in str(token.morph)):
                    has_passive = True
                    break

            if has_passive:
                passive_count += 1
            else:
                active_count += 1

        # If there's a mix of active and passive, might indicate paraphrasing attempts
        total_sentences = len(sentences)
        if total_sentences > 5:
            active_ratio = active_count / total_sentences
            passive_ratio = passive_count / total_sentences

            # Suspicious if both ratios are between 0.3 and 0.7
            if 0.3 < active_ratio < 0.7 and 0.3 < passive_ratio < 0.7:
                return {
                    'detected': True,
                    'active_ratio': active_ratio,
                    'passive_ratio': passive_ratio,
                    'confidence': 0.7
                }

        return {'detected': False, 'confidence': 0.0}

    def _check_tense_change(self, sentences: List[str], text: str) -> Dict:
        """Check for inconsistent tense usage"""
        tense_patterns = []

        for sentence in sentences:
            doc = self.nlp(sentence)

            # Analyze verb tenses
            tenses = []
            for token in doc:
                if token.pos_ == 'VERB':
                    tense = token.morph.get('Tense', ['Pres'])[0]  # Default to present
                    tenses.append(tense)

            if tenses:
                most_common_tense = Counter(tenses).most_common(1)[0][0]
                tense_consistency = Counter(tenses)[most_common_tense] / len(tenses)

                if tense_consistency < 0.6:  # Less than 60% consistency
                    tense_patterns.append({
                        'sentence': sentence,
                        'tenses': Counter(tenses),
                        'consistency': tense_consistency
                    })

        return {
            'detected': len(tense_patterns) > 0,
            'count': len(tense_patterns),
            'examples': tense_patterns[:3]
        }

    def _check_word_order_change(self, sentences: List[str], text: str) -> Dict:
        """Check for unusual word order patterns"""
        suspicious_sentences = []

        for sentence in sentences:
            doc = self.nlp(sentence)

            # Check for complex sentence structures
            clauses = list(doc.sents)
            if len(clauses) > 2:  # Multiple clauses might indicate paraphrasing
                suspicious_sentences.append({
                    'sentence': sentence,
                    'clause_count': len(clauses),
                    'indicator': 'complex_structure'
                })

        return {
            'detected': len(suspicious_sentences) > 0,
            'count': len(suspicious_sentences),
            'examples': suspicious_sentences[:3]
        }

    def _compare_with_sources(self, text: str, sources: List[str]) -> List[Dict]:
        """Compare text with original sources"""
        suspicious_sections = []

        for i, source in enumerate(sources):
            similarity = self._calculate_semantic_similarity(text, source)

            if similarity > 0.3:  # 30% semantic similarity
                suspicious_sections.append({
                    'source_index': i,
                    'similarity': similarity,
                    'type': 'source_comparison',
                    'confidence': similarity
                })

        return suspicious_sections

    def _analyze_academic_patterns(self, sentences: List[str]) -> List[Dict]:
        """Analyze overuse of academic patterns"""
        pattern_matches = []

        for sentence in sentences:
            sentence_lower = sentence.lower()
            matched_patterns = []

            for category, patterns in self.academic_patterns.items():
                for pattern in patterns:
                    if pattern in sentence_lower:
                        matched_patterns.append({
                            'pattern': pattern,
                            'category': category
                        })

            if len(matched_patterns) > 2:  # Multiple patterns in one sentence
                pattern_matches.append({
                    'sentence': sentence,
                    'patterns': matched_patterns,
                    'pattern_count': len(matched_patterns)
                })

        return pattern_matches

    def _get_synonyms(self, word: str) -> Set[str]:
        """Get synonyms for a word using WordNet"""
        synonyms = set()

        try:
            for syn in wordnet.synsets(word):
                for lemma in syn.lemmas():
                    synonyms.add(lemma.name().lower())
        except:
            pass

        return synonyms

    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between texts"""
        if not text1 or not text2:
            return 0.0

        # Use simple word overlap for semantic similarity
        words1 = set(word_tokenize(text1.lower()))
        words2 = set(word_tokenize(text2.lower()))

        # Remove stop words
        words1 = words1 - self.stop_words
        words2 = words2 - self.stop_words

        if not words1 or not words2:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _calculate_paraphrase_score(self, indicators: Dict, suspicious_sections: List) -> float:
        """Calculate overall paraphrase percentage"""
        if not indicators and not suspicious_sections:
            return 0.0

        # Weight different indicators
        weights = {
            'synonym_replacement': 0.25,
            'structure_change': 0.20,
            'voice_change': 0.25,
            'tense_change': 0.15,
            'word_order_change': 0.15
        }

        total_score = 0.0
        total_weight = 0.0

        # Score based on indicators
        for indicator_type, result in indicators.items():
            if indicator_type in weights:
                weight = weights[indicator_type]
                confidence = result.get('confidence', 0.5) if isinstance(result, dict) else 0.5
                total_score += confidence * weight
                total_weight += weight

        # Add score from suspicious sections
        if suspicious_sections:
            avg_section_confidence = sum(section.get('confidence', 0.5) for section in suspicious_sections) / len(suspicious_sections)
            total_score += avg_section_confidence * 0.3
            total_weight += 0.3

        if total_weight == 0:
            return 0.0

        return min(100.0, (total_score / total_weight) * 100)

    def _determine_risk_level(self, paraphrase_percentage: float) -> str:
        """Determine risk level based on paraphrase percentage"""
        if paraphrase_percentage >= 60:
            return 'high'
        elif paraphrase_percentage >= 30:
            return 'medium'
        else:
            return 'low'

    def generate_report(self, text: str, results: Dict) -> str:
        """Generate detailed paraphrase detection report"""
        report = []
        report.append("=== PARAPHRASE DETECTION REPORT ===\n")
        report.append(f"Text Length: {len(text)} characters\n")
        report.append(f"Overall Paraphrase Score: {results['paraphrase_percentage']".1f"}%\n")
        report.append(f"Risk Level: {results['risk_level'].upper()}\n")

        if results['paraphrasing_indicators']:
            report.append(f"\nParaphrasing Indicators Detected: {len(results['paraphrasing_indicators'])}")
            for indicator, details in results['paraphrasing_indicators'].items():
                report.append(f"\n  {indicator.replace('_', ' ').title()}:")
                report.append(f"    Detected: {details.get('detected', False)}")
                if 'confidence' in details:
                    report.append(f"    Confidence: {details['confidence']".2f"}")

        if results['suspicious_sections']:
            report.append(f"\nSuspicious Sections: {len(results['suspicious_sections'])}")
            for i, section in enumerate(results['suspicious_sections'][:5], 1):
                report.append(f"\n  {i}. Confidence: {section.get('confidence', 0)".2f"}")
                if 'sentence' in section:
                    report.append(f"     Text: {section['sentence'][:100]}...")

        return '\n'.join(report)