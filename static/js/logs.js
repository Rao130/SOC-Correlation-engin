// Logs management JavaScript
let currentPage = 1;
let pageSize = 50;
let totalLogs = 0;
let currentFilters = {};
let sortField = 'timestamp';
let sortOrder = -1;
let autoRefreshInterval = null;
let timelineChart = null;

// Initialize logs page
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.hash === '#logs' || document.getElementById('logs-section').classList.contains('active')) {
        initializeLogsPage();
    }
});

function initializeLogsPage() {
    loadLogFilters();
    loadLogStats();
    loadLogs();
    loadLogTimeline();
}

// Load log filter options
async function loadLogFilters() {
    try {
        // Load log levels
        const levelsResponse = await fetch('/api/logs/levels');
        const levels = await levelsResponse.json();
        const levelSelect = document.getElementById('log-level-filter');
        levels.forEach(level => {
            const option = document.createElement('option');
            option.value = level.value;
            option.textContent = level.label;
            levelSelect.appendChild(option);
        });

        // Load categories
        const categoriesResponse = await fetch('/api/logs/categories');
        const categories = await categoriesResponse.json();
        const categorySelect = document.getElementById('log-category-filter');
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.value;
            option.textContent = category.label;
            categorySelect.appendChild(option);
        });

        // Load modules
        const modulesResponse = await fetch('/api/logs/modules');
        const modules = await modulesResponse.json();
        const moduleSelect = document.getElementById('log-module-filter');
        modules.forEach(module => {
            const option = document.createElement('option');
            option.value = module.value;
            option.textContent = `${module.label} (${module.count})`;
            moduleSelect.appendChild(option);
        });

        // Load unique filters
        const uniqueResponse = await fetch('/api/logs/unique-filters');
        const uniqueData = await uniqueResponse.json();

        // Load users
        const userSelect = document.getElementById('log-user-filter');
        uniqueData.users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.value;
            option.textContent = `${user.value} (${user.count})`;
            userSelect.appendChild(option);
        });

        // Load IP addresses
        const ipSelect = document.getElementById('log-ip-filter');
        uniqueData.ip_addresses.forEach(ip => {
            const option = document.createElement('option');
            option.value = ip.value;
            option.textContent = `${ip.value} (${ip.count})`;
            ipSelect.appendChild(option);
        });

        // Load error codes
        const errorResponse = await fetch('/api/logs/error-codes');
        const errorCodes = await errorResponse.json();
        const errorSelect = document.getElementById('log-error-filter');
        errorCodes.forEach(error => {
            const option = document.createElement('option');
            option.value = error.value;
            option.textContent = `${error.value} (${error.count})`;
            errorSelect.appendChild(option);
        });

    } catch (error) {
        console.error('Error loading log filters:', error);
    }
}

// Load log statistics
async function loadLogStats() {
    try {
        const response = await fetch('/api/logs/stats');
        const stats = await response.json();

        document.getElementById('total-logs').textContent = stats.total_logs.toLocaleString();
        document.getElementById('error-logs').textContent = stats.recent_errors.toLocaleString();
        document.getElementById('critical-logs').textContent = stats.critical_alerts.toLocaleString();
        
        if (stats.avg_response_time) {
            document.getElementById('avg-response-time').textContent = `${stats.avg_response_time.toFixed(2)}ms`;
        } else {
            document.getElementById('avg-response-time').textContent = 'N/A';
        }

    } catch (error) {
        console.error('Error loading log stats:', error);
    }
}

