/**
 * API Service Layer
 * Handles all API communication with the backend
 */

const API_BASE_URL = 'http://localhost:8000';

class ApiService {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    // Get auth token from storage
    getToken() {
        return localStorage.getItem('access_token');
    }

    // Get auth headers
    getAuthHeaders() {
        const token = this.getToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    // Generic request handler
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...this.getAuthHeaders(),
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            // Handle no content responses
            if (response.status === 204) {
                return { success: true };
            }

            const data = await response.json();

            if (!response.ok) {
                throw new ApiError(data.detail || 'An error occurred', response.status);
            }

            return data;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError('Network error. Please check your connection.', 0);
        }
    }

    // GET request
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    // POST request
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // PUT request
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // DELETE request
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // Form data POST (for login)
    async postForm(endpoint, data) {
        const url = `${this.baseUrl}${endpoint}`;
        const formData = new URLSearchParams(data);

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData
            });

            const result = await response.json();

            if (!response.ok) {
                throw new ApiError(result.detail || 'An error occurred', response.status);
            }

            return result;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError('Network error. Please check your connection.', 0);
        }
    }
}

// Custom API Error
class ApiError extends Error {
    constructor(message, status) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
    }
}

// API Methods organized by resource

const api = new ApiService();

// Auth API
const authApi = {
    async register(email, password) {
        return api.post('/auth/register', { email, password });
    },

    async login(email, password) {
        return api.postForm('/auth/login', { username: email, password });
    },

    async getCurrentUser() {
        return api.get('/me');
    }
};

// Notes/Posts API
const postsApi = {
    async getAll() {
        return api.get('/notes');
    },

    async getById(id) {
        return api.get(`/notes/${id}`);
    },

    async create(title, content) {
        return api.post('/notes', { title, content });
    },

    async update(id, title, content) {
        return api.put(`/notes/${id}`, { title, content });
    },

    async delete(id) {
        return api.delete(`/notes/${id}`);
    },

    async getVersions(id) {
        return api.get(`/notes/${id}/versions`);
    }
};

// Comments API
const commentsApi = {
    async getByNote(noteId) {
        return api.get(`/comments/note/${noteId}`);
    },

    async create(noteId, content, parentId = null) {
        return api.post('/comments', { note_id: noteId, content, parent_id: parentId });
    },

    async delete(commentId) {
        return api.delete(`/comments/${commentId}`);
    }
};

// Admin API
const adminApi = {
    async getUsers() {
        return api.get('/admin/users');
    },

    async deleteUser(email) {
        return api.delete(`/admin/users/${email}`);
    },

    async hideComment(commentId) {
        return api.put(`/admin/comments/${commentId}/hide`);
    },

    async lockComments(noteId) {
        return api.put(`/admin/notes/${noteId}/lock-comments`);
    }
};

// Export for use
window.api = api;
window.authApi = authApi;
window.postsApi = postsApi;
window.commentsApi = commentsApi;
window.adminApi = adminApi;
window.ApiError = ApiError;
