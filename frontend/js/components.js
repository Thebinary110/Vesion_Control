/**
 * UI Components
 * Reusable UI component generators
 */

class Components {

    // Post Card Component
    static createPostCard(post, onClick) {
        return window.utils.createElement('article', 'post-card animate-fadeInUp', { onclick: () => onClick(post) },
            window.utils.createElement('div', 'post-card-image', {},
                window.utils.createElement('img', '', { 
                    src: `https://picsum.photos/seed/${post.id}/800/450`, // Placeholder image
                    alt: post.title,
                    loading: 'lazy'
                })
            ),
            window.utils.createElement('div', 'post-card-content', {},
                window.utils.createElement('div', 'post-card-category', {}, 'Blog'),
                window.utils.createElement('h3', 'post-card-title', {}, post.title),
                window.utils.createElement('p', 'post-card-excerpt', {}, 
                    post.content.length > 100 ? post.content.substring(0, 100) + '...' : post.content
                ),
                window.utils.createElement('div', 'post-card-footer', {},
                    window.utils.createElement('div', 'post-card-author', {},
                        window.utils.createElement('div', 'avatar avatar-xs', {}, 
                            window.utils.createElement('img', '', { src: utils.getAvatarUrl(post.owner_id) })
                        ),
                        window.utils.createElement('span', 'post-card-author-name', {}, `User ${post.owner_id}`)
                    ),
                    window.utils.createElement('span', 'post-card-date', {}, utils.timeAgo(post.created_at || new Date()))
                )
            )
        );
    }

    // Comment Component
    static createComment(comment, isOwner, onDelete) {
        return window.utils.createElement('div', 'comment animate-fadeIn', { id: `comment-${comment.id}` },
            window.utils.createElement('div', 'avatar avatar-sm', {},
                window.utils.createElement('img', '', { src: utils.getAvatarUrl(comment.user_id) })
            ),
            window.utils.createElement('div', 'comment-body', {},
                window.utils.createElement('div', 'comment-header', {},
                    window.utils.createElement('span', 'comment-author', {}, `User ${comment.user_id}`),
                    window.utils.createElement('span', 'comment-time', {}, utils.timeAgo(comment.created_at))
                ),
                window.utils.createElement('div', 'comment-content', {}, comment.content),
                window.utils.createElement('div', 'comment-actions', {},
                    window.utils.createElement('button', 'comment-action', {}, 'Reply'),
                    isOwner ? window.utils.createElement('button', 'comment-action hover-shake', { onclick: () => onDelete(comment.id) }, 'Delete') : null
                )
            )
        );
    }

    // Render Comments List
    static renderCommentsList(comments, currentUserId, onDelete) {
        const list = document.createElement('div');
        list.className = 'comment-list';

        if (comments.length === 0) {
            list.appendChild(
                window.utils.createElement('div', 'empty-state', {},
                    window.utils.createElement('div', 'text-muted', {}, 'No comments yet. Be the first to share your thoughts!')
                )
            );
            return list;
        }

        comments.forEach(comment => {
            const isOwner = currentUserId === comment.user_id;
            list.appendChild(this.createComment(comment, isOwner, onDelete));
        });

        return list;
    }

    // Modal Component
    static createModal(title, contentElement, onClose) {
        const backdrop = window.utils.createElement('div', 'modal-backdrop active', { onclick: (e) => {
            if (e.target === backdrop) onClose();
        }});

        const modal = window.utils.createElement('div', 'modal active animate-scaleIn', {},
            window.utils.createElement('div', 'modal-header', {},
                window.utils.createElement('h3', '', {}, title),
                window.utils.createElement('button', 'btn-ghost btn-icon', { onclick: onClose }, '✕')
            ),
            window.utils.createElement('div', 'modal-body', {}, contentElement)
        );

        backdrop.appendChild(modal);
        return backdrop;
    }

    // Reaction Button
    static createReactionBtn(type, count, active, onClick) {
        const icons = {
            like: '👍',
            love: '❤️',
            fire: '🔥',
            think: '🤔',
            sad: '😢'
        };

        return window.utils.createElement('button', `reaction-btn reaction-btn--${type} ${active ? 'active' : ''}`, 
            { onclick: onClick, title: type },
            icons[type]
        );
    }
}

window.Components = Components;
