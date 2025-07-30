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


    document.getElementById('gigForm').addEventListener('submit', function(e) {
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

    // Initialize real-time chat if available
    if (document.getElementById('chat-container')) {
        initializeChat();
    }

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
});

function initializeChat() {
    const chatContainer = document.getElementById('chat-container');
    const gigId = chatContainer.dataset.gigId;
    const userId = chatContainer.dataset.userId;
    const messagesContainer = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    
    // Determine WebSocket protocol (ws:// or wss://)
    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const chatSocket = new WebSocket(
        `${wsProtocol}${window.location.host}/ws/chat/${gigId}/`
    );

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const isSender = data.username === chatContainer.dataset.username;
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${isSender ? 'sent' : 'received'}`;
        messageElement.innerHTML = `
            <div class="message-header">
                <span class="sender">${data.username}</span>
                <span class="timestamp">${new Date(data.timestamp).toLocaleTimeString()}</span>
            </div>
            <p>${data.message}</p>
        `;
        
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    };

    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
        // Show reconnect button or attempt to reconnect
        showReconnectButton();
    };

    chatSocket.onerror = function(e) {
        console.error('WebSocket error:', e);
    };

    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const messageInput = this.querySelector('input[name="message"]');
        const message = messageInput.value.trim();
        
        if (message && chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify({
                'message': message
            }));
            messageInput.value = '';
        } else if (!chatSocket.OPEN) {
            showReconnectButton();
        }
    });

    function showReconnectButton() {
        const reconnectBtn = document.createElement('button');
        reconnectBtn.className = 'btn-reconnect';
        reconnectBtn.textContent = 'Reconnect Chat';
        reconnectBtn.addEventListener('click', function() {
            this.remove();
            initializeChat();
        });
        chatContainer.appendChild(reconnectBtn);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Search and filter functionality
    const gigSearch = document.getElementById('gig-search');
    const categoryFilter = document.getElementById('category-filter');
    const gigCards = document.querySelectorAll('.gig-card');

    function filterGigs() {
        const searchTerm = gigSearch.value.toLowerCase();
        const category = categoryFilter.value.toLowerCase();

        gigCards.forEach(card => {
            const title = card.querySelector('h3').textContent.toLowerCase();
            const description = card.querySelector('.gig-description').textContent.toLowerCase();
            const cardCategory = card.dataset.category;

            const matchesSearch = title.includes(searchTerm) || description.includes(searchTerm);
            const matchesCategory = category === '' || cardCategory === category;

            if (matchesSearch && matchesCategory) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    gigSearch.addEventListener('input', filterGigs);
    categoryFilter.addEventListener('change', filterGigs);

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