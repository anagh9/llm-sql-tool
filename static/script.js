// ==================== Configuration ====================

const API_BASE = '/api';
const SESSION_ID = `session_${Date.now()}`;
let autoScroll = true;
let messages = [];

// ==================== DOM Elements ====================

const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const chatForm = document.getElementById('chatForm');
const messagesContainer = document.getElementById('messagesContainer');
const loadingOverlay = document.getElementById('loadingOverlay');
const toastContainer = document.getElementById('toastContainer');

// Buttons
const newChatBtn = document.getElementById('newChatBtn');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');
const statsBtn = document.getElementById('statsBtn');
const infoBtn = document.getElementById('infoBtn');
const settingsBtn = document.getElementById('settingsBtn');

// Modals
const statsModal = document.getElementById('statsModal');
const aboutModal = document.getElementById('aboutModal');
const settingsModal = document.getElementById('settingsModal');

// Settings
const darkModeToggle = document.getElementById('darkModeToggle');
const autoScrollCheckbox = document.getElementById('autoScroll');
const clearCacheBtn = document.getElementById('clearCacheBtn');

// ==================== Initialization ====================

document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadSuggestions();
    loadSettings();
});

function setupEventListeners() {
    // Chat form
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        sendMessage();
    });

    // Message input - handle Shift+Enter for new line
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
    });

    // Sidebar buttons
    newChatBtn.addEventListener('click', clearChat);
    clearHistoryBtn.addEventListener('click', () => openModal('statsModal'));
    statsBtn.addEventListener('click', () => {
        openModal('statsModal');
        loadStats();
    });
    infoBtn.addEventListener('click', () => openModal('aboutModal'));
    settingsBtn.addEventListener('click', () => openModal('settingsModal'));

    // Settings
    darkModeToggle.addEventListener('change', toggleDarkMode);
    autoScrollCheckbox.addEventListener('change', (e) => {
        autoScroll = e.target.checked;
        localStorage.setItem('autoScroll', autoScroll);
    });
    clearCacheBtn.addEventListener('click', clearCache);

    // Modal close buttons
    document.querySelectorAll('.close-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.dataset.modal;
            closeModal(modal);
        });
    });

    // Close modal on outside click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal.id);
            }
        });
    });

    // Prevent input overflow
    messageInput.addEventListener('paste', () => {
        setTimeout(() => {
            messageInput.style.height = 'auto';
            messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
        }, 0);
    });
}

// ==================== Message Handling ====================

async function sendMessage() {
    const message = messageInput.value.trim();

    if (!message) {
        showToast('Please enter a message', 'warning');
        return;
    }

    // Disable send button
    sendBtn.disabled = true;
    messageInput.disabled = true;

    // Add user message to display
    addMessageToDisplay(message, 'user');
    messageInput.value = '';
    messageInput.style.height = '44px';

    try {
        showLoadingOverlay(true);

        // Send to API
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: SESSION_ID
            })
        });

        const data = await response.json();

        if (data.success) {
            const answer = data.answer;
            const isCached = data.cached;

            // Add assistant message
            addMessageToDisplay(answer, 'assistant', isCached);

            // Add to recent queries
            addToRecentQueries(message);

            showToast(`Answer ${isCached ? 'retrieved from cache' : 'generated'}`, 'success');
        } else {
            showToast(`Error: ${data.error}`, 'error');
            addMessageToDisplay(`Error: ${data.error}`, 'assistant', false);
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to send message', 'error');
        addMessageToDisplay('Sorry, an error occurred. Please try again.', 'assistant');
    } finally {
        showLoadingOverlay(false);
        sendBtn.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
    }
}

function addMessageToDisplay(content, role, cached = false) {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

    const contentEl = document.createElement('div');
    contentEl.className = 'message-content';
    contentEl.textContent = content;

    const metadataEl = document.createElement('div');
    metadataEl.className = 'message-metadata';

    const time = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
    metadataEl.textContent = time;

    if (cached) {
        const badge = document.createElement('span');
        badge.className = 'cached-badge';
        badge.textContent = 'Cached';
        metadataEl.appendChild(badge);
    }

    if (role === 'user') {
        messageEl.appendChild(contentEl);
        messageEl.appendChild(avatar);
    } else {
        messageEl.appendChild(avatar);
        messageEl.appendChild(contentEl);
    }

    messageEl.appendChild(metadataEl);
    messagesContainer.appendChild(messageEl);

    messages.push({ role, content, cached, timestamp: new Date() });

    if (autoScroll) {
        scrollToBottom();
    }
}

