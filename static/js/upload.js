document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const browseButton = document.getElementById('browseButton');
    const uploadForm = document.getElementById('uploadForm');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const submitButton = document.getElementById('submitButton');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const result = document.getElementById('result');
    const probabilityBar = document.getElementById('probabilityBar');
    const probabilityValue = document.getElementById('probabilityValue');
    const reasoningText = document.getElementById('reasoningText');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when dragging over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);

    // Handle browse button click
    browseButton.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle file input change
    fileInput.addEventListener('change', handleFileSelect);

    // Handle form submission
    uploadForm.addEventListener('submit', handleSubmit);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        dropZone.classList.add('dragover');
    }

    function unhighlight(e) {
        dropZone.classList.remove('dragover');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFileSelect(e) {
        const files = e.target.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            showFileInfo(file);
        }
    }

    function showFileInfo(file) {
        fileName.textContent = file.name;
        fileInfo.classList.remove('d-none');
        submitButton.classList.remove('d-none');
    }

    async function handleSubmit(e) {
        e.preventDefault();

        const file = fileInput.files[0];
        if (!file) {
            showError('Please select a file first.');
            return;
        }

        // Show loading state
        loadingSpinner.classList.remove('d-none');
        submitButton.disabled = true;
        result.classList.add('d-none');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                showResult(data);
            } else {
                showError(data.error || 'An error occurred during upload.');
            }
        } catch (error) {
            showError('Network error occurred.');
        } finally {
            loadingSpinner.classList.add('d-none');
            submitButton.disabled = false;
        }
    }

    function showResult(data) {
        result.classList.remove('d-none');
        const probability = parseFloat(data.ai_generated_probability);
        probabilityBar.style.width = `${probability}%`;
        probabilityBar.classList.remove('bg-success', 'bg-warning', 'bg-danger');

        if (probability < 30) {
            probabilityBar.classList.add('bg-success');
        } else if (probability < 70) {
            probabilityBar.classList.add('bg-warning');
        } else {
            probabilityBar.classList.add('bg-danger');
        }

        probabilityValue.textContent = `${probability}%`;

        // Display reasoning if available
        if (data.reasoning) {
            reasoningText.textContent = data.reasoning;
            reasoningText.parentElement.classList.remove('d-none');
        } else {
            reasoningText.parentElement.classList.add('d-none');
        }
    }

    function showError(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show mt-3';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        uploadForm.insertAdjacentElement('afterend', alert);

        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
});