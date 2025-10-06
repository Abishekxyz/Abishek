#!/usr/bin/env python3
"""
Writing Analysis Module
Provides writing feedback, readability scoring, and style suggestions
"""

import re
import nltk
from typing import Dict, List, Tuple, Optional
from collections import Counter
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy
import textstat
from config import Config

class WritingAnalyzer:
    """Comprehensive writing analysis system"""

    def __init__(self):
        # Initialize NLTK components
        try:
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
        except LookupError:
            nltk.download('stopwords')
            nltk.download('wordnet')
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()

        # Initialize spaCy
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            print("Downloading spaCy model...")
            import subprocess
            subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'], check=True)
            self.nlp = spacy.load('en_core_web_sm')

        # Writing quality indicators
        self.quality_indicators = {
            'readability': self._analyze_readability,
            'grammar': self._analyze_grammar,
            'style': self._analyze_style,
            'vocabulary': self._analyze_vocabulary,
            'structure': self._analyze_structure
        }

        # Common writing issues
        self.common_issues = {
            'passive_voice': self._detect_passive_voice,
            'wordiness': self._detect_wordiness,
            'repetition': self._detect_repetition,
            'cliches': self._detect_cliches,
            'jargon': self._detect_jargon
        }

    def analyze_writing(self, text: str) -> Dict:
        """
        Comprehensive writing analysis

        Args:
            text: Text to analyze

        Returns:
            Dictionary containing writing analysis results
        """
        results = {
            'overall_score': 100.0,
            'readability_score': 0.0,
            'grammar_score': 100.0,
            'style_score': 100.0,
            'vocabulary_score': 100.0,
            'structure_score': 100.0,
            'readability_metrics': {},
            'grammar_issues': [],
            'style_issues': [],
            'vocabulary_analysis': {},
            'structure_analysis': {},
            'suggestions': [],
            'details': {}
        }

        if not text or len(text.strip()) < 50:
            return results

        # Basic text metrics
        sentences = sent_tokenize(text)
        words = word_tokenize(text.lower())

        if not sentences or not words:
            return results

        # Analyze each quality indicator
        quality_results = {}
        for indicator, analyzer in self.quality_indicators.items():
            quality_results[indicator] = analyzer(sentences, words, text)

        results.update(quality_results)

        # Detect common writing issues
        issue_results = {}
        for issue, detector in self.common_issues.items():
            issue_results[issue] = detector(sentences, words, text)

        # Flatten issue results into main results
        for issue_type, issues in issue_results.items():
            if issue_type == 'passive_voice':
                results['grammar_issues'].extend(issues)
            elif issue_type in ['wordiness', 'repetition', 'cliches']:
                results['style_issues'].extend(issues)
            elif issue_type == 'jargon':
                results['vocabulary_analysis']['jargon_issues'] = issues

        # Calculate overall scores
        results['readability_score'] = quality_results['readability']['score']
        results['grammar_score'] = self._calculate_grammar_score(results['grammar_issues'])
        results['style_score'] = self._calculate_style_score(results['style_issues'])
        results['vocabulary_score'] = quality_results['vocabulary']['score']
        results['structure_score'] = quality_results['structure']['score']

        # Calculate overall writing score
        weights = {
            'readability': 0.25,
            'grammar': 0.25,
            'style': 0.20,
            'vocabulary': 0.15,
            'structure': 0.15
        }

        overall_score = sum(
            results[key] * weights[key.replace('_score', '')]
            for key in ['readability_score', 'grammar_score', 'style_score', 'vocabulary_score', 'structure_score']
        )
        results['overall_score'] = overall_score

        # Generate suggestions
        results['suggestions'] = self._generate_writing_suggestions(results)

        # Store detailed information
        results['details'] = {
            'sentence_count': len(sentences),
            'word_count': len(words),
            'character_count': len(text),
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0
        }

        return results

    def _analyze_readability(self, sentences: List[str], words: List[str], text: str) -> Dict:
        """Analyze text readability"""
        # Use textstat for comprehensive readability metrics
        metrics = {
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
            'flesch_reading_ease': textstat.flesch_reading_ease(text),
            'smog_index': textstat.smog_index(text),
            'coleman_liau_index': textstat.coleman_liau_index(text),
            'automated_readability_index': textstat.automated_readability_index(text),
            'dale_chall_readability_score': textstat.dale_chall_readability_score(text),
            'difficult_words': textstat.difficult_words(text),
            'linsear_write_formula': textstat.linsear_write_formula(text),
            'gunning_fog': textstat.gunning_fog(text)
        }

        # Calculate overall readability score (0-100, higher is more readable)
        # Flesch Reading Ease: 0-100, higher is easier to read
        # We'll invert some metrics that measure difficulty
        ease_score = metrics['flesch_reading_ease']

        # Grade level should be reasonable for the context (aim for 8-12)
        grade_level = metrics['flesch_kincaid_grade']
        if 8 <= grade_level <= 12:
            grade_score = 100
        elif grade_level < 8:
            grade_score = 80  # Too simple
        else:
            grade_score = max(20, 100 - (grade_level - 12) * 10)  # Too complex

        overall_score = (ease_score * 0.7) + (grade_score * 0.3)

        return {
            'score': min(100, max(0, overall_score)),
            'metrics': metrics,
            'interpretation': self._interpret_readability(ease_score, grade_level)
        }

    def _interpret_readability(self, ease_score: float, grade_level: float) -> str:
        """Interpret readability scores"""
        if ease_score >= 80:
            return "Very Easy to Read"
        elif ease_score >= 60:
            return "Easy to Read"
        elif ease_score >= 40:
            return "Average Difficulty"
        elif ease_score >= 20:
            return "Difficult to Read"
        else:
            return "Very Difficult to Read"

    def _analyze_grammar(self, sentences: List[str], words: List[str], text: str) -> Dict:
        """Analyze grammar quality"""
        issues = []

        # Check for common grammar issues using spaCy
        doc = self.nlp(text)

        for token in doc:
            # Check for subject-verb agreement issues (simplified)
            if token.pos_ == 'VERB' and token.dep_ == 'ROOT':
                # Look for agreement issues
                subject = self._find_subject(token)
                if subject and not self._check_agreement(token, subject):
                    issues.append({
                        'type': 'subject_verb_agreement',
                        'word': token.text,
                        'suggestion': f"Check subject-verb agreement for '{token.text}'"
                    })

        # Check sentence fragments
        for sentence in sentences:
            if not self._is_complete_sentence(sentence):
                issues.append({
                    'type': 'sentence_fragment',
                    'sentence': sentence,
                    'suggestion': "Complete this sentence fragment"
                })

        # Check run-on sentences
        for sentence in sentences:
            if self._is_run_on_sentence(sentence):
                issues.append({
                    'type': 'run_on_sentence',
                    'sentence': sentence[:50] + '...',
                    'suggestion': "Break this run-on sentence into smaller sentences"
                })

        return {
            'score': self._calculate_grammar_score(issues),
            'issues': issues,
            'issue_count': len(issues)
        }

    def _analyze_style(self, sentences: List[str], words: List[str], text: str) -> Dict:
        """Analyze writing style"""
        issues = []

        # Check for passive voice overuse
        passive_count = 0
        for sentence in sentences:
            if self._is_passive_voice(sentence):
                passive_count += 1

        passive_ratio = passive_count / len(sentences) if sentences else 0
        if passive_ratio > 0.3:  # More than 30% passive
            issues.append({
                'type': 'passive_voice_overuse',
                'ratio': passive_ratio,
                'suggestion': f"Consider using more active voice ({passive_ratio".1%"}) of sentences are passive)"
            })

        # Check for wordiness
        wordy_sentences = self._find_wordy_sentences(sentences)
        issues.extend(wordy_sentences)

        # Check for repetitive phrases
        repetitive_phrases = self._find_repetitive_phrases(words)
        issues.extend(repetitive_phrases)

        return {
            'score': self._calculate_style_score(issues),
            'issues': issues,
            'passive_ratio': passive_ratio,
            'issue_count': len(issues)
        }

    def _analyze_vocabulary(self, sentences: List[str], words: List[str], text: str) -> Dict:
        """Analyze vocabulary usage"""
        # Calculate lexical diversity
        unique_words = set(words)
        lexical_diversity = len(unique_words) / len(words) if words else 0

        # Find complex words
        complex_words = [word for word in words if len(word) > 6 and word not in self.stop_words]

        # Check for jargon
        jargon_words = self._identify_jargon(words)

        # Vocabulary score based on diversity and complexity
        diversity_score = min(100, lexical_diversity * 200)  # Scale to 0-100
        complexity_score = min(100, len(complex_words) / len(words) * 500) if words else 0

        overall_score = (diversity_score * 0.6) + (complexity_score * 0.4)

        return {
            'score': overall_score,
            'lexical_diversity': lexical_diversity,
            'complex_words_count': len(complex_words),
            'jargon_words': jargon_words,
            'unique_words': len(unique_words)
        }

    def _analyze_structure(self, sentences: List[str], words: List[str], text: str) -> Dict:
        """Analyze text structure"""
        analysis = {
            'paragraph_count': len([s for s in sentences if s.strip() == '']),
            'avg_paragraph_length': 0,
            'transition_words': 0,
            'logical_flow': 'unknown'
        }

        # Count paragraphs (approximate)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        analysis['paragraph_count'] = len(paragraphs)

        if paragraphs:
            analysis['avg_paragraph_length'] = sum(len(p.split()) for p in paragraphs) / len(paragraphs)

        # Check for transition words
        transition_words = {
            'however', 'therefore', 'furthermore', 'moreover', 'consequently',
            'nevertheless', 'although', 'because', 'since', 'while', 'whereas'
        }

        transition_count = sum(1 for word in words if word in transition_words)
        analysis['transition_words'] = transition_count

        # Simple flow assessment
        if transition_count > len(sentences) * 0.1:  # At least 10% transition words
            analysis['logical_flow'] = 'good'
        else:
            analysis['logical_flow'] = 'needs_improvement'

        # Structure score
        structure_score = 50  # Base score

        if analysis['avg_paragraph_length'] > 100:  # Good paragraph length
            structure_score += 25

        if analysis['logical_flow'] == 'good':
            structure_score += 25

        return {
            'score': min(100, structure_score),
            'analysis': analysis
        }

    def _detect_passive_voice(self, sentences: List[str], words: List[str], text: str) -> List[Dict]:
        """Detect passive voice usage"""
        issues = []

        for i, sentence in enumerate(sentences):
            if self._is_passive_voice(sentence):
                issues.append({
                    'sentence': sentence,
                    'position': i,
                    'type': 'passive_voice',
                    'suggestion': 'Consider rewriting in active voice'
                })

        return issues

    def _detect_wordiness(self, sentences: List[str], words: List[str], text: str) -> List[Dict]:
        """Detect wordy sentences"""
        issues = []

        for i, sentence in enumerate(sentences):
            word_count = len(sentence.split())

            # Check for overly long sentences
            if word_count > 40:
                issues.append({
                    'sentence': sentence[:50] + '...',
                    'position': i,
                    'type': 'wordy_sentence',
                    'word_count': word_count,
                    'suggestion': 'Consider breaking into shorter sentences'
                })

            # Check for redundant phrases
            redundant_phrases = [
                'in order to', 'due to the fact that', 'at this point in time',
                'for the purpose of', 'in the event that'
            ]

            for phrase in redundant_phrases:
                if phrase in sentence.lower():
                    issues.append({
                        'sentence': sentence,
                        'position': i,
                        'type': 'redundant_phrase',
                        'phrase': phrase,
                        'suggestion': f"Consider simplifying '{phrase}'"
                    })

        return issues

    def _detect_repetition(self, sentences: List[str], words: List[str], text: str) -> List[Dict]:
        """Detect word repetition"""
        issues = []

        # Find repeated words
        word_counts = Counter(words)
        repeated_words = [(word, count) for word, count in word_counts.items() if count > 5 and len(word) > 3]

        for word, count in repeated_words:
            issues.append({
                'word': word,
                'count': count,
                'type': 'word_repetition',
                'suggestion': f"Consider varying vocabulary (word '{word}' used {count} times)"
            })

        return issues

    def _detect_cliches(self, sentences: List[str], words: List[str], text: str) -> List[Dict]:
        """Detect cliche usage"""
        issues = []

        cliches = [
            'at the end of the day', 'think outside the box', 'it is what it is',
            'actions speak louder than words', 'when all is said and done',
            'last but not least', 'needless to say', 'crystal clear'
        ]

        for i, sentence in enumerate(sentences):
            for cliche in cliches:
                if cliche.lower() in sentence.lower():
                    issues.append({
                        'sentence': sentence,
                        'position': i,
                        'type': 'cliche',
                        'cliche': cliche,
                        'suggestion': f"Consider replacing cliche '{cliche}' with original expression"
                    })

        return issues

    def _detect_jargon(self, sentences: List[str], words: List[str], text: str) -> List[Dict]:
        """Detect jargon usage"""
        issues = []

        # Common academic jargon
        jargon_terms = [
            'paradigm', 'methodology', 'empirical', 'quantitative', 'qualitative',
            'hypothesis', 'correlation', 'statistically significant', 'literature review'
        ]

        for i, sentence in enumerate(sentences):
            for term in jargon_terms:
                if term.lower() in sentence.lower():
                    issues.append({
                        'sentence': sentence,
                        'position': i,
                        'type': 'jargon',
                        'term': term,
                        'suggestion': f"Consider explaining '{term}' for general audience"
                    })

        return issues

    def _is_passive_voice(self, sentence: str) -> bool:
        """Check if sentence is in passive voice"""
        doc = self.nlp(sentence)

        for token in doc:
            if token.pos_ == 'VERB':
                # Check for passive auxiliary verbs followed by past participle
                if token.dep_ == 'aux:pass' or (token.head.pos_ == 'AUX' and 'pass' in str(token.head.morph)):
                    return True

        return False

    def _find_subject(self, verb_token) -> Optional[str]:
        """Find subject of a verb"""
        for token in verb_token.head.children:
            if token.dep_ in ['nsubj', 'nsubjpass']:
                return token.text
        return None

    def _check_agreement(self, verb_token, subject_token) -> bool:
        """Check subject-verb agreement (simplified)"""
        # This is a simplified check - real implementation would be more complex
        return True  # Placeholder

    def _is_complete_sentence(self, sentence: str) -> bool:
        """Check if sentence is complete"""
        doc = self.nlp(sentence)

        # Check for subject and verb
        has_subject = any(token.dep_ in ['nsubj', 'nsubjpass'] for token in doc)
        has_verb = any(token.pos_ == 'VERB' for token in doc)

        return has_subject and has_verb

    def _is_run_on_sentence(self, sentence: str) -> bool:
        """Check if sentence is a run-on"""
        # Simple heuristic: very long sentences or multiple independent clauses
        word_count = len(sentence.split())

        if word_count > 50:  # Very long sentence
            return True

        # Count independent clauses (sentences with multiple subjects/verbs)
        doc = self.nlp(sentence)
        root_verbs = [token for token in doc if token.dep_ == 'ROOT' and token.pos_ == 'VERB']

        return len(root_verbs) > 1

    def _find_wordy_sentences(self, sentences: List[str]) -> List[Dict]:
        """Find wordy sentences"""
        issues = []

        for i, sentence in enumerate(sentences):
            word_count = len(sentence.split())

            if word_count > 35:  # Somewhat long sentence
                issues.append({
                    'sentence': sentence[:60] + '...',
                    'position': i,
                    'type': 'wordy',
                    'word_count': word_count,
                    'suggestion': 'Consider making this sentence more concise'
                })

        return issues

    def _find_repetitive_phrases(self, words: List[str]) -> List[Dict]:
        """Find repetitive phrases"""
        issues = []

        # Look for repeated 2-3 word phrases
        phrase_counts = Counter()

        for i in range(len(words) - 2):
            phrase = ' '.join(words[i:i+3])
            if len(phrase.split()) == 3:
                phrase_counts[phrase] += 1

        repetitive_phrases = [phrase for phrase, count in phrase_counts.items() if count > 3]

        for phrase in repetitive_phrases:
            issues.append({
                'phrase': phrase,
                'count': phrase_counts[phrase],
                'type': 'phrase_repetition',
                'suggestion': f"Consider varying the phrase '{phrase}'"
            })

        return issues

    def _identify_jargon(self, words: List[str]) -> List[str]:
        """Identify jargon words"""
        jargon = []

        # Academic jargon list
        academic_jargon = {
            'paradigm', 'methodology', 'empirical', 'quantitative', 'qualitative',
            'hypothesis', 'correlation', 'statistically significant', 'literature review',
            'epistemology', 'ontology', 'hermeneutics', 'phenomenology'
        }

        for word in words:
            if word in academic_jargon:
                jargon.append(word)

        return list(set(jargon))

    def _calculate_grammar_score(self, issues: List[Dict]) -> float:
        """Calculate grammar score based on issues"""
        if not issues:
            return 100.0

        # Penalize based on issue count and severity
        penalty_per_issue = 5.0  # Points deducted per issue
        total_penalty = len(issues) * penalty_per_issue

        return max(0.0, 100.0 - total_penalty)

    def _calculate_style_score(self, issues: List[Dict]) -> float:
        """Calculate style score based on issues"""
        if not issues:
            return 100.0

        # Different penalties for different issue types
        penalties = {
            'passive_voice_overuse': 10.0,
            'wordy_sentence': 3.0,
            'wordy': 2.0,
            'word_repetition': 2.0,
            'redundant_phrase': 3.0,
            'cliche': 2.0
        }

        total_penalty = 0.0
        for issue in issues:
            issue_type = issue.get('type', 'unknown')
            total_penalty += penalties.get(issue_type, 2.0)

        return max(0.0, 100.0 - total_penalty)

    def _generate_writing_suggestions(self, results: Dict) -> List[str]:
        """Generate comprehensive writing suggestions"""
        suggestions = []

        # Readability suggestions
        readability_score = results['readability_score']
        if readability_score < 60:
            suggestions.append("Improve readability by using shorter sentences and simpler words")
        elif readability_score > 90:
            suggestions.append("Consider adding more sophisticated vocabulary for advanced readers")

        # Grammar suggestions
        if results['grammar_score'] < 80:
            suggestions.append("Review grammar and sentence structure")

        # Style suggestions
        if results['style_score'] < 80:
            suggestions.append("Work on writing style - avoid passive voice and wordiness")

        # Vocabulary suggestions
        vocab_score = results['vocabulary_score']
        if vocab_score < 60:
            suggestions.append("Expand vocabulary and improve word choice")
        elif vocab_score > 90:
            suggestions.append("Excellent vocabulary usage")

        # Structure suggestions
        if results['structure_score'] < 70:
            suggestions.append("Improve text structure and logical flow")

        # Specific issue suggestions
        if results['grammar_issues']:
            suggestions.append(f"Fix {len(results['grammar_issues'])} grammar issues")

        if results['style_issues']:
            suggestions.append(f"Address {len(results['style_issues'])} style issues")

        return suggestions

    def generate_report(self, text: str, results: Dict) -> str:
        """Generate detailed writing analysis report"""
        report = []
        report.append("=== WRITING ANALYSIS REPORT ===\n")
        report.append(f"Overall Writing Score: {results['overall_score']".1f"}%\n")
        report.append(f"Readability Score: {results['readability_score']".1f"}%\n")
        report.append(f"Grammar Score: {results['grammar_score']".1f"}%\n")
        report.append(f"Style Score: {results['style_score']".1f"}%\n")
        report.append(f"Vocabulary Score: {results['vocabulary_score']".1f"}%\n")
        report.append(f"Structure Score: {results['structure_score']".1f"}%\n")

        # Readability details
        if 'readability' in results and 'metrics' in results['readability']:
            report.append(f"\nReadability Metrics:")
            metrics = results['readability']['metrics']
            report.append(f"  Flesch-Kincaid Grade Level: {metrics['flesch_kincaid_grade']".1f"}")
            report.append(f"  Flesch Reading Ease: {metrics['flesch_reading_ease']".1f"}")
            report.append(f"  Interpretation: {results['readability'].get('interpretation', 'Unknown')}")

        # Issues summary
        total_grammar_issues = len(results.get('grammar_issues', []))
        total_style_issues = len(results.get('style_issues', []))

        if total_grammar_issues > 0 or total_style_issues > 0:
            report.append(f"\nIssues Found:")
            report.append(f"  Grammar Issues: {total_grammar_issues}")
            report.append(f"  Style Issues: {total_style_issues}")

        # Suggestions
        if results.get('suggestions'):
            report.append(f"\nSuggestions for Improvement:")
            for i, suggestion in enumerate(results['suggestions'], 1):
                report.append(f"  {i}. {suggestion}")

        # Vocabulary analysis
        vocab = results.get('vocabulary_analysis', {})
        if vocab:
            report.append(f"\nVocabulary Analysis:")
            report.append(f"  Lexical Diversity: {vocab.get('lexical_diversity', 0)".3f"}")
            report.append(f"  Complex Words: {vocab.get('complex_words_count', 0)}")
            if vocab.get('jargon_words'):
                report.append(f"  Jargon Terms: {', '.join(vocab['jargon_words'][:5])}")

        return '\n'.join(report)