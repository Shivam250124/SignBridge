// SignBridge - Main JavaScript

// Global utility functions
const SignBridge = {
    // API base URL
    API_URL: window.location.origin,
    
    // Make API request
    async apiRequest(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.API_URL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    // Format timestamp
    formatTime(date = new Date()) {
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // Show toast notification
    showNotification(message, type = 'info') {
        console.log(`[${type.toUpperCase()}] ${message}`);

        // Remove any existing toast with same message to avoid stacking
        const existing = document.querySelector('.sb-toast');
        if (existing) existing.remove();

        const colors = {
            success: '#22c55e',
            error:   '#ef4444',
            warning: '#f59e0b',
            info:    '#3b82f6'
        };
        const icons = {
            success: '✅',
            error:   '❌',
            warning: '⚠️',
            info:    'ℹ️'
        };

        const toast = document.createElement('div');
        toast.className = 'sb-toast';
        toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span> ${message}`;
        toast.style.cssText = `
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: ${colors[type] || colors.info};
            color: white;
            padding: 0.75rem 1.25rem;
            border-radius: 0.5rem;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            font-size: 0.95rem;
            font-weight: 600;
            z-index: 99999;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            max-width: 320px;
            animation: sbSlideIn 0.3s ease-out;
        `;

        // Inject keyframe once
        if (!document.getElementById('sb-toast-style')) {
            const style = document.createElement('style');
            style.id = 'sb-toast-style';
            style.textContent = `
                @keyframes sbSlideIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to   { opacity: 1; transform: translateY(0); }
                }
                @keyframes sbSlideOut {
                    from { opacity: 1; transform: translateY(0); }
                    to   { opacity: 0; transform: translateY(20px); }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'sbSlideOut 0.3s ease-in forwards';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },
    
    // Debounce function
    debounce(func, wait) {
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
};

// Make SignBridge globally available
window.SignBridge = SignBridge;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌉 SignBridge initialized');
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});
