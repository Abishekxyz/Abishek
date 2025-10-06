# 📥 Installation Guide
## AI-Powered Academic Integrity Checker

---

## 🖥️ System Requirements

### Minimum Requirements
- **Processor**: Intel Core i3 or equivalent
- **RAM**: 4GB (8GB recommended)
- **Storage**: 20GB free space
- **Operating System**: Windows 10/11, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **Internet**: Required for initial setup and some features

### Software Requirements
- Python 3.8+
- pip (Python package installer)
- Web browser (Chrome, Firefox, Safari, or Edge)

---

## 🚀 Quick Start (3 Steps)

### Option 1: Automated Setup (Recommended)

#### Windows Users:
1. Double-click `run.bat`
2. Wait for installation to complete
3. Access the application at http://localhost:5000

#### Linux/Mac Users:
```bash
chmod +x run.sh
./run.sh
```

### Option 2: Manual Setup

#### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Step 2: Initialize Database
```bash
python database.py
```

#### Step 3: Run Application
```bash
python app.py
```

#### Step 4: Access Application
Open your browser and navigate to:
```
http://localhost:5000
```

---

## 📋 Detailed Installation Instructions

### Windows Installation

1. **Install Python**
   - Download Python from https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify installation:
     ```cmd
     python --version
     ```

2. **Download Project**
   - Extract the project ZIP file
   - Open Command Prompt in the project folder

3. **Install Dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Initialize Database**
   ```cmd
   python database.py
   ```

5. **Run Application**
   ```cmd
   python app.py
   ```

6. **Access Application**
   - Open browser: http://localhost:5000

### Linux/macOS Installation

1. **Install Python (if not already installed)**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```
   
   **macOS (using Homebrew):**
   ```bash
   brew install python3
   ```

2. **Download and Extract Project**
   ```bash
   unzip academic-integrity-checker.zip
   cd academic-integrity-checker
   ```

3. **Create Virtual Environment (Recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

5. **Initialize Database**
   ```bash
   python3 database.py
   ```

6. **Run Application**
   ```bash
   python3 app.py
   ```

7. **Access Application**
   Open browser: http://localhost:5000

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
**Error**: `Address already in use`

**Solution**: Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

#### 2. Module Not Found Error
**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

#### 3. Database Error
**Error**: `no such table: users`

**Solution**: Initialize database:
```bash
python database.py
```

#### 4. Permission Denied (Linux/Mac)
**Error**: `Permission denied: './run.sh'`

**Solution**: Make script executable:
```bash
chmod +x run.sh
```

#### 5. PDF Extraction Not Working
**Error**: Issues reading PDF files

**Solution**: Ensure PyPDF2 is installed:
```bash
pip install PyPDF2==3.0.1
```

#### 6. DOCX Files Not Reading
**Error**: Issues reading DOCX files

**Solution**: Install python-docx:
```bash
pip install python-docx
```

---

## 🎯 First Time Usage

### 1. Create Account
- Navigate to http://localhost:5000
- Click "Register" tab
- Enter username, email, and password
- Click "Create Account"

### 2. Access Dashboard
- After registration, you'll be redirected to dashboard
- View statistics and available features

### 3. Analyze Your First Document
- Click "Analyze Document"
- Paste text or upload a file
- Click "Analyze Document"
- View comprehensive results
- Download report (optional)

### 4. Try Resume Analyzer
- Click "Analyze Resume"
- Upload your resume
- Get professional feedback
- Download analysis report

---

## 🌐 Network Configuration

### Running on Local Network

To access from other devices on your network:

1. Find your IP address:
   
   **Windows:**
   ```cmd
   ipconfig
   ```
   
   **Linux/Mac:**
   ```bash
   ifconfig
   ```

2. Modify `app.py`:
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

3. Access from other devices:
   ```
   http://YOUR_IP_ADDRESS:5000
   ```

### Firewall Configuration

If you can't access from other devices:

**Windows:**
- Windows Firewall → Allow an app → Add Python

**Linux:**
```bash
sudo ufw allow 5000
```

---

## 💾 Database Management

### Backup Database
```bash
cp academic_integrity.db academic_integrity_backup.db
```

### Reset Database
```bash
rm academic_integrity.db
python database.py
```

---

## 🔄 Updating the Application

1. Backup your database
2. Extract new version files
3. Copy your database to new folder
4. Run installation again:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

---

## 🎨 Customization

### Change Port
Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=YOUR_PORT)
```

### Change Upload Size Limit
Edit `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

---

## 📊 Performance Optimization

### For Large Documents

1. Increase upload limit (see Customization)
2. Use SSD for better database performance
3. Close other applications to free RAM

### For Multiple Users

1. Consider using production server (Gunicorn/uWSGI)
2. Use PostgreSQL instead of SQLite
3. Implement caching

---

## 🔐 Security Recommendations

1. **Change Secret Key** in `app.py`:
   ```python
   app.secret_key = 'your-secure-random-key-here'
   ```

2. **Use HTTPS** in production

3. **Enable CORS** if needed for API access

4. **Regular Backups** of database

---

## 📞 Getting Help

If you encounter issues:

1. Check this guide
2. Review error messages
3. Check Python and pip versions
4. Ensure all dependencies are installed
5. Try running with verbose output:
   ```bash
   python app.py --verbose
   ```

---

## ✅ Verification Checklist

After installation, verify:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed
- [ ] Database initialized
- [ ] Application starts without errors
- [ ] Can access http://localhost:5000
- [ ] Can register new account
- [ ] Can login successfully
- [ ] Can analyze document
- [ ] Can analyze resume
- [ ] Can view history
- [ ] Can download reports

---

## 🎉 Installation Complete!

You're all set! Start using the AI-Powered Academic Integrity Checker.

**Default Access:**
- URL: http://localhost:5000
- Create your account on first visit

**Need Help?**
- Check README.md for usage guide
- Review troubleshooting section above

---

**Happy Analyzing! 🚀**
