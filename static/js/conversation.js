document.getElementById('message-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const receiverId = document.getElementById('receiver_id').value;
    const content = document.getElementById('message-content').value.trim();
    
    if (!content) return;
    
    try {
        const response = await fetch('/messages/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                receiver_id: parseInt(receiverId),
                content: content
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Add message to conversation
            addMessageToConversation(content, 'sent');
            document.getElementById('message-content').value = '';
        } else {
            alert('Error sending message: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to send message');
    }
});

function addMessageToConversation(content, type) {
    const messagesList = document.getElementById('messages-list');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `
        <div class="message-content">${content}</div>
        <div class="message-time">Just now</div>
    `;
    messagesList.insertBefore(messageDiv, messagesList.firstChild);
}