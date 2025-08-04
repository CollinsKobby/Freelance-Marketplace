// Handle chat functionality
document.addEventListener('DOMContentLoaded', function() {
    // Toggle chat visibility
    const chatToggle = document.getElementById('chat-toggle');
    const chatContainer = document.getElementById('chat-container');
    
    if (chatToggle && chatContainer) {
        chatToggle.addEventListener('click', function() {
            chatContainer.classList.toggle('active');
        });
    }
    
    // Close chat
    const closeChat = document.querySelector('.close-chat');
    if (closeChat) {
        closeChat.addEventListener('click', function() {
            chatContainer.classList.remove('active');
        });
    }
    
    // Chat form submission
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const messageInput = this.querySelector('input[name="message"]');
            const message = messageInput.value.trim();
            
            if (message) {
                // In a real app, this would send the message via AJAX
                console.log('Sending message:', message);
                
                // Add message to UI
                const messagesContainer = document.getElementById('chat-messages');
                const newMessage = document.createElement('div');
                newMessage.className = 'message sent';
                newMessage.innerHTML = `
                    <p>${message}</p>
                    <span class="timestamp">Just now</span>
                `;
                messagesContainer.appendChild(newMessage);
                
                // Clear input
                messageInput.value = '';
                
                // Scroll to bottom
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        });
    }
    
    // Handle bid form validation
    const bidForm = document.querySelector('form[action*="bid"]');
    if (bidForm) {
        bidForm.addEventListener('submit', function(e) {
            const amountInput = this.querySelector('input[name="amount"]');
            const amount = parseFloat(amountInput.value);
            const startingPrice = parseFloat(this.dataset.startingPrice);
            
            if (amount < startingPrice) {
                e.preventDefault();
                alert(`Your bid must be at least ${startingPrice}`);
            }
        });
    }
});
// Real-time chat updates with WebSocket
function setupChatWebSocket(gigId) {
    const chatSocket = new WebSocket(
        `ws://${window.location.host}/ws/chat/${gigId}/`
    );

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const messagesContainer = document.getElementById('chat-messages');
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${data.sender_id === {{ request.user.id }} ? 'sent' : 'received'}`;
        messageElement.innerHTML = `
            <p>${data.message}</p>
            <span class="timestamp">${new Date(data.timestamp).toLocaleTimeString()}</span>
        `;
        
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    };

    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };

    return chatSocket;
}

// Initialize WebSocket when chat is open
document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
        const gigId = chatContainer.dataset.gigId;
        const chatSocket = setupChatWebSocket(gigId);
        
        document.getElementById('chat-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const messageInput = this.querySelector('input[name="message"]');
            const message = messageInput.value.trim();
            
            if (message) {
                chatSocket.send(JSON.stringify({
                    'message': message
                }));
                messageInput.value = '';
            }
        });
    }
});

// File upload preview
document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener('change', function() {
        const preview = this.nextElementSibling;
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
            reader.readAsDataURL(this.files[0]);
        }
    });
});