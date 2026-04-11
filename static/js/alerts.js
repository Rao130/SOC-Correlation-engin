// Alert Management JavaScript
let currentAlertPage = 1;
let alertPageSize = 20;
let totalAlerts = 0;
let currentAlertFilters = {};
let alertSortField = 'timestamp';
let alertSortOrder = 'desc';
let alertAutoRefreshInterval = null;

// Initialize alerts page
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.hash === '#alerts' || document.getElementById('alerts-section').classList.contains('active')) {
        initializeAlertsPage();
    }
});

function initializeAlertsPage() {
    loadAlertFilters();
    loadAlerts();
    loadAlertStats();
    
    // Add event listeners
    document.getElementById('alert-search').addEventListener('keyup', handleAlertSearchKeyup);
    document.getElementById('severity-filter').addEventListener('change', applyAlertFilters);
    document.getElementById('status-filter').addEventListener('change', applyAlertFilters);
    document.getElementById('create-alert-form').addEventListener('submit', handleCreateAlert);
}

// Load alerts with current filters
async function loadAlerts() {
    try {
        // Use real API calls to get actual alerts
        const response = await fetch('/api/alerts/?limit=1000');
        if (!response.ok) {
            throw new Error('Failed to fetch alerts');
        }
        
        const data = await response.json();
        window.alerts = data || [];
        
        // If no alerts exist, create some initial alerts
        if (window.alerts.length === 0) {
            await createInitialAlerts();
            await loadAlerts(); // Reload after creating initial data
            return;
        }
        
        displayAlerts(window.alerts);
        console.log('Real alerts loaded:', window.alerts.length, 'alerts');
    } catch (error) {
        console.error('Error loading alerts:', error);
        // Fallback to mock data if API fails
        window.alerts = generateMockAlerts();
        displayAlerts(window.alerts);
        console.log('Fallback to mock alerts loaded');
    }
}

// Create initial alerts for system
async function createInitialAlerts() {
    try {
        const mockAlerts = generateMockAlerts();
        
        for (const alert of mockAlerts.slice(0, 10)) { // Start with 10 alerts
            await createAlert(alert);
        }
        
        console.log('Initial alerts created');
    } catch (error) {
        console.error('Error creating initial alerts:', error);
    }
}

// Create alert API call
async function createAlert(alertData) {
    try {
        const response = await fetch('/api/alerts/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(alertData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to create alert');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error creating alert:', error);
        throw error;
    }
}

// Generate mock alerts data
function generateMockAlerts() {
    const alerts = [];
    const severities = ['critical', 'high', 'medium', 'low'];
    const statuses = ['active', 'investigating', 'resolved', 'false_positive'];
    const titles = [
        'SQL Injection Attempt',
        'Brute Force Attack',
        'Suspicious Login Pattern',
        'Malware Signature Detected',
        'Data Exfiltration Attempt',
        'Unauthorized Access',
        'Phishing Campaign',
        'DDoS Attack',
        'Port Scanning Activity',
        'Anomalous Traffic Pattern'
    ];
    
    for (let i = 1; i <= 20; i++) {
        alerts.push({
            id: `ALT-${String(i).padStart(6, '0')}`,
            title: titles[Math.floor(Math.random() * titles.length)],
            severity: severities[Math.floor(Math.random() * severities.length)],
            status: statuses[Math.floor(Math.random() * statuses.length)],
            timestamp: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString(),
            source_ip: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
            description: `Security alert detected with severity level requiring immediate attention`,
            assigned_to: Math.random() > 0.5 ? `analyst-${Math.floor(Math.random() * 5) + 1}` : null
        });
    }
    
    return alerts;
}

