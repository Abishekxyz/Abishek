"""
Report Generator Module
Generates downloadable PDF reports with analysis results
"""

import os
from datetime import datetime
from io import BytesIO


class ReportGenerator:
    def __init__(self):
        self.reports_dir = 'reports'
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate(self, title, content, submission_type, originality_score, created_at, analysis_results, username):
        """
        Generate PDF report
        Returns: path to generated PDF
        """
        # For now, generate HTML report (can be converted to PDF with pdfkit/weasyprint)
        report_html = self.generate_html_report(
            title, content, submission_type, originality_score, 
            created_at, analysis_results, username
        )
        
        # Save HTML report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'report_{timestamp}.html'
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_html)
        
        return filepath
    
    def generate_html_report(self, title, content, submission_type, originality_score, created_at, analysis_results, username):
        """Generate HTML report"""
        
        if submission_type == 'resume':
            return self.generate_resume_report(title, analysis_results, username, created_at)
        else:
            return self.generate_document_report(title, content, originality_score, analysis_results, username, created_at)
    
    def generate_document_report(self, title, content, originality_score, analysis_results, username, created_at):
        """Generate document analysis report"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Academic Integrity Report - {title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 40px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ border-bottom: 3px solid #2196F3; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ color: #2196F3; font-size: 28px; margin-bottom: 10px; }}
        .header .meta {{ color: #666; font-size: 14px; }}
        .score-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0; }}
        .score-box .score {{ font-size: 48px; font-weight: bold; }}
        .score-box .label {{ font-size: 16px; margin-top: 10px; opacity: 0.9; }}
        .section {{ margin: 30px 0; padding: 20px; background: #f9f9f9; border-left: 4px solid #2196F3; border-radius: 5px; }}
        .section h2 {{ color: #333; font-size: 20px; margin-bottom: 15px; }}
        .section-content {{ color: #555; line-height: 1.6; }}
        .metric {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e0e0e0; }}
        .metric:last-child {{ border-bottom: none; }}
        .metric-label {{ font-weight: 600; color: #555; }}
        .metric-value {{ color: #2196F3; font-weight: bold; }}
        .status-badge {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 14px; font-weight: 600; }}
        .status-success {{ background: #4caf50; color: white; }}
        .status-warning {{ background: #ff9800; color: white; }}
        .status-danger {{ background: #f44336; color: white; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid #e0e0e0; text-align: center; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Academic Integrity Report</h1>
            <div class="meta">
                <strong>Document:</strong> {title}<br>
                <strong>Analyzed by:</strong> {username}<br>
                <strong>Date:</strong> {created_at}<br>
                <strong>Report Type:</strong> Comprehensive Analysis
            </div>
        </div>
        
        <div class="score-box">
            <div class="score">{originality_score}%</div>
            <div class="label">Overall Originality Score</div>
        </div>
        
        <div class="section">
            <h2>🔍 Plagiarism Detection</h2>
            <div class="section-content">
                <div class="metric">
                    <span class="metric-label">Similarity Percentage:</span>
                    <span class="metric-value">{analysis_results.get('plagiarism', {}).get('similarity_percentage', 0)}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Matches Found:</span>
                    <span class="metric-value">{analysis_results.get('plagiarism', {}).get('matches_found', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="metric-value">{analysis_results.get('plagiarism', {}).get('status', 'N/A')}</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🤖 AI-Generated Content Detection</h2>
            <div class="section-content">
                <div class="metric">
                    <span class="metric-label">AI Probability:</span>
                    <span class="metric-value">{analysis_results.get('ai_detection', {}).get('ai_percentage', 0)}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Confidence Level:</span>
                    <span class="metric-value">{analysis_results.get('ai_detection', {}).get('confidence_level', 'N/A')}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="metric-value">{analysis_results.get('ai_detection', {}).get('status', 'N/A')}</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📝 Paraphrase Detection</h2>
            <div class="section-content">
                <div class="metric">
                    <span class="metric-label">Paraphrase Percentage:</span>
                    <span class="metric-value">{analysis_results.get('paraphrase', {}).get('paraphrase_percentage', 0)}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="metric-value">{analysis_results.get('paraphrase', {}).get('status', 'N/A')}</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📚 Citation Analysis</h2>
            <div class="section-content">
                <div class="metric">
                    <span class="metric-label">Citations Found:</span>
                    <span class="metric-value">{analysis_results.get('citations', {}).get('citations_found', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Citation Style:</span>
                    <span class="metric-value">{analysis_results.get('citations', {}).get('detected_style', 'N/A')}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Errors Found:</span>
                    <span class="metric-value">{len(analysis_results.get('citations', {}).get('errors', []))}</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📖 Readability Analysis</h2>
            <div class="section-content">
                <div class="metric">
                    <span class="metric-label">Flesch Reading Ease:</span>
                    <span class="metric-value">{analysis_results.get('readability', {}).get('scores', {}).get('flesch_reading_ease', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Reading Level:</span>
                    <span class="metric-value">{analysis_results.get('readability', {}).get('reading_level', 'N/A')}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="metric-value">{analysis_results.get('readability', {}).get('status', 'N/A')}</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>✍️ Writing Quality</h2>
            <div class="section-content">
                <div class="metric">
                    <span class="metric-label">Writing Score:</span>
                    <span class="metric-value">{analysis_results.get('writing', {}).get('writing_score', 0)}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Passive Voice:</span>
                    <span class="metric-value">{analysis_results.get('writing', {}).get('passive_voice', {}).get('percentage', 0)}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="metric-value">{analysis_results.get('writing', {}).get('status', 'N/A')}</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by AI-Powered Academic Integrity Checker</p>
            <p>© 2024 Academic Integrity System | Confidential Report</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def generate_resume_report(self, title, analysis_results, username, created_at):
        """Generate resume analysis report"""
        
        result = analysis_results
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Resume Analysis Report - {title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 40px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ border-bottom: 3px solid #4caf50; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ color: #4caf50; font-size: 28px; margin-bottom: 10px; }}
        .header .meta {{ color: #666; font-size: 14px; }}
        .score-box {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0; }}
        .score-box .score {{ font-size: 48px; font-weight: bold; }}
        .score-box .label {{ font-size: 16px; margin-top: 10px; opacity: 0.9; }}
        .section {{ margin: 30px 0; padding: 20px; background: #f9f9f9; border-left: 4px solid #4caf50; border-radius: 5px; }}
        .section h2 {{ color: #333; font-size: 20px; margin-bottom: 15px; }}
        .section-content {{ color: #555; line-height: 1.6; }}
        .metric {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e0e0e0; }}
        .metric:last-child {{ border-bottom: none; }}
        .metric-label {{ font-weight: 600; color: #555; }}
        .metric-value {{ color: #4caf50; font-weight: bold; }}
        .suggestion {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .suggestion-title {{ font-weight: 600; color: #856404; margin-bottom: 5px; }}
        .suggestion-text {{ color: #856404; font-size: 14px; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid #e0e0e0; text-align: center; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 Resume Analysis Report</h1>
            <div class="meta">
                <strong>Resume:</strong> {title}<br>
                <strong>Analyzed by:</strong> {username}<br>
                <strong>Date:</strong> {created_at}<br>
                <strong>Report Type:</strong> Professional Resume Analysis
            </div>
        </div>
        
        <div class="score-box">
            <div class="score">{result.get('overall_score', 0)}%</div>
            <div class="label">Overall Resume Score</div>
        </div>
        
        <div class="section">
            <h2>📋 Section Analysis</h2>
            <div class="section-content">
                <div class="metric">
                    <span class="metric-label">Required Sections Found:</span>
                    <span class="metric-value">{', '.join(result.get('sections', {}).get('found_required', []))}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Optional Sections:</span>
                    <span class="metric-value">{', '.join(result.get('sections', {}).get('found_optional', [])) or 'None'}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Section Score:</span>
                    <span class="metric-value">{result.get('sections', {}).get('section_score', 0)}%</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔑 Keyword Analysis</h2>
            <div class="section-content">
                <div class="metric">
                    <span class="metric-label">Total Keywords Found:</span>
                    <span class="metric-value">{result.get('keywords', {}).get('total_keywords', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Technical Skills:</span>
                    <span class="metric-value">{result.get('keywords', {}).get('keyword_counts', {}).get('technical', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Soft Skills:</span>
                    <span class="metric-value">{result.get('keywords', {}).get('keyword_counts', {}).get('soft_skills', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Action Verbs:</span>
                    <span class="metric-value">{result.get('keywords', {}).get('keyword_counts', {}).get('action_verbs', 0)}</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🤖 ATS Compatibility</h2>
            <div class="section-content">
                <div class="metric">
                    <span class="metric-label">ATS Score:</span>
                    <span class="metric-value">{result.get('ats_compatibility', {}).get('ats_score', 0)}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Is ATS Compatible:</span>
                    <span class="metric-value">{'Yes' if result.get('ats_compatibility', {}).get('is_compatible') else 'No'}</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>💼 Content Quality</h2>
            <div class="section-content">
                <div class="metric">
                    <span class="metric-label">Content Score:</span>
                    <span class="metric-value">{result.get('content_quality', {}).get('content_score', 0)}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Quantifiable Achievements:</span>
                    <span class="metric-value">{result.get('content_quality', {}).get('quantifiable_achievements', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Has Metrics:</span>
                    <span class="metric-value">{'Yes' if result.get('content_quality', {}).get('has_metrics') else 'No'}</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>💡 Improvement Suggestions</h2>
            <div class="section-content">
"""
        
        for suggestion in result.get('suggestions', [])[:5]:
            html += f"""
                <div class="suggestion">
                    <div class="suggestion-title">{suggestion.get('category', 'General')} - Priority: {suggestion.get('priority', 'Medium')}</div>
                    <div class="suggestion-text">{suggestion.get('suggestion', '')}</div>
                </div>
"""
        
        html += """
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by AI-Powered Resume Analyzer</p>
            <p>© 2024 Academic Integrity System | Confidential Report</p>
        </div>
    </div>
</body>
</html>
"""
        return html
