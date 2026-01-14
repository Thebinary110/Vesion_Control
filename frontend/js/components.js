/**
 * UI Components
 * Reusable UI component generators
 */

const { createElement } = window.utils;

class Components {

    // Post Card Component
    static createPostCard(post, onClick) {
        return createElement('article', 'post-card animate-fadeInUp', { onclick: () => onClick(post) },
            createElement('div', 'post-card-image', {},
                createElement('img', '', { 
                    src: `https://picsum.photos/seed/${post.id}/800/450`, // Placeholder image
                    alt: post.title,
                    loading: 'lazy'
                })
            ),
            createElement('div', 'post-card-content', {},
                createElement('div', 'post-card-category', {}, 'Blog'),
                createElement('h3', 'post-card-title', {}, post.title),
                createElement('p', 'post-card-excerpt', {}, 
                    post.content.length > 100 ? post.content.substring(0, 100) + '...' : post.content
                ),
                createElement('div', 'post-card-footer', {},
                    createElement('div', 'post-card-author', {},
                        createElement('div', 'avatar avatar-xs', {}, 
                            createElement('img', '', { src: utils.getAvatarUrl(post.owner_id) }) // Assuming owner_id can be mapped
                        ),
                        createElement('span', 'post-card-author-name', {}, `User ${post.owner_id}`)
                    ),
                    createElement('span', 'post-card-date', {}, utils.timeAgo(post.created_at || new Date()))
                )
            )
        );
    }

    // Comment Component
    static createComment(comment, isOwner, onDelete) {
        return createElement('div', 'comment animate-fadeIn', { id: `comment-${comment.id}` },
            createElement('div', 'avatar avatar-sm', {},
                createElement('img', '', { src: utils.getAvatarUrl(comment.user_id) })
            ),
            createElement('div', 'comment-body', {},
                createElement('div', 'comment-header', {},
                    createElement('span', 'comment-author', {}, `User ${comment.user_id}`),
                    createElement('span', 'comment-time', {}, utils.timeAgo(comment.created_at))
                ),
                createElement('div', 'comment-content', {}, comment.content),
                createElement('div', 'comment-actions', {},
                    createElement('button', 'comment-action', {}, 'Reply'),
                    isOwner ? createElement('button', 'comment-action hover-shake', { onclick: () => onDelete(comment.id) }, 'Delete') : null
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
                createElement('div', 'empty-state', {},
                    createElement('div', 'text-muted', {}, 'No comments yet. Be the first to share your thoughts!')
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
        const backdrop = createElement('div', 'modal-backdrop active', { onclick: (e) => {
            if (e.target === backdrop) onClose();
        }});

        const modal = createElement('div', 'modal active animate-scaleIn', {},
            createElement('div', 'modal-header', {},
                createElement('h3', '', {}, title),
                createElement('button', 'btn-ghost btn-icon', { onclick: onClose }, '✕')
            ),
            createElement('div', 'modal-body', {}, contentElement)
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

        return createElement('button', `reaction-btn reaction-btn--${type} ${active ? 'active' : ''}`, 
            { onclick: onClick, title: type },
            icons[type]
        );
    }
}

window.Components = Components;
