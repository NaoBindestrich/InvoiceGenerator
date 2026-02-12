/**
 * Settings Form Handler
 * Manages company settings configuration
 */

// Load existing settings when page loads
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/company-settings');
        if (response.ok) {
            const settings = await response.json();
            populateForm(settings);
        }
    } catch (error) {
        console.log('No existing settings found, using defaults');
    }
});

// Populate form with existing settings
function populateForm(settings) {
    const form = document.getElementById('settingsForm');
    const inputs = form.querySelectorAll('input');
    
    inputs.forEach(input => {
        const fieldName = input.name;
        if (settings[fieldName]) {
            input.value = settings[fieldName];
        }
    });
}

// Handle form submission
document.getElementById('settingsForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const settings = {};
    
    formData.forEach((value, key) => {
        settings[key] = value;
    });
    
    try {
        const response = await fetch('/api/company-settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settings)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess(result.message);
            // Show success section after a short delay
            setTimeout(() => {
                document.getElementById('settingsSection').style.display = 'none';
                document.getElementById('successSection').style.display = 'block';
            }, 1000);
        } else {
            showAlert(result.error || 'Failed to save settings', 'error');
        }
    } catch (error) {
        showAlert('Failed to save settings: ' + error.message, 'error');
    }
});

// Show alert message
function showAlert(message, type = 'error') {
    const alert = document.getElementById('alert');
    alert.textContent = message;
    alert.className = `alert alert-${type} show`;
    
    setTimeout(() => {
        alert.classList.remove('show');
    }, 5000);
}

// Show success message
function showSuccess(message) {
    showAlert(message, 'success');
}
