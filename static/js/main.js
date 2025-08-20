// Modal management functions
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function openEditModal(jobId, name, url, seleniumInstructions, event) {
    console.log('=== EDIT MODAL DEBUG START ===');
    console.log('Parameters received:', {
        jobId: jobId, 
        name: name, 
        url: url, 
        seleniumInstructions: seleniumInstructions,
        event: event
    });
    
    // Prevent event bubbling if event is available
    if (event) {
        event.stopPropagation();
        console.log('Event propagation stopped');
    }
    
    // Set form values
    const nameField = document.getElementById('edit_name');
    const urlField = document.getElementById('edit_url');
    const instructionsField = document.getElementById('edit_selenium_instructions');
    const form = document.getElementById('editForm');
    
    console.log('DOM elements found:', {
        nameField: nameField ? 'FOUND' : 'NOT FOUND',
        urlField: urlField ? 'FOUND' : 'NOT FOUND',
        instructionsField: instructionsField ? 'FOUND' : 'NOT FOUND',
        form: form ? 'FOUND' : 'NOT FOUND'
    });
    
    if (nameField) {
        nameField.value = name || '';
        console.log('Name field set to:', nameField.value);
    } else {
        console.error('Name field not found!');
    }
    
    if (urlField) {
        urlField.value = url || '';
        console.log('URL field set to:', urlField.value);
    } else {
        console.error('URL field not found!');
    }
    
    if (instructionsField) {
        instructionsField.value = seleniumInstructions || '';
        console.log('Instructions field set to:', instructionsField.value);
        console.log('Instructions field type:', instructionsField.type);
        console.log('Instructions field tagName:', instructionsField.tagName);
    } else {
        console.error('Instructions field not found!');
    }
    
    if (form) {
        form.action = '/update_job/' + jobId;
        console.log('Form action set to:', form.action);
    } else {
        console.error('Form not found!');
    }
    
    console.log('=== EDIT MODAL DEBUG END ===');
    openModal('editModal');
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            alert.style.display = 'none';
        });
    }, 5000);
});

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = 'var(--error)';
                } else {
                    field.style.borderColor = 'var(--border-primary)';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
});

// Enhanced search functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.closest('form').submit();
            }
        });
    }
});

// Job card toggle functionality
function toggleJobCard(jobId) {
    const detailsElement = document.getElementById('details-' + jobId);
    const expandIcon = document.getElementById('expand-' + jobId);
    const jobCard = detailsElement.closest('.job-card');
    
    if (detailsElement.style.display === 'none' || !detailsElement.style.display) {
        // Expand
        detailsElement.style.display = 'block';
        expandIcon.classList.add('expanded');
        jobCard.classList.add('expanded');
    } else {
        // Collapse
        detailsElement.style.display = 'none';
        expandIcon.classList.remove('expanded');
        jobCard.classList.remove('expanded');
    }
}

// Show macro help modal
function showMacroHelp() {
    openModal('macroModal');
}

// Add event listeners when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, setting up event listeners');
    
    // Handle edit button clicks using event delegation on job-actions containers
    const jobActionsContainers = document.querySelectorAll('.job-actions');
    console.log('Found', jobActionsContainers.length, 'job-actions containers');
    
    jobActionsContainers.forEach(container => {
        // Stop propagation for the entire actions container
        container.addEventListener('click', function(event) {
            event.stopPropagation();
            console.log('Job actions container clicked');
            
            // Check if the clicked element is an edit button
            if (event.target.classList.contains('edit-job-btn')) {
                console.log('Edit button clicked!');
                
                const button = event.target;
                const jobId = button.dataset.jobId;
                const jobName = button.dataset.jobName;
                const jobUrl = button.dataset.jobUrl;
                const jobInstructions = button.dataset.jobInstructions;
                
                console.log('Job data:', {jobId, jobName, jobUrl, jobInstructions});
                openEditModal(jobId, jobName, jobUrl, jobInstructions, event);
            }
        });
    });
});