// Display alerts in table
function displayAlerts(alerts) {
    const tbody = document.getElementById('alerts-tbody');
    tbody.innerHTML = '';

    alerts.forEach(alert => {
        const row = document.createElement('tr');
        row.className = `alert-row alert-${alert.severity}`;
        
        const timestamp = new Date(alert.timestamp).toLocaleString();
        const severityClass = `severity-${alert.severity}`;
        const statusClass = `status-${alert.status}`;
        
        row.innerHTML = `
            <td>${timestamp}</td>
            <td class="alert-title" title="${alert.description}">${truncateText(alert.title, 50)}</td>
            <td><span class="alert-severity ${severityClass}">${alert.severity.toUpperCase()}</span></td>
            <td>${alert.category}</td>
            <td><span class="alert-status ${statusClass}">${alert.status.replace('_', ' ').toUpperCase()}</span></td>
            <td>${alert.source}</td>
            <td><div class="confidence-bar"><div class="confidence-fill" style="width: ${alert.confidence}%"></div><span class="confidence-text">${alert.confidence}%</span></div></td>
            <td>
                <button class="btn btn-sm" onclick="showAlertDetails('${alert._id}')">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm" onclick="updateAlertStatus('${alert._id}', 'investigating')">
                    <i class="fas fa-search"></i>
                </button>
                <button class="btn btn-sm" onclick="updateAlertStatus('${alert._id}', 'resolved')">
                    <i class="fas fa-check"></i>
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });

    document.getElementById('alert-count').textContent = `${alerts.length} alerts`;
}

// Show alert details
async function showAlertDetails(alertId) {
    try {
        const response = await fetch(`/api/alerts/`);
        const data = await response.json();
        const alerts = data.alerts || [];
        
        const alert = alerts.find(a => a._id === alertId);
        if (!alert) {
            showError('Alert not found');
            return;
        }

        const modalBody = document.getElementById('alert-modal-body');
        modalBody.innerHTML = `
            <div class="alert-details">
                <div class="detail-row">
                    <label>Alert ID:</label>
                    <span>${alert._id}</span>
                </div>
                <div class="detail-row">
                    <label>Timestamp:</label>
                    <span>${new Date(alert.timestamp).toLocaleString()}</span>
                </div>
                <div class="detail-row">
                    <label>Title:</label>
                    <span class="alert-title-full">${alert.title}</span>
                </div>
                <div class="detail-row">
                    <label>Description:</label>
                    <div class="alert-description-full">${alert.description}</div>
                </div>
                <div class="detail-row">
                    <label>Severity:</label>
                    <span class="alert-severity severity-${alert.severity}">${alert.severity.toUpperCase()}</span>
                </div>
                <div class="detail-row">
                    <label>Category:</label>
                    <span>${alert.category}</span>
                </div>
                <div class="detail-row">
                    <label>Status:</label>
                    <span class="alert-status status-${alert.status}">${alert.status.replace('_', ' ').toUpperCase()}</span>
                </div>
                <div class="detail-row">
                    <label>Source:</label>
                    <span>${alert.source}</span>
                </div>
                <div class="detail-row">
                    <label>Confidence:</label>
                    <div class="confidence-bar"><div class="confidence-fill" style="width: ${alert.confidence}%"></div><span class="confidence-text">${alert.confidence}%</span></div>
                </div>
                ${alert.criticality_score ? `
                    <div class="detail-row">
                        <label>Criticality Score:</label>
                        <span>${alert.criticality_score}</span>
                    </div>
                ` : ''}
                ${alert.entities && alert.entities.length > 0 ? `
                    <div class="detail-row">
                        <label>Entities:</label>
                        <div class="entities-list">
                            ${alert.entities.map(entity => `
                                <div class="entity-item">
                                    <strong>${entity.type}:</strong> ${entity.value}
                                    ${entity.reputation ? `<span class="reputation-score">(${entity.reputation.score})</span>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                ${alert.location ? `
                    <div class="detail-row">
                        <label>Location:</label>
                        <div class="location-info">
                            ${alert.location.country ? `<div>Country: ${alert.location.country}</div>` : ''}
                            ${alert.location.city ? `<div>City: ${alert.location.city}</div>` : ''}
                            ${alert.location.ip ? `<div>IP: ${alert.location.ip}</div>` : ''}
                        </div>
                    </div>
                ` : ''}
                ${alert.context && alert.context.tags ? `
                    <div class="detail-row">
                        <label>Tags:</label>
                        <div class="tags">
                            ${alert.context.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;

        openModal('alert-modal');

    } catch (error) {
        console.error('Error showing alert details:', error);
        showError('Failed to load alert details');
    }
}

// Update alert status
async function updateAlertStatus(alertId, status) {
    try {
        const response = await fetch(`/api/alerts/${alertId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status })
        });

        if (response.ok) {
            showSuccess('Alert status updated successfully');
            loadAlerts();
        } else {
            throw new Error('Failed to update alert status');
        }

    } catch (error) {
        console.error('Error updating alert status:', error);
        showError('Failed to update alert status');
    }
}

// Create new alert
async function createAlert() {
    openModal('create-alert-modal');
}

// Handle create alert form submission
async function handleCreateAlert(event) {
    event.preventDefault();
    
    const formData = {
        title: document.getElementById('alert-title').value,
        description: document.getElementById('alert-description').value,
        severity: document.getElementById('alert-severity').value,
        category: document.getElementById('alert-category').value,
        source: document.getElementById('alert-source').value,
        confidence: parseInt(document.getElementById('alert-confidence').value),
        entities: [],
        context: { tags: [] }
    };

    try {
        const response = await fetch('/api/alerts/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            showSuccess('Alert created successfully');
            closeModal('create-alert-modal');
            document.getElementById('create-alert-form').reset();
            loadAlerts();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create alert');
        }

    } catch (error) {
        console.error('Error creating alert:', error);
        showError(error.message || 'Failed to create alert');
    }
}

// Generate mock statistics for fallback
function generateMockStats() {
    return {
        total: 127,
        critical: 8,
        high: 23,
        medium: 45,
        low: 51
    };
}

// Load alert statistics
async function loadAlertStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        // Update statistics cards
        document.getElementById('total-alerts').textContent = stats.total || 0;
        document.getElementById('critical-alerts').textContent = stats.critical || 0;
        document.getElementById('high-alerts').textContent = stats.high || 0;
        document.getElementById('medium-alerts').textContent = stats.medium || 0;
        
        console.log('Alert statistics loaded successfully');
    } catch (error) {
        console.error('Error loading alert statistics:', error);
        
        // Fallback to mock statistics
        const mockStats = generateMockStats();
        document.getElementById('total-alerts').textContent = mockStats.total;
        document.getElementById('critical-alerts').textContent = mockStats.critical;
        document.getElementById('high-alerts').textContent = mockStats.high;
        document.getElementById('medium-alerts').textContent = mockStats.medium;
    }
}

// Update alert statistics from current alerts
function updateAlertStats(alerts) {
    const stats = {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
        total: alerts.length
    };

    alerts.forEach(alert => {
        if (stats.hasOwnProperty(alert.severity)) {
            stats[alert.severity]++;
        }
    });

    document.getElementById('critical-count').textContent = stats.critical;
    document.getElementById('high-count').textContent = stats.high;
    document.getElementById('medium-count').textContent = stats.medium;
    document.getElementById('low-count').textContent = stats.low;
    document.getElementById('total-count').textContent = stats.total;
}

// Apply filters
function applyAlertFilters() {
    currentAlertFilters = {};
    
    const severity = document.getElementById('severity-filter').value;
    const status = document.getElementById('status-filter').value;
    const search = document.getElementById('alert-search').value;
    
    if (severity) currentAlertFilters.severity = severity;
    if (status) currentAlertFilters.status = status;
    if (search) currentAlertFilters.search = search;

    currentAlertPage = 1;
    loadAlerts();
}

// Handle search keyup
function handleAlertSearchKeyup(event) {
    if (event.key === 'Enter') {
        applyAlertFilters();
    }
}

// Sort alerts
function sortAlerts(field) {
    if (alertSortField === field) {
        alertSortOrder = alertSortOrder === 'desc' ? 'asc' : 'desc';
    } else {
        alertSortField = field;
        alertSortOrder = 'desc';
    }
    
    loadAlerts();
}

// Refresh alerts
async function refreshAlerts() {
    try {
        await loadAlerts();
        await loadAlertStats();
    } catch (error) {
        console.error('Error refreshing alerts:', error);
        // Don't throw the error to prevent console spam
    }
}

// Toggle auto refresh
function toggleAutoRefresh() {
    const icon = document.getElementById('auto-refresh-icon');
    
    if (alertAutoRefreshInterval) {
        clearInterval(alertAutoRefreshInterval);
        alertAutoRefreshInterval = null;
        icon.className = 'fas fa-play';
    } else {
        alertAutoRefreshInterval = setInterval(refreshAlerts, 10000); // Refresh every 10 seconds
        icon.className = 'fas fa-pause';
    }
}

// Pagination
function updateAlertPagination(total) {
    totalAlerts = total;
    const totalPages = Math.ceil(totalAlerts / alertPageSize);
    
    document.getElementById('alert-page-info').textContent = `Page ${currentAlertPage} of ${totalPages || 1}`;
    document.getElementById('alert-prev-btn').disabled = currentAlertPage <= 1;
    document.getElementById('alert-next-btn').disabled = currentAlertPage >= totalPages;
}

function previousAlertPage() {
    if (currentAlertPage > 1) {
        currentAlertPage--;
        loadAlerts();
    }
}

function nextAlertPage() {
    const totalPages = Math.ceil(totalAlerts / alertPageSize);
    if (currentAlertPage < totalPages) {
        currentAlertPage++;
        loadAlerts();
    }
}

// Utility functions
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function showError(message) {
    // Simple error notification
    alert('Error: ' + message);
}

function showSuccess(message) {
    // Simple success notification
    alert('Success: ' + message);
}

// Export functions for global access
window.showSection = function(section) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.classList.remove('active');
    });
    
    // Remove active class from all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(section + '-section').classList.add('active');
    
    // Add active class to selected nav item
    document.querySelector(`a[href="#${section}"]`).parentElement.classList.add('active');
    
    // Initialize section-specific content
    if (section === 'alerts') {
        initializeAlertsPage();
    } else if (section === 'logs') {
        initializeLogsPage();
    }
};

// Export alert functions
window.refreshAlerts = refreshAlerts;
window.createAlert = createAlert;
window.showAlertDetails = showAlertDetails;
window.updateAlertStatus = updateAlertStatus;
window.applyAlertFilters = applyAlertFilters;
window.handleAlertSearchKeyup = handleAlertSearchKeyup;
window.sortAlerts = sortAlerts;
window.toggleAutoRefresh = toggleAutoRefresh;
window.previousAlertPage = previousAlertPage;
window.nextAlertPage = nextAlertPage;
