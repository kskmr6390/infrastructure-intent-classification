// Intent Classification Chat Application

let currentSessionId = null;
let feedbackData = {};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadSessions();
    autoResizeTextarea();
});

// Auto-resize textarea
function autoResizeTextarea() {
    const textarea = document.getElementById('messageInput');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
}

// Toggle sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}

// Load all sessions
async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        const data = await response.json();
        
        if (data.success) {
            displaySessions(data.sessions);
        } else {
            showError('Failed to load sessions');
        }
    } catch (error) {
        console.error('Error loading sessions:', error);
        showError('Error loading sessions');
    }
}

// Display sessions in sidebar
function displaySessions(sessions) {
    const container = document.getElementById('sessionsContainer');
    
    if (sessions.length === 0) {
        container.innerHTML = '<div class="loading">No sessions yet. Create one to start!</div>';
        return;
    }
    
    container.innerHTML = sessions.map(session => `
        <div class="session-item ${session.session_id === currentSessionId ? 'active' : ''}" 
             onclick="loadSession('${session.session_id}')">
            <div class="session-info">
                <div class="session-name">${escapeHtml(session.session_name)}</div>
                <div class="session-meta">
                    ${session.message_count || 0} messages • ${formatDate(session.updated_at)}
                </div>
            </div>
            <div class="session-actions">
                <button class="btn-icon" onclick="event.stopPropagation(); deleteSession('${session.session_id}')" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// Create new session
async function createNewSession() {
    try {
        const response = await fetch('/api/sessions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_name: `Chat ${new Date().toLocaleString()}`
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            await loadSessions();
            loadSession(data.session.session_id);
        } else {
            showError('Failed to create session');
        }
    } catch (error) {
        console.error('Error creating session:', error);
        showError('Error creating session');
    }
}

// Load specific session
async function loadSession(sessionId) {
    try {
        const response = await fetch(`/api/sessions/${sessionId}`);
        const data = await response.json();
        
        if (data.success) {
            currentSessionId = sessionId;
            document.getElementById('sessionTitle').textContent = data.session.session_name;
            displayMessages(data.messages);
            loadSessions(); // Refresh sidebar
        } else {
            showError('Failed to load session');
        }
    } catch (error) {
        console.error('Error loading session:', error);
        showError('Error loading session');
    }
}

// Display messages
function displayMessages(messages) {
    const container = document.getElementById('messagesContainer');
    
    if (messages.length === 0) {
        container.innerHTML = `
            <div class="welcome-screen">
                <div class="welcome-icon">
                    <i class="fas fa-robot"></i>
                </div>
                <h1>Start a Conversation</h1>
                <p>Ask me about network infrastructure queries!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = messages.map(msg => {
        if (msg.role === 'user') {
            return `
                <div class="message user">
                    <div class="message-header">
                        <div class="message-avatar">
                            <i class="fas fa-user"></i>
                        </div>
                        <div class="message-sender">You</div>
                    </div>
                    <div class="message-content">${escapeHtml(msg.content)}</div>
                    <div class="message-footer">
                        <span class="message-time">${formatTime(msg.timestamp)}</span>
                    </div>
                </div>
            `;
        } else {
            const confidenceClass = getConfidenceClass(msg.confidence);
            return `
                <div class="message assistant">
                    <div class="message-header">
                        <div class="message-avatar">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="message-sender">Assistant</div>
                    </div>
                    <div class="message-content">${formatMessage(msg.content)}</div>
                    <div class="message-footer">
                        <span class="message-time">${formatTime(msg.timestamp)}</span>
                        ${msg.confidence ? `<span class="confidence-badge ${confidenceClass}">${(msg.confidence * 100).toFixed(1)}%</span>` : ''}
                        ${msg.is_uncertain ? '<button class="btn-feedback" onclick="openFeedbackModal(' + msg.message_id + ', \'' + escapeHtml(getPreviousUserMessage(msg.message_id)) + '\', \'' + escapeHtml(msg.predicted_intent) + '\', ' + msg.confidence + ')"><i class="fas fa-comment"></i> Provide Feedback</button>' : ''}
                    </div>
                </div>
            `;
        }
    }).join('');
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

// Get confidence class
function getConfidenceClass(confidence) {
    if (!confidence) return 'confidence-medium';
    if (confidence >= 0.85) return 'confidence-high';
    if (confidence >= 0.7) return 'confidence-medium';
    return 'confidence-low';
}

// Format message content (convert markdown-style to HTML)
function formatMessage(content) {
    content = escapeHtml(content);
    content = content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    content = content.replace(/\n/g, '<br>');
    return content;
}

// Send message
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    if (!currentSessionId) {
        showError('Please create or select a session first');
        return;
    }
    
    // Disable input
    input.disabled = true;
    document.getElementById('sendButton').disabled = true;
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: message
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            input.value = '';
            input.style.height = 'auto';
            loadSession(currentSessionId);
        } else {
            showError(data.error || 'Failed to send message');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        showError('Error sending message');
    } finally {
        input.disabled = false;
        document.getElementById('sendButton').disabled = false;
        input.focus();
    }
}

// Handle keyboard events
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Send example query
function sendExampleQuery(element) {
    const query = element.textContent.trim();
    document.getElementById('messageInput').value = query;
    
    if (!currentSessionId) {
        createNewSession().then(() => {
            setTimeout(() => sendMessage(), 500);
        });
    } else {
        sendMessage();
    }
}

