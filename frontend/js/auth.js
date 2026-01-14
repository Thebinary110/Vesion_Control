/**
 * Authentication Module
 * Handles login, registration, session management
 */

class AuthManager {
    constructor() {
        this.user = null;
        this.isAuthenticated = false;
        this.listeners = [];
    }

    // Initialize auth state
    async init() {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                this.user = await authApi.getCurrentUser();
                this.isAuthenticated = true;
                this.notifyListeners();
            } catch (error) {
                // Token expired or invalid
                this.logout();
            }
        }
        return this.isAuthenticated;
    }

    // Register new user
    async register(email, password) {
        try {
            const result = await authApi.register(email, password);
            showToast('Account created successfully! Please log in.', 'success');
            return result;
        } catch (error) {
            showToast(error.message, 'error');
            throw error;
        }
    }

    // Login user
    async login(email, password) {
        try {
            const result = await authApi.login(email, password);
            localStorage.setItem('access_token', result.access_token);
            this.user = await authApi.getCurrentUser();
            this.isAuthenticated = true;
            this.notifyListeners();
            showToast(`Welcome back!`, 'success');
            return result;
        } catch (error) {
            showToast(error.message, 'error');
            throw error;
        }
    }

    // Logout user
    logout() {
        localStorage.removeItem('access_token');
        this.user = null;
        this.isAuthenticated = false;
        this.notifyListeners();
        showToast('You have been logged out.', 'info');
    }

    // Get user info
    getUser() {
        return this.user;
    }

    // Check if user is admin
    isAdmin() {
        return this.user?.role === 'admin';
    }

    // Subscribe to auth changes
    onAuthChange(callback) {
        this.listeners.push(callback);
        return () => {
            this.listeners = this.listeners.filter(l => l !== callback);
        };
    }

    // Notify all listeners of auth state change
    notifyListeners() {
        this.listeners.forEach(callback => callback(this.isAuthenticated, this.user));
    }
}

// Create global auth manager instance
const auth = new AuthManager();
window.auth = auth;
