// ============================================
// AI STUDENT CHATBOT - MAIN JAVASCRIPT
// ============================================

// DOM Elements
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const themeToggle = document.getElementById('themeToggle');
const voiceBtn = document.getElementById('voiceBtn');
const uploadBtn = document.getElementById('uploadBtn');
const historyBtn = document.getElementById('historyBtn');
const quickActions = document.getElementById('quickActions');
const suggestionsList = document.getElementById('suggestionsList');

// Analytics Elements
const statTotalQueries = document.getElementById('statTotalQueries');
const statActiveUsers = document.getElementById('statActiveUsers');
const statAccuracy = document.getElementById('statAccuracy');
const statRecentActivity = document.getElementById('statRecentActivity');
const statTodayActivity = document.getElementById('statTodayActivity');
const statSuccessRate = document.getElementById('statSuccessRate');
const statAvgConfidence = document.getElementById('statAvgConfidence');
const lastUpdated = document.getElementById('lastUpdated');

// State Management
let sessionId = localStorage.getItem('sessionId') || generateSessionId();
let conversationHistory = JSON.parse(localStorage.getItem('conversationHistory') || '[]');
let isRecording = false;
let currentTheme = localStorage.getItem('theme') || 'light';
let analyticsData = null;

// Markdown parser
const md = window.markdownit({
    html: true,
    breaks: true,
    linkify: true,
    typographer: true,
    highlight: function (str, lang) {
        return '<pre><code class="language-' + lang + '">' + md.utils.escapeHtml(str) + '</code></pre>';
    }
});

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    console.log('🤖 AI Student Assistant Initializing...');
    
    // Set theme
    applyTheme(currentTheme);
    
    // Load initial data
    loadQuickActions();
    loadSuggestions();
    updateStatistics(true); // Initial load
    
    // Set up event listeners
    setupEventListeners();
    
    // Show welcome message
    showWelcomeMessage();
    
    // Load conversation history if exists
    if (conversationHistory.length > 0) {
        console.log(`📚 Loaded ${conversationHistory.length} previous conversations`);
    }
    
    // Auto-refresh statistics every 30 seconds
    setInterval(() => updateStatistics(false), 30000);
    
    console.log('✅ Application initialized successfully');
});

// ============================================
// CORE FUNCTIONS
// ============================================

function generateSessionId() {
    const id = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('sessionId', id);
    return id;
}

function setupEventListeners() {
    // Send message on Enter key
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Send button click
    sendBtn.addEventListener('click', sendMessage);
    
    // Theme toggle
    themeToggle.addEventListener('click', toggleTheme);
    
    // Voice button
    voiceBtn.addEventListener('click', showVoiceModal);
    
    // Upload button
    uploadBtn.addEventListener('click', () => {
        showNotification('📁 File upload feature coming soon!');
    });
    
    // History button
    historyBtn.addEventListener('click', showHistoryModal);
    
    // Start voice recording
    document.getElementById('startVoice')?.addEventListener('click', toggleVoiceRecording);
    
    // Voice input toggle
    document.getElementById('toggleVoiceBtn')?.addEventListener('click', showVoiceModal);
    
    // Input focus
    messageInput.addEventListener('focus', () => {
        messageInput.parentElement.classList.add('focused');
    });
    
    messageInput.addEventListener('blur', () => {
        messageInput.parentElement.classList.remove('focused');
    });
}

// ============================================
// THEME MANAGEMENT
// ============================================

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const icon = themeToggle.querySelector('i');
    icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
}

function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(currentTheme);
    localStorage.setItem('theme', currentTheme);
    
    showNotification(`Switched to ${currentTheme} theme`);
}

// ============================================
// MESSAGE HANDLING
// ============================================

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Clear input
    messageInput.value = '';
    
    // Add user message
    addMessage(message, 'user');
    
    // Show typing indicator
    showTyping(true);
    
    try {
        // Send to backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        // Hide typing indicator
        showTyping(false);
        
        // Add bot response
        setTimeout(() => {
            addMessage(data.response, 'bot', data);
            
            // Update conversation history
            conversationHistory.push({
                query: message,
                response: data.response,
                category: data.category,
                confidence: data.confidence,
                timestamp: new Date().toISOString()
            });
            
            // Save to localStorage (limit to 100 messages)
            if (conversationHistory.length > 100) {
                conversationHistory = conversationHistory.slice(-100);
            }
            localStorage.setItem('conversationHistory', JSON.stringify(conversationHistory));
            
            // Update statistics
            updateStatistics(false);
            
            // Load new suggestions based on category
            if (data.category) {
                loadSuggestions(data.category);
            }
            
        }, 500);
        
    } catch (error) {
        console.error('Error sending message:', error);
        showTyping(false);
        addMessage('⚠️ **Connection Error:** Sorry, I encountered an error. Please check your connection and try again.', 'bot');
    }
}

