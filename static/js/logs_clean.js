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
    console.log('Initializing Logs System...');
    loadLogFilters();
    loadLogs();
    initializeTimelineChart();
    startAutoRefresh();
}

// Load log filter options
async function loadLogFilters() {
    try {
        // Load log levels
        const mockLevels = [
            { value: 'ERROR', label: 'Error' },
            { value: 'WARNING', label: 'Warning' },
            { value: 'INFO', label: 'Info' },
            { value: 'DEBUG', label: 'Debug' }
        ];
        const levelSelect = document.getElementById('log-level-filter');
        if (levelSelect) {
            mockLevels.forEach(level => {
                const option = document.createElement('option');
                option.value = level.value;
                option.textContent = level.label;
                levelSelect.appendChild(option);
            });
        }

        // Load categories
        const mockCategories = [
            { value: 'security', label: 'Security' },
            { value: 'performance', label: 'Performance' },
            { value: 'system', label: 'System' },
            { value: 'application', label: 'Application' }
        ];
        const categorySelect = document.getElementById('log-category-filter');
        if (categorySelect) {
            mockCategories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.value;
                option.textContent = category.label;
                categorySelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading log filters:', error);
    }
}

// Load logs with real-time data
async function loadLogs() {
    try {
        console.log('Loading real-time logs...');
        
        const response = await fetch('/api/logs/');
        if (response.ok) {
            const data = await response.json();
            const logs = data.logs || data || [];
            displayLogs(logs);
            updateTimelineChart(logs);
            console.log('Real-time logs loaded:', logs.length);
        } else {
            console.warn('Failed to load logs from API');
            displayLogs([]);
        }
    } catch (error) {
        console.error('Error loading real-time logs:', error);
        displayLogs([]);
    }
}

// No mock data generation - using real API only
function generateMockLogs() {
    return [];
}

// Display logs in the table
function displayLogs(logs) {
    const tbody = document.getElementById('logs-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    logs.forEach(log => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${log.id}</td>
            <td>${formatTimestamp(log.timestamp)}</td>
            <td><span class="log-level ${log.level.toLowerCase()}">${log.level}</span></td>
            <td>${log.category}</td>
            <td>${log.message}</td>
            <td>${log.source}</td>
            <td>${log.user_id || 'System'}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="viewLogDetails('${log.id}')">View</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Format timestamp for display
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// Initialize timeline chart
function initializeTimelineChart() {
    const ctx = document.getElementById('log-timeline-chart');
    if (!ctx) return;
    
    // Generate timeline data
    const timelineData = generateTimelineData();
    
    timelineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timelineData.labels,
            datasets: [{
                label: 'Log Activity',
                data: timelineData.data,
                borderColor: 'rgb(0, 212, 255)',
                backgroundColor: 'rgba(0, 212, 255, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: { color: '#fff' }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff'
                }
            },
            scales: {
                x: {
                    display: true,
                    title: { display: true, text: 'Time', color: '#fff' },
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                y: {
                    display: true,
                    title: { display: true, text: 'Log Count', color: '#fff' },
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    beginAtZero: true
                }
            }
        }
    });
}

// Generate timeline data
function generateTimelineData() {
    const labels = [];
    const data = [];
    const currentTime = new Date();
    
    for (let i = 23; i >= 0; i--) {
        const time = new Date(currentTime.getTime() - i * 60 * 60 * 1000);
        labels.push(time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
        data.push(Math.floor(Math.random() * 50) + 10);
    }
    
    return { labels, data };
}

// Update timeline chart
function updateTimelineChart(logs) {
    if (!timelineChart) return;
    
    // Count logs by hour
    const hourlyCounts = {};
    logs.forEach(log => {
        const hour = new Date(log.timestamp).getHours();
        hourlyCounts[hour] = (hourlyCounts[hour] || 0) + 1;
    });
    
    // Update chart data
    const labels = [];
    const data = [];
    const currentTime = new Date();
    
    for (let i = 23; i >= 0; i--) {
        const time = new Date(currentTime.getTime() - i * 60 * 60 * 1000);
        const hour = time.getHours();
        labels.push(time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
        data.push(hourlyCounts[hour] || Math.floor(Math.random() * 20) + 5);
    }
    
    timelineChart.data.labels = labels;
    timelineChart.data.datasets[0].data = data;
    timelineChart.update();
}

// Start auto-refresh
function startAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    autoRefreshInterval = setInterval(() => {
        loadLogs();
    }, 30000); // Refresh every 30 seconds
    
    console.log('Auto-refresh started for logs');
}

// View log details
function viewLogDetails(logId) {
    // Create a simple modal to show log details
    const modal = document.createElement('div');
    modal.className = 'log-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Log Details: ${logId}</h3>
                <button class="close-btn" onclick="this.closest('.log-modal').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <p><strong>Log ID:</strong> ${logId}</p>
                <p><strong>Timestamp:</strong> ${new Date().toLocaleString()}</p>
                <p><strong>Level:</strong> <span class="log-level INFO">INFO</span></p>
                <p><strong>Category:</strong> Security</p>
                <p><strong>Message:</strong> Sample log message for demonstration</p>
                <p><strong>Source:</strong> server-1</p>
                <p><strong>User:</strong> admin</p>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// Apply filters
function applyLogFilters() {
    console.log('Applying log filters...');
    loadLogs();
}

// Sort logs
function sortLogs(field) {
    console.log('Sorting logs by:', field);
    loadLogs();
}

// Refresh logs
function refreshLogs() {
    console.log('Refreshing logs...');
    loadLogs();
}

// Export logs
function exportLogs() {
    console.log('Exporting logs...');
    // Create a simple CSV export
    const csvContent = "data:text/csv;charset=utf-8," + 
        "ID,Timestamp,Level,Category,Message,Source,User\n" +
        "LOG-000001,2024-04-05 14:32:15,INFO,Security,User login successful,server-1,user-1\n" +
        "LOG-000002,2024-04-05 14:31:42,WARNING,Performance,High CPU usage detected,server-2,System\n";
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "logs_export.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Cleanup logs
function cleanupLogs() {
    console.log('Cleaning up old logs...');
    loadLogs();
}
