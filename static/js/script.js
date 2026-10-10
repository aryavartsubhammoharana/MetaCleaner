document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    
    // Status Indicator
    const statusIndicator = document.getElementById('status-indicator-dot');
    const statusText = document.getElementById('status-display-text');
    
    // Steps
    const stepUpload = document.getElementById('step-upload');
    const stepPreview = document.getElementById('step-preview');
    const stepLoading = document.getElementById('step-loading');
    const stepDownloadReady = document.getElementById('step-download-ready');
    
    // Step 2 Preview Elements
    const previewFilename = document.getElementById('preview-filename');
    const previewFilesize = document.getElementById('preview-filesize');
    const previewFiletype = document.getElementById('preview-filetype');
    const previewFileIcon = document.getElementById('preview-file-icon');
    const metadataTable = document.getElementById('metadata-table');
    const metadataTableBody = document.getElementById('metadata-table-body');
    const noMetadataMsg = document.getElementById('no-metadata-msg');
    
    // Step 3 Loading Elements
    const loadingTitleStatus = document.getElementById('loading-title-status');
    const loadingSubStatus = document.getElementById('loading-sub-status');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const progressPercentageText = document.getElementById('progress-percentage-text');
    
    // Step 4 Stats Elements
    const statOriginalSize = document.getElementById('stat-original-size');
    const statCleanedSize = document.getElementById('stat-cleaned-size');
    const statTime = document.getElementById('stat-time');
    
    // Action Buttons
    const btnCancelPreview = document.getElementById('btn-cancel-preview');
    const btnDiscardPreview = document.getElementById('btn-discard-preview');
    const btnProcessClean = document.getElementById('btn-process-clean');
    const btnResetCleaner = document.getElementById('btn-reset-cleaner');
    const btnDownloadFile = document.getElementById('btn-download-file');
    
    // State
    let currentFileData = null;
    let rawSelectedFile = null;
    
    // ----------------------------------------------------
    // Status & Step Helpers
    // ----------------------------------------------------
    const setStatus = (state, text) => {
        if (!statusIndicator || !statusText) return;
        statusIndicator.className = `status-indicator-dot ${state}`;
        statusText.textContent = text;
    };
    
    const showStep = (stepElement) => {
        [stepUpload, stepPreview, stepLoading, stepDownloadReady].forEach(step => {
            if (step) step.classList.remove('active');
        });
        if (stepElement) stepElement.classList.add('active');
    };
    
    const getFileIconSVG = (category) => {
        const icons = {
            image: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>`,
            document: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`,
            text: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>`,
            audio: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>`,
            video: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>`,
            unknown: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/></svg>`
        };
        return icons[category] || icons.unknown;
    };
    
    // ----------------------------------------------------
    // Drag & Drop File Handling
    // ----------------------------------------------------
    if (dropZone) {
        dropZone.addEventListener('click', () => {
            if (fileInput) fileInput.click();
        });
        
        ['dragenter', 'dragover'].forEach(name => {
            dropZone.addEventListener(name, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add('dragover');
            });
        });
        
        ['dragleave', 'drop'].forEach(name => {
            dropZone.addEventListener(name, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove('dragover');
            });
        });
        
        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files && files.length > 0) {
                handleFileSelection(files[0]);
            }
        });
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files.length > 0) {
                handleFileSelection(e.target.files[0]);
            }
        });
    }
    
    // ----------------------------------------------------
    // File Upload & Scan
    // ----------------------------------------------------
    const handleFileSelection = (file) => {
        const MAX_SIZE = 25 * 1024 * 1024;
        if (file.size > MAX_SIZE) {
            alert('File size exceeds the 25MB limit.');
            if (fileInput) fileInput.value = '';
            return;
        }

        rawSelectedFile = file;
        showStep(stepLoading);
        setStatus('processing', 'Analyzing file...');
        
        if (loadingTitleStatus) loadingTitleStatus.textContent = 'Scanning File...';
        if (loadingSubStatus) loadingSubStatus.textContent = 'Parsing metadata structures and checking integrity.';
        if (progressBarFill) progressBarFill.style.width = '25%';
        if (progressPercentageText) progressPercentageText.textContent = '25%';
        
        const formData = new FormData();
        formData.append('file', file);
        
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);
        
        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable && progressBarFill) {
                const pct = Math.min(85, Math.round((e.loaded / e.total) * 60) + 25);
                progressBarFill.style.width = `${pct}%`;
                if (progressPercentageText) progressPercentageText.textContent = `${pct}%`;
            }
        };
        
        xhr.onload = () => {
            if (xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.success) {
                        currentFileData = response.data;
                        displayMetadataPreview(response.data);
                    } else {
                        handleUploadError(response.message || 'File upload failed.');
                    }
                } catch (e) {
                    handleUploadError('Unexpected server response format.');
                }
            } else {
                let errMsg = 'Failed to analyze file.';
                try {
                    const res = JSON.parse(xhr.responseText);
                    errMsg = res.message || errMsg;
                } catch (e) {}
                handleUploadError(errMsg);
            }
        };
        
        xhr.onerror = () => {
            handleUploadError('Network connection interrupted during scan.');
        };
        
        xhr.send(formData);
    };
    
    const handleUploadError = (message) => {
        alert(`Error: ${message}`);
        resetCleanerUI();
    };
    
    const displayMetadataPreview = (data) => {
        if (previewFilename) previewFilename.textContent = data.original_name;
        if (previewFilesize) previewFilesize.textContent = data.formatted_size;
        if (previewFiletype) previewFiletype.textContent = (data.category || 'FILE').toUpperCase();
        if (previewFileIcon) previewFileIcon.innerHTML = getFileIconSVG(data.category);
        
        if (metadataTableBody) metadataTableBody.innerHTML = '';
        const metadata = data.metadata || {};
        const keys = Object.keys(metadata);
        
        if (keys.length === 0) {
            if (metadataTable) metadataTable.classList.add('hidden');
            if (noMetadataMsg) noMetadataMsg.classList.remove('hidden');
        } else {
            if (metadataTable) metadataTable.classList.remove('hidden');
            if (noMetadataMsg) noMetadataMsg.classList.add('hidden');
            
            keys.forEach(key => {
                const row = document.createElement('tr');
                const keyCell = document.createElement('td');
                keyCell.textContent = key;
                const valCell = document.createElement('td');
                valCell.textContent = metadata[key];
                row.appendChild(keyCell);
                row.appendChild(valCell);
                metadataTableBody.appendChild(row);
            });
        }
        
        setStatus('active', 'Previewing metadata');
        showStep(stepPreview);
    };
    
    // ----------------------------------------------------
    // Metadata Cleaning Action
    // ----------------------------------------------------
    if (btnProcessClean) {
        btnProcessClean.addEventListener('click', () => {
            if (!currentFileData && !rawSelectedFile) return;
            
            showStep(stepLoading);
            setStatus('processing', 'Purging metadata...');
            
            if (loadingTitleStatus) loadingTitleStatus.textContent = 'Cleaning File...';
            if (loadingSubStatus) loadingSubStatus.textContent = 'Stripping geolocation, author info, and EXIF headers.';
            
            let progress = 20;
            const progressInterval = setInterval(() => {
                progress += 10;
                if (progress > 85) {
                    clearInterval(progressInterval);
                } else if (progressBarFill && progressPercentageText) {
                    progressBarFill.style.width = `${progress}%`;
                    progressPercentageText.textContent = `${progress}%`;
                }
            }, 80);
            
            // Clean request with serverless fallback
            const executeClean = () => {
                fetch('/clean', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ file_id: currentFileData.file_id })
                })
                .then(async (res) => {
                    clearInterval(progressInterval);
                    if (res.status === 404 && rawSelectedFile) {
                        // Serverless container switched! Fallback to direct multipart upload to /clean
                        return executeCleanMultipart();
                    }
                    return res.json();
                })
                .then(data => {
                    if (!data) return;
                    if (data.success) {
                        if (progressBarFill) progressBarFill.style.width = '100%';
                        if (progressPercentageText) progressPercentageText.textContent = '100%';
                        setTimeout(() => displaySuccessPage(data.data), 200);
                    } else {
                        alert(`Cleaning failed: ${data.message}`);
                        resetCleanerUI();
                    }
                })
                .catch(() => {
                    clearInterval(progressInterval);
                    alert('Network communication interrupted during cleaning.');
                    resetCleanerUI();
                });
            };
            
            // Multipart fallback for serverless lambda instances
            const executeCleanMultipart = () => {
                const fd = new FormData();
                fd.append('file', rawSelectedFile);
                return fetch('/clean', {
                    method: 'POST',
                    body: fd
                }).then(r => r.json());
            };
            
            executeClean();
        });
    }
    
    const displaySuccessPage = (cleanData) => {
        if (statOriginalSize) statOriginalSize.textContent = currentFileData ? currentFileData.formatted_size : cleanData.original_size;
        if (statCleanedSize) statCleanedSize.textContent = cleanData.cleaned_size;
        if (statTime) statTime.textContent = `${cleanData.time_taken_ms} ms`;
        
        if (btnDownloadFile) {
            const originalName = currentFileData ? currentFileData.original_name : 'cleaned_file';
            btnDownloadFile.href = `/download/${cleanData.cleaned_file_id}?name=${encodeURIComponent(originalName)}`;
        }
        
        setStatus('success', 'File cleaned');
        showStep(stepDownloadReady);
    };
    
    // ----------------------------------------------------
    // UI Reset Triggers
    // ----------------------------------------------------
    const resetCleanerUI = () => {
        currentFileData = null;
        rawSelectedFile = null;
        if (fileInput) fileInput.value = '';
        setStatus('active', 'Ready to scan');
        showStep(stepUpload);
    };
    
    if (btnCancelPreview) btnCancelPreview.addEventListener('click', resetCleanerUI);
    if (btnDiscardPreview) btnDiscardPreview.addEventListener('click', resetCleanerUI);
    if (btnResetCleaner) btnResetCleaner.addEventListener('click', resetCleanerUI);
    
    if (btnDownloadFile) {
        btnDownloadFile.addEventListener('click', () => {
            setTimeout(resetCleanerUI, 1200);
        });
    }
});