function sendQuickMessage(message) {
    messageInput.value = message;
    sendMessage();
}

function addMessage(content, sender, metadata = {}) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const timestamp = new Date().toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    const avatarIcon = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
    const senderName = sender === 'user' ? 'You' : 'AI Assistant';
    
    // Format content with markdown
    const formattedContent = md.render(content);
    
    // Build message HTML
    let messageHTML = `
        <div class="message-avatar">
            <div class="avatar-pulse">
                <i class="${avatarIcon}"></i>
            </div>
        </div>
        <div class="message-content">
            <div class="message-header">
                <span class="sender">${senderName}</span>
                <span class="timestamp">${timestamp}</span>
            </div>
            <div class="message-body">
                ${formattedContent}
            </div>
    `;
    
    // Add metadata if available
    if (metadata.confidence || metadata.category) {
        messageHTML += `
            <div class="message-footer">
                <div class="quick-tips">
        `;
        
        if (metadata.confidence) {
            const confidencePercent = Math.round(metadata.confidence * 100);
            let confidenceColor = '#10b981'; // Green
            if (confidencePercent < 70) confidenceColor = '#f59e0b'; // Yellow
            if (confidencePercent < 50) confidenceColor = '#ef4444'; // Red
            
            messageHTML += `
                <span style="color: ${confidenceColor}; font-weight: 600;">
                    Confidence: ${confidencePercent}%
                </span>
            `;
        }
        
        if (metadata.category) {
            messageHTML += `
                <span>•</span>
                <span>Category: ${metadata.category}</span>
            `;
        }
        
        messageHTML += `
                </div>
            </div>
        `;
    }
    
    messageHTML += `</div>`;
    
    messageDiv.innerHTML = messageHTML;
    
    // Add to chat container
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Add animation
    messageDiv.style.animation = 'messageSlide 0.3s ease-out';
}