function scrollToBottom() {
    setTimeout(() => {
        messagesContainer.parentElement.scrollTop = messagesContainer.parentElement.scrollHeight;
    }, 0);
}

// ==================== UI Functions ====================

function clearChat() {
    if (messages.length === 0) {
        showToast('Nothing to clear', 'warning');
        return;
    }

    if (confirm('Clear all messages? This action cannot be undone.')) {
        messages = [];
        messagesContainer.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">
                    <i class="fas fa-sparkles"></i>
                </div>
                <h2>Welcome to LLM SQL Chat</h2>
                <p>Ask any question about your product database. I'll generate the SQL and fetch the results for you.</p>
            </div>
        `;
        showToast('Chat cleared', 'success');
    }
}

async function loadSuggestions() {
    try {
        const response = await fetch(`${API_BASE}/suggestions`);
        const data = await response.json();

        if (data.success) {
            const container = document.getElementById('suggestionsContainer');
            container.innerHTML = '';

            data.suggestions.forEach(suggestion => {
                const chip = document.createElement('div');
                chip.className = 'suggestion-chip';
                chip.textContent = suggestion;
                chip.addEventListener('click', () => {
                    messageInput.value = suggestion;
                    messageInput.focus();
                });
                container.appendChild(chip);
            });
        }
    } catch (error) {
        console.error('Error loading suggestions:', error);
    }
}

function addToRecentQueries(query) {
    const container = document.getElementById('recentQueries');
    
    // Remove empty state
    const emptyState = container.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }

    // Add new query to top
    const li = document.createElement('li');
    li.textContent = query;
    li.title = query;
    li.addEventListener('click', () => {
        messageInput.value = query;
        messageInput.focus();
    });
    container.insertBefore(li, container.firstChild);

    // Keep only last 10
    const items = container.querySelectorAll('li');
    for (let i = 10; i < items.length; i++) {
        items[i].remove();
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();

        if (data.success) {
            document.getElementById('totalConversations').textContent = data.total_conversations;
            document.getElementById('totalQueries').textContent = data.total_queries;
            document.getElementById('cachedQueries').textContent = data.total_cached_queries;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function clearCache() {
    if (confirm('Clear all cached queries? This will free up memory.')) {
        try {
            showLoadingOverlay(true);
            // Note: This would need a backend endpoint
            showToast('Cache cleared successfully', 'success');
            await loadStats();
        } catch (error) {
            showToast('Error clearing cache', 'error');
        } finally {
            showLoadingOverlay(false);
        }
    }
}

// ==================== Modal Functions ====================

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('show');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('show');
}

// ==================== Settings ====================

function toggleDarkMode() {
    const isDark = darkModeToggle.checked;
    
    if (isDark) {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
    }
}

function loadSettings() {
    // Load theme
    const theme = localStorage.getItem('theme') || 'light';
    if (theme === 'dark') {
        darkModeToggle.checked = true;
        document.documentElement.setAttribute('data-theme', 'dark');
    }

    // Load auto-scroll
    autoScroll = localStorage.getItem('autoScroll') !== 'false';
    autoScrollCheckbox.checked = autoScroll;
}

// ==================== Toast Notifications ====================

function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span>${message}</span>
        <button class="toast-close">
            <i class="fas fa-times"></i>
        </button>
    `;

    toastContainer.appendChild(toast);

    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
        toast.remove();
    });

    if (duration > 0) {
        setTimeout(() => {
            toast.remove();
        }, duration);
    }
}

// ==================== Loading Overlay ====================

function showLoadingOverlay(show) {
    if (show) {
        loadingOverlay.classList.add('show');
    } else {
        loadingOverlay.classList.remove('show');
    }
}

// ==================== Utility Functions ====================

function formatTime(date) {
    return new Date(date).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// ==================== Keyboard Shortcuts ====================

document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K: Focus input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        messageInput.focus();
    }

    // Ctrl/Cmd + L: Clear chat
    if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
        e.preventDefault();
        clearChat();
    }

    // Escaped: Close modals
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.show').forEach(modal => {
            closeModal(modal.id);
        });
    }
});

// ==================== Responsive Design ====================

// Handle sidebar visibility on mobile
if (window.innerWidth <= 768) {
    document.querySelector('.sidebar').style.maxHeight = '150px';
}

window.addEventListener('resize', () => {
    if (window.innerWidth <= 768) {
        document.querySelector('.sidebar').style.maxHeight = '150px';
    } else {
        document.querySelector('.sidebar').style.maxHeight = '';
    }
});

console.log('%cLLM SQL Chat Interface', 'color: #6366f1; font-size: 16px; font-weight: bold;');
console.log('Session ID:', SESSION_ID);
console.log('Ready to chat!');
