// Aura Bank Shared JS Application Utilities

// Toast System
function showToast(message, type = 'success') {
    let toastBox = document.getElementById('toast-box');
    if (!toastBox) {
        toastBox = document.createElement('div');
        toastBox.id = 'toast-box';
        toastBox.className = 'toast-container';
        document.body.appendChild(toastBox);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let iconClass = 'fa-circle-check';
    if (type === 'error') {
        iconClass = 'fa-circle-exclamation';
    } else if (type === 'info') {
        iconClass = 'fa-circle-info';
    }

    toast.innerHTML = `
        <i class="fa-solid ${iconClass}" style="font-size: 16px;"></i>
        <span>${message}</span>
    `;

    toastBox.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastSlideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) reverse';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 4000);
}

// Password Visibility Toggle
function togglePasswordVisibility(inputId, icon) {
    const input = document.getElementById(inputId);
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fa-regular fa-eye-slash password-toggle';
    } else {
        input.type = 'password';
        icon.className = 'fa-regular fa-eye password-toggle';
    }
}

// API Fetch Helper with Authorization
async function apiFetch(url, options = {}) {
    const token = localStorage.getItem('aura_session_token');
    
    // Set headers
    const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {})
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    // Handle session expiration
    if (response.status === 401 && !url.includes('/api/login') && !url.includes('/api/register')) {
        localStorage.removeItem('aura_session_token');
        showToast('Sesi Anda telah berakhir. Silakan masuk kembali.', 'error');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1500);
        throw new Error('Unauthorized');
    }

    return response;
}
