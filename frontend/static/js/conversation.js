// SignBridge - Conversation History Manager

class ConversationManager {
    constructor(maxMessages = 50) {
        this.messages = [];
        this.maxMessages = maxMessages;
        this.container = null;
    }
    
    init(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('Conversation container not found');
            return false;
        }
        return true;
    }
    
    addMessage(sender, content, type = 'text') {
        const message = {
            id: Date.now(),
            sender: sender, // 'deaf' or 'hearing'
            content: content,
            type: type,
            timestamp: new Date()
        };
        
        this.messages.push(message);
        
        // Limit messages
        if (this.messages.length > this.maxMessages) {
            this.messages.shift();
        }
        
        this.render();
        this.scrollToBottom();
        
        return message;
    }
    
    render() {
        if (!this.container) return;
        
        // Clear empty state
        const emptyState = this.container.querySelector('.conversation-empty');
        if (emptyState) {
            emptyState.remove();
        }
        
        // Clear and render all messages
        this.container.innerHTML = '';
        
        this.messages.forEach(msg => {
            const messageEl = this.createMessageElement(msg);
            this.container.appendChild(messageEl);
        });
    }
    
    createMessageElement(message) {
        const div = document.createElement('div');
        div.className = `message ${message.sender}`;
        div.dataset.id = message.id;
        
        const icon = message.sender === 'deaf' ? '👋' : '🗣️';
        const senderLabel = message.sender === 'deaf' ? 'Deaf User' : 'Hearing User';
        
        div.innerHTML = `
            <div class="message-header">
                <span class="message-sender">
                    <span>${icon}</span>
                    ${senderLabel}
                </span>
                <span class="message-time">${SignBridge.formatTime(message.timestamp)}</span>
            </div>
            <div class="message-content">${this.escapeHtml(message.content)}</div>
        `;
        
        return div;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    scrollToBottom() {
        if (this.container) {
            this.container.scrollTop = this.container.scrollHeight;
        }
    }
    
    clear() {
        this.messages = [];
        if (this.container) {
            this.container.innerHTML = `
                <div class="conversation-empty">
                    <i class="fas fa-comments"></i>
                    <p>Start communicating to see conversation history</p>
                </div>
            `;
        }
    }
    
    save() {
        const text = this.messages.map(msg => {
            const time = SignBridge.formatTime(msg.timestamp);
            const sender = msg.sender === 'deaf' ? 'Deaf User' : 'Hearing User';
            return `[${time}] ${sender}: ${msg.content}`;
        }).join('\n');
        
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `signbridge-conversation-${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        SignBridge.showNotification('Conversation saved!', 'success');
    }
    
    getMessages() {
        return [...this.messages];
    }
}

// Make globally available
window.ConversationManager = ConversationManager;
