/**
 * Utility Functions
 * Helper methods for DOM manipulation, formatting, etc.
 */

// Format date relative to now (e.g., "2 hours ago")
function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    let interval = Math.floor(seconds / 31536000);
    if (interval >= 1) return interval + " year" + (interval === 1 ? "" : "s") + " ago";

    interval = Math.floor(seconds / 2592000);
    if (interval >= 1) return interval + " month" + (interval === 1 ? "" : "s") + " ago";

    interval = Math.floor(seconds / 86400);
    if (interval >= 1) return interval + " day" + (interval === 1 ? "" : "s") + " ago";

    interval = Math.floor(seconds / 3600);
    if (interval >= 1) return interval + " hour" + (interval === 1 ? "" : "s") + " ago";

    interval = Math.floor(seconds / 60);
    if (interval >= 1) return interval + " minute" + (interval === 1 ? "" : "s") + " ago";

    return "just now";
}

// Format full date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Generate avatar URL based on email (using Gravatar logic or placeholder)
function getAvatarUrl(email) {
    // Simple hashed-color placeholder generator
    // In a real app, use Gravatar or backend implementation
    return `https://api.dicebear.com/7.x/avataaars/svg?seed=${email}`;
}

// DOM Element Creator Helper
function createElement(tag, className, attributes = {}, ...children) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    
    Object.keys(attributes).forEach(key => {
        if (key.startsWith('on') && typeof attributes[key] === 'function') {
            element.addEventListener(key.substring(2).toLowerCase(), attributes[key]);
        } else if (key === 'dataset') {
            Object.keys(attributes.dataset).forEach(dataKey => {
                element.dataset[dataKey] = attributes.dataset[dataKey];
            });
        } else {
            element.setAttribute(key, attributes[key]);
        }
    });

    children.forEach(child => {
        if (typeof child === 'string' || typeof child === 'number') {
            element.appendChild(document.createTextNode(child));
        } else if (child instanceof Node) {
            element.appendChild(child);
        } else if (Array.isArray(child)) { // Handle array of children
            child.forEach(c => element.appendChild(c));
        }
    });

    return element;
}

// Theme Management
const themeManager = {
    init() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        return savedTheme;
    },
    
    toggle() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        return next;
    }
};

// Toast Notifications
function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = createElement('div', 'toast-container');
        document.body.appendChild(container);
    }

    const iconMap = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    const toast = createElement('div', `toast toast-${type}`, {},
        createElement('span', 'toast-icon', {}, iconMap[type]),
        createElement('span', 'toast-message', {}, message)
    );

    container.appendChild(toast);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.add('toast-exit');
        toast.addEventListener('animationend', () => toast.remove());
    }, 3000);
}

// Debounce Function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export to window
window.utils = {
    timeAgo,
    formatDate,
    getAvatarUrl,
    createElement,
    themeManager, 
    showToast,
    debounce
};
