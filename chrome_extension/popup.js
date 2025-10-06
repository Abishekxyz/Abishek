// Academic Integrity Checker - Popup Script

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const analyzeSelectionBtn = document.getElementById('analyze-selection');
    const openSidebarBtn = document.getElementById('open-sidebar');
    const openSettingsBtn = document.getElementById('open-settings');
    const analysisContent = document.getElementById('analysis-content');

    // Load last analysis results
    loadLastAnalysis();

    // Event listeners
    analyzeSelectionBtn.addEventListener('click', analyzeCurrentSelection);
    openSidebarBtn.addEventListener('click', openSidebar);
    openSettingsBtn.addEventListener('click', openSettings);

    // Load last analysis from storage
    async function loadLastAnalysis() {
        try {
            const result = await chrome.storage.local.get(['lastAnalysis']);

            if (result.lastAnalysis) {
                const analysis = result.lastAnalysis;
                displayAnalysisResults(analysis);
            }
        } catch (error) {
            console.error('Error loading last analysis:', error);
        }
    }

    // Display analysis results in popup
    function displayAnalysisResults(analysis) {
        const { result, timestamp } = analysis;
        const date = new Date(timestamp).toLocaleString();

        analysisContent.innerHTML = `
            <div class="score-display">
                <div class="overall-score ${getScoreClass(result.overall_score)}">
                    ${result.overall_score}%
                </div>
                <small class="text-muted">Analyzed ${date}</small>
            </div>

            <div class="score-item">
                <span class="score-label">Plagiarism:</span>
                <span class="score-value ${getScoreClass(result.scores?.plagiarism)}">
                    ${result.scores?.plagiarism || 0}%
                </span>
            </div>

            <div class="score-item">
                <span class="score-label">AI Content:</span>
                <span class="score-value ${getScoreClass(result.scores?.ai_content)}">
                    ${result.scores?.ai_content || 0}%
                </span>
            </div>

            <div class="score-item">
                <span class="score-label">Citations:</span>
                <span class="score-value ${getScoreClass(result.scores?.citation)}">
                    ${result.scores?.citation || 0}%
                </span>
            </div>

            <div class="score-item">
                <span class="score-label">Writing:</span>
                <span class="score-value ${getScoreClass(result.scores?.readability)}">
                    ${result.scores?.readability || 0}%
                </span>
            </div>
        `;
    }

    // Get CSS class for score
    function getScoreClass(score) {
        if (score >= 80) return 'score-excellent';
        if (score >= 60) return 'score-good';
        if (score >= 40) return 'score-fair';
        return 'score-poor';
    }

    // Analyze current selection
    async function analyzeCurrentSelection() {
        try {
            // Get current tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

            if (!tab) {
                showMessage('No active tab found', 'error');
                return;
            }

            // Execute script to get selected text
            const results = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: getSelectedText
            });

            const selectedText = results[0].result;

            if (!selectedText || selectedText.length < 50) {
                showMessage('Please select at least 50 characters of text', 'warning');
                return;
            }

            // Show loading state
            analyzeSelectionBtn.innerHTML = '<span class="spinner"></span> Analyzing...';
            analyzeSelectionBtn.disabled = true;

            // Send to background script for analysis
            chrome.runtime.sendMessage({
                action: 'analyzeText',
                text: selectedText
            }, (response) => {
                // Restore button
                analyzeSelectionBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Selection';
                analyzeSelectionBtn.disabled = false;

                if (response && response.success) {
                    // Reload analysis results
                    loadLastAnalysis();
                }
            });

        } catch (error) {
            console.error('Error analyzing selection:', error);
            showMessage('Error analyzing text', 'error');

            // Restore button
            analyzeSelectionBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Selection';
            analyzeSelectionBtn.disabled = false;
        }
    }

    // Get selected text from current tab
    function getSelectedText() {
        return window.getSelection().toString().trim();
    }

    // Open sidebar in current tab
    async function openSidebar() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

            if (tab && tab.url.includes('docs.google.com')) {
                await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    function: () => {
                        if (window.academicIntegrityChecker) {
                            window.academicIntegrityChecker.openSidebar();
                        }
                    }
                });
            } else {
                showMessage('Sidebar only available in Google Docs', 'warning');
            }
        } catch (error) {
            console.error('Error opening sidebar:', error);
        }
    }

    // Open settings page
    function openSettings() {
        chrome.runtime.openOptionsPage();
    }

    // Show message in popup
    function showMessage(message, type = 'info') {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };

        analysisContent.innerHTML = `
            <div class="score-display" style="border-left: 4px solid ${colors[type]}">
                <p>${message}</p>
            </div>
        `;

        // Auto-hide after 3 seconds
        setTimeout(() => {
            loadLastAnalysis();
        }, 3000);
    }

    // Listen for analysis updates from background script
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.action === 'analysisComplete') {
            loadLastAnalysis();
        }
    });
});