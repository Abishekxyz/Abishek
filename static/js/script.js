// Academic Integrity Checker - JavaScript Functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // File upload drag and drop functionality
    initializeFileUpload();

    // Form validation enhancements
    initializeFormValidation();

    // Chart initialization (if Chart.js is loaded)
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }

    // Real-time text analysis (if on text analysis page)
    initializeTextAnalysis();

    // Auto-refresh for analysis status
    initializeStatusRefresh();

    // Copy to clipboard functionality
    initializeClipboard();

    // Theme toggle (if needed)
    initializeThemeToggle();
});

// File Upload Drag and Drop
function initializeFileUpload() {
    const fileUploadArea = document.querySelector('.file-upload-area');
    if (!fileUploadArea) return;

    const fileInput = document.getElementById('file');

    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileUploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        fileUploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileUploadArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        fileUploadArea.classList.add('dragover');
    }

    function unhighlight(e) {
        fileUploadArea.classList.remove('dragover');
    }

    fileUploadArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            fileInput.files = files;
            // Trigger change event to update form
            fileInput.dispatchEvent(new Event('change'));
        }
    }

    // File input change event
    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            // Show file info
            showFileInfo(file);
        }
    });
}

function showFileInfo(file) {
    const infoDiv = document.getElementById('file-info');
    if (!infoDiv) return;

    const size = (file.size / (1024 * 1024)).toFixed(2);
    const type = file.type || 'Unknown';

    infoDiv.innerHTML = `
        <div class="alert alert-info">
            <strong>Selected:</strong> ${file.name}<br>
            <strong>Size:</strong> ${size} MB<br>
            <strong>Type:</strong> ${type}
        </div>
    `;
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');

    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }

            form.classList.add('was-validated');
        }, false);
    });

    // Real-time validation for text areas
    const textAreas = document.querySelectorAll('textarea');
    textAreas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            validateTextLength(this);
        });
    });
}

function validateTextLength(textarea) {
    const minLength = 100;
    const currentLength = textarea.value.length;
    const feedback = textarea.parentNode.querySelector('.invalid-feedback') ||
                     textarea.parentNode.querySelector('.valid-feedback');

    if (currentLength < minLength) {
        textarea.classList.add('is-invalid');
        textarea.classList.remove('is-valid');

        if (feedback) {
            feedback.textContent = `Text must be at least ${minLength} characters. Current: ${currentLength}`;
        }
    } else {
        textarea.classList.remove('is-invalid');
        textarea.classList.add('is-valid');
    }
}

// Charts Initialization
function initializeCharts() {
    // Dashboard charts
    const analysisTypesCtx = document.getElementById('analysisTypesChart');
    if (analysisTypesCtx) {
        new Chart(analysisTypesCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Document Analysis', 'Resume Analysis', 'Text Analysis'],
                datasets: [{
                    data: [65, 20, 15],
                    backgroundColor: ['#007bff', '#28a745', '#ffc107']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    const scoreDistributionCtx = document.getElementById('scoreDistributionChart');
    if (scoreDistributionCtx) {
        new Chart(scoreDistributionCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Excellent (90-100%)', 'Good (80-89%)', 'Fair (70-79%)', 'Poor (<70%)'],
                datasets: [{
                    label: 'Analyses',
                    data: [3, 5, 2, 1],
                    backgroundColor: ['#28a745', '#20c997', '#ffc107', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } }
            }
        });
    }
}

// Text Analysis Features
function initializeTextAnalysis() {
    const textArea = document.getElementById('text');
    if (!textArea) return;

    // Character count
    const charCount = document.getElementById('char-count');
    const wordCount = document.getElementById('word-count');

    if (charCount) {
        textArea.addEventListener('input', function() {
            charCount.textContent = this.value.length;
        });
    }

    if (wordCount) {
        textArea.addEventListener('input', function() {
            const words = this.value.trim().split(/\s+/).filter(word => word.length > 0);
            wordCount.textContent = words.length;
        });
    }

    // Auto-save draft (if localStorage is available)
    if (typeof Storage !== 'undefined') {
        const savedDraft = localStorage.getItem('text-analysis-draft');
        if (savedDraft) {
            textArea.value = savedDraft;
            if (charCount) charCount.textContent = savedDraft.length;
            if (wordCount) {
                const words = savedDraft.trim().split(/\s+/).filter(word => word.length > 0);
                wordCount.textContent = words.length;
            }
        }

        // Save draft on input
        let saveTimeout;
        textArea.addEventListener('input', function() {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                localStorage.setItem('text-analysis-draft', this.value);
            }, 1000);
        });
    }
}

// Status Auto-refresh
function initializeStatusRefresh() {
    const statusPage = document.querySelector('.analysis-status-card');
    if (!statusPage) return;

    // Refresh every 5 seconds if status is processing
    if (statusPage.querySelector('.status-processing')) {
        setInterval(function() {
            fetch(window.location.href)
                .then(response => response.text())
                .then(html => {
                    if (html.includes('status-completed') || html.includes('Analysis Complete')) {
                        location.reload();
                    }
                })
                .catch(error => console.log('Refresh error:', error));
        }, 5000);
    }
}

// Clipboard functionality
function initializeClipboard() {
    const copyButtons = document.querySelectorAll('[data-clipboard-target]');

    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-clipboard-target');
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                const textToCopy = targetElement.textContent || targetElement.value;

                navigator.clipboard.writeText(textToCopy).then(() => {
                    // Show success feedback
                    const originalText = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    this.classList.add('btn-success');

                    setTimeout(() => {
                        this.innerHTML = originalText;
                        this.classList.remove('btn-success');
                    }, 2000);
                }).catch(() => {
                    // Fallback for older browsers
                    const textArea = document.createElement('textarea');
                    textArea.value = textToCopy;
                    document.body.appendChild(textArea);
                    textArea.select();

                    try {
                        document.execCommand('copy');
                        this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                        this.classList.add('btn-success');

                        setTimeout(() => {
                            this.innerHTML = originalText;
                            this.classList.remove('btn-success');
                        }, 2000);
                    } catch (err) {
                        console.error('Failed to copy text: ', err);
                    }

                    document.body.removeChild(textArea);
                });
            }
        });
    });
}

// Theme Toggle (Optional)
function initializeThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;

    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        // Update button icon
        const icon = this.querySelector('i');
        icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    });
}

// Utility Functions

// Show toast notification
function showToast(message, type = 'info') {
    const toastHtml = `
        <div class="toast toast-${type}" role="alert">
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;

    const container = document.getElementById('toast-container') || createToastContainer();
    container.insertAdjacentHTML('beforeend', toastHtml);

    const toastElement = container.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);

    toast.show();

    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.dispose();
        toastElement.remove();
    }, 5000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Debounce function for performance
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

// Animate elements on scroll
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    document.querySelectorAll('.feature-card, .card').forEach(el => {
        observer.observe(el);
    });
}

// Initialize scroll animations
initializeScrollAnimations();

// Export functions for use in templates
window.AcademicIntegrityChecker = {
    showToast,
    formatFileSize,
    debounce
};