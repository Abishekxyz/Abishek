"""
Resume Analyzer Module (Module 8)
Analyzes resumes for quality, keywords, ATS compatibility, and provides improvement suggestions
"""

import re
from collections import Counter


class ResumeAnalyzer:
    def __init__(self):
        # ATS-friendly keywords by category
        self.skill_keywords = {
            'technical': ['python', 'java', 'javascript', 'sql', 'aws', 'docker', 'kubernetes', 'react', 'node', 'machine learning', 'ai', 'data analysis'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'problem-solving', 'analytical', 'creative', 'organized', 'detail-oriented'],
            'action_verbs': ['achieved', 'developed', 'managed', 'led', 'created', 'implemented', 'designed', 'improved', 'increased', 'reduced']
        }
        
        # Common resume sections
        self.required_sections = ['experience', 'education', 'skills']
        self.optional_sections = ['summary', 'objective', 'projects', 'certifications', 'awards']
    
    def analyze(self, resume_text):
        """
        Comprehensive resume analysis
        Returns: dict with scores, suggestions, and detailed analysis
        """
        # Convert to lowercase for analysis
        text_lower = resume_text.lower()
        
        # Analyze different aspects
        sections_analysis = self.analyze_sections(resume_text)
        keywords_analysis = self.analyze_keywords(text_lower)
        ats_compatibility = self.check_ats_compatibility(resume_text)
        formatting_analysis = self.analyze_formatting(resume_text)
        content_quality = self.analyze_content_quality(resume_text)
        contact_info = self.check_contact_information(resume_text)
        action_verbs = self.analyze_action_verbs(text_lower)
        
        # Calculate overall score
        overall_score = self.calculate_overall_score(
            sections_analysis, keywords_analysis, ats_compatibility,
            formatting_analysis, content_quality, contact_info, action_verbs
        )
        
        # Generate improvement suggestions
        suggestions = self.generate_suggestions(
            sections_analysis, keywords_analysis, ats_compatibility,
            formatting_analysis, content_quality, contact_info, action_verbs
        )
        
        return {
            'overall_score': overall_score,
            'sections': sections_analysis,
            'keywords': keywords_analysis,
            'ats_compatibility': ats_compatibility,
            'formatting': formatting_analysis,
            'content_quality': content_quality,
            'contact_info': contact_info,
            'action_verbs': action_verbs,
            'suggestions': suggestions,
            'status': self.get_status(overall_score)
        }
    
    def analyze_sections(self, text):
        """Analyze resume sections"""
        text_lower = text.lower()
        found_sections = []
        missing_required = []
        
        # Check required sections
        for section in self.required_sections:
            if section in text_lower:
                found_sections.append(section)
            else:
                missing_required.append(section)
        
        # Check optional sections
        found_optional = []
        for section in self.optional_sections:
            if section in text_lower:
                found_optional.append(section)
        
        section_score = (len(found_sections) / len(self.required_sections)) * 100
        
        return {
            'found_required': found_sections,
            'missing_required': missing_required,
            'found_optional': found_optional,
            'section_score': round(section_score, 2),
            'recommendation': 'All required sections present' if not missing_required else f'Add missing sections: {", ".join(missing_required)}'
        }
    
    def analyze_keywords(self, text_lower):
        """Analyze resume keywords for ATS"""
        found_keywords = {
            'technical': [],
            'soft_skills': [],
            'action_verbs': []
        }
        
        keyword_counts = {
            'technical': 0,
            'soft_skills': 0,
            'action_verbs': 0
        }
        
        # Find keywords
        for category, keywords in self.skill_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords[category].append(keyword)
                    keyword_counts[category] += 1
        
        total_keywords = sum(keyword_counts.values())
        
        return {
            'total_keywords': total_keywords,
            'found_keywords': found_keywords,
            'keyword_counts': keyword_counts,
            'keyword_density': self.calculate_keyword_density(text_lower, total_keywords),
            'recommendation': 'Good keyword usage' if total_keywords > 10 else 'Add more relevant keywords for ATS'
        }
    
    def calculate_keyword_density(self, text, keyword_count):
        """Calculate keyword density"""
        words = len(text.split())
        density = (keyword_count / words) * 100 if words > 0 else 0
        return round(density, 2)
    
    def check_ats_compatibility(self, text):
        """Check ATS (Applicant Tracking System) compatibility"""
        issues = []
        score = 100
        
        # Check for problematic formatting
        if re.search(r'[│┤╢╖╕╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌]', text):
            issues.append("Contains special characters that may confuse ATS")
            score -= 20
        
        # Check for tables (simplified check)
        if text.count('|') > 5:
            issues.append("May contain tables which can confuse ATS")
            score -= 15
        
        # Check for headers/footers indicators
        if re.search(r'page\s+\d+\s+of\s+\d+', text.lower()):
            issues.append("Contains page numbers which may confuse ATS")
            score -= 10
        
        # Check length
        words = len(text.split())
        if words < 200:
            issues.append("Resume is too short (less than 200 words)")
            score -= 20
        elif words > 1000:
            issues.append("Resume is too long (more than 1000 words)")
            score -= 10
        
        # Check for contact information
        if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            issues.append("Email address not found")
            score -= 15
        
        if not issues:
            issues.append("Resume is ATS-compatible")
        
        return {
            'ats_score': max(score, 0),
            'is_compatible': score >= 70,
            'issues': issues,
            'recommendation': 'ATS-friendly' if score >= 70 else 'Needs ATS optimization'
        }
    
    def analyze_formatting(self, text):
        """Analyze resume formatting"""
        issues = []
        score = 100
        
        # Check for consistent spacing
        lines = text.split('\n')
        empty_line_ratio = sum(1 for line in lines if not line.strip()) / len(lines) if lines else 0
        
        if empty_line_ratio > 0.5:
            issues.append("Too many empty lines")
            score -= 10
        
        # Check for bullet points
        bullet_count = sum(1 for line in lines if line.strip().startswith(('•', '-', '*', '○')))
        if bullet_count < 3:
            issues.append("Consider using bullet points for better readability")
            score -= 15
        
        # Check for sections (headers)
        section_headers = sum(1 for line in lines if line.isupper() and len(line.split()) <= 3)
        if section_headers < 2:
            issues.append("Use clear section headers")
            score -= 10
        
        if not issues:
            issues.append("Good formatting")
        
        return {
            'formatting_score': max(score, 0),
            'bullet_points_used': bullet_count,
            'issues': issues,
            'recommendation': 'Good formatting' if score >= 80 else 'Improve formatting'
        }
    
    def analyze_content_quality(self, text):
        """Analyze resume content quality"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        # Check for quantifiable achievements
        numbers = re.findall(r'\d+%|\$\d+|\d+\+', text)
        has_metrics = len(numbers) > 0
        
        # Check for specific achievements vs. responsibilities
        achievement_indicators = ['achieved', 'improved', 'increased', 'reduced', 'generated', 'saved']
        achievement_count = sum(1 for word in achievement_indicators if word in text.lower())
        
        # Calculate content score
        content_score = 70
        if has_metrics:
            content_score += 15
        if achievement_count > 3:
            content_score += 15
        
        return {
            'content_score': min(content_score, 100),
            'has_metrics': has_metrics,
            'quantifiable_achievements': len(numbers),
            'achievement_count': achievement_count,
            'recommendation': 'Strong content' if content_score >= 85 else 'Add more quantifiable achievements'
        }
    
    def check_contact_information(self, text):
        """Check for contact information"""
        has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))
        has_phone = bool(re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text))
        has_linkedin = 'linkedin' in text.lower()
        
        found_info = []
        if has_email:
            found_info.append('email')
        if has_phone:
            found_info.append('phone')
        if has_linkedin:
            found_info.append('linkedin')
        
        completeness = (len(found_info) / 3) * 100
        
        return {
            'has_email': has_email,
            'has_phone': has_phone,
            'has_linkedin': has_linkedin,
            'completeness': round(completeness, 2),
            'found_info': found_info,
            'recommendation': 'Complete contact info' if completeness >= 66 else 'Add missing contact information'
        }
    
    def analyze_action_verbs(self, text_lower):
        """Analyze use of strong action verbs"""
        found_verbs = []
        for verb in self.skill_keywords['action_verbs']:
            if verb in text_lower:
                count = len(re.findall(r'\b' + verb + r'\b', text_lower))
                found_verbs.append({'verb': verb, 'count': count})
        
        total_action_verbs = sum(v['count'] for v in found_verbs)
        
        return {
            'total_action_verbs': total_action_verbs,
            'unique_action_verbs': len(found_verbs),
            'found_verbs': found_verbs[:5],  # Top 5
            'recommendation': 'Good use of action verbs' if total_action_verbs > 5 else 'Use more strong action verbs'
        }
    
    def calculate_overall_score(self, sections, keywords, ats, formatting, content, contact, action_verbs):
        """Calculate overall resume score"""
        weights = {
            'sections': 0.20,
            'keywords': 0.15,
            'ats': 0.25,
            'formatting': 0.15,
            'content': 0.15,
            'contact': 0.05,
            'action_verbs': 0.05
        }
        
        score = (
            sections['section_score'] * weights['sections'] +
            min(keywords['total_keywords'] * 5, 100) * weights['keywords'] +
            ats['ats_score'] * weights['ats'] +
            formatting['formatting_score'] * weights['formatting'] +
            content['content_score'] * weights['content'] +
            contact['completeness'] * weights['contact'] +
            min(action_verbs['total_action_verbs'] * 10, 100) * weights['action_verbs']
        )
        
        return round(score, 2)
    
    def generate_suggestions(self, sections, keywords, ats, formatting, content, contact, action_verbs):
        """Generate improvement suggestions"""
        suggestions = []
        
        # Section suggestions
        if sections['missing_required']:
            suggestions.append({
                'category': 'Sections',
                'priority': 'High',
                'suggestion': f"Add missing sections: {', '.join(sections['missing_required'])}"
            })
        
        # Keyword suggestions
        if keywords['total_keywords'] < 10:
            suggestions.append({
                'category': 'Keywords',
                'priority': 'High',
                'suggestion': 'Add more relevant industry keywords for better ATS performance'
            })
        
        # ATS suggestions
        if not ats['is_compatible']:
            for issue in ats['issues'][:2]:
                suggestions.append({
                    'category': 'ATS Compatibility',
                    'priority': 'High',
                    'suggestion': issue
                })
        
        # Content suggestions
        if content['content_score'] < 85:
            suggestions.append({
                'category': 'Content',
                'priority': 'Medium',
                'suggestion': 'Add more quantifiable achievements (numbers, percentages, dollar amounts)'
            })
        
        # Action verb suggestions
        if action_verbs['total_action_verbs'] < 5:
            suggestions.append({
                'category': 'Action Verbs',
                'priority': 'Medium',
                'suggestion': 'Start bullet points with strong action verbs (e.g., achieved, developed, led)'
            })
        
        # Contact info suggestions
        if contact['completeness'] < 66:
            suggestions.append({
                'category': 'Contact Information',
                'priority': 'High',
                'suggestion': 'Ensure email, phone, and LinkedIn profile are included'
            })
        
        # Formatting suggestions
        if formatting['formatting_score'] < 80:
            suggestions.append({
                'category': 'Formatting',
                'priority': 'Medium',
                'suggestion': 'Improve formatting with clear sections and bullet points'
            })
        
        if not suggestions:
            suggestions.append({
                'category': 'Overall',
                'priority': 'Info',
                'suggestion': 'Resume is well-structured. Consider minor refinements.'
            })
        
        return suggestions[:8]  # Return top 8 suggestions
    
    def get_status(self, score):
        """Get overall status"""
        if score >= 90:
            return "Excellent - Resume is highly optimized"
        elif score >= 75:
            return "Good - Resume is well-structured"
        elif score >= 60:
            return "Fair - Resume needs improvements"
        else:
            return "Needs Work - Significant improvements required"
