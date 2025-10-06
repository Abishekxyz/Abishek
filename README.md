# 🎓 AI-Powered Academic Integrity Checker

## 📌 Project Overview

A comprehensive, professional AI-powered system that ensures the originality and authenticity of academic content. This system detects plagiarism, paraphrasing, AI-generated text, and citation manipulation while providing real-time feedback, readability checks, and writing enhancement suggestions.

### ✨ Key Features

1. **Plagiarism Detection** - Compare text against online & offline sources
2. **Paraphrase Detection** - Check if text meaning is copied but rewritten
3. **AI-Generated Text Detection** - Identify ChatGPT/AI-written content
4. **Citation Verification** - Validate if references exist and are correctly formatted
5. **Citation Generator & Corrector** - Auto-suggest proper citations in APA/MLA/IEEE format
6. **Readability Score** - Analyze text complexity using Flesch index
7. **Writing Style Feedback** - Highlight passive voice, repeated words, grammar issues
8. **Resume Analyzer (Module 8)** - Professional resume analysis with ATS compatibility check
9. **Fact-Check Mode** - Detect if claims are backed by reliable sources
10. **Similarity Heatmap** - Visual representation of copied text
11. **Report Generator** - Downloadable PDF reports with detailed analysis
12. **User Dashboard** - Track submission history and statistics

---

## 🏗️ Project Structure

