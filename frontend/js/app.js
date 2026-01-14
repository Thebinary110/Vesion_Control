
class App {
    constructor() {
        this.currentView = null;
        this.views = {
            login: 'view-login',
            feed: 'view-feed',
            post: 'view-post',
            create: 'view-editor',
            admin: 'view-admin'
        };
        
        this.container = document.getElementById('main-content');
        this.navbar = document.getElementById('navbar');
    }

    async init() {
        // Initialize Theme
        utils.themeManager.init();
        document.getElementById('themeBtn').onclick = () => utils.themeManager.toggle();

        // Initialize Auth
        const isAuthenticated = await auth.init();
        
        // Setup Navigation
        this.setupNavigation();

        // Setup User Dropdown
        this.setupDropdown();

        if (isAuthenticated) {
            this.showNavbar(true);
            this.navigateTo('feed');
        } else {
            this.showNavbar(false);
            this.navigateTo('login');
        }

        // Listen for auth changes
        auth.onAuthChange((isAuth, user) => {
            if (isAuth) {
                this.showNavbar(true);
                this.updateUserUI(user);
                if (this.currentView === 'login') this.navigateTo('feed');
            } else {
                this.showNavbar(false);
                this.navigateTo('login');
            }
        });
    }

    setupNavigation() {
        document.querySelectorAll('[data-view]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = e.target.closest('[data-view]').dataset.view;
                this.navigateTo(view);
            });
        });

        // Global link handler for dynamic content
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[data-route]');
            if (link) {
                e.preventDefault();
                // Simple router logic: data-route="post:123"
                const [view, id] = link.dataset.route.split(':');
                this.navigateTo(view, id);
            }
        });
        
        // Logout handler
        document.querySelector('[data-action="logout"]').onclick = () => auth.logout();
        
        // Admin link visibility
        const adminLink = document.getElementById('adminLink');
        if (auth.isAdmin()) {
            adminLink.style.display = 'flex';
            adminLink.onclick = () => this.navigateTo('admin');
        }
    }

    setupDropdown() {
        const dropdown = document.getElementById('userDropdown');
        dropdown.addEventListener('click', () => {
            dropdown.classList.toggle('active');
        });
        
        // Close on click outside
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
            }
        });
    }

    showNavbar(show) {
        if (show) {
            this.navbar.classList.remove('hidden');
            this.updateUserUI(auth.getUser());
        } else {
            this.navbar.classList.add('hidden');
        }
    }

    updateUserUI(user) {
        if (!user) return;
        const navAvatar = document.getElementById('navAvatar');
        if (navAvatar) navAvatar.src = utils.getAvatarUrl(user.email);
        
        const adminLink = document.getElementById('adminLink');
        if (adminLink && user.role === 'admin') {
            adminLink.style.display = 'flex';
        }
    }

    async navigateTo(viewName, param = null) {
        this.currentView = viewName;
        
        // Update Active Link
        document.querySelectorAll('.navbar-link').forEach(link => {
            link.classList.toggle('active', link.dataset.view === viewName);
        });

        // Clear Container
        this.container.innerHTML = '';
        const loading = document.createElement('div');
        loading.className = 'loading-overlay';
        loading.innerHTML = '<div class="loading-spinner"></div>';
        this.container.appendChild(loading);

        // Get Template
        const templateId = this.views[viewName];
        if (!templateId) return; // 404
        
        const template = document.getElementById(templateId);
        const content = template.content.cloneNode(true);

        // Initialize View Logic
        try {
            switch (viewName) {
                case 'login':
                    this.initLoginView(content);
                    break;
                case 'feed':
                    await this.initFeedView(content);
                    break;
                case 'post':
                    await this.initPostView(content, param);
                    break;
                case 'create':
                    this.initEditorView(content);
                    break;
                case 'admin':
                    await this.initAdminView(content);
                    break;
            }
        } catch (error) {
            console.error('View Error:', error);
            utils.showToast('Error loading view', 'error');
        } finally {
            this.container.innerHTML = '';
            this.container.appendChild(content);
        }
    }

    /* === VIEW CONTROLLERS === */

    initLoginView(dom) {
        const form = dom.getElementById('authForm');
        const emailInput = dom.getElementById('email');
        const passwordInput = dom.getElementById('password');
        const tabs = dom.querySelectorAll('.tab');
        let mode = 'login'; // login or register

        tabs.forEach(tab => {
            tab.onclick = () => {
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                mode = tab.dataset.tab;
            };
        });

        form.onsubmit = async (e) => {
            e.preventDefault();
            const email = emailInput.value;
            const password = passwordInput.value;

            try {
                if (mode === 'login') {
                    await auth.login(email, password);
                } else {
                    await auth.register(email, password);
                    // Switch to login tab
                    tabs[0].click();
                }
            } catch (err) {
                // Error handled in auth
            }
        };
    }

    async initFeedView(dom) {
        const posts = await postsApi.getAll();
        const container = dom.querySelector('.page-feed');
        
        posts.forEach(post => {
            const card = Components.createPostCard(post, (p) => {
                this.navigateTo('post', p.id);
            });
            container.appendChild(card);
        });
        
        // Empty state
        if (posts.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="grid-column: 1/-1;">
                    <div class="empty-state-icon">📝</div>
                    <div class="empty-state-title">No posts yet</div>
                    <p class="empty-state-description">Be the first to share something with the world.</p>
                    <button class="btn btn-primary" onclick="app.navigateTo('create')">Create Post</button>
                </div>
            `;
        }
    }

    async initPostView(dom, postId) {
        // Fetch data in parallel
        const [post, comments] = await Promise.all([
            postsApi.getById(postId),
            commentsApi.getByNote(postId)
        ]);

        const user = auth.getUser();

        // Populate Post
        dom.getElementById('post-title').innerText = post.title;
        dom.getElementById('post-body').innerText = post.content;
        // Fallback since we don't have a markdown parser loaded yet, just text:
        // dom.getElementById('post-body').innerText = post.content;   
        
        dom.getElementById('post-hero-img').src = `https://picsum.photos/seed/${post.id}/1200/600`;
        dom.getElementById('post-author-name').innerText = `User ${post.owner_id}`;
        dom.getElementById('post-date').innerText = utils.formatDate(post.created_at);
        dom.getElementById('post-author-avatar').src = utils.getAvatarUrl(post.owner_id);

        // Populate Comments
        const commentsList = dom.getElementById('comments-list');
        const renderedComments = Components.renderCommentsList(comments, user?.id, async (id) => {
            if(confirm('Delete this comment?')) {
                await commentsApi.delete(id);
                this.navigateTo('post', postId); // Refresh
            }
        });
        commentsList.appendChild(renderedComments);

        // Comment Form
        const commentAvatar = dom.getElementById('comment-avatar');
        if (commentAvatar && user) commentAvatar.src = utils.getAvatarUrl(user.email);
        
        const commentInput = dom.getElementById('comment-input');
        
        dom.getElementById('post-comment-btn').onclick = async () => {
            const content = commentInput.value;
            if(!content.trim()) return;
            
            await commentsApi.create(postId, content);
            this.navigateTo('post', postId); // Refresh
        };
    }

    initEditorView(dom) {
        const titleInput = dom.getElementById('editor-title');
        const contentInput = dom.getElementById('editor-content');

        dom.getElementById('publish-btn').onclick = async () => {
            const title = titleInput.value;
            const content = contentInput.value;

            if(!title || !content) {
                utils.showToast('Please fill in both title and content', 'warning');
                return;
            }

            try {
                await postsApi.create(title, content);
                utils.showToast('Post published successfully!', 'success');
                this.navigateTo('feed');
            } catch (err) {
                utils.showToast(err.message, 'error');
            }
        };

        dom.getElementById('cancel-edit').onclick = () => {
            if(confirm('Discard changes?')) this.navigateTo('feed');
        };
    }

    async initAdminView(dom) {
        if (!auth.isAdmin()) {
            utils.showToast('Access Denied', 'error');
            this.navigateTo('feed');
            return;
        }

        const users = await adminApi.getUsers();
        dom.getElementById('admin-user-count').innerText = users.length;

        const table = dom.getElementById('admin-users-table');
        if (users.length === 0) {
            table.innerHTML = '<div class="p-4 text-center">No users found</div>';
        } else {
            const tbody = document.createElement('tbody');
            // Header
            const thead = document.createElement('thead');
            thead.innerHTML = `
                <tr>
                    <th>ID</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Joined</th>
                    <th>Actions</th>
                </tr>
            `;
            const tableEl = document.createElement('table');
            tableEl.appendChild(thead);
            
            users.forEach(u => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${u.id}</td>
                    <td>
                        <div class="flex items-center gap-sm">
                            <div class="avatar avatar-xs"><img src="${utils.getAvatarUrl(u.email)}"></div>
                            ${u.email}
                        </div>
                    </td>
                    <td><span class="badge ${u.role === 'admin' ? 'badge-admin' : 'badge-primary'}">${u.role}</span></td>
                    <td>${utils.formatDate(u.created_at || new Date())}</td>
                    <td>
                        <button class="btn btn-sm btn-danger delete-user-btn" data-email="${u.email}">Delete</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            tableEl.appendChild(tbody);
            table.innerHTML = '';
            table.appendChild(tableEl);

            // Bind delete events
            table.querySelectorAll('.delete-user-btn').forEach(btn => {
                btn.onclick = async () => {
                    const email = btn.dataset.email;
                    if(confirm(`Are you sure you want to delete user ${email}?`)) {
                        await adminApi.deleteUser(email);
                        this.navigateTo('admin'); // Refresh
                    }
                };
            });
        }
    }
}

// Initialize App on DOM Content Loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
    window.app.init();
});
