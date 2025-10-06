// Academic Integrity Checker - Google Docs Content Script

class AcademicIntegrityChecker {
  constructor() {
    this.settings = {};
    this.sidebarOpen = false;
    this.analysisResults = null;

    this.init();
  }

  async init() {
    // Get settings from background script
    this.settings = await this.getSettings();

    // Create floating action button
    this.createFloatingButton();

    // Listen for text selection changes
    this.setupTextSelectionListener();

    // Listen for keyboard shortcuts
    this.setupKeyboardShortcuts();

    // Inject CSS for highlights
    this.injectHighlightCSS();
  }

  async getSettings() {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ action: 'getSettings' }, (settings) => {
        resolve(settings || {});
      });
    });
  }

  createFloatingButton() {
    // Create floating action button
    const fab = document.createElement('div');
    fab.id = 'aic-floating-button';
    fab.innerHTML = `
      <button class="aic-fab-btn" title="Academic Integrity Checker">
        <i class="fas fa-shield-alt"></i>
      </button>
    `;

    // Add to page
    document.body.appendChild(fab);

    // Add event listener
    fab.querySelector('.aic-fab-btn').addEventListener('click', () => {
      this.toggleSidebar();
    });

    // Add context menu
    document.addEventListener('contextmenu', (e) => {
      if (window.getSelection().toString().length > 50) {
        // Could add custom context menu here
      }
    });
  }

  toggleSidebar() {
    if (this.sidebarOpen) {
      this.closeSidebar();
    } else {
      this.openSidebar();
    }
  }

  openSidebar() {
    // Create sidebar iframe
    const sidebar = document.createElement('div');
    sidebar.id = 'aic-sidebar';
    sidebar.innerHTML = `
      <div class="aic-sidebar-header">
        <h3><i class="fas fa-shield-alt"></i> Integrity Check</h3>
        <button class="aic-close-btn" onclick="window.academicIntegrityChecker.closeSidebar()">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="aic-sidebar-content">
        <div class="aic-loading">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading checker...</p>
        </div>
      </div>
    `;

    document.body.appendChild(sidebar);
    this.sidebarOpen = true;

    // Load sidebar content
    this.loadSidebarContent();
  }

  closeSidebar() {
    const sidebar = document.getElementById('aic-sidebar');
    if (sidebar) {
      sidebar.remove();
    }
    this.sidebarOpen = false;
  }

  async loadSidebarContent() {
    const sidebarContent = document.querySelector('.aic-sidebar-content');
    if (!sidebarContent) return;

    try {
      // Get current document content
      const content = this.getDocumentContent();

      if (content.length < this.settings.minTextLength) {
        sidebarContent.innerHTML = `
          <div class="aic-error">
            <i class="fas fa-exclamation-triangle"></i>
            <p>Document too short for analysis (${content.length} characters). Minimum ${this.settings.minTextLength} characters required.</p>
          </div>
        `;
        return;
      }

      // Show analysis interface
      sidebarContent.innerHTML = `
        <div class="aic-analysis-section">
          <h4>Quick Analysis</h4>
          <div class="aic-score-display">
            <div class="aic-score-item">
              <span class="aic-score-label">Overall Score:</span>
              <span class="aic-score-value" id="overall-score">-</span>
            </div>
          </div>
          <button class="aic-analyze-btn" onclick="window.academicIntegrityChecker.analyzeDocument()">
            <i class="fas fa-search"></i> Analyze Document
          </button>
        </div>

        <div class="aic-real-time-section">
          <h4>Real-time Checking</h4>
          <label class="aic-toggle">
            <input type="checkbox" id="realtime-toggle" ${this.settings.enableRealTime ? 'checked' : ''}>
            <span class="aic-toggle-slider"></span>
            Enable real-time analysis
          </label>
        </div>

        <div class="aic-settings-section">
          <h4>Settings</h4>
          <div class="aic-setting-item">
            <label>Check Interval:</label>
            <select id="check-interval">
              <option value="15000" ${this.settings.checkInterval === 15000 ? 'selected' : ''}>15 seconds</option>
              <option value="30000" ${this.settings.checkInterval === 30000 ? 'selected' : ''}>30 seconds</option>
              <option value="60000" ${this.settings.checkInterval === 60000 ? 'selected' : ''}>1 minute</option>
            </select>
          </div>
        </div>

        <div class="aic-results-section" id="results-section" style="display: none;">
          <h4>Latest Results</h4>
          <div id="analysis-results">
            <!-- Results will be displayed here -->
          </div>
        </div>
      `;

      // Add event listeners
      document.getElementById('realtime-toggle').addEventListener('change', (e) => {
        this.updateSetting('enableRealTime', e.target.checked);
      });

      document.getElementById('check-interval').addEventListener('change', (e) => {
        this.updateSetting('checkInterval', parseInt(e.target.value));
      });

    } catch (error) {
      sidebarContent.innerHTML = `
        <div class="aic-error">
          <i class="fas fa-exclamation-circle"></i>
          <p>Error loading checker: ${error.message}</p>
        </div>
      `;
    }
  }

  getDocumentContent() {
    try {
      // Try to get content from Google Docs editor
      const docContent = document.querySelector('.kix-page-content');
      if (docContent) {
        return docContent.textContent.trim();
      }

      // Fallback to body content
      return document.body ? document.body.textContent.trim() : '';
    } catch (error) {
      console.error('Error getting document content:', error);
      return '';
    }
  }

  async analyzeDocument() {
    const content = this.getDocumentContent();
    if (!content) return;

    const analyzeBtn = document.querySelector('.aic-analyze-btn');
    const originalText = analyzeBtn.innerHTML;

    // Show loading state
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    analyzeBtn.disabled = true;

    try {
      const response = await fetch(`${this.settings.apiEndpoint}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: content,
          analysis_type: 'document'
        })
      });

      if (response.ok) {
        const result = await response.json();

        // Display results
        this.displayAnalysisResults(result);

        // Update overall score display
        const scoreElement = document.getElementById('overall-score');
        if (scoreElement) {
          scoreElement.textContent = `${result.overall_score}%`;
        }

        // Show results section
        document.getElementById('results-section').style.display = 'block';

      } else {
        throw new Error('Analysis failed');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      this.showNotification('Analysis failed. Please try again.', 'error');
    } finally {
      // Restore button
      analyzeBtn.innerHTML = originalText;
      analyzeBtn.disabled = false;
    }
  }

  displayAnalysisResults(results) {
    const resultsContainer = document.getElementById('analysis-results');
    if (!resultsContainer) return;

    resultsContainer.innerHTML = `
      <div class="aic-result-item">
        <div class="aic-result-header">
          <span class="aic-result-label">Plagiarism Score:</span>
          <span class="aic-result-value ${this.getScoreClass(results.scores?.plagiarism)}">
            ${results.scores?.plagiarism || 0}%
          </span>
        </div>
      </div>

      <div class="aic-result-item">
        <div class="aic-result-header">
          <span class="aic-result-label">AI Content Score:</span>
          <span class="aic-result-value ${this.getScoreClass(results.scores?.ai_content)}">
            ${results.scores?.ai_content || 0}%
          </span>
        </div>
      </div>

      <div class="aic-result-item">
        <div class="aic-result-header">
          <span class="aic-result-label">Citation Score:</span>
          <span class="aic-result-value ${this.getScoreClass(results.scores?.citation)}">
            ${results.scores?.citation || 0}%
          </span>
        </div>
      </div>

      <div class="aic-result-item">
        <div class="aic-result-header">
          <span class="aic-result-label">Writing Score:</span>
          <span class="aic-result-value ${this.getScoreClass(results.scores?.readability)}">
            ${results.scores?.readability || 0}%
          </span>
        </div>
      </div>

      <div class="aic-actions">
        <button class="aic-btn-primary" onclick="window.academicIntegrityChecker.openFullReport()">
          <i class="fas fa-external-link-alt"></i> View Full Report
        </button>
      </div>
    `;
  }

  getScoreClass(score) {
    if (score >= 80) return 'aic-score-excellent';
    if (score >= 60) return 'aic-score-good';
    if (score >= 40) return 'aic-score-fair';
    return 'aic-score-poor';
  }

  openFullReport() {
    // Open full report in new tab
    chrome.runtime.sendMessage({
      action: 'showNotification',
      message: 'Full report feature coming soon!',
      type: 'info'
    });
  }

  setupTextSelectionListener() {
    let selectionTimeout;

    document.addEventListener('selectionchange', () => {
      clearTimeout(selectionTimeout);
      selectionTimeout = setTimeout(() => {
        const selection = window.getSelection();
        const selectedText = selection.toString().trim();

        if (selectedText.length >= 50) {
          // Could highlight selection or show tooltip
          this.highlightSelection(selection);
        }
      }, 500);
    });
  }

  highlightSelection(selection) {
    // Remove existing highlights
    this.removeHighlights();

    if (selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);

      // Create highlight span
      const highlight = document.createElement('span');
      highlight.className = 'aic-text-highlight';
      highlight.style.backgroundColor = 'rgba(255, 235, 59, 0.3)';
      highlight.style.borderRadius = '2px';

      try {
        range.surroundContents(highlight);
      } catch (error) {
        // Range might contain complex elements, skip highlighting
      }
    }
  }

  removeHighlights() {
    const highlights = document.querySelectorAll('.aic-text-highlight');
    highlights.forEach(highlight => {
      const parent = highlight.parentNode;
      parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
      parent.normalize();
    });
  }

  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl+Shift+A to analyze current selection
      if (e.ctrlKey && e.shiftKey && e.key === 'A') {
        e.preventDefault();
        const selectedText = window.getSelection().toString();
        if (selectedText) {
          chrome.runtime.sendMessage({
            action: 'analyzeText',
            text: selectedText
          });
        }
      }

      // Ctrl+Shift+S to toggle sidebar
      if (e.ctrlKey && e.shiftKey && e.key === 'S') {
        e.preventDefault();
        this.toggleSidebar();
      }
    });
  }

  async updateSetting(key, value) {
    this.settings[key] = value;

    // Save to Chrome storage
    await chrome.storage.sync.set({ [key]: value });

    // Notify background script
    chrome.runtime.sendMessage({
      action: 'updateSettings',
      settings: this.settings
    });
  }

  showNotification(message, type = 'info') {
    chrome.runtime.sendMessage({
      action: 'showNotification',
      message: message,
      type: type
    });
  }

  injectHighlightCSS() {
    const css = `
      .aic-text-highlight {
        position: relative;
        cursor: pointer;
      }

      .aic-text-highlight:hover::after {
        content: "Check integrity";
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        white-space: nowrap;
        z-index: 1000;
      }

      #aic-floating-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 10000;
      }

      .aic-fab-btn {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: linear-gradient(135deg, #007bff, #0056b3);
        border: none;
        color: white;
        font-size: 20px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
      }

      .aic-fab-btn:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
      }

      #aic-sidebar {
        position: fixed;
        right: 0;
        top: 0;
        width: 350px;
        height: 100vh;
        background: white;
        box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
        z-index: 10001;
        transform: translateX(100%);
        transition: transform 0.3s ease;
      }

      #aic-sidebar.open {
        transform: translateX(0);
      }

      .aic-sidebar-header {
        padding: 1rem;
        border-bottom: 1px solid #eee;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #f8f9fa;
      }

      .aic-sidebar-header h3 {
        margin: 0;
        font-size: 1.1rem;
        color: #007bff;
      }

      .aic-close-btn {
        background: none;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        color: #666;
      }

      .aic-sidebar-content {
        padding: 1rem;
        height: calc(100vh - 70px);
        overflow-y: auto;
      }

      .aic-loading {
        text-align: center;
        padding: 2rem;
        color: #666;
      }

      .aic-error {
        text-align: center;
        padding: 2rem;
        color: #dc3545;
      }

      .aic-analysis-section,
      .aic-real-time-section,
      .aic-settings-section {
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #eee;
      }

      .aic-score-display {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
      }

      .aic-score-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .aic-score-value {
        font-weight: bold;
        font-size: 1.2rem;
      }

      .aic-score-excellent { color: #28a745; }
      .aic-score-good { color: #20c997; }
      .aic-score-fair { color: #ffc107; }
      .aic-score-poor { color: #dc3545; }

      .aic-analyze-btn {
        width: 100%;
        background: linear-gradient(135deg, #007bff, #0056b3);
        border: none;
        color: white;
        padding: 0.75rem;
        border-radius: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
      }

      .aic-analyze-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
      }

      .aic-toggle {
        display: flex;
        align-items: center;
        cursor: pointer;
        margin-bottom: 1rem;
      }

      .aic-toggle input {
        display: none;
      }

      .aic-toggle-slider {
        width: 44px;
        height: 24px;
        background-color: #ccc;
        border-radius: 24px;
        margin-right: 12px;
        position: relative;
        transition: 0.3s;
      }

      .aic-toggle-slider:before {
        content: "";
        position: absolute;
        height: 18px;
        width: 18px;
        left: 3px;
        top: 3px;
        background-color: white;
        border-radius: 50%;
        transition: 0.3s;
      }

      .aic-toggle input:checked + .aic-toggle-slider {
        background-color: #007bff;
      }

      .aic-toggle input:checked + .aic-toggle-slider:before {
        transform: translateX(20px);
      }

      .aic-setting-item {
        margin-bottom: 1rem;
      }

      .aic-setting-item label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
      }

      .aic-setting-item select {
        width: 100%;
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 0.25rem;
      }

      .aic-results-section {
        margin-top: 2rem;
      }

      .aic-result-item {
        background: #f8f9fa;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
      }

      .aic-result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .aic-result-label {
        font-weight: 500;
      }

      .aic-result-value {
        font-weight: bold;
      }

      .aic-actions {
        margin-top: 1rem;
        text-align: center;
      }

      .aic-btn-primary {
        background: linear-gradient(135deg, #007bff, #0056b3);
        border: none;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
        transition: all 0.3s ease;
      }

      .aic-btn-primary:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
      }

      @media (max-width: 768px) {
        #aic-sidebar {
          width: 100vw;
        }
      }
    `;

    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
  }
}

// Initialize the checker
window.academicIntegrityChecker = new AcademicIntegrityChecker();