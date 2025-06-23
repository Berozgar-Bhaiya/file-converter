// File Converter JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('conversionForm');
    const fileInput = document.getElementById('file');
    const filesInput = document.getElementById('files');
    const conversionTypeSelect = document.getElementById('conversion_type');
    const submitBtn = document.getElementById('submitBtn');
    const progressSection = document.getElementById('progressSection');
    const fileInfo = document.getElementById('fileInfo');
    const fileLabel = document.getElementById('fileLabel');

    // File extension validation mapping
    const allowedExtensions = {
        // Document conversions
        'pdf_to_docx': ['.pdf'],
        'docx_to_pdf': ['.docx'],
        'doc_to_pdf': ['.doc'],
        'pptx_to_pdf': ['.pptx'],
        'pdf_to_txt': ['.pdf'],
        'txt_to_pdf': ['.txt'],
        'xlsx_to_csv': ['.xlsx', '.xls'],
        'csv_to_xlsx': ['.csv'],
        'xlsx_to_pdf': ['.xlsx', '.xls'],
        'csv_to_pdf': ['.csv'],
        'html_to_pdf': ['.html', '.htm'],
        'epub_to_pdf': ['.epub'],
        'pdf_to_html': ['.pdf'],
        
        // Image conversions
        'jpg_to_png': ['.jpg', '.jpeg'],
        'png_to_jpg': ['.png'],
        'webp_to_jpg': ['.webp'],
        'jpg_to_webp': ['.jpg', '.jpeg'],
        'image_to_pdf': ['.jpg', '.jpeg', '.png', '.webp', '.bmp'],
        'pdf_to_png': ['.pdf'],
        'bmp_to_png': ['.bmp'],
        
        // Audio conversions
        'mp3_to_wav': ['.mp3'],
        'wav_to_mp3': ['.wav'],
        'mp4_to_mp3': ['.mp4'],
        
        // Video conversions
        'mp4_to_avi': ['.mp4'],
        'avi_to_mp4': ['.avi'],
        'mkv_to_mp4': ['.mkv'],
        'mp4_to_webm': ['.mp4'],
        
        // Additional audio
        'ogg_to_mp3': ['.ogg'],
        
        // Extras
        'compress_pdf': ['.pdf'],
        'merge_pdfs': ['.pdf'],
        'merge_images': ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
    };

    // Update file info based on conversion type
    conversionTypeSelect.addEventListener('change', function() {
        const conversionType = this.value;
        
        // Handle multi-file operations
        if (conversionType === 'merge_pdfs') {
            fileInput.classList.add('d-none');
            filesInput.classList.remove('d-none');
            fileInput.required = false;
            filesInput.required = true;
            filesInput.accept = '.pdf';
            fileLabel.textContent = 'Choose Multiple PDF Files';
            fileInfo.textContent = 'Select 2 or more PDF files to merge | Maximum file size: 50MB each';
        } else if (conversionType === 'merge_images') {
            fileInput.classList.add('d-none');
            filesInput.classList.remove('d-none');
            fileInput.required = false;
            filesInput.required = true;
            filesInput.accept = '.jpg,.jpeg,.png,.webp,.bmp';
            fileLabel.textContent = 'Choose Multiple Image Files';
            fileInfo.textContent = 'Select 2 or more images (JPG, PNG, WEBP, BMP) to merge into PDF | Maximum file size: 50MB each';
        } else {
            // Single file conversion
            fileInput.classList.remove('d-none');
            filesInput.classList.add('d-none');
            fileInput.required = true;
            filesInput.required = false;
            filesInput.accept = '';
            fileLabel.textContent = 'Choose File';
            
            if (conversionType && allowedExtensions[conversionType]) {
                const extensions = allowedExtensions[conversionType].join(', ');
                fileInfo.textContent = `Accepted formats: ${extensions} | Maximum file size: 50MB`;
            } else {
                fileInfo.textContent = 'Maximum file size: 50MB';
            }
        }
        
        // Clear file inputs when conversion type changes
        fileInput.value = '';
        filesInput.value = '';
        validateForm();
    });

    // Single file input validation
    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            if (!validateSingleFile(file, conversionTypeSelect.value)) {
                this.value = '';
                return;
            }

            // Update file info with selected file details
            const fileSize = formatFileSize(file.size);
            fileInfo.innerHTML = `
                <i class="fas fa-file me-1"></i>
                Selected: <strong>${file.name}</strong> (${fileSize})
            `;
        }
        
        validateForm();
    });

    // Multiple files input validation
    filesInput.addEventListener('change', function() {
        const files = Array.from(this.files);
        const conversionType = conversionTypeSelect.value;
        
        if (files.length < 2) {
            const fileType = conversionType === 'merge_pdfs' ? 'PDF' : 'image';
            showAlert(`Please select at least 2 ${fileType} files to merge.`, 'error');
            this.value = '';
            return;
        }

        if (files.length > 10) {
            showAlert('Maximum 10 files allowed for merging.', 'error');
            this.value = '';
            return;
        }

        // Validate each file based on conversion type
        let totalSize = 0;
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            
            // Check file size
            const maxSize = 50 * 1024 * 1024; // 50MB in bytes
            if (file.size > maxSize) {
                showAlert(`File "${file.name}" is too large. Maximum size is 50MB.`, 'error');
                this.value = '';
                return;
            }

            // Validate file type based on conversion
            if (conversionType === 'merge_pdfs') {
                if (!file.name.toLowerCase().endsWith('.pdf')) {
                    showAlert(`File "${file.name}" is not a PDF. Only PDF files can be merged.`, 'error');
                    this.value = '';
                    return;
                }
            } else if (conversionType === 'merge_images') {
                const imageExtensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp'];
                const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
                if (!imageExtensions.includes(fileExt)) {
                    showAlert(`File "${file.name}" is not a supported image. Only JPG, PNG, WEBP, BMP images can be merged.`, 'error');
                    this.value = '';
                    return;
                }
            }

            totalSize += file.size;
        }

        // Update file info with selected files
        const totalSizeFormatted = formatFileSize(totalSize);
        const fileType = conversionType === 'merge_pdfs' ? 'PDF' : 'image';
        const icon = conversionType === 'merge_pdfs' ? 'fa-file-pdf' : 'fa-images';
        
        fileInfo.innerHTML = `
            <i class="fas ${icon} me-1"></i>
            Selected: <strong>${files.length} ${fileType} files</strong> (Total: ${totalSizeFormatted})
        `;
        
        validateForm();
    });

    function validateSingleFile(file, conversionType) {
        // Check file size (50MB limit)
        const maxSize = 50 * 1024 * 1024; // 50MB in bytes
        if (file.size > maxSize) {
            showAlert('File too large. Maximum size is 50MB.', 'error');
            return false;
        }

        // Check file extension
        if (conversionType && allowedExtensions[conversionType]) {
            const fileName = file.name.toLowerCase();
            const isValidExtension = allowedExtensions[conversionType].some(ext => 
                fileName.endsWith(ext.toLowerCase())
            );
            
            if (!isValidExtension) {
                const extensions = allowedExtensions[conversionType].join(', ');
                showAlert(`Invalid file type. Please select a file with one of these extensions: ${extensions}`, 'error');
                return false;
            }
        }

        return true;
    }

    // Form validation
    function validateForm() {
        const conversionType = conversionTypeSelect.value;
        let hasFiles = false;
        
        if (conversionType === 'merge_pdfs' || conversionType === 'merge_images') {
            hasFiles = filesInput.files.length >= 2;
        } else {
            hasFiles = fileInput.files.length > 0;
        }
        
        const hasConversionType = conversionType !== '';
        
        submitBtn.disabled = !(hasFiles && hasConversionType);
        
        if (submitBtn.disabled) {
            if (conversionType === 'merge_pdfs') {
                submitBtn.innerHTML = '<i class="fas fa-compress-arrows-alt me-2"></i>Merge PDFs';
            } else if (conversionType === 'merge_images') {
                submitBtn.innerHTML = '<i class="fas fa-images me-2"></i>Merge Images';
            } else {
                submitBtn.innerHTML = '<i class="fas fa-play me-2"></i>Convert File';
            }
        } else {
            if (conversionType === 'merge_pdfs') {
                submitBtn.innerHTML = '<i class="fas fa-compress-arrows-alt me-2"></i>Merge PDFs';
            } else if (conversionType === 'merge_images') {
                submitBtn.innerHTML = '<i class="fas fa-images me-2"></i>Merge Images';
            } else {
                submitBtn.innerHTML = '<i class="fas fa-play me-2"></i>Convert File';
            }
        }
    }

    // Form submission handling
    form.addEventListener('submit', function(e) {
        if (submitBtn.disabled) {
            e.preventDefault();
            return;
        }

        // Show progress indicator
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Converting...';
        progressSection.style.display = 'block';
        
        // Scroll to progress section
        progressSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });

    // Utility function to format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Utility function to show alerts
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'check-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert alert at the top of the main container
        const main = document.querySelector('main.container');
        main.insertBefore(alertDiv, main.firstChild);
        
        // Auto-remove alert after 5 seconds
        setTimeout(function() {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // Drag and drop functionality
    const fileUploadWrapper = document.querySelector('.file-upload-wrapper');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileUploadWrapper.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        fileUploadWrapper.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileUploadWrapper.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        fileUploadWrapper.classList.add('drag-over');
    }

    function unhighlight(e) {
        fileUploadWrapper.classList.remove('drag-over');
    }

    fileUploadWrapper.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(event);
        }
    }

    // Initial form validation
    validateForm();
});
