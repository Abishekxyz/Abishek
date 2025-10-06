# AI-Powered Academic Integrity Checker

A comprehensive AI-based system for detecting plagiarism, AI-generated content, and ensuring academic integrity with real-time feedback and writing enhancement suggestions.

## Features

### Core Features
- **Plagiarism Detection**: Compare text against online & offline sources
- **Paraphrase Detection**: Identify copied meaning with rewritten text
- **AI-Generated Text Detection**: Detect ChatGPT/AI-written content
- **Citation Verification**: Validate references and formatting

### Advanced Features
- **Citation Generator & Corrector**: Auto-suggest proper citations (APA/MLA/IEEE)
- **Readability Score**: Analyze text complexity (Flesch index)
- **Writing Style Feedback**: Highlight passive voice, grammar issues
- **Fact-Check Mode**: Verify claims against reliable sources
- **AI Paraphrase Detector**: Identify AI-rewritten content
- **Similarity Heatmap**: Visual representation of copied content
- **Document History Checker**: Track edits and detect style changes
- **Chrome Extension**: Real-time checking in Google Docs/Word online
- **Report Generator**: Comprehensive integrity reports with scores

### Modules
1. User Login & Dashboard
2. Text Input / File Upload (docx, pdf, txt)
3. Plagiarism & Paraphrase Analysis
4. AI-Generated Content Detection
5. Citation Validator & Generator
6. Writing Feedback & Readability Scoring
7. Report Generation
8. Resume Analyzer (Additional Module)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd academic-integrity-checker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download required NLTK data:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
```

4. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

5. Set up the database:
```python
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
```

6. Run the application:
```bash
python app.py
```

## Usage

1. Open your browser and go to `http://localhost:5000`
2. Register/Login to access the dashboard
3. Upload documents or paste text for analysis
4. View comprehensive reports with similarity scores and suggestions

## Project Structure

```
academic-integrity-checker/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── static/                # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── upload.html
│   └── report.html
├── ai_modules/            # AI detection modules
│   ├── plagiarism_detector.py
│   ├── paraphrase_detector.py
│   ├── ai_content_detector.py
│   ├── citation_validator.py
│   └── writing_analyzer.py
├── utils/                 # Utility functions
│   ├── text_processor.py
│   ├── file_handler.py
│   └── report_generator.py
├── chrome_extension/      # Chrome extension files
└── tests/                 # Test files
```

## API Endpoints

- `POST /api/analyze` - Analyze text/file for integrity
- `GET /api/report/<id>` - Get analysis report
- `POST /api/citations` - Generate citations
- `GET /api/dashboard` - User dashboard data

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For support and questions, please open an issue on GitHub.