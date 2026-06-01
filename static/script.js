document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatContainer = document.getElementById('chat-container');

    // Scroll to bottom of chat
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Add a message to the UI
    function appendMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        let avatarHTML = '';
        if (sender === 'user') {
            avatarHTML = '<div class="avatar"><i class="ph ph-user"></i></div>';
        } else {
            avatarHTML = '<div class="avatar"><i class="ph ph-cpu"></i></div>';
        }

        // Simple markdown parsing for code blocks and newlines
        let formattedText = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        messageDiv.innerHTML = `
            ${avatarHTML}
            <div class="message-content">
                <p>${formattedText}</p>
            </div>
        `;
        
        chatContainer.appendChild(messageDiv);
        scrollToBottom();
        return messageDiv;
    }

    // Show typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message system-message typing-msg';
        typingDiv.innerHTML = `
            <div class="avatar"><i class="ph ph-cpu"></i></div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
            </div>
        `;
        chatContainer.appendChild(typingDiv);
        scrollToBottom();
        return typingDiv;
    }

    // Handle form submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;

        // Display user message
        appendMessage('user', message);
        userInput.value = '';
        
        // Show typing indicator
        const typingIndicator = showTypingIndicator();

        try {
            // Send request to backend API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            // Remove typing indicator
            typingIndicator.remove();

            if (response.ok) {
                appendMessage('system', data.result);
            } else {
                appendMessage('system', 'Error: ' + (data.error || 'Something went wrong.'));
            }

        } catch (error) {
            // Remove typing indicator
            typingIndicator.remove();
            appendMessage('system', 'Network Error: Could not connect to the agent.');
            console.error('Error:', error);
        }
    });
});
