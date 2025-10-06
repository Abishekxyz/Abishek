// Academic Integrity Checker - Chrome Extension Background Script

// Default settings
const DEFAULT_SETTINGS = {
  apiEndpoint: 'http://localhost:5000',
  checkInterval: 30000, // 30 seconds
  minTextLength: 100,
  enableRealTime: true,
  selectedChecks: {
    plagiarism: true,
    aiContent: true,
    grammar: true,
    style: false
  }
};

// Initialize extension
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    // Set default settings on first install
    chrome.storage.sync.set(DEFAULT_SETTINGS);

    // Create context menu
    createContextMenu();
  }
});

// Create context menu for manual checking
function createContextMenu() {
  chrome.contextMenus.create({
    id: 'check-selection',
    title: 'Check Academic Integrity',
    contexts: ['selection']
  });

  chrome.contextMenus.create({
    id: 'check-page',
    title: 'Check Entire Page',
    contexts: ['page']
  });
}

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'check-selection' && info.selectionText) {
    checkSelectedText(info.selectionText, tab);
  } else if (info.menuItemId === 'check-page') {
    checkEntirePage(tab);
  }
});

// Check selected text
async function checkSelectedText(selectedText, tab) {
  try {
    const settings = await getSettings();

    if (selectedText.length < settings.minTextLength) {
      showNotification('Selection too short for analysis', 'warning');
      return;
    }

    // Show loading notification
    showNotification('Analyzing text...', 'info');

    // Send to API
    const response = await fetch(`${settings.apiEndpoint}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: selectedText,
        analysis_type: 'document'
      })
    });

    if (response.ok) {
      const result = await response.json();

      // Store result for popup display
      await chrome.storage.local.set({
        lastAnalysis: {
          text: selectedText.substring(0, 200) + '...',
          result: result,
          timestamp: Date.now()
        }
      });

      // Show results in popup
      chrome.action.openPopup();

      showNotification('Analysis complete!', 'success');
    } else {
      throw new Error('API request failed');
    }
  } catch (error) {
    console.error('Error checking text:', error);
    showNotification('Error analyzing text. Please try again.', 'error');
  }
}

// Check entire page content
async function checkEntirePage(tab) {
  try {
    // Inject content script to extract page text
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: extractPageText
    });

    const pageText = results[0].result;

    if (!pageText || pageText.length < 100) {
      showNotification('Insufficient text content on page', 'warning');
      return;
    }

    await checkSelectedText(pageText, tab);
  } catch (error) {
    console.error('Error checking page:', error);
    showNotification('Error extracting page content', 'error');
  }
}

// Extract text content from page
function extractPageText() {
  // Remove script and style elements
  const scripts = document.querySelectorAll('script, style');
  scripts.forEach(el => el.remove());

  // Get main content (try to avoid headers, footers, etc.)
  const body = document.body;
  const content = body ? body.innerText || body.textContent : '';

  return content.trim();
}

// Get user settings
async function getSettings() {
  return new Promise((resolve) => {
    chrome.storage.sync.get(DEFAULT_SETTINGS, (settings) => {
      resolve(settings);
    });
  });
}

// Show notification
function showNotification(message, type = 'info') {
  const icons = {
    success: 'icons/success.png',
    error: 'icons/error.png',
    warning: 'icons/warning.png',
    info: 'icons/info.png'
  };

  chrome.notifications.create({
    type: 'basic',
    iconUrl: icons[type] || icons.info,
    title: 'Academic Integrity Checker',
    message: message
  });
}

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzeText') {
    checkSelectedText(request.text, sender.tab);
  } else if (request.action === 'getSettings') {
    getSettings().then(sendResponse);
    return true; // Keep message channel open for async response
  } else if (request.action === 'showNotification') {
    showNotification(request.message, request.type);
  }
});

// Periodic real-time checking
chrome.alarms.create('realtime-check', { delayInMinutes: 0.5, periodInMinutes: 0.5 });

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === 'realtime-check') {
    const settings = await getSettings();

    if (settings.enableRealTime) {
      // Get all Google Docs tabs
      const tabs = await chrome.tabs.query({
        url: 'https://docs.google.com/document/*'
      });

      for (const tab of tabs) {
        try {
          const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            function: getDocumentContent
          });

          const content = results[0].result;

          if (content && content.length >= settings.minTextLength) {
            // Check if content has changed significantly
            const lastCheck = await getLastCheck(tab.id);

            if (hasContentChanged(content, lastCheck)) {
              await checkSelectedText(content, tab);

              // Update last check
              await chrome.storage.local.set({
                [`lastCheck_${tab.id}`]: {
                  content: content,
                  timestamp: Date.now()
                }
              });
            }
          }
        } catch (error) {
          console.error(`Error checking tab ${tab.id}:`, error);
        }
      }
    }
  }
});

// Get document content from Google Docs
function getDocumentContent() {
  try {
    // Try to get the main document content
    const docContent = document.querySelector('.kix-page-content');
    if (docContent) {
      return docContent.textContent.trim();
    }

    // Fallback: get body content
    return document.body ? document.body.textContent.trim() : '';
  } catch (error) {
    console.error('Error getting document content:', error);
    return '';
  }
}

// Check if content has changed significantly
function hasContentChanged(newContent, lastCheck) {
  if (!lastCheck) return true;

  // Simple change detection - compare length and hash
  const newLength = newContent.length;
  const oldLength = lastCheck.content.length;

  // If length changed by more than 10%, consider it changed
  const lengthDiff = Math.abs(newLength - oldLength) / oldLength;
  if (lengthDiff > 0.1) return true;

  // Could implement more sophisticated change detection here
  return false;
}

// Get last check for a tab
async function getLastCheck(tabId) {
  return new Promise((resolve) => {
    chrome.storage.local.get([`lastCheck_${tabId}`], (result) => {
      resolve(result[`lastCheck_${tabId}`]);
    });
  });
}

// Handle tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url.includes('docs.google.com')) {
    // Inject content script if needed
    chrome.scripting.executeScript({
      target: { tabId: tabId },
      files: ['content-google-docs.js']
    }).catch(error => {
      // Script might already be injected
      console.log('Content script injection:', error.message);
    });
  }
});