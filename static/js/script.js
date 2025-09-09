let currentConversionType = '';
let selectedFiles = [];

// Conversion type configurations
const conversionConfig = {
    'pdf-to-docx': {
        title: 'Convert PDF to DOCX',
        accept: '.pdf',
        formats: 'PDF files',
        multiple: false,
        endpoint: '/convert/pdf-to-docx'
    },
    'docx-to-pdf': {
        title: 'Convert DOCX to PDF',
        accept: '.docx,.doc',
        formats: 'DOCX, DOC files',
        multiple: false,
        endpoint: '/convert/docx-to-pdf'
    },
    'pdf-to-jpg': {
        title: 'Convert PDF to JPG',
        accept: '.pdf',
        formats: 'PDF files',
        multiple: false,
        endpoint: '/convert/pdf-to-jpg'
    },
    'jpg-to-pdf': {
        title: 'Convert JPG to PDF',
        accept: '.jpg,.jpeg,.png,.bmp,.tiff',
        formats: 'JPG, PNG, BMP, TIFF files',
        multiple: true,
        endpoint: '/convert/jpg-to-pdf'
    },
    'ocr': {
        title: 'Extract Text (OCR)',
        accept: '.pdf,.jpg,.jpeg,.png,.bmp,.tiff',
        formats: 'PDF, JPG, PNG, BMP, TIFF files',
        multiple: false,
        endpoint: '/ocr'
    }
};

// Show upload form modal
function showUploadForm(conversionType) {
    currentConversionType = conversionType;
    const config = conversionConfig[conversionType];
    
    document.getElementById('modalTitle').textContent = config.title;
    document.getElementById('supportedFormats').textContent = config.formats;
    document.getElementById('fileInput').accept = config.accept;
    document.getElementById('fileInput').multiple = config.multiple;
    
    // Reset form
    resetForm();
    
    document.getElementById('uploadModal').style.display = 'block';
}

// Close modal
function closeModal() {
    document.getElementById('uploadModal').style.display = 'none';
    resetForm();
}

// Reset form to initial state
function resetForm() {
    selectedFiles = [];
    document.getElementById('fileList').innerHTML = '';
    document.getElementById('progressArea').style.display = 'none';
    document.getElementById('resultArea').style.display = 'none';
    document.getElementById('uploadForm').style.display = 'block';
    
    const progressFill = document.querySelector('.progress-fill');
    progressFill.style.width = '0%';
}

// File input change handler
document.getElementById('fileInput').addEventListener('change', function(e) {
    handleFiles(e.target.files);
});

// Drag and drop handlers
const uploadArea = document.getElementById('uploadArea');

uploadArea.addEventListener('click', function() {
    document.getElementById('fileInput').click();
});

uploadArea.addEventListener('dragover', function(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', function(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', function(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
});

// Handle selected files
function handleFiles(files) {
    const config = conversionConfig[currentConversionType];
    const fileList = document.getElementById('fileList');
    
    if (!config.multiple) {
        selectedFiles = [];
        fileList.innerHTML = '';
    }
    
    for (let file of files) {
        if (validateFile(file)) {
            selectedFiles.push(file);
            addFileToList(file);
        }
    }
}

// Validate file
function validateFile(file) {
    const config = conversionConfig[currentConversionType];
    const allowedExtensions = config.accept.split(',').map(ext => ext.trim().toLowerCase());
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedExtensions.includes(fileExtension)) {
        alert(`File type not supported. Please select: ${config.formats}`);
        return false;
    }
    
    // Check file size (16MB limit)
    if (file.size > 16 * 1024 * 1024) {
        alert('File size too large. Maximum size is 16MB.');
        return false;
    }
    
    return true;
}

// Add file to display list
function addFileToList(file) {
    const fileList = document.getElementById('fileList');
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.innerHTML = `
        <div>
            <div class="file-name">${file.name}</div>
            <div class="file-size">${formatFileSize(file.size)}</div>
        </div>
        <button type="button" class="remove-file" onclick="removeFile('${file.name}')">×</button>
    `;
    fileList.appendChild(fileItem);
}

// Remove file from list
function removeFile(fileName) {
    selectedFiles = selectedFiles.filter(file => file.name !== fileName);
    updateFileList();
}

