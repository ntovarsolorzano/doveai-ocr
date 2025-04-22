document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const selectedFileName = document.getElementById('selected-file-name');
    const selectedFileSize = document.getElementById('selected-file-size');
    const removeFileBtn = document.getElementById('remove-file');
    const processFileBtn = document.getElementById('process-file-btn');
    const processTextBtn = document.getElementById('process-text-btn');
    const textInput = document.getElementById('text-input');
    const outputSection = document.getElementById('output-section');
    const markdownOutput = document.getElementById('markdown-output');
    const previewView = document.getElementById('preview-view');
    const viewBtns = document.querySelectorAll('.view-btn');
    const outputViews = document.querySelectorAll('.output-view');
    const copyBtn = document.getElementById('copy-btn');
    const downloadBtn = document.getElementById('download-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    // Ensure loading overlay is hidden on page load
    loadingOverlay.hidden = true;

    // API Endpoints
    const API_URL = 'http://localhost:7000/api';
    const UPLOAD_ENDPOINT = `${API_URL}/upload`;
    const EXTRACT_ENDPOINT = `${API_URL}/extract`;
    const CONVERT_ENDPOINT = `${API_URL}/convert`;

    // State
    let currentFile = null;
    let currentMarkdown = '';

    // Initialize
    initTheme();
    initEventListeners();

    // Theme Toggle
    function initTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.setAttribute('data-theme', 'dark');
            darkModeToggle.checked = true;
        }
    }

    function toggleTheme() {
        if (darkModeToggle.checked) {
            document.body.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
        }
    }

    // Tab Switching
    function switchTab(tabId) {
        tabBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabId);
        });

        tabContents.forEach(content => {
            content.classList.toggle('active', content.id === `${tabId}-tab`);
        });
    }

    // File Handling
    function handleFileSelect(file) {
        if (!file) return;

        // Check file type
        const fileType = file.type;
        if (!['application/pdf', 'image/png', 'image/jpeg'].includes(fileType)) {
            showError('Unsupported file type. Please upload a PDF or image file.');
            return;
        }

        // Check file size (10MB max)
        if (file.size > 10 * 1024 * 1024) {
            showError('File too large. Maximum size is 10MB.');
            return;
        }

        currentFile = file;
        
        // Display file info
        selectedFileName.textContent = file.name;
        selectedFileSize.textContent = formatFileSize(file.size);
        fileInfo.hidden = false;
        processFileBtn.disabled = false;
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' bytes';
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        else return (bytes / 1048576).toFixed(1) + ' MB';
    }

    function removeFile() {
        currentFile = null;
        fileInput.value = '';
        fileInfo.hidden = true;
        processFileBtn.disabled = true;
    }

    // API Calls
    async function processFile() {
        if (!currentFile) return;

        showLoading(true);
        
        try {
            const formData = new FormData();
            formData.append('file', currentFile);
            
            const response = await fetch(EXTRACT_ENDPOINT, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || 'Failed to process file');
            }
            
            if (result.success) {
                displayResult(result.markdown);
            } else {
                throw new Error(result.error || 'Processing failed');
            }
        } catch (error) {
            showError(error.message);
        } finally {
            showLoading(false);
        }
    }

    async function processText() {
        const text = textInput.value.trim();
        if (!text) {
            showError('Please enter some text to convert.');
            return;
        }

        showLoading(true);
        
        try {
            const formData = new FormData();
            formData.append('text', text);
            
            const response = await fetch(CONVERT_ENDPOINT, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || 'Failed to convert text');
            }
            
            if (result.success) {
                displayResult(result.markdown);
            } else {
                throw new Error(result.error || 'Conversion failed');
            }
        } catch (error) {
            showError(error.message);
        } finally {
            showLoading(false);
        }
    }

    // Display Results
    function displayResult(markdown) {
        currentMarkdown = markdown;
        
        // Display markdown
        markdownOutput.textContent = markdown;
        if (window.hljs) {
            hljs.highlightElement(markdownOutput);
        }
        
        // Render preview
        if (window.marked) {
            previewView.innerHTML = marked.parse(markdown);
        } else {
            previewView.innerHTML = '<p>Preview not available. Marked.js library not loaded.</p>';
        }
        
        // Show output section
        outputSection.hidden = false;
        
        // Scroll to output
        outputSection.scrollIntoView({ behavior: 'smooth' });
    }

    function switchView(viewType) {
        viewBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === viewType);
        });

        outputViews.forEach(view => {
            view.classList.toggle('active', view.id === `${viewType}-view`);
        });
    }

    // Utility Functions
    function copyToClipboard() {
        navigator.clipboard.writeText(currentMarkdown)
            .then(() => {
                showNotification('Copied to clipboard!');
            })
            .catch(err => {
                showError('Failed to copy: ' + err);
            });
    }

    function downloadMarkdown() {
        const blob = new Blob([currentMarkdown], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'extracted_text.md';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function showLoading(show) {
        loadingOverlay.hidden = !show;
        loadingOverlay.style.display = show ? 'flex' : 'none';
    }

    function showError(message) {
        alert(message);
    }

    function showNotification(message) {
        // Simple notification
        alert(message);
    }

    // Drag and Drop
    function handleDragOver(e) {
        e.preventDefault();
        dropArea.classList.add('highlight');
    }

    function handleDragLeave() {
        dropArea.classList.remove('highlight');
    }

    function handleDrop(e) {
        e.preventDefault();
        dropArea.classList.remove('highlight');
        
        if (e.dataTransfer.files.length) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    }

    // Event Listeners
    function initEventListeners() {
        // Theme toggle
        darkModeToggle.addEventListener('change', toggleTheme);
        
        // Tab switching
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => switchTab(btn.dataset.tab));
        });
        
        // File input
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) {
                handleFileSelect(e.target.files[0]);
            }
        });
        
        // Remove file
        removeFileBtn.addEventListener('click', removeFile);
        
        // Process buttons
        processFileBtn.addEventListener('click', processFile);
        processTextBtn.addEventListener('click', processText);
        
        // View switching
        viewBtns.forEach(btn => {
            btn.addEventListener('click', () => switchView(btn.dataset.view));
        });
        
        // Copy and download
        copyBtn.addEventListener('click', copyToClipboard);
        downloadBtn.addEventListener('click', downloadMarkdown);
        
        // Drag and drop
        dropArea.addEventListener('dragover', handleDragOver);
        dropArea.addEventListener('dragleave', handleDragLeave);
        dropArea.addEventListener('drop', handleDrop);
    }
});
