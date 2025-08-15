/**
 * Marketplace-specific JavaScript for GigGh
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize price range display
    const priceInputs = document.querySelectorAll('input[type="range"]');
    priceInputs.forEach(input => {
        const output = input.nextElementSibling;
        output.textContent = formatCurrency(input.value);
        
        input.addEventListener('input', function() {
            output.textContent = formatCurrency(this.value);
        });
    });

    // Gig image preview
    const gigImageInput = document.getElementById('id_image');
    if (gigImageInput) {
        const imagePreview = document.getElementById('image-preview');
        
        gigImageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                }
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    // Form validation
    document.getElementById('gigForm')?.addEventListener('submit', function(e) {
        const timelineType = document.getElementById('id_timeline_type').value;
        const startingPrice = parseFloat(document.getElementById('id_starting_price').value);
        const endingPrice = parseFloat(document.getElementById('id_ending_price').value);
        
        // Validate timeline
        if (timelineType === 'fixed_date') {
            const fixedDate = document.getElementById('id_timeline_fixed_date').value;
            if (!fixedDate) {
                alert('Please select a fixed date');
                e.preventDefault();
                return;
            }
        } else if (timelineType === 'duration') {
            const startDate = document.getElementById('id_timeline_duration_start').value;
            const endDate = document.getElementById('id_timeline_duration_end').value;
            if (!startDate || !endDate) {
                alert('Please select both start and end dates');
                e.preventDefault();
                return;
            }
        }
        
        // Validate prices
        if (endingPrice < startingPrice) {
            alert('Ending price must be greater than starting price');
            e.preventDefault();
        }
    });
    
    // Bid amount validation
    const bidForms = document.querySelectorAll('form[action*="bid"]');
    bidForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const amountInput = this.querySelector('input[name="amount"]');
            const minAmount = parseFloat(amountInput.dataset.min);
            
            if (parseFloat(amountInput.value) < minAmount) {
                e.preventDefault();
                alert(`Your bid must be at least ${formatCurrency(minAmount)}`);
                amountInput.focus();
            }
        });
    });

    // Submission file validation
    const submissionForms = document.querySelectorAll('form[action*="submit"]');
    submissionForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const fileInput = this.querySelector('input[type="file"]');
            const maxSize = 20 * 1024 * 1024; // 20MB
            
            if (fileInput.files[0] && fileInput.files[0].size > maxSize) {
                e.preventDefault();
                alert('File size must be less than 20MB');
            }
        });
    });

    initializeChat();
    setupChatForm();
    scrollToBottom();

    // Toggle bid details
    document.querySelectorAll('.bid-card').forEach(card => {
        const toggle = card.querySelector('.toggle-details');
        if (toggle) {
            toggle.addEventListener('click', function() {
                card.querySelector('.bid-details').classList.toggle('expanded');
                this.textContent = this.textContent === 'Show Details' ? 'Hide Details' : 'Show Details';
            });
        }
    });

    // Payment method toggle
    document.querySelectorAll('input[name="payment_method"]').forEach(radio => {
        radio.addEventListener('change', function() {
            document.querySelectorAll('.payment-details').forEach(el => {
                el.style.display = 'none';
            });
            document.getElementById(`${this.value}-details`).style.display = 'block';
        });
    });

    // Search and filter functionality
    const gigSearch = document.getElementById('gig-search');
    const categoryFilter = document.getElementById('category-filter');
    const gigCards = document.querySelectorAll('.gig-card');

    function filterGigs() {
        const searchTerm = gigSearch?.value.toLowerCase();
        const category = categoryFilter?.value.toLowerCase();

        gigCards.forEach(card => {
            const title = card.querySelector('h3').textContent.toLowerCase();
            const description = card.querySelector('.gig-description').textContent.toLowerCase();
            const cardCategory = card.dataset.category;

            const matchesSearch = !searchTerm || title.includes(searchTerm) || description.includes(searchTerm);
            const matchesCategory = !category || category === '' || cardCategory === category;

            if (matchesSearch && matchesCategory) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    gigSearch?.addEventListener('input', filterGigs);
    categoryFilter?.addEventListener('change', filterGigs);

    // Animation for how-it-works steps
    const steps = document.querySelectorAll('.step');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = 1;
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    steps.forEach(step => {
        step.style.opacity = 0;
        step.style.transform = 'translateY(20px)';
        step.style.transition = 'all 0.5s ease';
        observer.observe(step);
    });
});

/**
 * Initialize real-time chat functionality
 */
let chatSocket = null;

