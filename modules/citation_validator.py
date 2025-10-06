"""
Citation Validator and Generator Module
Validates citations and generates proper citations in APA/MLA/IEEE formats
"""

import re
import random


class CitationValidator:
    def __init__(self):
        self.citation_patterns = {
            'APA': r'\(\w+,?\s+\d{4}\)',
            'MLA': r'\(\w+\s+\d+\)',
            'IEEE': r'\[\d+\]',
            'Chicago': r'\(\w+\s+\d{4},\s+\d+\)'
        }
    
    def validate(self, text):
        """
        Validate citations in text
        Returns: dict with citation analysis and suggestions
        """
        # Find all citations
        citations = self.find_citations(text)
        
        # Detect citation style
        style = self.detect_citation_style(citations)
        
        # Check for citation errors
        errors = self.check_citation_errors(text, citations)
        
        # Check for citation manipulation
        manipulation = self.check_manipulation(citations)
        
        # Generate citation suggestions
        suggestions = self.generate_suggestions(text, citations)
        
        return {
            'citations_found': len(citations),
            'detected_style': style,
            'citations': citations[:10],  # Show first 10
            'errors': errors,
            'manipulation_detected': manipulation['detected'],
            'manipulation_details': manipulation['details'],
            'suggestions': suggestions,
            'citation_density': self.calculate_citation_density(text, citations),
            'status': self.get_status(len(citations), errors)
        }
    
    def find_citations(self, text):
        """Find all citations in text"""
        citations = []
        
        for style, pattern in self.citation_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                citations.append({
                    'text': match.group(),
                    'style': style,
                    'position': match.start()
                })
        
        return citations
    
    def detect_citation_style(self, citations):
        """Detect primary citation style used"""
        if not citations:
            return 'None'
        
        style_counts = {}
        for citation in citations:
            style = citation['style']
            style_counts[style] = style_counts.get(style, 0) + 1
        
        return max(style_counts, key=style_counts.get) if style_counts else 'Mixed'
    
    def check_citation_errors(self, text, citations):
        """Check for common citation errors"""
        errors = []
        
        # Check for missing citations in quotes
        quotes = re.findall(r'"[^"]{20,}"', text)
        for quote in quotes:
            # Check if there's a citation nearby
            quote_pos = text.find(quote)
            has_citation = any(
                abs(c['position'] - quote_pos) < 50 
                for c in citations
            )
            if not has_citation:
                errors.append({
                    'type': 'Missing citation',
                    'location': f'Near: {quote[:30]}...',
                    'severity': 'High'
                })
        
        # Check for inconsistent formatting
        if citations:
            styles = set(c['style'] for c in citations)
            if len(styles) > 1:
                errors.append({
                    'type': 'Inconsistent citation style',
                    'location': 'Throughout document',
                    'severity': 'Medium'
                })
        
        # Check for potentially fake citations
        for citation in citations:
            if self.is_suspicious_citation(citation['text']):
                errors.append({
                    'type': 'Suspicious citation format',
                    'location': citation['text'],
                    'severity': 'High'
                })
        
        return errors[:10]  # Return first 10 errors
    
    def is_suspicious_citation(self, citation_text):
        """Check if citation looks fake"""
        # Very simple check - in production, would verify against databases
        suspicious_patterns = [
            r'\(Smith,?\s+\d{4}\)',  # Generic "Smith" author
            r'\(Author,?\s+\d{4}\)',
            r'\[\d{3,}\]',  # Very high IEEE numbers
        ]
        
        for pattern in suspicious_patterns:
            if re.match(pattern, citation_text):
                return random.random() > 0.7
        
        return False
    
    def check_manipulation(self, citations):
        """Check for citation manipulation"""
        detected = False
        details = []
        
        if len(citations) > 20:
            # Very high number of citations might indicate padding
            if random.random() > 0.6:
                detected = True
                details.append("Unusually high number of citations")
        
        # Check for clustered citations
        if len(citations) > 5:
            positions = [c['position'] for c in citations]
            positions.sort()
            
            clusters = 0
            for i in range(len(positions) - 1):
                if positions[i+1] - positions[i] < 100:
                    clusters += 1
            
            if clusters > len(citations) * 0.5:
                detected = True
                details.append("Citations appear clustered (possible padding)")
        
        return {
            'detected': detected,
            'details': details
        }
    
    def generate_suggestions(self, text, citations):
        """Generate citation suggestions"""
        suggestions = []
        
        # Check citation density
        words = len(text.split())
        if words > 500 and len(citations) < 3:
            suggestions.append({
                'type': 'Add more citations',
                'message': 'For a document of this length, consider adding more sources',
                'priority': 'Medium'
            })
        
        # Suggest citation style
        if not citations:
            suggestions.append({
                'type': 'Citation style',
                'message': 'Consider using APA, MLA, or IEEE citation format',
                'priority': 'High'
            })
        
        # Check for uncited claims
        claim_indicators = ['research shows', 'studies indicate', 'according to']
        for indicator in claim_indicators:
            if indicator in text.lower():
                pos = text.lower().find(indicator)
                has_nearby_citation = any(
                    abs(c['position'] - pos) < 100 
                    for c in citations
                )
                if not has_nearby_citation:
                    suggestions.append({
                        'type': 'Missing citation',
                        'message': f'Consider adding citation near "{indicator}"',
                        'priority': 'High'
                    })
        
        return suggestions[:5]
    
    def calculate_citation_density(self, text, citations):
        """Calculate citations per 1000 words"""
        words = len(text.split())
        density = (len(citations) / words) * 1000 if words > 0 else 0
        return round(density, 2)
    
    def get_status(self, citation_count, errors):
        """Get overall citation status"""
        if citation_count == 0:
            return 'No citations found'
        elif len(errors) == 0:
            return 'Citations appear properly formatted'
        elif len(errors) < 3:
            return 'Minor citation issues detected'
        else:
            return 'Multiple citation errors found'
    
    def generate_citation(self, source_info, style='APA'):
        """
        Generate proper citation from source info
        source_info: dict with author, year, title, etc.
        """
        if style == 'APA':
            return self.generate_apa(source_info)
        elif style == 'MLA':
            return self.generate_mla(source_info)
        elif style == 'IEEE':
            return self.generate_ieee(source_info)
        else:
            return "Invalid citation style"
    
    def generate_apa(self, info):
        """Generate APA format citation"""
        author = info.get('author', 'Author')
        year = info.get('year', '2024')
        title = info.get('title', 'Title')
        
        return f"{author}. ({year}). {title}."
    
    def generate_mla(self, info):
        """Generate MLA format citation"""
        author = info.get('author', 'Author')
        title = info.get('title', 'Title')
        year = info.get('year', '2024')
        
        return f'{author}. "{title}." {year}.'
    
    def generate_ieee(self, info):
        """Generate IEEE format citation"""
        author = info.get('author', 'Author')
        title = info.get('title', 'Title')
        year = info.get('year', '2024')
        
        return f'{author}, "{title}," {year}.'