// Load log timeline
async function loadLogTimeline() {
    try {
        const response = await fetch('/api/logs/timeline');
        const data = await response.json();

        const ctx = document.getElementById('log-timeline-chart').getContext('2d');
        
        if (timelineChart) {
            timelineChart.destroy();
        }

        timelineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.timeline.map(item => new Date(item.timestamp).toLocaleTimeString()),
                datasets: [{
                    label: 'Total Logs',
                    data: data.timeline.map(item => item.total),
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                }, {
                    label: 'Errors',
                    data: data.timeline.map(item => item.errors),
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Log Activity Timeline'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error loading log timeline:', error);
    }
}

// Load logs with current filters
async function loadLogs() {
    try {
        const params = new URLSearchParams();
        
        if (currentFilters.level) params.append('level', currentFilters.level);
        if (currentFilters.category) params.append('category', currentFilters.category);
        if (currentFilters.module) params.append('module', currentFilters.module);
        if (currentFilters.user_id) params.append('user_id', currentFilters.user_id);
        if (currentFilters.ip_address) params.append('ip_address', currentFilters.ip_address);
        if (currentFilters.error_code) params.append('error_code', currentFilters.error_code);
        if (currentFilters.search_text) params.append('search_text', currentFilters.search_text);
        if (currentFilters.start_time) params.append('start_time', currentFilters.start_time.toISOString());
        if (currentFilters.end_time) params.append('end_time', currentFilters.end_time.toISOString());
        
        params.append('skip', (currentPage - 1) * pageSize);
        params.append('limit', pageSize);

        const response = await fetch(`/api/logs?${params}`);
        const logs = await response.json();

        displayLogs(logs);
        updatePagination();

    } catch (error) {
        console.error('Error loading logs:', error);
        showError('Failed to load logs');
    }
}

// Display logs in table
function displayLogs(logs) {
    const tbody = document.getElementById('logs-table-body');
    tbody.innerHTML = '';

    logs.forEach(log => {
        const row = document.createElement('tr');
        row.className = `log-row log-${log.level.toLowerCase()}`;
        
        const timestamp = new Date(log.timestamp).toLocaleString();
        const levelClass = `level-${log.level.toLowerCase()}`;
        
        row.innerHTML = `
            <td>${timestamp}</td>
            <td><span class="log-level ${levelClass}">${log.level}</span></td>
            <td>${log.category}</td>
            <td class="log-message" title="${log.message}">${truncateText(log.message, 100)}</td>
            <td>${log.module}</td>
            <td>${log.user_id || '-'}</td>
            <td>${log.ip_address || '-'}</td>
            <td>
                <button class="btn btn-sm" onclick="showLogDetails('${log.id}')">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });

    document.getElementById('log-count').textContent = `${logs.length} logs`;
}

// Show log details
async function showLogDetails(logId) {
    try {
        // Find the log in current page or fetch it
        const params = new URLSearchParams();
        Object.keys(currentFilters).forEach(key => {
            if (currentFilters[key]) {
                params.append(key, currentFilters[key]);
            }
        });
        params.append('skip', 0);
        params.append('limit', 1000);

        const response = await fetch(`/api/logs?${params}`);
        const logs = await response.json();
        
        const log = logs.find(l => l.id === logId);
        if (!log) {
            showError('Log not found');
            return;
        }

        const modalBody = document.getElementById('log-modal-body');
        modalBody.innerHTML = `
            <div class="log-details">
                <div class="detail-row">
                    <label>Timestamp:</label>
                    <span>${new Date(log.timestamp).toLocaleString()}</span>
                </div>
                <div class="detail-row">
                    <label>Level:</label>
                    <span class="log-level level-${log.level.toLowerCase()}">${log.level}</span>
                </div>
                <div class="detail-row">
                    <label>Category:</label>
                    <span>${log.category}</span>
                </div>
                <div class="detail-row">
                    <label>Module:</label>
                    <span>${log.module}</span>
                </div>
                <div class="detail-row">
                    <label>Function:</label>
                    <span>${log.function}</span>
                </div>
                ${log.line ? `<div class="detail-row"><label>Line:</label><span>${log.line}</span></div>` : ''}
                <div class="detail-row">
                    <label>Message:</label>
                    <div class="log-message-full">${log.message}</div>
                </div>
                ${log.user_id ? `<div class="detail-row"><label>User ID:</label><span>${log.user_id}</span></div>` : ''}
                ${log.session_id ? `<div class="detail-row"><label>Session ID:</label><span>${log.session_id}</span></div>` : ''}
                ${log.ip_address ? `<div class="detail-row"><label>IP Address:</label><span>${log.ip_address}</span></div>` : ''}
                ${log.request_id ? `<div class="detail-row"><label>Request ID:</label><span>${log.request_id}</span></div>` : ''}
                ${log.duration_ms ? `<div class="detail-row"><label>Duration:</label><span>${log.duration_ms}ms</span></div>` : ''}
                ${log.error_code ? `<div class="detail-row"><label>Error Code:</label><span>${log.error_code}</span></div>` : ''}
                ${log.stack_trace ? `
                    <div class="detail-row">
                        <label>Stack Trace:</label>
                        <pre class="stack-trace">${log.stack_trace}</pre>
                    </div>
                ` : ''}
                ${log.metadata ? `
                    <div class="detail-row">
                        <label>Metadata:</label>
                        <pre class="metadata">${JSON.stringify(log.metadata, null, 2)}</pre>
                    </div>
                ` : ''}
                ${log.tags && log.tags.length > 0 ? `
                    <div class="detail-row">
                        <label>Tags:</label>
                        <div class="tags">
                            ${log.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;

        openModal('log-modal');

    } catch (error) {
        console.error('Error showing log details:', error);
        showError('Failed to load log details');
    }
}

// Apply filters
function applyLogFilters() {
    currentFilters = {};
    
    const level = document.getElementById('log-level-filter').value;
    const category = document.getElementById('log-category-filter').value;
    const module = document.getElementById('log-module-filter').value;
    const timeRange = document.getElementById('log-time-filter').value;
    const userId = document.getElementById('log-user-filter').value;
    const ipAddress = document.getElementById('log-ip-filter').value;
    const errorCode = document.getElementById('log-error-filter').value;
    const searchText = document.getElementById('log-search-input').value;

    if (level) currentFilters.level = level;
    if (category) currentFilters.category = category;
    if (module) currentFilters.module = module;
    if (userId) currentFilters.user_id = userId;
    if (ipAddress) currentFilters.ip_address = ipAddress;
    if (errorCode) currentFilters.error_code = errorCode;
    if (searchText) currentFilters.search_text = searchText;

    // Set time range
    if (timeRange) {
        const now = new Date();
        let startTime;
        
        switch (timeRange) {
            case '1h':
                startTime = new Date(now.getTime() - 60 * 60 * 1000);
                break;
            case '6h':
                startTime = new Date(now.getTime() - 6 * 60 * 60 * 1000);
                break;
            case '24h':
                startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
                break;
            case '7d':
                startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                break;
        }
        
        if (startTime) {
            currentFilters.start_time = startTime;
            currentFilters.end_time = now;
        }
    }

    currentPage = 1;
    loadLogs();
}

// Handle search keyup
function handleSearchKeyup(event) {
    if (event.key === 'Enter') {
        applyLogFilters();
    }
}

// Sort logs
function sortLogs(field) {
    if (sortField === field) {
        sortOrder = sortOrder * -1;
    } else {
        sortField = field;
        sortOrder = -1;
    }
    
    loadLogs();
}

// Refresh logs
function refreshLogs() {
    loadLogStats();
    loadLogs();
    loadLogTimeline();
}

// Export logs
async function exportLogs() {
    try {
        const format = prompt('Export format (json/csv):', 'json');
        if (!format || !['json', 'csv'].includes(format)) {
            return;
        }

        const params = new URLSearchParams();
        params.append('format', format);
        
        Object.keys(currentFilters).forEach(key => {
            if (currentFilters[key]) {
                if (key === 'start_time' || key === 'end_time') {
                    params.append(key, currentFilters[key].toISOString());
                } else {
                    params.append(key, currentFilters[key]);
                }
            }
        });

        const response = await fetch(`/api/logs/export?${params}`);
        const blob = await response.blob();
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `logs_${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    } catch (error) {
        console.error('Error exporting logs:', error);
        showError('Failed to export logs');
    }
}

// Cleanup old logs
async function cleanupLogs() {
    if (!confirm('Are you sure you want to clean up old logs? This action cannot be undone.')) {
        return;
    }

    const days = prompt('Delete logs older than how many days?', '30');
    if (!days || isNaN(days) || days < 1) {
        return;
    }

    try {
        const response = await fetch(`/api/logs/cleanup?days=${days}`, { method: 'DELETE' });
        const result = await response.json();
        
        showSuccess(result.message);
        refreshLogs();

    } catch (error) {
        console.error('Error cleaning up logs:', error);
        showError('Failed to cleanup logs');
    }
}

// Toggle auto refresh
function toggleAutoRefresh() {
    const icon = document.getElementById('auto-refresh-icon');
    
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        icon.className = 'fas fa-play';
    } else {
        autoRefreshInterval = setInterval(refreshLogs, 5000);
        icon.className = 'fas fa-pause';
    }
}

// Pagination
function updatePagination() {
    const totalPages = Math.ceil(totalLogs / pageSize);
    
    document.getElementById('page-info').textContent = `Page ${currentPage} of ${totalPages || 1}`;
    document.getElementById('prev-btn').disabled = currentPage <= 1;
    document.getElementById('next-btn').disabled = currentPage >= totalPages;
}

function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        loadLogs();
    }
}

function nextPage() {
    const totalPages = Math.ceil(totalLogs / pageSize);
    if (currentPage < totalPages) {
        currentPage++;
        loadLogs();
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
    // You can implement a better notification system here
    alert('Error: ' + message);
}

function showSuccess(message) {
    // You can implement a better notification system here
    alert('Success: ' + message);
}

// Make logs functions global
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
    if (section === 'logs') {
        initializeLogsPage();
    }
};

// Export functions for global access
window.refreshLogs = refreshLogs;
window.exportLogs = exportLogs;
window.cleanupLogs = cleanupLogs;
window.applyLogFilters = applyLogFilters;
window.handleSearchKeyup = handleSearchKeyup;
window.sortLogs = sortLogs;
window.showLogDetails = showLogDetails;
window.toggleAutoRefresh = toggleAutoRefresh;
window.previousPage = previousPage;
window.nextPage = nextPage;