function initializeChat() {
    const chatContainer = document.getElementById('chat-container');
    if (!chatContainer) {
        console.error('Chat container not found');
        return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const gigId = chatContainer.dataset.gigId;
    
    // Close existing connection if any
    if (chatSocket) {
        chatSocket.close();
    }

    chatSocket = new WebSocket(
        `${protocol}${window.location.host}/ws/chat/${gigId}/`
    );

    chatSocket.onopen = function() {
        console.log('WebSocket connected');
    };

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log("Received message data:", data);  // Debug
        
        if (data.status === 'saved' && data.message_id) {
            // Replace optimistic update with confirmed message
            updateMessageId('temp-' + data.timestamp, data.message_id);
            console.log(`Message saved with ID: ${data.message_id}`);
        }
        else if (data.message) {
            addMessageToChat(
                data.message,
                data.sender === chatContainer.dataset.currentUser,
                data.timestamp,
                data.message_id
            );
        }
    };

    chatSocket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };

    chatSocket.onclose = function() {
        console.log('WebSocket disconnected');
    };

    function updateMessageId(tempId, permanentId) {
        const messageElement = document.querySelector(`[data-message-id="${tempId}"]`);
        if (messageElement) {
            messageElement.dataset.messageId = permanentId;
            console.log(`Updated message ID from ${tempId} to ${permanentId}`);
        }
    }
}

function setupChatForm() {
    const chatForm = document.getElementById('chat-form');
    if (!chatForm) return;

    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        
        const messageInput = this.querySelector('input[name="message"]');
        const message = messageInput.value.trim();
        const chatContainer = document.getElementById('chat-container');
        
        if (!message || !chatSocket) return;

        // Add optimistic update with temporary ID
        const tempId = 'temp-' + Date.now();
        addMessageToChat(
            message,
            true,
            new Date().toISOString(),
            tempId
        );

        try {
            chatSocket.send(JSON.stringify({
                'message': message,
                'sender': chatContainer.dataset.currentUser,
                'recipient': chatContainer.dataset.recipient,
                'gig_id': chatContainer.dataset.gigId
            }));
            messageInput.value = '';
        } catch (error) {
            console.error('Error sending message:', error);
            removeMessage(tempId); // Remove optimistic update if failed
        }
    });
}

function sendChatMessage() {
    const chatForm = document.getElementById('chat-form');
    const messageInput = chatForm.querySelector('input[name="message"]');
    const message = messageInput.value.trim();
    const chatContainer = document.getElementById('chat-container');
    
    if (!chatContainer) {
        console.error('Chat container not found!');
        return;
    }

    // Get gig_id from URL as fallback
    const pathParts = window.location.pathname.split('/');
    const gigIdFromUrl = pathParts[pathParts.length - 2]; // Assuming URL is /gigs/7/...

    const messageData = {
        'message': message,
        'sender': chatContainer.dataset.currentUser,
        'recipient': chatContainer.dataset.recipient,
        'gig_id': chatContainer.dataset.gigId || gigIdFromUrl // Primary + fallback
    };

    // Final validation
    if (!messageData.gig_id) {
        console.error('Missing gig_id! Available data:', {
            dataset: chatContainer.dataset,
            fromUrl: gigIdFromUrl
        });
        alert('System error: Missing gig information. Please refresh.');
        return;
    }

    console.log('Sending message with:', messageData)

    // Validate all fields
    const missingFields = Object.entries(messageData)
        .filter(([key, value]) => !value)
        .map(([key]) => key);

    if (missingFields.length > 0) {
        console.error('Missing required fields:', missingFields);
        alert(`Missing required data: ${missingFields.join(', ')}`);
        return;
    }

    // Add optimistic update
    const tempId = 'temp-' + Date.now();
    addMessageToChat(message, true, new Date().toISOString(), tempId);

    try {
        window.chatSocket.send(JSON.stringify(messageData));
        messageInput.value = '';
    } catch (error) {
        console.error('Error sending message:', error);
        removeMessage(tempId);
    }
}

function addMessageToChat(message, isSent, timestamp, messageId) {
    const messagesContainer = document.getElementById('chat-messages');
    if (!messagesContainer) return;

    const messageElement = document.createElement('div');
    messageElement.className = `message ${isSent ? 'sent' : 'received'}`;
    messageElement.dataset.messageId = messageId;
    messageElement.innerHTML = `
        <div class="message-content">
            <p>${message}</p>
            <span class="timestamp">${new Date(timestamp).toLocaleString()}</span>
        </div>
    `;
    messagesContainer.appendChild(messageElement);
    scrollToBottom();
}

function removeMessage(messageId) {
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
    if (messageElement) {
        messageElement.remove();
    }
}

function scrollToBottom() {
    const messagesContainer = document.getElementById('chat-messages');
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

/**
 * Format currency for display
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-GH', {
        style: 'currency',
        currency: 'GHS'
    }).format(amount);
}

// Add this as an alternative if you still have issues
document.getElementById('send-button')?.addEventListener('click', function() {
    const messageInput = document.querySelector('#chat-form input[name="message"]');
    const message = messageInput.value.trim();
    
    if (message && chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        const chatContainer = document.getElementById('chat-container');
        addMessageToChat(message, true, new Date().toISOString());
        
        chatSocket.send(JSON.stringify({
            'message': message,
            'sender': chatContainer.dataset.currentUser,
            'recipient': chatContainer.dataset.recipient
        }));
        
        messageInput.value = '';
    }
});