function showTyping(show) {
    typingIndicator.style.display = show ? 'block' : 'none';
    if (show) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

function showWelcomeMessage() {
    const hour = new Date().getHours();
    let greeting = "Good evening";
    
    if (hour < 12) greeting = "Good morning";
    else if (hour < 18) greeting = "Good afternoon";
    
    const welcomeMessage = `
🌟 **${greeting}! I'm your AI Student Assistant** 🤖

I'm here to help you 24/7 with all your academic and campus needs.

🎓 **I can assist with:**
• **Exam schedules** and dates 📅
• **Fee payments** and deadlines 💰
• **Library resources** and timings 📚
• **Hostel facilities** and admission 🏠
• **Course registration** and syllabus 🎓
• **Transport schedules** and routes 🚌
• **Document services** and certificates 📄
• **Results** and grading system 📊

💡 **Quick Tips:**
1. Use the **Quick Actions** buttons for instant answers
2. Type **naturally** like you're talking to a friend
3. Check the **Analytics Dashboard** for statistics
4. Switch between **light/dark** theme as per your preference

🔍 **Try asking:**
• "When are the mid-term exams?"
• "How to pay fees online?"
• "What are the library timings?"
• "How to apply for hostel?"

I'm here to make your campus life easier! 🚀
    `;
    
    addMessage(welcomeMessage, 'bot');
}

// ============================================
// QUICK ACTIONS & SUGGESTIONS
// ============================================

async function loadQuickActions() {
    try {
        const response = await fetch('/api/quick_actions');
        const data = await response.json();
        
        if (quickActions && data.actions) {
            quickActions.innerHTML = data.actions.map(action => `
                <button class="action-btn" onclick="sendQuickMessage('${action.text}')" 
                        style="border-left: 3px solid ${action.color};">
                    <span class="action-icon">${action.icon}</span>
                    <span class="action-text">${action.text}</span>
                </button>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading quick actions:', error);
        
        // Fallback actions
        const fallbackActions = [
            { icon: '📅', text: 'Exam Schedule', color: '#3B82F6' },
            { icon: '💰', text: 'Pay Fees', color: '#10B981' },
            { icon: '📚', text: 'Library', color: '#8B5CF6' },
            { icon: '🏠', text: 'Hostel', color: '#F59E0B' },
            { icon: '🚌', text: 'Transport', color: '#EF4444' },
            { icon: '📄', text: 'Documents', color: '#6366F1' },
            { icon: '🎓', text: 'Courses', color: '#EC4899' },
            { icon: '📊', text: 'Results', color: '#14B8A6' }
        ];
        
        if (quickActions) {
            quickActions.innerHTML = fallbackActions.map(action => `
                <button class="action-btn" onclick="sendQuickMessage('${action.text}')"
                        style="border-left: 3px solid ${action.color};">
                    <span class="action-icon">${action.icon}</span>
                    <span class="action-text">${action.text}</span>
                </button>
            `).join('');
        }
    }
}

async function loadSuggestions(category = 'academics') {
    try {
        const response = await fetch(`/api/suggestions?category=${category}`);
        const data = await response.json();
        
        if (suggestionsList && data.suggestions) {
            suggestionsList.innerHTML = data.suggestions.map(suggestion => `
                <div class="suggestion-item" onclick="sendQuickMessage('${suggestion}')">
                    <i class="fas fa-chevron-right"></i> ${suggestion}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading suggestions:', error);
        
        // Fallback suggestions
        const fallbackSuggestions = [
            'exam schedule for next semester',
            'how to check attendance percentage',
            'fee payment deadline this month',
            'library opening hours today',
            'hostel admission process',
            'bus schedule for college',
            'course registration dates',
            'when are results declared'
        ];
        
        if (suggestionsList) {
            suggestionsList.innerHTML = fallbackSuggestions.map(suggestion => `
                <div class="suggestion-item" onclick="sendQuickMessage('${suggestion}')">
                    <i class="fas fa-chevron-right"></i> ${suggestion}
                </div>
            `).join('');
        }
    }
}

// ============================================
// ANALYTICS & STATISTICS
// ============================================

async function updateStatistics(showNotification = false) {
    try {
        const response = await fetch('/api/statistics');
        if (!response.ok) {
            throw new Error('Statistics API not available');
        }
        
        const data = await response.json();
        analyticsData = data;
        
        // Update analytics dashboard
        updateAnalyticsUI(data);
        
        // Update last updated time
        const now = new Date();
        lastUpdated.textContent = now.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });
        
        if (showNotification) {
            showNotification('📊 Analytics updated successfully');
        }
        
        console.log('✅ Statistics updated:', data);
        
    } catch (error) {
        console.error('Error updating statistics:', error);
        
        // Use fallback data
        const fallbackData = {
            total_queries: conversationHistory.length || 156,
            unique_users: 24,
            avg_confidence: 0.87,
            success_rate: 92.5,
            recent_activity: 12,
            today_activity: 8
        };
        
        updateAnalyticsUI(fallbackData);
        
        if (showNotification) {
            showNotification('⚠️ Using offline analytics data');
        }
    }
}

function updateAnalyticsUI(data) {
    // Helper function to animate value changes
    function animateValue(element, newValue, suffix = '') {
        if (!element) return;
        
        const oldValue = parseFloat(element.textContent.replace(suffix, '')) || 0;
        const diff = Math.abs(newValue - oldValue);
        
        if (diff > 0) {
            element.classList.add('stat-update');
            setTimeout(() => {
                element.classList.remove('stat-update');
            }, 500);
        }
        
        element.textContent = typeof newValue === 'number' 
            ? newValue.toLocaleString() + suffix 
            : newValue + suffix;
    }
    
    // Update main stats cards
    if (statTotalQueries) {
        animateValue(statTotalQueries.querySelector('.stat-value-fix'), data.total_queries || 0);
    }
    
    if (statActiveUsers) {
        animateValue(statActiveUsers.querySelector('.stat-value-fix'), data.unique_users || 1);
    }
    
    if (statAccuracy) {
        const accuracy = data.success_rate || data.avg_confidence * 100 || 95;
        animateValue(statAccuracy.querySelector('.stat-value-fix'), Math.round(accuracy), '%');
    }
    
    // Update detailed stats
    if (statRecentActivity) {
        animateValue(statRecentActivity, data.recent_activity || 0);
    }
    
    if (statTodayActivity) {
        animateValue(statTodayActivity, data.today_activity || 0);
    }
    
    if (statSuccessRate) {
        const successRate = data.success_rate || (data.avg_confidence * 100) || 95;
        animateValue(statSuccessRate, successRate.toFixed(1), '%');
        
        // Update color based on success rate
        statSuccessRate.className = 'stat-row-value';
        if (successRate >= 90) statSuccessRate.classList.add('high');
        else if (successRate >= 75) statSuccessRate.classList.add('medium');
        else statSuccessRate.classList.add('low');
    }
    
    if (statAvgConfidence) {
        const avgConf = data.avg_confidence * 100 || 87;
        animateValue(statAvgConfidence, avgConf.toFixed(1), '%');
        
        // Update color based on confidence
        statAvgConfidence.className = 'stat-row-value';
        if (avgConf >= 85) statAvgConfidence.classList.add('high');
        else if (avgConf >= 70) statAvgConfidence.classList.add('medium');
        else statAvgConfidence.classList.add('low');
    }
    
    // Update category distribution if available
    if (data.categories && data.categories.length > 0) {
        updateCategoryDistribution(data.categories);
    }
}

function updateCategoryDistribution(categories) {
    // This function could be expanded to show a chart
    console.log('Category distribution:', categories);
}

// ============================================
// VOICE INPUT
// ============================================

function showVoiceModal() {
    const modal = document.getElementById('voiceModal');
    if (modal) {
        modal.style.display = 'flex';
        showNotification('🎤 Voice feature simulation - Coming soon!');
    }
}

function toggleVoiceRecording() {
    if (!isRecording) {
        isRecording = true;
        document.querySelector('.voice-status').textContent = '🎤 Listening... Speak now!';
        document.getElementById('startVoice').textContent = 'Stop Listening';
        
        // Simulate voice processing
        setTimeout(() => {
            const simulatedText = "Show me the exam schedule for this semester";
            messageInput.value = simulatedText;
            stopVoiceRecording();
            document.querySelector('.voice-status').textContent = '✅ Processing complete!';
            
            setTimeout(() => {
                closeModal('voiceModal');
                sendMessage();
            }, 1000);
        }, 2000);
    } else {
        stopVoiceRecording();
    }
}

function stopVoiceRecording() {
    isRecording = false;
    document.querySelector('.voice-status').textContent = 'Click and speak your question...';
    document.getElementById('startVoice').textContent = 'Start Listening';
}

// ============================================
// HISTORY MANAGEMENT
// ============================================

function showHistoryModal() {
    const modal = document.getElementById('historyModal');
    const historyList = document.getElementById('historyList');
    
    if (!modal || !historyList) return;
    
    if (conversationHistory.length === 0) {
        historyList.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #6b7280;">
                <i class="fas fa-history fa-2x" style="margin-bottom: 1rem; opacity: 0.5;"></i>
                <p>No conversation history yet.</p>
                <p style="font-size: 0.875rem; margin-top: 0.5rem;">Start chatting to see history here!</p>
            </div>
        `;
    } else {
        // Show last 10 conversations
        const recentHistory = conversationHistory.slice(-10).reverse();
        historyList.innerHTML = recentHistory.map((item, index) => `
            <div class="history-item">
                <div class="history-query">
                    <strong>Q:</strong> ${item.query.substring(0, 80)}${item.query.length > 80 ? '...' : ''}
                </div>
                <div class="history-response">
                    <strong>A:</strong> ${item.response.substring(0, 100)}${item.response.length > 100 ? '...' : ''}
                </div>
                <div class="history-time">
                    <i class="far fa-clock"></i> ${new Date(item.timestamp).toLocaleString()}
                    ${item.confidence ? ` • <i class="fas fa-chart-line"></i> ${Math.round(item.confidence * 100)}%` : ''}
                </div>
            </div>
        `).join('');
    }
    
    modal.style.display = 'flex';
}

function clearHistory() {
    if (conversationHistory.length > 0 && confirm('Are you sure you want to clear all chat history?')) {
        conversationHistory = [];
        localStorage.removeItem('conversationHistory');
        showHistoryModal(); // Refresh modal
        showNotification('🗑️ Chat history cleared');
    }
}

// ============================================
// NOTIFICATION SYSTEM
// ============================================

function showNotification(message) {
    const notification = document.getElementById('notification');
    const notificationText = document.getElementById('notificationText');
    
    if (!notification || !notificationText) return;
    
    notificationText.textContent = message;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function exportChat() {
    const chatData = {
        sessionId: sessionId,
        timestamp: new Date().toISOString(),
        totalConversations: conversationHistory.length,
        conversations: conversationHistory
    };
    
    const dataStr = JSON.stringify(chatData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `student-chatbot-export-${sessionId}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    showNotification('💾 Chat exported successfully!');
}

function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
}

// ============================================
// GLOBAL EXPORTS
// ============================================

// Make functions available globally
window.sendQuickMessage = sendQuickMessage;
window.showHistoryModal = showHistoryModal;
window.clearHistory = clearHistory;
window.exportChat = exportChat;
window.updateStatistics = updateStatistics;
window.closeModal = function(modalId) {
    document.getElementById(modalId).style.display = 'none';
};

console.log('🚀 AI Student Assistant JavaScript loaded successfully!');