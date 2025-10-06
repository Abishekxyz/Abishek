#!/usr/bin/env python3
"""
Resume Analysis Module
Analyzes resumes/CVs for content quality, formatting, and completeness
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from collections import Counter
import spacy
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from config import Config

class ResumeAnalyzer:
    """Comprehensive resume analysis system"""

    def __init__(self):
        # Initialize spaCy for NLP
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            print("Downloading spaCy model...")
            import subprocess
            subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'], check=True)
            self.nlp = spacy.load('en_core_web_sm')

        # Initialize NLTK
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords')
            self.stop_words = set(stopwords.words('english'))

        # Resume sections to look for
        self.expected_sections = [
            'contact_information', 'summary', 'experience', 'education',
            'skills', 'certifications', 'projects', 'awards'
        ]

        # Keywords for different job categories
        self.job_categories = {
            'technical': ['python', 'java', 'javascript', 'sql', 'git', 'agile', 'docker', 'aws'],
            'management': ['leadership', 'strategy', 'planning', 'budget', 'team', 'project'],
            'creative': ['design', 'creative', 'content', 'marketing', 'branding', 'social media'],
            'analytical': ['analysis', 'research', 'data', 'statistics', 'reporting', 'metrics']
        }

        # Action verbs that should be used
        self.action_verbs = [
            'achieved', 'improved', 'increased', 'developed', 'created', 'implemented',
            'managed', 'led', 'designed', 'analyzed', 'delivered', 'launched'
        ]

    def analyze_resume(self, text: str) -> Dict:
        """
        Comprehensive resume analysis

        Args:
            text: Resume text to analyze

        Returns:
            Dictionary containing resume analysis results
        """
        results = {
            'overall_score': 0.0,
            'completeness_score': 0.0,
            'format_score': 0.0,
            'content_score': 0.0,
            'keyword_score': 0.0,
            'sections_found': [],
            'missing_sections': [],
            'contact_info': {},
            'experience_analysis': {},
            'education_analysis': {},
            'skills_analysis': {},
            'strengths': [],
            'weaknesses': [],
            'suggestions': [],
            'details': {}
        }

        if not text or len(text.strip()) < 100:
            return results

        # Clean and preprocess text
        clean_text = self._preprocess_text(text)

        # Analyze different aspects
        sections = self._extract_sections(clean_text)
        results['sections_found'] = sections['found']
        results['missing_sections'] = sections['missing']

        # Calculate completeness score
        results['completeness_score'] = self._calculate_completeness_score(sections['found'])

        # Analyze format
        results['format_score'] = self._analyze_format(clean_text)

        # Analyze content quality
        results['content_score'] = self._analyze_content_quality(clean_text, sections)

        # Analyze keywords and skills
        results['keyword_score'] = self._analyze_keywords(clean_text)

        # Extract contact information
        results['contact_info'] = self._extract_contact_info(clean_text)

        # Analyze experience section
        results['experience_analysis'] = self._analyze_experience_section(clean_text)

        # Analyze education section
        results['education_analysis'] = self._analyze_education_section(clean_text)

        # Analyze skills section
        results['skills_analysis'] = self._analyze_skills_section(clean_text)

        # Calculate overall score
        weights = {
            'completeness': 0.25,
            'format': 0.20,
            'content': 0.30,
            'keyword': 0.25
        }

        results['overall_score'] = (
            results['completeness_score'] * weights['completeness'] +
            results['format_score'] * weights['format'] +
            results['content_score'] * weights['content'] +
            results['keyword_score'] * weights['keyword']
        )

        # Identify strengths and weaknesses
        results['strengths'], results['weaknesses'] = self._identify_strengths_weaknesses(results)

        # Generate suggestions
        results['suggestions'] = self._generate_resume_suggestions(results)

        # Store detailed information
        results['details'] = {
            'word_count': len(clean_text.split()),
            'line_count': len(clean_text.split('\n')),
            'sections_count': len(results['sections_found']),
            'missing_sections_count': len(results['missing_sections'])
        }

        return results

    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize resume text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Fix common OCR errors (if any)
        text = re.sub(r'[lI]', '1', text)  # Fix potential 1/l/I confusion
        text = re.sub(r'[oO]', '0', text)  # Fix potential 0/o/O confusion

        return text.strip()

    def _extract_sections(self, text: str) -> Dict:
        """Extract resume sections"""
        sections = {
            'found': [],
            'missing': []
        }

        # Convert to lowercase for matching
        text_lower = text.lower()

        # Check for each expected section
        for section in self.expected_sections:
            # Common variations of section headers
            section_patterns = self._get_section_patterns(section)

            found = False
            for pattern in section_patterns:
                if re.search(pattern, text_lower):
                    sections['found'].append(section)
                    found = True
                    break

            if not found:
                sections['missing'].append(section)

        return sections

    def _get_section_patterns(self, section: str) -> List[str]:
        """Get regex patterns for section headers"""
        patterns = {
            'contact_information': [
                r'\b(contact|personal|info)\b.*\n.*\n.*\n',
                r'\b(name|email|phone|address|linkedin)\b',
                r'\b(profile|summary)\b'
            ],
            'summary': [
                r'\b(summary|objective|profile|overview)\b',
                r'\b(professional summary|career objective)\b'
            ],
            'experience': [
                r'\b(experience|work|employment|career)\b',
                r'\b(professional experience|work history)\b'
            ],
            'education': [
                r'\b(education|academic|degree|qualification)\b',
                r'\b(educational background|academic history)\b'
            ],
            'skills': [
                r'\b(skills|abilities|competencies|expertise)\b',
                r'\b(technical skills|core competencies)\b'
            ],
            'certifications': [
                r'\b(certifications?|certificates?|licenses?)\b',
                r'\b(professional certifications?|credentials)\b'
            ],
            'projects': [
                r'\b(projects?|portfolio|work samples)\b',
                r'\b(personal projects?|academic projects?)\b'
            ],
            'awards': [
                r'\b(awards?|honors?|achievements?|recognition)\b',
                r'\b(awards and honors?|achievements?)\b'
            ]
        }

        return patterns.get(section, [f'\\b{section.replace("_", " ")}\\b'])

    def _calculate_completeness_score(self, found_sections: List[str]) -> float:
        """Calculate how complete the resume is"""
        total_expected = len(self.expected_sections)
        found_count = len(found_sections)

        # Weight sections differently
        weights = {
            'contact_information': 0.15,  # Essential
            'experience': 0.25,           # Most important
            'education': 0.20,            # Very important
            'skills': 0.15,               # Important
            'summary': 0.10,              # Nice to have
            'certifications': 0.08,       # Nice to have
            'projects': 0.05,             # Nice to have
            'awards': 0.02                # Optional
        }

        score = 0.0
        for section in found_sections:
            score += weights.get(section, 0.05) * 100

        return min(100.0, score)

    def _analyze_format(self, text: str) -> float:
        """Analyze resume formatting"""
        score = 100.0

        # Check for consistent formatting
        lines = text.split('\n')

        # Check for bullet points (good formatting)
        bullet_count = sum(1 for line in lines if line.strip().startswith(('•', '-', '*', '◦')))

        # Check for proper section headers (capitalization)
        header_count = sum(1 for line in lines if line.isupper() and len(line.strip()) > 2)

        # Check for consistent spacing
        empty_lines = sum(1 for line in lines if not line.strip())

        # Positive indicators
        if bullet_count > 5:
            score += 10  # Well-formatted with bullets
        if header_count > 2:
            score += 5   # Clear section headers
        if 3 <= empty_lines <= 10:
            score += 5   # Good spacing

        # Negative indicators
        if len(lines) < 10:
            score -= 20  # Too short
        if bullet_count == 0:
            score -= 15  # No bullet points (poor formatting)
        if empty_lines > 20:
            score -= 10  # Too much empty space

        return max(0.0, min(100.0, score))

    def _analyze_content_quality(self, text: str, sections: Dict) -> float:
        """Analyze content quality"""
        score = 50.0  # Base score

        # Check for quantifiable achievements
        quantifiable = self._find_quantifiable_achievements(text)

        # Check for action verbs
        action_verb_count = self._count_action_verbs(text)

        # Check for specific details vs generic statements
        generic_phrases = [
            'responsible for', 'worked on', 'helped with', 'involved in',
            'participated in', 'assisted with'
        ]

        generic_count = sum(text.lower().count(phrase) for phrase in generic_phrases)

        # Positive indicators
        if quantifiable > 0:
            score += 20  # Has quantifiable achievements
        if action_verb_count > 3:
            score += 15  # Uses action verbs
        if len(text.split()) > 200:
            score += 10  # Sufficient content length

        # Negative indicators
        if generic_count > 3:
            score -= 15  # Too many generic phrases
        if quantifiable == 0:
            score -= 10  # No quantifiable achievements

        return max(0.0, min(100.0, score))

    def _analyze_keywords(self, text: str) -> float:
        """Analyze keyword optimization"""
        text_lower = text.lower()

        # Count relevant keywords across categories
        total_keywords = 0
        matched_keywords = 0

        for category, keywords in self.job_categories.items():
            for keyword in keywords:
                total_keywords += 1
                if keyword in text_lower:
                    matched_keywords += 1

        # Calculate keyword density (should be reasonable, not stuffed)
        keyword_density = matched_keywords / total_keywords if total_keywords > 0 else 0

        # Ideal density is around 2-5%
        if 0.02 <= keyword_density <= 0.05:
            score = 90  # Good keyword usage
        elif keyword_density > 0.05:
            score = 60  # Keyword stuffing
        else:
            score = 40  # Too few keywords

        return score

    def _extract_contact_info(self, text: str) -> Dict:
        """Extract contact information"""
        contact_info = {
            'name': None,
            'email': None,
            'phone': None,
            'linkedin': None,
            'location': None
        }

        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]

        # Extract phone number
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = phones[0]

        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[^\s]+'
        linkedins = re.findall(linkedin_pattern, text)
        if linkedins:
            contact_info['linkedin'] = linkedins[0]

        # Extract name (first line or capitalized words)
        lines = text.split('\n')
        first_line = lines[0].strip()
        if first_line and len(first_line.split()) <= 4:  # Likely a name
            contact_info['name'] = first_line

        # Extract location
        location_indicators = ['city', 'state', 'country', 'location']
        for line in lines[:10]:  # Check first 10 lines
            if any(indicator in line.lower() for indicator in location_indicators):
                contact_info['location'] = line.strip()
                break

        return contact_info

    def _analyze_experience_section(self, text: str) -> Dict:
        """Analyze experience section"""
        analysis = {
            'years_experience': 0,
            'job_titles': [],
            'companies': [],
            'achievements': [],
            'responsibilities': []
        }

        # Extract job titles and companies
        lines = text.split('\n')

        for line in lines:
            line_lower = line.lower().strip()

            # Look for job titles (capitalized words, specific patterns)
            if (line and line[0].isupper() and len(line.split()) <= 5 and
                not line.isupper()):  # Not a section header
                analysis['job_titles'].append(line.strip())

            # Look for company names (often preceded by "at" or similar)
            if re.search(r'\bat\s+[A-Z][a-zA-Z\s&]+', line):
                company_match = re.search(r'\bat\s+([A-Z][a-zA-Z\s&]+)', line)
                if company_match:
                    analysis['companies'].append(company_match.group(1).strip())

        # Estimate years of experience (rough calculation)
        experience_indicators = ['years?', 'year', 'experience', 'tenure']
        for line in lines:
            if any(indicator in line.lower() for indicator in experience_indicators):
                numbers = re.findall(r'\d+', line)
                if numbers:
                    analysis['years_experience'] = max(analysis['years_experience'], int(numbers[0]))

        return analysis

    def _analyze_education_section(self, text: str) -> Dict:
        """Analyze education section"""
        analysis = {
            'degrees': [],
            'institutions': [],
            'gpa': None,
            'graduation_years': []
        }

        # Common degree patterns
        degree_patterns = [
            r'\b(Bachelor|Master|PhD|Doctorate|MBA|B\.S\.|B\.A\.|M\.S\.|M\.A\.|Ph\.D\.)\b',
            r'\b(Bachelors?|Masters?|Doctorate)\b'
        ]

        # Extract degrees
        for pattern in degree_patterns:
            degrees = re.findall(pattern, text, re.IGNORECASE)
            analysis['degrees'].extend(degrees)

        # Extract institutions
        institution_patterns = [
            r'\b(University|College|Institute|School)\s+of\s+[A-Z][a-z]+',
            r'\b[A-Z][a-z]+\s+(University|College|Institute)'
        ]

        for pattern in institution_patterns:
            institutions = re.findall(pattern, text, re.IGNORECASE)
            analysis['institutions'].extend(institutions)

        # Extract GPA
        gpa_pattern = r'GPA[:\s]+(\d\.\d+)'
        gpa_match = re.search(gpa_pattern, text, re.IGNORECASE)
        if gpa_match:
            analysis['gpa'] = float(gpa_match.group(1))

        # Extract graduation years
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, text)
        analysis['graduation_years'] = [int(year) for year in years if 1950 <= int(year) <= datetime.now().year]

        return analysis

    def _analyze_skills_section(self, text: str) -> Dict:
        """Analyze skills section"""
        analysis = {
            'technical_skills': [],
            'soft_skills': [],
            'languages': [],
            'tools': [],
            'skill_count': 0
        }

        # Common skill categories
        skill_patterns = {
            'technical': ['python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'node', 'git'],
            'soft': ['leadership', 'communication', 'teamwork', 'problem.solving', 'analytical'],
            'languages': ['english', 'spanish', 'french', 'german', 'chinese', 'japanese'],
            'tools': ['excel', 'powerpoint', 'word', 'jira', 'confluence', 'slack']
        }

        text_lower = text.lower()

        for category, skills in skill_patterns.items():
            for skill in skills:
                if skill in text_lower:
                    if category == 'technical':
                        analysis['technical_skills'].append(skill)
                    elif category == 'soft':
                        analysis['soft_skills'].append(skill)
                    elif category == 'languages':
                        analysis['languages'].append(skill)
                    elif category == 'tools':
                        analysis['tools'].append(skill)

        analysis['skill_count'] = (len(analysis['technical_skills']) +
                                 len(analysis['soft_skills']) +
                                 len(analysis['languages']) +
                                 len(analysis['tools']))

        return analysis

    def _find_quantifiable_achievements(self, text: str) -> int:
        """Find quantifiable achievements"""
        # Patterns for numbers with context
        quantifiable_patterns = [
            r'\d+%',           # Percentages
            r'\$\d+',          # Dollar amounts
            r'\d+\s*(million|billion|thousand)',  # Large numbers
            r'\d+\s*(users|customers|clients|employees|projects)',  # Count nouns
            r'increased?\s+by\s+\d+',  # Increase patterns
            r'reduced?\s+by\s+\d+',   # Reduction patterns
        ]

        count = 0
        for pattern in quantifiable_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            count += len(matches)

        return count

    def _count_action_verbs(self, text: str) -> int:
        """Count action verbs used"""
        action_verb_count = 0

        for verb in self.action_verbs:
            action_verb_count += text.lower().count(verb)

        return action_verb_count

    def _identify_strengths_weaknesses(self, results: Dict) -> Tuple[List[str], List[str]]:
        """Identify resume strengths and weaknesses"""
        strengths = []
        weaknesses = []

        # Completeness strengths/weaknesses
        if results['completeness_score'] >= 80:
            strengths.append("Complete resume with all essential sections")
        elif results['completeness_score'] < 50:
            weaknesses.append("Missing important resume sections")

        # Format strengths/weaknesses
        if results['format_score'] >= 80:
            strengths.append("Well-formatted and professional appearance")
        elif results['format_score'] < 60:
            weaknesses.append("Poor formatting - consider improving layout")

        # Content strengths/weaknesses
        if results['content_score'] >= 80:
            strengths.append("Strong content with quantifiable achievements")
        elif results['content_score'] < 50:
            weaknesses.append("Weak content - add more specific achievements")

        # Keyword strengths/weaknesses
        if results['keyword_score'] >= 80:
            strengths.append("Good use of relevant keywords")
        elif results['keyword_score'] < 50:
            weaknesses.append("Missing important keywords for ATS")

        return strengths, weaknesses

    def _generate_resume_suggestions(self, results: Dict) -> List[str]:
        """Generate resume improvement suggestions"""
        suggestions = []

        # Missing sections suggestions
        if results['missing_sections']:
            suggestions.append(f"Add missing sections: {', '.join(results['missing_sections'])}")

        # Contact info suggestions
        contact_info = results['contact_info']
        missing_contact = [k for k, v in contact_info.items() if not v]
        if missing_contact:
            suggestions.append(f"Add missing contact information: {', '.join(missing_contact)}")

        # Content suggestions
        if results['content_score'] < 70:
            suggestions.append("Add more quantifiable achievements and specific results")
            suggestions.append("Use action verbs to describe accomplishments")

        # Format suggestions
        if results['format_score'] < 70:
            suggestions.append("Improve formatting with consistent bullets and spacing")
            suggestions.append("Use clear section headers")

        # Keyword suggestions
        if results['keyword_score'] < 70:
            suggestions.append("Include more industry-specific keywords")
            suggestions.append("Research job descriptions for relevant keywords")

        # Length suggestions
        word_count = results['details'].get('word_count', 0)
        if word_count < 150:
            suggestions.append("Resume seems too short - add more details")
        elif word_count > 800:
            suggestions.append("Resume is quite long - consider condensing")

        return suggestions

    def generate_report(self, text: str, results: Dict) -> str:
        """Generate detailed resume analysis report"""
        report = []
        report.append("=== RESUME ANALYSIS REPORT ===\n")
        report.append(f"Overall Score: {results['overall_score']".1f"}%\n")
        report.append(f"Completeness Score: {results['completeness_score']".1f"}%\n")
        report.append(f"Format Score: {results['format_score']".1f"}%\n")
        report.append(f"Content Score: {results['content_score']".1f"}%\n")
        report.append(f"Keyword Score: {results['keyword_score']".1f"}%\n")

        # Sections analysis
        if results['sections_found'] or results['missing_sections']:
            report.append(f"\nResume Sections:")
            if results['sections_found']:
                report.append(f"  Found: {', '.join(results['sections_found'])}")
            if results['missing_sections']:
                report.append(f"  Missing: {', '.join(results['missing_sections'])}")

        # Contact information
        contact_info = results['contact_info']
        if any(contact_info.values()):
            report.append(f"\nContact Information:")
            for key, value in contact_info.items():
                if value:
                    report.append(f"  {key.title()}: {value}")

        # Experience analysis
        exp_analysis = results['experience_analysis']
        if exp_analysis:
            report.append(f"\nExperience Analysis:")
            if exp_analysis.get('job_titles'):
                report.append(f"  Job Titles: {', '.join(exp_analysis['job_titles'][:3])}")
            if exp_analysis.get('years_experience'):
                report.append(f"  Years Experience: {exp_analysis['years_experience']}")

        # Skills analysis
        skills_analysis = results['skills_analysis']
        if skills_analysis.get('skill_count', 0) > 0:
            report.append(f"\nSkills Analysis:")
            if skills_analysis.get('technical_skills'):
                report.append(f"  Technical Skills: {', '.join(skills_analysis['technical_skills'][:5])}")
            if skills_analysis.get('soft_skills'):
                report.append(f"  Soft Skills: {', '.join(skills_analysis['soft_skills'][:3])}")

        # Strengths and weaknesses
        if results['strengths']:
            report.append(f"\nStrengths:")
            for strength in results['strengths']:
                report.append(f"  ✓ {strength}")

        if results['weaknesses']:
            report.append(f"\nAreas for Improvement:")
            for weakness in results['weaknesses']:
                report.append(f"  • {weakness}")

        # Suggestions
        if results['suggestions']:
            report.append(f"\nRecommendations:")
            for i, suggestion in enumerate(results['suggestions'], 1):
                report.append(f"  {i}. {suggestion}")

        return '\n'.join(report)