/**
 * MeTTa Brain Chat Interface
 * Direct conversation with the MeTTa reasoning engine
 */

class MeTTaChat {
    constructor() {
        this.apiBase = '/api';
        this.debugMode = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.focusInput();
        console.log('🧠 MeTTa Brain Chat initialized');
    }

    setupEventListeners() {
        // Send message on button click
        document.getElementById('send-button').addEventListener('click', () => {
            this.sendMessage();
        });

        // Send message on Enter key
        document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Debug mode toggle
        document.getElementById('debug-mode').addEventListener('change', (e) => {
            this.debugMode = e.target.checked;
            const debugPanel = document.getElementById('debug-panel');
            if (this.debugMode) {
                debugPanel.classList.add('active');
            } else {
                debugPanel.classList.remove('active');
            }
        });

        // Close debug panel
        document.getElementById('close-debug').addEventListener('click', () => {
            document.getElementById('debug-panel').classList.remove('active');
            document.getElementById('debug-mode').checked = false;
            this.debugMode = false;
        });

        // Clear chat
        document.getElementById('clear-chat').addEventListener('click', () => {
            this.clearChat();
        });
    }

    focusInput() {
        document.getElementById('chat-input').focus();
    }

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();

        if (!message) return;

        // Clear input and disable send button
        input.value = '';
        this.setSendButtonState(false);

        // Add user message to chat
        this.addMessage(message, 'user');

        // Show loading
        this.showLoading();

        try {
            // Send to MeTTa brain
            const response = await this.askMeTTaBrain(message);
            
            // Hide loading
            this.hideLoading();

            if (response.success) {
                // Add bot response
                this.addMessage(response.natural_answer || response.processed_result, 'bot');

                // Show debug output if enabled
                if (this.debugMode && response.raw_result) {
                    this.updateDebugPanel(response);
                    this.addDebugToMessage(response);
                }
            } else {
                this.addMessage(`❌ Error: ${response.error}`, 'bot');
            }

        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Connection error: ${error.message}`, 'bot');
        }

        // Re-enable send button and focus input
        this.setSendButtonState(true);
        this.focusInput();
    }

    async askMeTTaBrain(question) {
        const response = await fetch(`${this.apiBase}/ask-metta`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });

        return await response.json();
    }

    addMessage(text, sender) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-brain"></i>';

        const content = document.createElement('div');
        content.className = 'message-content';

        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.innerHTML = this.formatMessage(text);

        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = new Date().toLocaleTimeString();

        content.appendChild(messageText);
        content.appendChild(messageTime);

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    addDebugToMessage(response) {
        const messagesContainer = document.getElementById('chat-messages');
        const lastMessage = messagesContainer.lastElementChild;
        const messageText = lastMessage.querySelector('.message-text');

        const debugOutput = document.createElement('div');
        debugOutput.className = 'debug-output';
        debugOutput.innerHTML = `
            <span class="debug-label">🔍 MeTTa Query:</span>
            ${this.escapeHtml(response.query || 'N/A')}
            
            <span class="debug-label">🧠 Raw MeTTa Result:</span>
            ${this.escapeHtml(response.raw_result || 'N/A')}
        `;

        messageText.appendChild(debugOutput);
    }

    updateDebugPanel(response) {
        const debugContent = document.getElementById('debug-content');
        const timestamp = new Date().toLocaleTimeString();
        
        const debugEntry = document.createElement('div');
        debugEntry.innerHTML = `
            <div style="color: #ffff00; margin-bottom: 0.5rem;">[${timestamp}] New Query</div>
            <div style="color: #00ffff;">Query: ${this.escapeHtml(response.query || 'N/A')}</div>
            <div style="color: #00ff00; margin-top: 0.5rem;">Raw Result:</div>
            <div style="margin-left: 1rem; color: #90ee90;">${this.escapeHtml(response.raw_result || 'N/A')}</div>
            <div style="color: #ffa500; margin-top: 0.5rem;">Processed:</div>
            <div style="margin-left: 1rem; color: #ffb347;">${this.escapeHtml(response.processed_result || 'N/A')}</div>
            <hr style="border-color: #333; margin: 1rem 0;">
        `;

        debugContent.appendChild(debugEntry);
        debugContent.scrollTop = debugContent.scrollHeight;
    }

    formatMessage(text) {
        // Convert markdown-like formatting
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        text = text.replace(/`(.*?)`/g, '<code>$1</code>');
        
        // Convert newlines to breaks
        text = text.replace(/\n/g, '<br>');
        
        return text;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    setSendButtonState(enabled) {
        const sendButton = document.getElementById('send-button');
        sendButton.disabled = !enabled;
    }

    showLoading() {
        document.getElementById('loading-overlay').classList.add('active');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.remove('active');
    }

    clearChat() {
        const messagesContainer = document.getElementById('chat-messages');
        // Keep only the welcome message
        const welcomeMessage = messagesContainer.querySelector('.welcome-message');
        messagesContainer.innerHTML = '';
        if (welcomeMessage) {
            messagesContainer.appendChild(welcomeMessage);
        }

        // Clear debug panel
        const debugContent = document.getElementById('debug-content');
        debugContent.innerHTML = '<p class="debug-placeholder">Enable debug mode and ask a question to see raw MeTTa output...</p>';

        this.showToast('Chat cleared', 'info');
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        document.getElementById('toast-container').appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Global function for question chips
function askQuestion(question) {
    const input = document.getElementById('chat-input');
    input.value = question;
    input.focus();
    
    // Trigger send
    if (window.mettaChat) {
        window.mettaChat.sendMessage();
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mettaChat = new MeTTaChat();
    
    console.log('🧠 MeTTa Brain Chat ready!');
    console.log('💡 Try asking: "What is the next task?" or "Show all tasks"');
});

// Add some helpful styles dynamically
const additionalStyles = `
    .toast {
        position: fixed;
        top: 2rem;
        right: 2rem;
        padding: 1rem 1.5rem;
        border-radius: var(--radius-lg);
        color: white;
        font-weight: 500;
        box-shadow: var(--shadow-lg);
        transform: translateX(100%);
        transition: transform 0.3s ease;
        z-index: 1001;
    }
    
    .toast.show {
        transform: translateX(0);
    }
    
    .toast.info {
        background: var(--primary-color);
    }
    
    .toast.success {
        background: var(--success-color);
    }
    
    .toast.error {
        background: var(--error-color);
    }
`;

const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);
