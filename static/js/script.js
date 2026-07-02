document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const workspaceCard = document.getElementById('main-processor-card');
    
    // Status Indicator Elements
    const statusIndicator = document.getElementById('status-indicator-dot');
    const statusText = document.getElementById('status-display-text');
    
    // Step Containers
    const stepUpload = document.getElementById('step-upload');
    const stepPreview = document.getElementById('step-preview');
    const stepLoading = document.getElementById('step-loading');
    const stepDownloadReady = document.getElementById('step-download-ready');
    
    // Step 2 Preview Elements
    const previewFilename = document.getElementById('preview-filename');
    const previewFilesize = document.getElementById('preview-filesize');
    const previewFiletype = document.getElementById('preview-filetype');
    const previewFileIcon = document.getElementById('preview-file-icon');
    const metadataTableBody = document.getElementById('metadata-table-body');
    const metadataTable = document.getElementById('metadata-table');
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
    const btnHeroStart = document.getElementById('btn-hero-start');
    const btnCancelPreview = document.getElementById('btn-cancel-preview');
    const btnProcessClean = document.getElementById('btn-process-clean');
    const btnResetCleaner = document.getElementById('btn-reset-cleaner');
    const btnDownloadFile = document.getElementById('btn-download-file');
    
    // State variables
    let currentFileData = null;
    
    // ----------------------------------------------------
    // 1. Scroll helper for Hero Button
    // ----------------------------------------------------
    if (btnHeroStart) {
        btnHeroStart.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector('#workspace-anchor');
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }

    // ----------------------------------------------------
    // 2. 3D Mouse Parallax / Perspective Tilt Effect
    // ----------------------------------------------------
    const handleTilt = (e) => {
        const cardRect = workspaceCard.getBoundingClientRect();
        const cardWidth = cardRect.width;
        const cardHeight = cardRect.height;
        
        // Calculate mouse position relative to the card's center (coordinates -1 to 1)
        const mouseX = (e.clientX - cardRect.left) / cardWidth - 0.5;
        const mouseY = (e.clientY - cardRect.top) / cardHeight - 0.5;
        
        // Tilt degrees limit
        const maxTiltX = 6;
        const maxTiltY = 6;
        
        const tiltX = -(mouseY * maxTiltX).toFixed(2);
        const tiltY = (mouseX * maxTiltY).toFixed(2);
        
        // Apply transform
        workspaceCard.style.transform = `rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale3d(1.02, 1.02, 1.02)`;
        workspaceCard.style.transition = 'transform 0.05s ease';
    };
    
    const resetTilt = () => {
        workspaceCard.style.transform = 'rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
        workspaceCard.style.transition = 'transform 0.5s ease';
    };
    
    // Attach mouse interaction to processor card
    const workspaceWrapper = document.querySelector('.workspace-3d-wrapper');
    if (workspaceWrapper) {
        workspaceWrapper.addEventListener('mousemove', handleTilt);
        workspaceWrapper.addEventListener('mouseleave', resetTilt);
    }
    
    // ----------------------------------------------------
    // 3. Drag & Drop File Handling
    // ----------------------------------------------------
    
    // Trigger file dialog
    if (dropZone) {
        dropZone.addEventListener('click', () => fileInput.click());
        
        // Visual effects for Drag & Drop
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add('dragover');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove('dragover');
            }, false);
        });
        
        // Process dropped files
        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                handleFileSelection(files[0]);
            }
        });
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelection(e.target.files[0]);
            }
        });
    }
    
    // ----------------------------------------------------
    // 4. File Upload & Processing API calls
    // ----------------------------------------------------
    
    const setStatus = (status, text) => {
        statusIndicator.className = `status-indicator ${status}`;
        statusText.textContent = text;
    };
    
    const showStep = (stepElement) => {
        [stepUpload, stepPreview, stepLoading, stepDownloadReady].forEach(step => {
            step.classList.remove('active');
        });
        stepElement.classList.add('active');
    };
    
    const getFileIconSVG = (category) => {
        const icons = {
            image: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>`,
            document: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`,
            audio: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>`,
            video: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>`,
            unknown: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="12" y1="9" x2="12.01" y2="9"/></svg>`
        };
        return icons[category] || icons.unknown;
    };
    
    const handleFileSelection = (file) => {
        // Prepare interface transition
        showStep(stepLoading);
        setStatus('processing', 'Analyzing file structure...');
        
        loadingTitleStatus.textContent = "Scanning File...";
        loadingSubStatus.textContent = "Checking security signature and metadata logs.";
        progressBarFill.style.width = '20%';
        progressPercentageText.textContent = '20%';
        
        const formData = new FormData();
        formData.append('file', file);
        
        // Use standard XMLHttpRequest to support upload progress tracking
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);
        
        // Track upload progress
        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                // Map upload progress from 20% to 80%
                const pct = Math.round((e.loaded / e.total) * 60) + 20;
                progressBarFill.style.width = `${pct}%`;
                progressPercentageText.textContent = `${pct}%`;
            }
        };
        
        xhr.onload = () => {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.success) {
                    currentFileData = response.data;
                    displayMetadataPreview(response.data);
                } else {
                    handleUploadError(response.message);
                }
            } else {
                let errMsg = "An error occurred during file upload.";
                try {
                    const response = JSON.parse(xhr.responseText);
                    errMsg = response.message || errMsg;
                } catch(e) {}
                handleUploadError(errMsg);
            }
        };
        
        xhr.onerror = () => {
            handleUploadError("Network connection interrupted during scan.");
        };
        
        xhr.send(formData);
    };
    
    const handleUploadError = (message) => {
        alert(`Upload Failed: ${message}`);
        resetCleanerUI();
    };
    
    const displayMetadataPreview = (data) => {
        // Set info tags
        previewFilename.textContent = data.original_name;
        previewFilesize.textContent = data.formatted_size;
        previewFiletype.textContent = `${data.mime_type.split('/')[1].toUpperCase()} (${data.category.toUpperCase()})`;
        previewFileIcon.innerHTML = getFileIconSVG(data.category);
        
        // Empty table
        metadataTableBody.innerHTML = '';
        
        const metadata = data.metadata || {};
        const keys = Object.keys(metadata);
        
        if (keys.length === 0) {
            metadataTable.classList.add('hidden');
            noMetadataMsg.classList.remove('hidden');
        } else {
            metadataTable.classList.remove('hidden');
            noMetadataMsg.classList.add('hidden');
            
            keys.forEach(key => {
                const row = document.createElement('tr');
                const cellKey = document.createElement('td');
                cellKey.textContent = key;
                const cellVal = document.createElement('td');
                cellVal.textContent = metadata[key];
                
                row.appendChild(cellKey);
                row.appendChild(cellVal);
                metadataTableBody.appendChild(row);
            });
        }
        
        setStatus('idle', 'Previewing Metadata');
        showStep(stepPreview);
    };
    
    // ----------------------------------------------------
    // 5. Metadata Cleaning Actions
    // ----------------------------------------------------
    if (btnProcessClean) {
        btnProcessClean.addEventListener('click', () => {
            if (!currentFileData) return;
            
            // Switch to loading
            showStep(stepLoading);
            setStatus('processing', 'Purging metadata fields...');
            
            loadingTitleStatus.textContent = "Cleaning File...";
            loadingSubStatus.textContent = "Stripping geolocation logs, author records, and camera EXIF streams.";
            
            // Fast loading step animations
            let progress = 10;
            const progressInterval = setInterval(() => {
                progress += 8;
                if (progress > 90) {
                    clearInterval(progressInterval);
                } else {
                    progressBarFill.style.width = `${progress}%`;
                    progressPercentageText.textContent = `${progress}%`;
                    
                    // Rotate custom descriptions
                    if (progress > 30 && progress < 60) {
                        loadingSubStatus.textContent = "Removing software metadata chunks and timestamps.";
                    } else if (progress >= 60) {
                        loadingSubStatus.textContent = "Verifying clean file headers for structural safety.";
                    }
                }
            }, 100);
            
            // Call API
            fetch('/clean', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ file_id: currentFileData.file_id })
            })
            .then(res => res.json())
            .then(data => {
                clearInterval(progressInterval);
                if (data.success) {
                    progressBarFill.style.width = '100%';
                    progressPercentageText.textContent = '100%';
                    
                    setTimeout(() => {
                        displaySuccessPage(data.data);
                    }, 300);
                } else {
                    alert(`Cleaning failed: ${data.message}`);
                    resetCleanerUI();
                }
            })
            .catch(err => {
                clearInterval(progressInterval);
                alert("Network communication error during cleaning.");
                resetCleanerUI();
            });
        });
    }
    
    const displaySuccessPage = (cleanData) => {
        statOriginalSize.textContent = currentFileData.formatted_size;
        statCleanedSize.textContent = cleanData.cleaned_size;
        statTime.textContent = `${cleanData.time_taken_ms} ms`;
        
        // Update download button url with the original filename passed as name query param
        btnDownloadFile.href = `/download/${cleanData.cleaned_file_id}?name=${encodeURIComponent(currentFileData.original_name)}`;
        
        setStatus('success', 'Metadata Cleaned');
        showStep(stepDownloadReady);
    };
    
    // ----------------------------------------------------
    // 6. UI Reset triggers
    // ----------------------------------------------------
    const resetCleanerUI = () => {
        currentFileData = null;
        fileInput.value = '';
        setStatus('idle', 'Ready to Scan');
        showStep(stepUpload);
    };
    
    if (btnCancelPreview) {
        btnCancelPreview.addEventListener('click', resetCleanerUI);
    }
    
    if (btnResetCleaner) {
        btnResetCleaner.addEventListener('click', resetCleanerUI);
    }
    
    // On download click, wait a short moment and reset to homepage
    // because files are deleted from the disk on completion!
    if (btnDownloadFile) {
        btnDownloadFile.addEventListener('click', () => {
            setTimeout(() => {
                resetCleanerUI();
            }, 1500);
        });
    }
});