```
academic-integrity-checker/
│
├── app.py                      # Main Flask application
├── database.py                 # Database configuration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── modules/                    # AI Detection Modules
│   ├── __init__.py
│   ├── plagiarism_detector.py
│   ├── ai_detector.py
│   ├── paraphrase_detector.py
│   ├── citation_validator.py
│   ├── readability_checker.py
│   ├── writing_feedback.py
│   ├── resume_analyzer.py     # Module 8: Resume Analysis
│   └── report_generator.py
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   └── file_handler.py
│
├── templates/                  # Frontend HTML templates
│   ├── index.html             # Login/Register page
│   ├── dashboard.html         # User dashboard
│   ├── analyze.html           # Document analysis page
│   ├── resume_analyzer.html   # Resume analysis page
│   └── history.html           # Submission history
│
├── uploads/                    # Temporary file uploads
├── reports/                    # Generated reports
└── academic_integrity.db       # SQLite database
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Initialize Database

```bash
python database.py
```

### Step 3: Run the Application

```bash
python app.py
```

The application will start on **http://localhost:5000**

---

## 💻 Usage Guide

### 1. User Registration/Login
- Navigate to http://localhost:5000
- Register a new account or login with existing credentials
- Access the dashboard after successful authentication

### 2. Document Analysis
- Click "Analyze Document" from dashboard
- Choose to paste text or upload a file (TXT, PDF, DOCX)
- Click "Analyze Document" button
- View comprehensive analysis results including:
  - Originality score
  - Plagiarism detection
  - AI content detection
  - Paraphrase detection
  - Citation analysis
  - Readability metrics
  - Writing quality feedback
- Download detailed PDF report

### 3. Resume Analysis (Module 8)
- Click "Analyze Resume" from dashboard
- Upload your resume or paste text
- Get professional analysis including:
  - Overall resume score
  - Section completeness
  - Keyword optimization
  - ATS compatibility
  - Formatting assessment
  - Content quality
  - Contact information check
  - Actionable improvement suggestions
- Download resume analysis report

### 4. View History
- Access all previous submissions
- View scores and analysis dates
- Download reports for any submission

---

## 🔧 Technical Details

### Backend (Flask)
- **Framework**: Flask 3.0.0
- **Database**: SQLite3
- **Authentication**: Session-based with password hashing
- **File Processing**: Supports TXT, PDF, DOCX formats
- **API Endpoints**: RESTful design

### Frontend
- **Design**: Modern, responsive UI
- **Technology**: HTML5, CSS3, Vanilla JavaScript
- **Icons**: Font Awesome 6.4.0
- **Features**: Real-time updates, smooth animations

### AI Detection Modules
- **Plagiarism Detection**: Text similarity algorithms, sequence matching
- **AI Detection**: Pattern recognition, writing style analysis
- **Paraphrase Detection**: Semantic similarity, synonym usage patterns
- **Citation Validation**: Format detection (APA/MLA/IEEE), citation checking
- **Readability Analysis**: Flesch Reading Ease, Flesch-Kincaid Grade Level
- **Writing Feedback**: Passive voice detection, word repetition analysis
- **Resume Analyzer**: ATS compatibility, keyword extraction, content quality

---

## 📊 Features in Detail

### Module 1: User Authentication
- Secure registration and login
- Password hashing with Werkzeug
- Session management
- User dashboard with statistics

### Module 2: Text Input & File Upload
- Multiple input methods (text paste, file upload)
- Support for TXT, PDF, DOCX formats
- File size limit: 16MB
- Text extraction and preprocessing

### Module 3: Plagiarism & Paraphrase Analysis
- Similarity detection against known sources
- Online and offline source checking
- Paraphrase pattern recognition
- Heatmap visualization of copied content

### Module 4: AI-Generated Content Detection
- ChatGPT/GPT detection
- AI writing pattern analysis
- Confidence scoring
- Detailed breakdown of AI indicators

### Module 5: Citation Validator & Generator
- Multiple citation format support (APA, MLA, IEEE)
- Citation error detection
- Missing citation identification
- Auto-generation of proper citations

### Module 6: Writing Feedback & Readability
- Flesch Reading Ease score
- Grade level assessment
- Passive voice detection
- Word repetition analysis
- Sentence variety scoring

### Module 7: Report Generation
- Comprehensive PDF/HTML reports
- Visual score representations
- Detailed analysis breakdown
- Downloadable format

### Module 8: Resume Analyzer (Professional)
- **Section Analysis**: Check for required/optional sections
- **Keyword Optimization**: Technical skills, soft skills, action verbs
- **ATS Compatibility**: Check for ATS-friendly formatting
- **Formatting Assessment**: Bullet points, structure, layout
- **Content Quality**: Quantifiable achievements, metrics
- **Contact Information**: Email, phone, LinkedIn verification
- **Improvement Suggestions**: Prioritized recommendations
- **Overall Score**: Comprehensive resume rating

---

## 🎯 Use Cases

1. **Academic Institutions**
   - Verify student submissions
   - Detect plagiarism in essays and research papers
   - Ensure academic integrity

2. **Students & Researchers**
   - Self-check before submission
   - Improve writing quality
   - Verify citations and references
   - Optimize resumes for job applications

3. **Content Creators**
   - Ensure content originality
   - Check for AI-generated text
   - Improve readability

4. **HR Departments**
   - Analyze candidate resumes
   - Check ATS compatibility
   - Evaluate resume quality

---

## 🔐 Security Features

- Password hashing using Werkzeug
- Session-based authentication
- SQL injection prevention
- File upload validation
- Secure file handling

---

## 📈 Performance

- Fast analysis (typically under 10 seconds)
- Handles documents up to 16MB
- Efficient database queries
- Responsive frontend
- Scalable architecture

---

## 🛠️ Customization

### Adding New Detection Algorithms
1. Create a new module in `modules/`
2. Implement the detection logic
3. Import and integrate in `app.py`
4. Update frontend to display results

### Modifying Citation Formats
Edit `modules/citation_validator.py` to add new citation styles

### Changing UI Theme
Modify CSS in template files (`templates/*.html`)

---

## 🐛 Troubleshooting

### Database Error
```bash
python database.py
```

### Module Import Error
```bash
pip install -r requirements.txt
```

### Port Already in Use
Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

---

## 📝 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `POST /logout` - User logout
- `GET /check-auth` - Check authentication status

### Analysis
- `POST /api/analyze` - Analyze document
- `POST /api/analyze-resume` - Analyze resume
- `GET /api/stats` - Get user statistics
- `GET /api/submissions` - Get submission history
- `GET /api/submission/<id>` - Get submission details
- `GET /api/generate-report/<id>` - Generate PDF report

---

## 🔄 Future Enhancements

1. Chrome Extension for real-time checking
2. Integration with Google Docs
3. Advanced ML models for detection
4. Multi-language support
5. Fact-checking with external APIs
6. Collaborative features
7. Advanced analytics dashboard

---

## 👥 Credits

Developed as a comprehensive Academic Integrity System with AI-powered detection capabilities.

---

## 📄 License

This project is provided as-is for educational and professional use.

---

## 📞 Support

For issues or questions, please check the documentation or contact support.

---

## 🎉 Thank You!

Thank you for using the AI-Powered Academic Integrity Checker. We hope this tool helps maintain academic integrity and improves writing quality!