// Delete session
async function deleteSession(sessionId) {
    if (!confirm('Are you sure you want to delete this session?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/sessions/${sessionId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (currentSessionId === sessionId) {
                currentSessionId = null;
                document.getElementById('messagesContainer').innerHTML = `
                    <div class="welcome-screen">
                        <div class="welcome-icon">
                            <i class="fas fa-robot"></i>
                        </div>
                        <h1>Session Deleted</h1>
                        <p>Create a new session to continue</p>
                    </div>
                `;
                document.getElementById('sessionTitle').textContent = 'Select or create a session';
            }
            loadSessions();
        } else {
            showError('Failed to delete session');
        }
    } catch (error) {
        console.error('Error deleting session:', error);
        showError('Error deleting session');
    }
}

// Show session options
function showSessionOptions() {
    if (!currentSessionId) {
        showError('No session selected');
        return;
    }
    
    const newName = prompt('Enter new session name:');
    if (newName && newName.trim()) {
        updateSessionName(currentSessionId, newName.trim());
    }
}

// Update session name
async function updateSessionName(sessionId, newName) {
    try {
        const response = await fetch(`/api/sessions/${sessionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_name: newName
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('sessionTitle').textContent = newName;
            loadSessions();
        } else {
            showError('Failed to update session name');
        }
    } catch (error) {
        console.error('Error updating session:', error);
        showError('Error updating session');
    }
}

// Feedback modal
function openFeedbackModal(messageId, query, predictedIntent, confidence) {
    feedbackData = {
        message_id: messageId,
        query: query,
        predicted_intent: predictedIntent,
        confidence: confidence
    };
    
    document.getElementById('feedbackQuery').textContent = query;
    document.getElementById('feedbackPredicted').textContent = predictedIntent;
    document.getElementById('feedbackConfidence').textContent = (confidence * 100).toFixed(1) + '%';
    document.getElementById('correctIntent').value = '';
    
    document.getElementById('feedbackModal').classList.add('active');
}

function closeFeedbackModal() {
    document.getElementById('feedbackModal').classList.remove('active');
    feedbackData = {};
}

async function submitFeedback() {
    const correctIntent = document.getElementById('correctIntent').value.trim();
    
    if (!correctIntent) {
        alert('Please enter the correct intent');
        return;
    }
    
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message_id: feedbackData.message_id,
                session_id: currentSessionId,
                query: feedbackData.query,
                predicted_intent: feedbackData.predicted_intent,
                correct_intent: correctIntent,
                confidence: feedbackData.confidence
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            closeFeedbackModal();
            showSuccess('Feedback submitted successfully! Thank you for helping improve the model.');
        } else {
            showError('Failed to submit feedback');
        }
    } catch (error) {
        console.error('Error submitting feedback:', error);
        showError('Error submitting feedback');
    }
}

// Statistics modal
async function showStatistics() {
    document.getElementById('statisticsModal').classList.add('active');
    document.getElementById('statisticsContent').innerHTML = '<div class="loading">Loading statistics...</div>';
    
    try {
        const response = await fetch('/api/statistics');
        const data = await response.json();
        
        if (data.success) {
            displayStatistics(data.statistics);
        } else {
            document.getElementById('statisticsContent').innerHTML = '<div class="loading">Failed to load statistics</div>';
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
        document.getElementById('statisticsContent').innerHTML = '<div class="loading">Error loading statistics</div>';
    }
}

function displayStatistics(stats) {
    const feedbackStats = stats.feedback_stats || {};
    
    const html = `
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-label">Total Sessions</div>
                <div class="stat-value">${stats.total_sessions || 0}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Messages</div>
                <div class="stat-value">${stats.total_messages || 0}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Feedback Count</div>
                <div class="stat-value">${feedbackStats.total_feedback || 0}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Feedback Accuracy</div>
                <div class="stat-value">${((feedbackStats.accuracy || 0) * 100).toFixed(1)}%</div>
            </div>
        </div>
        
        ${feedbackStats.total_feedback > 0 ? `
            <div style="margin-top: 20px;">
                <h4>Feedback Details</h4>
                <p>Correct Predictions: ${feedbackStats.correct_predictions || 0}</p>
                <p>Incorrect Predictions: ${feedbackStats.incorrect_predictions || 0}</p>
                <p>Average Confidence: ${((feedbackStats.avg_confidence || 0) * 100).toFixed(1)}%</p>
            </div>
        ` : ''}
    `;
    
    document.getElementById('statisticsContent').innerHTML = html;
}

function closeStatisticsModal() {
    document.getElementById('statisticsModal').classList.remove('active');
}

// Utility functions
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function formatDate(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return Math.floor(diff / 60000) + ' min ago';
    if (diff < 86400000) return Math.floor(diff / 3600000) + ' hours ago';
    
    return date.toLocaleDateString();
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function getPreviousUserMessage(messageId) {
    // This is a simple implementation - in real scenario, you'd get this from the API
    return 'Query';
}

function showError(message) {
    alert('Error: ' + message);
}

function showSuccess(message) {
    alert(message);
}

// Close modals when clicking outside
window.onclick = function(event) {
    const feedbackModal = document.getElementById('feedbackModal');
    const statisticsModal = document.getElementById('statisticsModal');
    
    if (event.target === feedbackModal) {
        closeFeedbackModal();
    }
    if (event.target === statisticsModal) {
        closeStatisticsModal();
    }
}

