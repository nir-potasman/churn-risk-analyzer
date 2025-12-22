/**
 * Stampli Churn Risk Analyzer - Chat Interface
 * Handles user interactions and response formatting
 */

const chatContainer = document.getElementById('chatContainer');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');

// Set query from example buttons
function setQuery(query) {
    userInput.value = query;
    userInput.focus();
}

// Format duration from seconds to readable string
function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (mins > 0) {
        return `${mins} min ${secs} sec`;
    }
    return `${secs} sec`;
}

// Get risk level class based on score
function getRiskClass(score) {
    if (score >= 80) return 'critical';
    if (score >= 60) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
}

// Get risk level label
function getRiskLabel(riskLevel) {
    return riskLevel || 'Unknown';
}

// Create analysis card HTML
function createAnalysisCard(data) {
    const assessment = data.assessment;
    const companyName = data.company_name || 'Unknown Company';
    const score = assessment.churn_score || 0;
    const riskClass = getRiskClass(score);
    const riskLevel = assessment.risk_level || getRiskLabel(riskClass);
    
    let html = `
        <div class="analysis-card">
            <div class="analysis-header">
                <div>
                    <div class="company-name">${escapeHtml(companyName)}</div>
                    <div class="progress-bar">
                        <div class="progress-fill ${riskClass}" style="width: ${score}%"></div>
                    </div>
                </div>
                <div class="score-display">
                    <div class="score-circle ${riskClass}">
                        <span class="score-value">${score}</span>
                        <span class="score-label">Score</span>
                    </div>
                    <span class="risk-badge ${riskClass}">${riskLevel}</span>
                </div>
            </div>
    `;
    
    // Summary section
    if (assessment.summary) {
        html += `
            <div class="analysis-section">
                <div class="section-title">📋 Summary</div>
                <div class="section-content">${escapeHtml(assessment.summary)}</div>
            </div>
        `;
    }
    
    // Sentiment Analysis
    if (assessment.sentiment_analysis) {
        html += `
            <div class="analysis-section">
                <div class="section-title">💭 Sentiment Analysis</div>
                <div class="section-content">${escapeHtml(assessment.sentiment_analysis)}</div>
            </div>
        `;
    }
    
    // Red Flags section
    if (assessment.red_flags && assessment.red_flags.length > 0) {
        html += `
            <div class="analysis-section">
                <div class="section-title">🚩 Red Flags</div>
                <ul class="red-flags-list">
                    ${assessment.red_flags.map(flag => `<li>${escapeHtml(flag)}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    // Signals section (collapsible)
    if (assessment.signals && assessment.signals.length > 0) {
        html += `
            <div class="analysis-section">
                <div class="collapsible-header" onclick="toggleCollapsible(this)">
                    <div class="section-title" style="margin-bottom: 0">📊 Risk Signals (${assessment.signals.length})</div>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="collapsible-content">
                    <div class="signals-list" style="margin-top: 0.75rem">
                        ${assessment.signals.map(signal => `
                            <div class="signal-item">
                                <div class="signal-info">
                                    <div class="signal-category">${escapeHtml(signal.category || 'General')}</div>
                                    <div class="signal-description">${escapeHtml(signal.description || '')}</div>
                                </div>
                                <span class="severity-badge ${(signal.severity || 'medium').toLowerCase()}">${signal.severity || 'Medium'}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    // Recommendations section (collapsible)
    if (assessment.recommendations && assessment.recommendations.length > 0) {
        html += `
            <div class="analysis-section">
                <div class="collapsible-header" onclick="toggleCollapsible(this)">
                    <div class="section-title" style="margin-bottom: 0">💡 Recommendations (${assessment.recommendations.length})</div>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="collapsible-content">
                    <div class="recommendations-list" style="margin-top: 0.75rem">
                        ${assessment.recommendations.map(rec => `
                            <div class="recommendation-item">
                                <div class="recommendation-action">
                                    ${escapeHtml(rec.action || '')}
                                    ${rec.urgency ? `<span class="urgency-badge ${rec.urgency.toLowerCase()}">${rec.urgency}</span>` : ''}
                                </div>
                                ${rec.rationale ? `<div class="recommendation-rationale">${escapeHtml(rec.rationale)}</div>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    html += `</div>`;
    return html;
}

// Create transcript card HTML
function createTranscriptCard(transcript) {
    const transcriptId = `transcript-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    return `
        <div class="transcript-card">
            <div class="transcript-header">
                <span class="icon">📞</span>
                <div class="transcript-title">${escapeHtml(transcript.title || 'Call Transcript')}</div>
            </div>
            
            <div class="transcript-meta">
                <div class="meta-item">
                    <span class="icon">📅</span>
                    <span class="label">Date:</span>
                    <span class="value">${escapeHtml(transcript.date || 'N/A')}</span>
                </div>
                <div class="meta-item">
                    <span class="icon">⏰</span>
                    <span class="label">Time:</span>
                    <span class="value">${escapeHtml(transcript.time || 'N/A')}</span>
                </div>
                <div class="meta-item">
                    <span class="icon">⏱️</span>
                    <span class="label">Duration:</span>
                    <span class="value">${formatDuration(transcript.duration || 0)}</span>
                </div>
                <div class="meta-item">
                    <span class="icon">🏢</span>
                    <span class="label">Company:</span>
                    <span class="value">${escapeHtml(transcript.company || 'N/A')}</span>
                </div>
            </div>
            
            <div class="transcript-contacts">
                <div class="contact-row">
                    <span class="icon">👤</span>
                    <span class="label">Stampli Contact:</span>
                    <span class="value">${escapeHtml(transcript.stampli_contact || 'N/A')}</span>
                </div>
                <div class="contact-row">
                    <span class="icon">👥</span>
                    <span class="label">Company Contacts:</span>
                    <span class="value">${escapeHtml(transcript.company_contact || 'N/A')}</span>
                </div>
            </div>
            
            ${transcript.gong_url ? `
                <div class="gong-link">
                    <a href="${escapeHtml(transcript.gong_url)}" target="_blank" rel="noopener noreferrer">
                        🔗 View in Gong
                    </a>
                </div>
            ` : ''}
            
            <div class="transcript-body">
                <div class="section-title">📝 Transcript</div>
                <div class="transcript-text" id="${transcriptId}">
                    ${escapeHtml(transcript.transcript || 'No transcript available.')}
                </div>
                ${(transcript.transcript && transcript.transcript.length > 300) ? `
                    <button class="expand-btn" onclick="toggleTranscript('${transcriptId}', this)">
                        Show full transcript
                    </button>
                ` : ''}
            </div>
        </div>
    `;
}

// Create transcripts list HTML
function createTranscriptsList(data) {
    const transcripts = data.transcripts?.transcripts || data.transcripts || [];
    const companyName = data.company_name || 'Unknown Company';
    
    if (!transcripts.length) {
        return `<div class="error-message">No transcripts found for ${escapeHtml(companyName)}.</div>`;
    }
    
    let html = `<div style="margin-bottom: 0.5rem; color: var(--text-secondary);">
        Found ${transcripts.length} transcript${transcripts.length > 1 ? 's' : ''} for <strong>${escapeHtml(companyName)}</strong>
    </div>`;
    
    transcripts.forEach(transcript => {
        html += createTranscriptCard(transcript);
    });
    
    return html;
}

// Toggle collapsible sections
function toggleCollapsible(header) {
    header.classList.toggle('expanded');
    const content = header.nextElementSibling;
    content.classList.toggle('expanded');
}

// Toggle transcript expansion
function toggleTranscript(id, btn) {
    const element = document.getElementById(id);
    element.classList.toggle('expanded');
    btn.textContent = element.classList.contains('expanded') ? 'Show less' : 'Show full transcript';
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add message to chat
function addMessage(content, isUser = false, isHtml = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (isHtml) {
        contentDiv.innerHTML = content;
    } else {
        contentDiv.textContent = content;
    }
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageDiv;
}

// Add loading indicator
function addLoading() {
    const loadingHtml = `
        <div class="loading">
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span>Analyzing...</span>
        </div>
    `;
    return addMessage(loadingHtml, false, true);
}

// Format response based on intent
function formatResponse(data) {
    if (data.error) {
        return `<div class="error-message">❌ ${escapeHtml(data.error)}</div>`;
    }
    
    const intent = data.intent;
    
    if (intent === 'analysis' && data.assessment) {
        return createAnalysisCard(data);
    } else if (intent === 'transcript' && data.transcripts) {
        return createTranscriptsList(data);
    } else {
        // Fallback - show as formatted JSON
        return `<pre style="white-space: pre-wrap; font-size: 0.875rem;">${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
    }
}

// Handle form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const query = userInput.value.trim();
    if (!query) return;
    
    // Add user message
    addMessage(query, true);
    userInput.value = '';
    
    // Disable input while loading
    userInput.disabled = true;
    sendBtn.disabled = true;
    
    // Add loading indicator
    const loadingMsg = addLoading();
    
    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_query: query })
        });
        
        const data = await response.json();
        
        // Remove loading indicator
        loadingMsg.remove();
        
        // Add formatted response
        addMessage(formatResponse(data), false, true);
        
    } catch (error) {
        // Remove loading indicator
        loadingMsg.remove();
        
        // Show error
        addMessage(`<div class="error-message">❌ Failed to connect to the server. Please try again.</div>`, false, true);
    }
    
    // Re-enable input
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.focus();
});

// Handle clear button
clearBtn.addEventListener('click', () => {
    // Keep only the welcome message
    const messages = chatContainer.querySelectorAll('.message');
    messages.forEach((msg, index) => {
        if (index > 0) {
            msg.remove();
        }
    });
});

// Focus input on page load
userInput.focus();

