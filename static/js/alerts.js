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
        const params = new URLSearchParams();
        
        if (currentAlertFilters.severity) params.append('severity', currentAlertFilters.severity);
        if (currentAlertFilters.status) params.append('status', currentAlertFilters.status);
        if (currentAlertFilters.search) params.append('search', currentAlertFilters.search);
        
        params.append('skip', (currentAlertPage - 1) * alertPageSize);
        params.append('limit', alertPageSize);
        params.append('sort_by', alertSortField);
        params.append('sort_order', alertSortOrder);

        const response = await fetch(`/api/alerts/?${params}`);
        const data = await response.json();

        displayAlerts(data.alerts || []);
        updateAlertPagination(data.total || 0);
        updateAlertStats(data.alerts || []);

    } catch (error) {
        console.error('Error loading alerts:', error);
        showError('Failed to load alerts');
    }
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

// Load alert statistics
async function loadAlertStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        if (stats.alerts) {
            document.getElementById('critical-count').textContent = stats.alerts.critical || 0;
            document.getElementById('high-count').textContent = stats.alerts.high || 0;
            document.getElementById('medium-count').textContent = stats.alerts.medium || 0;
            document.getElementById('low-count').textContent = stats.alerts.low || 0;
            document.getElementById('total-count').textContent = stats.alerts.total || 0;
        }

    } catch (error) {
        console.error('Error loading alert stats:', error);
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
function refreshAlerts() {
    loadAlerts();
    loadAlertStats();
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
