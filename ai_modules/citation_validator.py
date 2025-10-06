#!/usr/bin/env python3
"""
Citation Validation and Generation Module
Validates existing citations and generates new ones in various formats
"""

import re
import json
import requests
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from urllib.parse import urlparse
import bibtexparser
from bs4 import BeautifulSoup
from config import Config

class CitationValidator:
    """Comprehensive citation validation and generation system"""

    def __init__(self):
        # Citation style patterns
        self.citation_patterns = {
            'apa': self._parse_apa_citations,
            'mla': self._parse_mla_citations,
            'ieee': self._parse_ieee_citations,
            'chicago': self._parse_chicago_citations,
            'harvard': self._parse_harvard_citations
        }

        # Common citation formats
        self.common_formats = {
            'book': self._format_book_citation,
            'journal': self._format_journal_citation,
            'website': self._format_website_citation,
            'conference': self._format_conference_citation
        }

        # DOI validation
        self.doi_pattern = re.compile(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', re.IGNORECASE)

        # URL validation patterns
        self.url_patterns = [
            re.compile(r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w)*)?)?', re.IGNORECASE),
            re.compile(r'www\.[-\w.]+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w)*)?)?', re.IGNORECASE)
        ]

    def validate_citations(self, text: str) -> Dict:
        """
        Validate all citations in the text

        Args:
            text: Text containing citations to validate

        Returns:
            Dictionary containing citation validation results
        """
        results = {
            'overall_score': 100.0,
            'total_citations': 0,
            'valid_citations': 0,
            'invalid_citations': 0,
            'missing_citations': 0,
            'citation_details': [],
            'style_consistency': 'unknown',
            'common_issues': [],
            'suggestions': [],
            'details': {}
        }

        if not text:
            return results

        # Extract citations from text
        citations = self._extract_citations(text)
        results['total_citations'] = len(citations)

        if not citations:
            return results

        # Validate each citation
        valid_count = 0
        citation_analyses = []

        for citation in citations:
            analysis = self._analyze_citation(citation, text)
            citation_analyses.append(analysis)

            if analysis['is_valid']:
                valid_count += 1

        results['valid_citations'] = valid_count
        results['invalid_citations'] = len(citations) - valid_count
        results['citation_details'] = citation_analyses

        # Calculate overall score
        if citations:
            results['overall_score'] = (valid_count / len(citations)) * 100

        # Check style consistency
        results['style_consistency'] = self._check_style_consistency(citation_analyses)

        # Identify common issues
        results['common_issues'] = self._identify_common_issues(citation_analyses)

        # Generate suggestions
        results['suggestions'] = self._generate_suggestions(citation_analyses, text)

        # Store detailed information
        results['details'] = {
            'citations_found': len(citations),
            'validation_rate': valid_count / len(citations) if citations else 0,
            'styles_detected': list(set(analysis.get('detected_style', 'unknown') for analysis in citation_analyses))
        }

        return results

    def generate_citations(self, text: str, style: str = 'apa') -> List[Dict]:
        """
        Generate citations for sources mentioned in text

        Args:
            text: Text containing source information
            style: Citation style (apa, mla, ieee, chicago, harvard)

        Returns:
            List of generated citations
        """
        citations = []

        # Extract potential sources from text
        sources = self._extract_sources_from_text(text)

        for source in sources:
            citation = self._generate_single_citation(source, style)
            if citation:
                citations.append(citation)

        return citations

    def _extract_citations(self, text: str) -> List[Dict]:
        """Extract citations from text using various patterns"""
        citations = []

        # Pattern for in-text citations like (Author, Year) or [1]
        patterns = [
            # APA style: (Author, Year)
            re.compile(r'\(([A-Z][a-z]+(?:\s+[A-Z]\.)?(?:\s*&\s*[A-Z][a-z]+)?),\s*\d{4}\)'),
            # MLA style: (Author Page)
            re.compile(r'\(([A-Z][a-z]+(?:\s+[A-Z]\.)?(?:\s*&\s*[A-Z][a-z]+)?)\s+\d+\)'),
            # IEEE style: [1], [1, 2]
            re.compile(r'\[(\d+(?:\s*,\s*\d+)*)\]'),
            # Numbered citations: 1. or (1)
            re.compile(r'\b(\d+)\.\s|\((\d+)\)'),
        ]

        for pattern in patterns:
            matches = pattern.finditer(text)
            for match in matches:
                citation_text = match.group(0)
                citations.append({
                    'text': citation_text,
                    'position': match.span(),
                    'pattern': pattern.pattern
                })

        # Remove duplicates based on position
        seen_positions = set()
        unique_citations = []

        for citation in citations:
            pos = citation['position']
            if pos not in seen_positions:
                unique_citations.append(citation)
                seen_positions.add(pos)

        return unique_citations

    def _analyze_citation(self, citation: Dict, full_text: str) -> Dict:
        """Analyze a single citation"""
        analysis = {
            'citation_text': citation['text'],
            'is_valid': False,
            'detected_style': 'unknown',
            'issues': [],
            'suggestions': [],
            'context': self._get_citation_context(full_text, citation['position']),
            'references_match': False
        }

        # Detect citation style
        style = self._detect_citation_style(citation['text'])
        analysis['detected_style'] = style

        # Validate based on style
        if style in self.citation_patterns:
            is_valid, issues = self.citation_patterns[style](citation['text'])
            analysis['is_valid'] = is_valid
            analysis['issues'] = issues
        else:
            analysis['issues'].append('Unrecognized citation format')

        # Check if citation has corresponding reference
        analysis['references_match'] = self._check_reference_match(citation['text'], full_text)

        return analysis

    def _detect_citation_style(self, citation_text: str) -> str:
        """Detect citation style from citation text"""
        # APA: (Author, Year)
        if re.search(r'\([A-Z][a-z]+,\s*\d{4}\)', citation_text):
            return 'apa'

        # MLA: (Author Page)
        if re.search(r'\([A-Z][a-z]+(?:\s+[A-Z]\.)?(?:\s*&\s*[A-Z][a-z]+)?\s+\d+\)', citation_text):
            return 'mla'

        # IEEE: [1]
        if re.search(r'^\[\d+\]$', citation_text):
            return 'ieee'

        # Chicago/Harvard: (Author Year) or superscript
        if re.search(r'\([A-Z][a-z]+(?:\s+[A-Z]\.)?\s+\d{4}\)', citation_text):
            return 'chicago'

        return 'unknown'

    def _parse_apa_citations(self, citation_text: str) -> Tuple[bool, List[str]]:
        """Parse APA-style citations"""
        issues = []

        # Check format: (Author, Year)
        if not re.match(r'\([A-Z][a-z]+(?:\s+[A-Z]\.)?(?:\s*&\s*[A-Z][a-z]+(?:\s+[A-Z]\.)?)?,\s*\d{4}\)', citation_text):
            issues.append('Invalid APA format')
            return False, issues

        # Check if year is reasonable (1900-2030)
        year_match = re.search(r'\d{4}', citation_text)
        if year_match:
            year = int(year_match.group())
            if not (1900 <= year <= 2030):
                issues.append('Suspicious publication year')

        return len(issues) == 0, issues

    def _parse_mla_citations(self, citation_text: str) -> Tuple[bool, List[str]]:
        """Parse MLA-style citations"""
        issues = []

        # Check format: (Author Page)
        if not re.match(r'\([A-Z][a-z]+(?:\s+[A-Z]\.)?(?:\s*&\s*[A-Z][a-z]+(?:\s+[A-Z]\.)?)?\s+\d+\)', citation_text):
            issues.append('Invalid MLA format')
            return False, issues

        # Check if page number is reasonable
        page_match = re.search(r'\d+', citation_text)
        if page_match:
            page = int(page_match.group())
            if page > 1000:
                issues.append('Suspicious page number')

        return len(issues) == 0, issues

    def _parse_ieee_citations(self, citation_text: str) -> Tuple[bool, List[str]]:
        """Parse IEEE-style citations"""
        issues = []

        # Check format: [1] or [1, 2, 3]
        if not re.match(r'^\[\d+(?:\s*,\s*\d+)*\]$', citation_text):
            issues.append('Invalid IEEE format')
            return False, issues

        # Check if numbers are reasonable
        numbers = [int(x.strip()) for x in citation_text.strip('[]').split(',')]
        if any(num > 1000 or num < 1 for num in numbers):
            issues.append('Suspicious citation numbers')

        return len(issues) == 0, issues

    def _parse_chicago_citations(self, citation_text: str) -> Tuple[bool, List[str]]:
        """Parse Chicago-style citations"""
        issues = []

        # Check format: (Author Year) or superscript
        if not (re.match(r'\([A-Z][a-z]+(?:\s+[A-Z]\.)?\s+\d{4}\)', citation_text) or
                re.match(r'^\d+$', citation_text)):  # Superscript number
            issues.append('Invalid Chicago format')
            return False, issues

        return len(issues) == 0, issues

    def _parse_harvard_citations(self, citation_text: str) -> Tuple[bool, List[str]]:
        """Parse Harvard-style citations"""
        issues = []

        # Check format: (Author Year)
        if not re.match(r'\([A-Z][a-z]+(?:\s+[A-Z]\.)?\s+\d{4}\)', citation_text):
            issues.append('Invalid Harvard format')
            return False, issues

        # Check year
        year_match = re.search(r'\d{4}', citation_text)
        if year_match:
            year = int(year_match.group())
            if not (1900 <= year <= 2030):
                issues.append('Suspicious publication year')

        return len(issues) == 0, issues

    def _get_citation_context(self, text: str, position: Tuple[int, int]) -> str:
        """Get context around citation"""
        start, end = position
        context_start = max(0, start - 50)
        context_end = min(len(text), end + 50)

        context = text[context_start:context_end]
        return context.strip()

    def _check_reference_match(self, citation_text: str, full_text: str) -> bool:
        """Check if citation has corresponding reference in text"""
        # Extract author/year from citation
        author_year_pattern = re.search(r'\(([A-Z][a-z]+(?:\s+[A-Z]\.)?(?:\s*&\s*[A-Z][a-z]+)?),\s*(\d{4})\)', citation_text)

        if not author_year_pattern:
            return False

        author, year = author_year_pattern.groups()

        # Look for reference section or bibliography
        ref_indicators = ['references', 'bibliography', 'works cited', 'literature cited']

        for indicator in ref_indicators:
            if indicator.lower() in full_text.lower():
                # Simple check: look for author and year in reference section
                ref_section = self._extract_reference_section(full_text, indicator)
                if author.lower() in ref_section.lower() and year in ref_section:
                    return True

        return False

    def _extract_reference_section(self, text: str, indicator: str) -> str:
        """Extract reference section from text"""
        lines = text.lower().split('\n')
        ref_start = -1

        for i, line in enumerate(lines):
            if indicator in line:
                ref_start = i
                break

        if ref_start == -1:
            return ""

        # Get next 50 lines as reference section
        ref_section = '\n'.join(lines[ref_start:ref_start + 50])
        return ref_section

    def _check_style_consistency(self, citation_analyses: List[Dict]) -> str:
        """Check consistency of citation styles"""
        styles = [analysis.get('detected_style', 'unknown') for analysis in citation_analyses]
        style_counts = {}

        for style in styles:
            style_counts[style] = style_counts.get(style, 0) + 1

        if not style_counts:
            return 'none'

        # Check if one style dominates
        total_citations = len(citation_analyses)
        for style, count in style_counts.items():
            if count / total_citations > 0.8:  # 80% of citations use same style
                return style

        return 'mixed'

    def _identify_common_issues(self, citation_analyses: List[Dict]) -> List[str]:
        """Identify common citation issues"""
        issues = []

        # Count issue types
        issue_counts = {}
        for analysis in citation_analyses:
            for issue in analysis.get('issues', []):
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

        # Return most common issues
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)

        for issue, count in sorted_issues[:5]:  # Top 5 issues
            issues.append(f"{issue} ({count} occurrences)")

        return issues

    def _generate_suggestions(self, citation_analyses: List[Dict], full_text: str) -> List[str]:
        """Generate suggestions for citation improvements"""
        suggestions = []

        # Check for missing references section
        has_references = any('references' in analysis['context'].lower() for analysis in citation_analyses)

        if not has_references:
            suggestions.append("Consider adding a References or Bibliography section")

        # Check for inconsistent formatting
        styles = list(set(analysis.get('detected_style', 'unknown') for analysis in citation_analyses))
        if len(styles) > 1 and 'unknown' not in styles:
            suggestions.append(f"Multiple citation styles detected: {', '.join(styles)}. Consider using consistent formatting.")

        # Check for incomplete citations
        for analysis in citation_analyses:
            if not analysis['is_valid']:
                suggestions.append(f"Fix citation: '{analysis['citation_text']}' - {', '.join(analysis['issues'])}")

        return suggestions

    def _extract_sources_from_text(self, text: str) -> List[Dict]:
        """Extract potential sources from text for citation generation"""
        sources = []

        # Look for URLs
        for pattern in self.url_patterns:
            urls = pattern.findall(text)
            for url in urls:
                if self._is_valid_url(url):
                    sources.append({
                        'type': 'website',
                        'url': url,
                        'title': self._extract_title_from_url(url) or "Web Source"
                    })

        # Look for book/journal mentions
        # Pattern: Author (Year) Title
        book_pattern = re.compile(r'([A-Z][a-z]+(?:\s+[A-Z]\.)?(?:\s*&\s*[A-Z][a-z]+)?)\s*\((\d{4})\)\s*([^.!?]+)')
        matches = book_pattern.findall(text)

        for match in matches:
            author, year, title = match
            sources.append({
                'type': 'book',
                'author': author,
                'year': year,
                'title': title.strip()
            })

        return sources

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and bool(parsed.scheme)
        except:
            return False

    def _extract_title_from_url(self, url: str) -> Optional[str]:
        """Extract page title from URL (simplified)"""
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.find('title')
                return title.get_text().strip() if title else None
        except:
            pass

        return None

    def _generate_single_citation(self, source: Dict, style: str) -> Optional[Dict]:
        """Generate a single citation in specified style"""
        try:
            if source['type'] in self.common_formats:
                citation_text = self.common_formats[source['type']](source, style)
                return {
                    'source': source,
                    'style': style,
                    'citation': citation_text,
                    'generated_at': datetime.utcnow().isoformat()
                }
        except Exception as e:
            print(f"Error generating citation: {e}")

        return None

    def _format_book_citation(self, source: Dict, style: str) -> str:
        """Format book citation"""
        author = source.get('author', 'Unknown Author')
        year = source.get('year', 'n.d.')
        title = source.get('title', 'Unknown Title')

        if style == 'apa':
            return f"{author}. ({year}). {title}. Publisher."
        elif style == 'mla':
            return f"{author}. {title}. Publisher, {year}."
        elif style == 'ieee':
            return f"{author}, \"{title},\" {year}."

        return f"{author} ({year}) {title}"

    def _format_journal_citation(self, source: Dict, style: str) -> str:
        """Format journal citation"""
        author = source.get('author', 'Unknown Author')
        year = source.get('year', 'n.d.')
        title = source.get('title', 'Unknown Title')
        journal = source.get('journal', 'Unknown Journal')
        volume = source.get('volume', '')
        pages = source.get('pages', '')

        if style == 'apa':
            return f"{author}. ({year}). {title}. {journal}, {volume}, {pages}."
        elif style == 'mla':
            return f"{author}. \"{title}.\" {journal}, vol. {volume}, {year}, pp. {pages}."

        return f"{author} ({year}) {title}, {journal}"

    def _format_website_citation(self, source: Dict, style: str) -> str:
        """Format website citation"""
        author = source.get('author', 'Unknown Author')
        title = source.get('title', 'Web Page Title')
        url = source.get('url', '')
        year = source.get('year', datetime.now().year)

        if style == 'apa':
            return f"{author}. ({year}). {title}. Retrieved from {url}"
        elif style == 'mla':
            return f"{author}. \"{title}.\" Website Title, {year}, {url}."

        return f"{author} ({year}) {title}, {url}"

    def _format_conference_citation(self, source: Dict, style: str) -> str:
        """Format conference citation"""
        author = source.get('author', 'Unknown Author')
        year = source.get('year', 'n.d.')
        title = source.get('title', 'Unknown Title')
        conference = source.get('conference', 'Unknown Conference')

        if style == 'apa':
            return f"{author}. ({year}). {title}. In Proceedings of {conference}."

        return f"{author} ({year}) {title}, {conference}"

    def generate_report(self, text: str, results: Dict) -> str:
        """Generate detailed citation validation report"""
        report = []
        report.append("=== CITATION VALIDATION REPORT ===\n")
        report.append(f"Total Citations Found: {results['total_citations']}\n")
        report.append(f"Valid Citations: {results['valid_citations']}\n")
        report.append(f"Invalid Citations: {results['invalid_citations']}\n")
        report.append(f"Overall Score: {results['overall_score']".1f"}%\n")
        report.append(f"Style Consistency: {results['style_consistency'].upper()}\n")

        if results['common_issues']:
            report.append(f"\nCommon Issues:")
            for issue in results['common_issues']:
                report.append(f"  • {issue}")

        if results['suggestions']:
            report.append(f"\nSuggestions:")
            for suggestion in results['suggestions']:
                report.append(f"  • {suggestion}")

        if results['citation_details']:
            report.append(f"\nDetailed Citation Analysis:")
            for i, detail in enumerate(results['citation_details'][:10], 1):  # Show first 10
                report.append(f"\n  {i}. '{detail['citation_text']}'")
                report.append(f"     Style: {detail['detected_style']}")
                report.append(f"     Valid: {detail['is_valid']}")
                if detail['issues']:
                    report.append(f"     Issues: {', '.join(detail['issues'])}")

        return '\n'.join(report)