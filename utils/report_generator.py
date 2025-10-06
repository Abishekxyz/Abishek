#!/usr/bin/env python3
"""
Report Generation Module
Creates comprehensive PDF reports for analysis results
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
import matplotlib.pyplot as plt
import seaborn as sns
import io
from config import Config

class ReportGenerator:
    """Comprehensive report generation system"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom styles for the report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkgreen,
            borderColor=colors.darkgreen,
            borderWidth=1,
            borderPadding=5
        ))

        # Subsection style
        self.styles.add(ParagraphStyle(
            name='Subsection',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.darkred
        ))

        # Metric style for scores and values
        self.styles.add(ParagraphStyle(
            name='Metric',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.darkblue,
            spaceAfter=6
        ))

        # Issue style for highlighting problems
        self.styles.add(ParagraphStyle(
            name='Issue',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.red,
            leftIndent=20,
            spaceAfter=4
        ))

        # Suggestion style
        self.styles.add(ParagraphStyle(
            name='Suggestion',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.darkgreen,
            leftIndent=20,
            spaceAfter=4
        ))

    def generate_pdf_report(self, analysis) -> str:
        """
        Generate comprehensive PDF report for analysis

        Args:
            analysis: Analysis database object

        Returns:
            Path to generated PDF file
        """
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"integrity_report_{analysis.id}_{timestamp}.pdf"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Build content
        story = []

        # Title page
        story.extend(self._create_title_page(analysis))

        # Executive summary
        story.extend(self._create_executive_summary(analysis))

        # Detailed results
        story.extend(self._create_detailed_results(analysis))

        # Recommendations
        story.extend(self._create_recommendations(analysis))

        # Generate PDF
        doc.build(story)

        return filepath

    def _create_title_page(self, analysis) -> List:
        """Create report title page"""
        story = []

        # Main title
        title = Paragraph("Academic Integrity Analysis Report", self.styles['CustomTitle'])
        story.append(title)

        story.append(Spacer(1, 0.5 * inch))

        # Analysis details
        details_data = [
            ['Analysis ID:', str(analysis.id)],
            ['Analysis Type:', analysis.analysis_type.title()],
            ['File Name:', analysis.filename or 'Text Input'],
            ['Analysis Date:', analysis.created_at.strftime('%Y-%m-%d %H:%M')],
            ['Processing Time:', f"{analysis.processing_time or 0".1f"} seconds"],
        ]

        details_table = Table(details_data, colWidths=[2*inch, 3*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(details_table)

        story.append(PageBreak())

        return story

    def _create_executive_summary(self, analysis) -> List:
        """Create executive summary section"""
        story = []

        # Section header
        header = Paragraph("Executive Summary", self.styles['SectionHeader'])
        story.append(header)

        # Overall score with visual indicator
        overall_score = analysis.overall_integrity_score or 0
        score_color = self._get_score_color(overall_score)

        score_text = f"Overall Integrity Score: {overall_score".1f"}%"
        score_paragraph = Paragraph(score_text, self.styles['Metric'])
        story.append(score_paragraph)

        # Score interpretation
        interpretation = self._interpret_overall_score(overall_score)
        interp_paragraph = Paragraph(f"Interpretation: {interpretation}", self.styles['Normal'])
        story.append(interp_paragraph)

        story.append(Spacer(1, 0.3 * inch))

        # Individual scores table
        scores_data = [
            ['Analysis Component', 'Score', 'Risk Level'],
            ['Plagiarism Detection', f"{analysis.plagiarism_score or 0".1f"}%", self._get_risk_level(analysis.plagiarism_score or 100)],
            ['Paraphrase Detection', f"{analysis.paraphrase_score or 0".1f"}%", self._get_risk_level(analysis.paraphrase_score or 100)],
            ['AI Content Detection', f"{analysis.ai_content_score or 0".1f"}%", self._get_risk_level(analysis.ai_content_score or 100)],
            ['Citation Validation', f"{analysis.citation_score or 0".1f"}%", self._get_risk_level(analysis.citation_score or 100)],
            ['Writing Quality', f"{analysis.readability_score or 0".1f"}%", self._get_risk_level(analysis.readability_score or 100)],
        ]

        scores_table = Table(scores_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(scores_table)

        story.append(Spacer(1, 0.5 * inch))

        return story

    def _create_detailed_results(self, analysis) -> List:
        """Create detailed results section"""
        story = []

        # Section header
        header = Paragraph("Detailed Analysis Results", self.styles['SectionHeader'])
        story.append(header)

        # Plagiarism Analysis
        story.extend(self._create_plagiarism_section(analysis))

        # AI Content Analysis
        story.extend(self._create_ai_content_section(analysis))

        # Citation Analysis
        story.extend(self._create_citation_section(analysis))

        # Writing Analysis
        story.extend(self._create_writing_section(analysis))

        # Resume Analysis (if applicable)
        if analysis.analysis_type == 'resume':
            story.extend(self._create_resume_section(analysis))

        return story

    def _create_plagiarism_section(self, analysis) -> List:
        """Create plagiarism analysis section"""
        story = []

        subsection = Paragraph("Plagiarism Detection", self.styles['Subsection'])
        story.append(subsection)

        # Parse plagiarism details
        plagiarism_details = json.loads(analysis.plagiarism_details) if analysis.plagiarism_details else {}

        score = plagiarism_details.get('overall_score', 100)
        risk = self._get_risk_level(score)

        score_text = f"Plagiarism Score: {score".1f"}% (Risk: {risk})"
        story.append(Paragraph(score_text, self.styles['Metric']))

        if plagiarism_details.get('matches'):
            matches = plagiarism_details['matches'][:5]  # Show top 5 matches

            for match in matches:
                match_text = f"• {match.get('type', 'Unknown')}: {match.get('similarity', 0)".1%"} similarity"
                if 'source' in match:
                    match_text += f" - {match['source']}"
                story.append(Paragraph(match_text, self.styles['Normal']))

        story.append(Spacer(1, 0.3 * inch))
        return story

    def _create_ai_content_section(self, analysis) -> List:
        """Create AI content analysis section"""
        story = []

        subsection = Paragraph("AI Content Detection", self.styles['Subsection'])
        story.append(subsection)

        ai_details = json.loads(analysis.ai_content_details) if analysis.ai_content_details else {}

        probability = ai_details.get('ai_probability', 0) * 100
        confidence = ai_details.get('confidence', 0) * 100

        story.append(Paragraph(f"AI Content Probability: {probability".1f"}%", self.styles['Metric']))
        story.append(Paragraph(f"Detection Confidence: {confidence".1f"}%", self.styles['Metric']))

        # AI indicators
        indicators = ai_details.get('ai_indicators', {})
        if indicators:
            story.append(Paragraph("AI Writing Indicators Detected:", self.styles['Normal']))
            for indicator, details in indicators.items():
                if details.get('detected', False):
                    indicator_text = f"• {indicator.replace('_', ' ').title()}"
                    story.append(Paragraph(indicator_text, self.styles['Normal']))

        story.append(Spacer(1, 0.3 * inch))
        return story

    def _create_citation_section(self, analysis) -> List:
        """Create citation analysis section"""
        story = []

        subsection = Paragraph("Citation Validation", self.styles['Subsection'])
        story.append(subsection)

        citation_details = json.loads(analysis.citation_details) if analysis.citation_details else {}

        score = citation_details.get('overall_score', 100)
        total_citations = citation_details.get('total_citations', 0)
        valid_citations = citation_details.get('valid_citations', 0)

        story.append(Paragraph(f"Citation Score: {score".1f"}%", self.styles['Metric']))
        story.append(Paragraph(f"Citations Found: {total_citations}", self.styles['Metric']))
        story.append(Paragraph(f"Valid Citations: {valid_citations}", self.styles['Metric']))

        # Common issues
        issues = citation_details.get('common_issues', [])
        if issues:
            story.append(Paragraph("Common Issues:", self.styles['Normal']))
            for issue in issues[:3]:
                story.append(Paragraph(f"• {issue}", self.styles['Issue']))

        story.append(Spacer(1, 0.3 * inch))
        return story

    def _create_writing_section(self, analysis) -> List:
        """Create writing analysis section"""
        story = []

        subsection = Paragraph("Writing Quality Analysis", self.styles['Subsection'])
        story.append(subsection)

        writing_details = json.loads(analysis.writing_feedback) if analysis.writing_feedback else {}

        readability = writing_details.get('readability_score', 0)
        grammar = writing_details.get('grammar_score', 100)
        style = writing_details.get('style_score', 100)

        story.append(Paragraph(f"Readability Score: {readability".1f"}%", self.styles['Metric']))
        story.append(Paragraph(f"Grammar Score: {grammar".1f"}%", self.styles['Metric']))
        story.append(Paragraph(f"Style Score: {style".1f"}%", self.styles['Metric']))

        # Readability metrics
        if 'readability' in writing_details and 'metrics' in writing_details['readability']:
            metrics = writing_details['readability']['metrics']
            story.append(Paragraph("Readability Metrics:", self.styles['Normal']))
            story.append(Paragraph(f"• Flesch-Kincaid Grade Level: {metrics.get('flesch_kincaid_grade', 0)".1f"}", self.styles['Normal']))
            story.append(Paragraph(f"• Flesch Reading Ease: {metrics.get('flesch_reading_ease', 0)".1f"}", self.styles['Normal']))

        story.append(Spacer(1, 0.3 * inch))
        return story

    def _create_resume_section(self, analysis) -> List:
        """Create resume analysis section"""
        story = []

        subsection = Paragraph("Resume Analysis", self.styles['Subsection'])
        story.append(subsection)

        resume_details = json.loads(analysis.resume_analysis) if analysis.resume_analysis else {}

        overall_score = resume_details.get('overall_score', 0)
        completeness = resume_details.get('completeness_score', 0)

        story.append(Paragraph(f"Resume Score: {overall_score".1f"}%", self.styles['Metric']))
        story.append(Paragraph(f"Completeness Score: {completeness".1f"}%", self.styles['Metric']))

        # Sections found/missing
        sections_found = resume_details.get('sections_found', [])
        missing_sections = resume_details.get('missing_sections', [])

        if sections_found:
            story.append(Paragraph(f"Sections Present: {', '.join(sections_found)}", self.styles['Normal']))

        if missing_sections:
            story.append(Paragraph("Missing Sections:", self.styles['Normal']))
            for section in missing_sections:
                story.append(Paragraph(f"• {section.replace('_', ' ').title()}", self.styles['Issue']))

        story.append(Spacer(1, 0.3 * inch))
        return story

    def _create_recommendations(self, analysis) -> List:
        """Create recommendations section"""
        story = []

        header = Paragraph("Recommendations", self.styles['SectionHeader'])
        story.append(header)

        # Generate recommendations based on scores
        recommendations = self._generate_recommendations(analysis)

        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", self.styles['Suggestion']))

        story.append(Spacer(1, 0.3 * inch))

        # Footer
        footer = Paragraph(
            f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>" +
            "Academic Integrity Checker - AI-Powered Analysis System",
            self.styles['Normal']
        )
        story.append(footer)

        return story

    def _get_score_color(self, score: float) -> colors.Color:
        """Get color based on score"""
        if score >= 80:
            return colors.darkgreen
        elif score >= 60:
            return colors.darkgoldenrod
        else:
            return colors.darkred

    def _get_risk_level(self, score: float) -> str:
        """Get risk level based on score"""
        if score >= 80:
            return "Low"
        elif score >= 60:
            return "Medium"
        else:
            return "High"

    def _interpret_overall_score(self, score: float) -> str:
        """Interpret overall integrity score"""
        if score >= 90:
            return "Excellent - High integrity content"
        elif score >= 80:
            return "Good - Minor issues detected"
        elif score >= 70:
            return "Fair - Some concerns identified"
        elif score >= 60:
            return "Poor - Significant issues found"
        else:
            return "Critical - Major integrity concerns"

    def _generate_recommendations(self, analysis) -> List[str]:
        """Generate specific recommendations based on analysis"""
        recommendations = []

        # General recommendations based on scores
        if analysis.plagiarism_score and analysis.plagiarism_score < 70:
            recommendations.append("Review content for potential plagiarism and ensure proper attribution")

        if analysis.ai_content_score and analysis.ai_content_score < 70:
            recommendations.append("Ensure content is original and not AI-generated")

        if analysis.citation_score and analysis.citation_score < 70:
            recommendations.append("Verify and correct citation formatting")

        if analysis.readability_score and analysis.readability_score < 60:
            recommendations.append("Improve writing clarity and readability")

        if analysis.analysis_type == 'resume':
            resume_details = json.loads(analysis.resume_analysis) if analysis.resume_analysis else {}
            if resume_details.get('missing_sections'):
                recommendations.append("Add missing resume sections to improve completeness")

        # Always include general advice
        recommendations.append("Review all flagged issues and make appropriate revisions")
        recommendations.append("Consider having another person review the content")

        return recommendations