// Update file list display
function updateFileList() {
    const fileList = document.getElementById('fileList');
    fileList.innerHTML = '';
    selectedFiles.forEach(file => addFileToList(file));
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Form submission handler
document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    if (selectedFiles.length === 0) {
        alert('Please select at least one file.');
        return;
    }
    
    const config = conversionConfig[currentConversionType];
    const formData = new FormData();
    
    if (config.multiple) {
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });
    } else {
        formData.append('file', selectedFiles[0]);
    }
    
    // Show progress
    document.getElementById('uploadForm').style.display = 'none';
    document.getElementById('progressArea').style.display = 'block';
    
    // Start progress animation
    let progress = 0;
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.getElementById('progressText');
    
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        progressFill.style.width = progress + '%';
    }, 200);
    
    // Make API request
    fetch(config.endpoint, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        
        if (!response.ok) {
            return response.json().then(err => Promise.reject(err));
        }
        
        if (currentConversionType === 'ocr') {
            return response.json();
        } else {
            return response.blob().then(blob => {
                const filename = getFilenameFromResponse(response) || 'converted_file';
                return { blob, filename };
            });
        }
    })
    .then(result => {
        document.getElementById('progressArea').style.display = 'none';
        document.getElementById('resultArea').style.display = 'block';
        
        if (currentConversionType === 'ocr') {
            showOCRResult(result);
        } else {
            showDownloadResult(result);
        }
    })
    .catch(error => {
        clearInterval(progressInterval);
        document.getElementById('progressArea').style.display = 'none';
        document.getElementById('uploadForm').style.display = 'block';
        
        console.error('Conversion error:', error);
        alert('Conversion failed: ' + (error.error || error.message || 'Unknown error'));
    });
});

// Get filename from response headers
function getFilenameFromResponse(response) {
    const contentDisposition = response.headers.get('Content-Disposition');
    if (contentDisposition) {
        const matches = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (matches && matches[1]) {
            return matches[1].replace(/['"]/g, '');
        }
    }
    return null;
}

// Show download result
function showDownloadResult(result) {
    const resultContent = document.getElementById('resultContent');
    
    // Create download link
    const url = window.URL.createObjectURL(result.blob);
    const downloadLink = document.createElement('a');
    downloadLink.href = url;
    downloadLink.download = result.filename;
    downloadLink.className = 'download-btn';
    downloadLink.textContent = '📥 Download Converted File';
    
    resultContent.innerHTML = '';
    resultContent.appendChild(downloadLink);
    
    // Auto-click download
    downloadLink.click();
    
    // Add option to convert another file
    const newConversionBtn = document.createElement('button');
    newConversionBtn.className = 'btn-primary';
    newConversionBtn.textContent = 'Convert Another File';
    newConversionBtn.style.marginTop = '1rem';
    newConversionBtn.onclick = () => {
        resetForm();
    };
    
    resultContent.appendChild(newConversionBtn);
}

// Show OCR result
function showOCRResult(result) {
    const resultContent = document.getElementById('resultContent');
    
    const ocrContainer = document.createElement('div');
    ocrContainer.className = 'ocr-result';
    
    const textArea = document.createElement('textarea');
    textArea.className = 'ocr-text';
    textArea.value = result.extracted_text;
    textArea.rows = 10;
    textArea.style.width = '100%';
    textArea.style.resize = 'vertical';
    
    const buttonsDiv = document.createElement('div');
    buttonsDiv.style.marginTop = '1rem';
    
    // Copy text button
    const copyBtn = document.createElement('button');
    copyBtn.className = 'edit-text-btn';
    copyBtn.textContent = '📋 Copy Text';
    copyBtn.onclick = () => {
        textArea.select();
        document.execCommand('copy');
        copyBtn.textContent = '✅ Copied!';
        setTimeout(() => {
            copyBtn.textContent = '📋 Copy Text';
        }, 2000);
    };
    
    // Download as DOCX button
    const docxBtn = document.createElement('button');
    docxBtn.className = 'edit-text-btn';
    docxBtn.textContent = '📄 Save as DOCX';
    docxBtn.style.marginLeft = '0.5rem';
    docxBtn.onclick = () => {
        const formattedText = textArea.value;
        fetch('/edit-text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: formattedText,
                operation: 'to_docx'
            })
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'extracted_text.docx';
            a.click();
        })
        .catch(error => {
            console.error('Error creating DOCX:', error);
            alert('Failed to create DOCX file');
        });
    };
    
    // New conversion button
    const newConversionBtn = document.createElement('button');
    newConversionBtn.className = 'btn-primary';
    newConversionBtn.textContent = 'Extract Text from Another File';
    newConversionBtn.style.marginLeft = '0.5rem';
    newConversionBtn.onclick = () => {
        resetForm();
    };
    
    buttonsDiv.appendChild(copyBtn);
    buttonsDiv.appendChild(docxBtn);
    buttonsDiv.appendChild(newConversionBtn);
    
    ocrContainer.appendChild(textArea);
    ocrContainer.appendChild(buttonsDiv);
    
    resultContent.innerHTML = '';
    resultContent.appendChild(ocrContainer);
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('uploadModal');
    if (event.target === modal) {
        closeModal();
    }
};

// Handle escape key to close modal
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeModal();
    }
});