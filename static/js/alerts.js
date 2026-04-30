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
    console.log('📋 Alerts.js loaded - DOM ready');
    
    // Always try to initialize alerts page
    setTimeout(() => {
        initializeAlertsPage();
    }, 1000);
});

// Also initialize when alerts section is shown
window.addEventListener('load', function() {
    console.log('📋 Window fully loaded - checking alerts section...');
    
    setTimeout(() => {
        const alertsSection = document.getElementById('alerts-section');
        if (alertsSection) {
            console.log('📋 Alerts section found, forcing alerts load...');
            initializeAlertsPage();
        }
    }, 1500);
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

// Load alerts with current filters from multiple real-time sources
async function loadAlerts() {
    try {
        console.log('Loading alerts from multiple real-time sources...');
        
        // Load database alerts
        let dbAlerts = [];
        try {
            const dbResponse = await fetch('/api/alerts/?limit=1000');
            if (dbResponse.ok) {
                const data = await dbResponse.json();
                dbAlerts = data || [];
                console.log('Database alerts loaded:', dbAlerts.length);
            }
        } catch (dbError) {
            console.warn('Error loading database alerts:', dbError);
        }
        
        // Load real-time network alerts
        let networkAlerts = [];
        try {
            const networkResponse = await fetch('/api/network/realtime-alerts');
            if (networkResponse.ok) {
                const networkData = await networkResponse.json();
                networkAlerts = networkData.alerts || [];
                console.log('Real-time network alerts loaded:', networkAlerts.length);
            }
        } catch (networkError) {
            console.warn('Error loading network alerts:', networkError);
        }
        
        // Load generated security alerts
        let generatedAlerts = [];
        try {
            const genResponse = await fetch('/api/analytics/generated-alerts');
            if (genResponse.ok) {
                const genData = await genResponse.json();
                generatedAlerts = genData.alerts || [];
                console.log('Generated alerts loaded:', generatedAlerts.length);
            }
        } catch (genError) {
            console.warn('Error loading generated alerts:', genError);
        }
        
        // Combine all alerts with priority to real-time data
        const allAlerts = [...networkAlerts, ...generatedAlerts, ...dbAlerts];
        
        // Remove duplicates based on timestamp and title
        const uniqueAlerts = [];
        const seen = new Set();
        for (const alert of allAlerts) {
            const key = `${alert.title}_${alert.timestamp}`;
            if (!seen.has(key)) {
                seen.add(key);
                uniqueAlerts.push(alert);
            }
        }
        
        // Sort by timestamp (newest first)
        uniqueAlerts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        
        window.alerts = uniqueAlerts;
        
        // If still no alerts, create network status alerts
        if (window.alerts.length === 0) {
            console.log('No alerts found, creating network status alerts...');
            await createNetworkStatusAlerts();
        }
        
        displayAlerts(window.alerts);
        console.log('Total real-time alerts loaded:', window.alerts.length, 'alerts');
        
    } catch (error) {
        console.error('Error loading alerts:', error);
        // Create fallback network status alerts
        await createNetworkStatusAlerts();
    }
}

// Create network status alerts as fallback
async function createNetworkStatusAlerts() {
    try {
        console.log('Creating network status alerts...');
        
        // Get current network metrics
        let metrics = null;
        let connections = null;
        let status = null;
        
        try {
            const metricsResponse = await fetch('/api/network/metrics');
            if (metricsResponse.ok) {
                metrics = await metricsResponse.json();
            }
        } catch (metricsError) {
            console.warn('Error loading network metrics:', metricsError);
        }
        
        try {
            const connectionsResponse = await fetch('/api/network/connections');
            if (connectionsResponse.ok) {
                connections = await connectionsResponse.json();
            }
        } catch (connectionsError) {
            console.warn('Error loading network connections:', connectionsError);
        }
        
        try {
            const statusResponse = await fetch('/api/network/status');
            if (statusResponse.ok) {
                status = await statusResponse.json();
            }
        } catch (statusError) {
            console.warn('Error loading network status:', statusError);
        }
        
        // Create comprehensive network status alert
        if (metrics || connections || status) {
            const activeConns = metrics?.active_connections || connections?.total_count || 0;
            const bytesTransferred = (metrics?.bytes_sent || 0) + (metrics?.bytes_recv || 0);
            const monitoringActive = status?.monitoring_active || false;
            
            const networkAlert = {
                _id: `network_${Date.now()}`,
                title: "Real-time Network Activity",
                description: `Monitoring ${activeConns} active connections with ${bytesTransferred > 0 ? 'active' : 'no'} data transfer. Status: ${monitoringActive ? 'Active' : 'Inactive'}`,
                severity: "low",
                category: "network_monitoring",
                source: "Network Monitor",
                status: "new",
                timestamp: new Date().toISOString(),
                confidence: 95,
                entities: [
                    {"type": "monitor", "value": "system_network"},
                    {"type": "metric", "value": `connections:${activeConns}`},
                    {"type": "metric", "value": `bytes:${bytesTransferred}`}
                ],
                context: {
                    "metrics": metrics,
                    "connections_count": activeConns,
                    "monitoring_active": monitoringActive
                }
            };
            
            window.alerts = [networkAlert];
            console.log('Created network status alert:', networkAlert);
            
        } else {
            // Create a default alert if no data available
            const defaultAlert = {
                _id: `default_${Date.now()}`,
                title: "Network Monitor Initializing",
                description: "Network monitoring is starting up. Real-time data will appear here momentarily.",
                severity: "low",
                category: "network_monitoring",
                source: "Real-time Monitor",
                status: "new",
                timestamp: new Date().toISOString(),
                confidence: 90,
                entities: [
                    {"type": "monitor", "value": "system_network"}
                ]
            };
            
            window.alerts = [defaultAlert];
            console.log('Created default network alert:', defaultAlert);
        }
        
    } catch (error) {
        console.error('Error creating network status alerts:', error);
        // Create minimal fallback alert
        window.alerts = [{
            _id: `fallback_${Date.now()}`,
            title: "System Starting",
            description: "Real-time monitoring is initializing.",
            severity: "low",
            category: "system",
            source: "System",
            status: "new",
            timestamp: new Date().toISOString(),
            confidence: 100
        }];
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

// Mock alerts generation disabled - using real network data only
// function generateMockAlerts() {
//     REMOVED - No longer generating fake data
// }

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

// Mock statistics generation disabled - using real data only
// function generateMockStats() {
//     REMOVED - No longer generating fake statistics
// }

// Load alert statistics from real-time sources
async function loadAlertStats() {
    try {
        // Get real-time statistics
        let realTimeStats = null;
        try {
            const response = await fetch('/api/analytics/realtime-stats');
            if (response.ok) {
                realTimeStats = await response.json();
                console.log('Real-time statistics loaded:', realTimeStats);
            }
        } catch (error) {
            console.warn('Error loading real-time stats:', error);
        }
        
        // Calculate statistics from current alerts if real-time stats not available
        let stats = {
            total: 0,
            critical: 0,
            high: 0,
            medium: 0,
            low: 0
        };
        
        if (realTimeStats && realTimeStats.alert_statistics) {
            const alertStats = realTimeStats.alert_statistics;
            stats.total = alertStats.total || 0;
            stats.critical = alertStats.by_severity?.critical || 0;
            stats.high = alertStats.by_severity?.high || 0;
            stats.medium = alertStats.by_severity?.medium || 0;
            stats.low = alertStats.by_severity?.low || 0;
        } else if (window.alerts && window.alerts.length > 0) {
            // Calculate from current alerts
            window.alerts.forEach(alert => {
                stats.total++;
                if (stats.hasOwnProperty(alert.severity)) {
                    stats[alert.severity]++;
                }
            });
        }
        
        // Update statistics cards
        document.getElementById('total-alerts').textContent = stats.total;
        document.getElementById('critical-alerts').textContent = stats.critical;
        document.getElementById('high-alerts').textContent = stats.high;
        document.getElementById('medium-alerts').textContent = stats.medium;
        
        console.log('Alert statistics calculated:', stats);
        
    } catch (error) {
        console.error('Error loading alert statistics:', error);
        
        // Show zero stats instead of mock data
        document.getElementById('total-alerts').textContent = '0';
        document.getElementById('critical-alerts').textContent = '0';
        document.getElementById('high-alerts').textContent = '0';
        document.getElementById('medium-alerts').textContent = '0';
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
        alertAutoRefreshInterval = setInterval(refreshAlerts, 5000); // Refresh every 5 seconds for real-time data
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
