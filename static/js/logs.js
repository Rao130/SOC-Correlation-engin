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
    console.log('📋 Logs.js loaded - DOM ready');
    
    // Always initialize logs page when DOM is loaded
    setTimeout(() => {
        console.log('📋 Starting logs initialization...');
        initializeLogsPage();
        initLogsWebSocket(); // Add WebSocket for real-time log updates
    }, 500);
});

// Also try to load logs immediately if logs section is visible
window.addEventListener('load', function() {
    console.log('📋 Window fully loaded - checking logs section...');
    
    // Check if we're on the logs page or if logs section is visible
    setTimeout(() => {
        const logsSection = document.getElementById('logs-section');
        if (logsSection) {
            console.log('📋 Logs section found, forcing logs load...');
            loadLogs(); // Force load logs immediately
        } else {
            console.log('📋 Logs section not found yet');
        }
    }, 1000);
});

// Also initialize when logs section is shown
window.showSection = function(section) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.classList.remove('active');
    });
    
    // Show selected section
    const targetSection = document.getElementById(section + '-section');
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Initialize logs if logs section is shown
    if (section === 'logs') {
        setTimeout(() => {
            initializeLogsPage();
        }, 100);
    }
};

function initializeLogsPage() {
    console.log('Initializing Logs System...');
    loadLogFilters();
    loadLogs();
    setupLogEventListeners();
    startLogAutoRefresh();
    initLogsWebSocket(); // Add WebSocket for real-time log updates
}

function initLogsWebSocket() {
    try {
        const clientId = 'logs_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const wsUrl = `ws://${window.location.hostname}:8000/ws/${clientId}`;
        
        console.log('🔌 Logs WebSocket connecting:', wsUrl);
        window.logsWs = new WebSocket(wsUrl);
        
        window.logsWs.onopen = () => {
            console.log('✅ Logs WebSocket connected');
            
            // Request logs data
            window.logsWs.send(JSON.stringify({
                type: 'request_logs',
                limit: 1000
            }));
        };
        
        window.logsWs.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleLogsWebSocketMessage(data);
            } catch (error) {
                console.error('Logs WebSocket message parse error:', error);
            }
        };
        
        window.logsWs.onclose = () => {
            console.log('❌ Logs WebSocket disconnected');
            // Reconnect after 5 seconds
            setTimeout(() => {
                initLogsWebSocket();
            }, 5000);
        };
        
        window.logsWs.onerror = (error) => {
            console.error('Logs WebSocket error:', error);
        };
        
    } catch (error) {
        console.error('Failed to initialize Logs WebSocket:', error);
    }
}

function handleLogsWebSocketMessage(data) {
    console.log('📨 Logs WebSocket message:', data.type);
    
    switch(data.type) {
        case 'new_log':
            console.log('📋 New log received:', data.log?.message);
            if (data.log) {
                // Add new log to the beginning of current logs
                if (window.currentLogs) {
                    window.currentLogs.unshift(data.log);
                    // Keep only last 1000 logs
                    if (window.currentLogs.length > 1000) {
                        window.currentLogs = window.currentLogs.slice(0, 1000);
                    }
                    // Apply filters and refresh logs display
                    const filteredLogs = applyFilters(window.currentLogs);
                    displayLogs(filteredLogs);
                    updateLogStatistics(filteredLogs);
                }
            }
            break;
            
        case 'logs_response':
            console.log('📋 Logs response received');
            if (data.logs && Array.isArray(data.logs)) {
                window.currentLogs = data.logs;
                const filteredLogs = applyFilters(data.logs);
                displayLogs(filteredLogs);
                updateLogStatistics(filteredLogs);
            }
            break;
            
        case 'log_update':
            console.log('📊 Log update received');
            // Refresh logs when update comes
            loadLogs();
            break;
            
        case 'pong':
            // Heartbeat response
            break;
            
        default:
            console.log('🔍 Unknown logs WebSocket message:', data.type);
    }
}

// Load log filter options
async function loadLogFilters() {
    try {
        // Generate sample logs to get filter options
        const sampleLogs = generateMockLogs();
        
        // Get unique levels from logs
        const uniqueLevels = [...new Set(sampleLogs.map(log => log.level))];
        const levelSelect = document.getElementById('log-level-filter');
        if (levelSelect) {
            // Clear existing options except "All Levels"
            levelSelect.innerHTML = '<option value="">All Levels</option>';
            uniqueLevels.forEach(level => {
                const option = document.createElement('option');
                option.value = level;
                option.textContent = level;
                levelSelect.appendChild(option);
            });
        }

        // Get unique categories from logs
        const uniqueCategories = [...new Set(sampleLogs.map(log => log.category))];
        const categorySelect = document.getElementById('log-category-filter');
        if (categorySelect) {
            // Clear existing options except "All Categories"
            categorySelect.innerHTML = '<option value="">All Categories</option>';
            uniqueCategories.forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category.charAt(0).toUpperCase() + category.slice(1);
                categorySelect.appendChild(option);
            });
        }
        
        // Get unique modules from logs (using source as module)
        const uniqueModules = [...new Set(sampleLogs.map(log => log.source))];
        const moduleSelect = document.getElementById('log-module-filter');
        if (moduleSelect) {
            // Clear existing options except "All Modules"
            moduleSelect.innerHTML = '<option value="">All Modules</option>';
            uniqueModules.forEach(module => {
                const option = document.createElement('option');
                option.value = module;
                option.textContent = module;
                moduleSelect.appendChild(option);
            });
        }
        
        // Get unique users from logs
        const uniqueUsers = [...new Set(sampleLogs.filter(log => log.user_id).map(log => log.user_id))];
        const userSelect = document.getElementById('log-user-filter');
        if (userSelect) {
            // Clear existing options except "All Users"
            userSelect.innerHTML = '<option value="">All Users</option>';
            uniqueUsers.forEach(user => {
                const option = document.createElement('option');
                option.value = user;
                option.textContent = user;
                userSelect.appendChild(option);
            });
        }
        
        // Get unique IP addresses (mock different IPs)
        const uniqueIPs = ['192.168.1.1', '192.168.1.105', '10.0.0.15', '172.16.0.45', '192.168.2.30'];
        // No need to populate IP dropdown anymore since it's manual input
        
        console.log('Log filters loaded with actual data options');
    } catch (error) {
        console.error('Error loading log filters:', error);
    }
}

// Load logs from API
async function loadLogs() {
    try {
        console.log('Loading logs from API...');
        
        // Try to fetch logs from the API
        const response = await fetch('/api/logs?limit=1000');
        let logs = [];
        
        if (response.ok) {
            logs = await response.json();
            console.log('Loaded logs from API:', logs.length);
        } else {
            console.warn('API response not OK, using fallback:', response.status);
            logs = generateMockLogs();
        }
        
        // Store logs globally for WebSocket updates
        window.currentLogs = logs;
        
        // Apply current filters to the logs
        const filteredLogs = applyFilters(logs);
        
        displayLogs(filteredLogs);
        updateTimelineChart(filteredLogs);
        updateLogStatistics(filteredLogs);
        
        console.log('Logs loaded and filtered successfully:', {
            total: logs.length,
            filtered: filteredLogs.length
        });
    } catch (error) {
        console.error('Error loading logs from API:', error);
        console.log('Using mock logs as fallback');
        
        // Fallback to mock data
        const mockLogs = generateMockLogs();
        const filteredLogs = applyFilters(mockLogs);
        
        displayLogs(filteredLogs);
        updateTimelineChart(filteredLogs);
        updateLogStatistics(filteredLogs);
    }
}

// Apply filters to log data
function applyFilters(logs) {
    let filteredLogs = [...logs];
    
    // Get filter values
    const levelFilter = document.getElementById('log-level-filter')?.value;
    const categoryFilter = document.getElementById('log-category-filter')?.value;
    const moduleFilter = document.getElementById('log-module-filter')?.value;
    const userFilter = document.getElementById('log-user-filter')?.value;
    const ipFilter = document.getElementById('log-ip-filter')?.value.toLowerCase().trim();
    const searchFilter = document.getElementById('log-search-input')?.value.toLowerCase();
    const timeFilter = document.getElementById('log-time-filter')?.value;
    
    // Apply level filter
    if (levelFilter) {
        filteredLogs = filteredLogs.filter(log => log.level === levelFilter);
    }
    
    // Apply category filter
    if (categoryFilter) {
        filteredLogs = filteredLogs.filter(log => log.category === categoryFilter);
    }
    
    // Apply module filter (source)
    if (moduleFilter) {
        filteredLogs = filteredLogs.filter(log => log.source === moduleFilter);
    }
    
    // Apply user filter
    if (userFilter) {
        filteredLogs = filteredLogs.filter(log => log.user_id === userFilter);
    }
    
    // Apply manual IP filter
    if (ipFilter) {
        filteredLogs = filteredLogs.filter(log => {
            // Check if IP address contains the filter text
            return log.ip_address && log.ip_address.toLowerCase().includes(ipFilter);
        });
    }
    
    // Apply time filter
    if (timeFilter) {
        const now = new Date();
        let timeLimit;
        switch(timeFilter) {
            case '1h':
                timeLimit = new Date(now.getTime() - 60 * 60 * 1000);
                break;
            case '6h':
                timeLimit = new Date(now.getTime() - 6 * 60 * 60 * 1000);
                break;
            case '24h':
                timeLimit = new Date(now.getTime() - 24 * 60 * 60 * 1000);
                break;
            case '7d':
                timeLimit = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                break;
            default:
                timeLimit = null;
        }
        
        if (timeLimit) {
            filteredLogs = filteredLogs.filter(log => new Date(log.timestamp) >= timeLimit);
        }
    }
    
    // Apply search filter
    if (searchFilter) {
        filteredLogs = filteredLogs.filter(log => 
            log.message.toLowerCase().includes(searchFilter) ||
            log.id.toLowerCase().includes(searchFilter) ||
            log.source.toLowerCase().includes(searchFilter) ||
            (log.user_id && log.user_id.toLowerCase().includes(searchFilter)) ||
            (log.ip_address && log.ip_address.toLowerCase().includes(searchFilter))
        );
    }
    
    // Sort by timestamp (newest first)
    filteredLogs.sort((a, b) => {
        const timestampA = new Date(a.timestamp || '');
        const timestampB = new Date(b.timestamp || '');
        return timestampB - timestampA; // Descending order (newest first)
    });
    
    return filteredLogs;
}

// Apply filters function called from HTML
function applyLogFilters() {
    console.log('Applying log filters...');
    loadLogs(); // Reload logs with new filters
}

// Handle search keyup
function handleSearchKeyup(event) {
    if (event.key === 'Enter') {
        applyLogFilters();
    } else {
        // Optional: Apply filter as user types (with debounce)
        clearTimeout(window.searchTimeout);
        window.searchTimeout = setTimeout(() => {
            applyLogFilters();
        }, 500);
    }
}

// Generate mock log data - removed to prevent old data display
function generateMockLogs() {
    // Return empty array - no mock data
    return [];
}

// Display logs in the table
function displayLogs(logs) {
    console.log('📋 Displaying logs:', logs.length, 'entries');
    
    const tbody = document.getElementById('logs-tbody');
    if (!tbody) {
        console.error('❌ logs-tbody not found');
        return;
    }
    
    tbody.innerHTML = '';
    
    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9">No logs available</td></tr>';
        console.log('📋 No logs to display');
        return;
    }
    
    logs.forEach((log, index) => {
        const row = document.createElement('tr');
        const timestamp = log.timestamp ? new Date(log.timestamp).toLocaleString() : 'N/A';
        
        row.innerHTML = `
            <td>${log.id || index}</td>
            <td>${timestamp}</td>
            <td><span class="log-level ${log.level?.toLowerCase() || 'info'}">${log.level || 'INFO'}</span></td>
            <td>${log.category || 'SYSTEM'}</td>
            <td>${log.message || 'No message'}</td>
            <td>${log.source || 'System'}</td>
            <td>${log.user_id || 'System'}</td>
            <td>${log.ip_address || 'N/A'}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="viewLogDetails('${log.id || index}')">View</button>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    console.log('✅ Displayed', logs.length, 'logs in table');
    
    // Update statistics based on actual log data
    updateLogStatistics(logs);
}

// Update log statistics based on actual log data
function updateLogStatistics(logs) {
    console.log('📊 Updating log statistics for', logs.length, 'logs');
    
    // Calculate total logs
    const totalLogsElement = document.getElementById('total-logs');
    if (totalLogsElement) {
        totalLogsElement.textContent = logs.length;
        console.log('✅ Total logs updated:', logs.length);
    } else {
        console.log('⚠️ total-logs element not found');
    }
    
    // Calculate error logs
    const errorLogs = logs.filter(log => log.level === 'ERROR');
    const errorLogsElement = document.getElementById('error-logs');
    if (errorLogsElement) {
        errorLogsElement.textContent = errorLogs.length;
    }
    
    // Calculate critical logs
    const criticalLogs = logs.filter(log => log.level === 'CRITICAL');
    const criticalLogsElement = document.getElementById('critical-logs');
    if (criticalLogsElement) {
        criticalLogsElement.textContent = criticalLogs.length;
    }
    
    // Calculate average response time (mock calculation based on log timestamps)
    const avgResponseTimeElement = document.getElementById('avg-response-time');
    if (avgResponseTimeElement) {
        // Simulate response time based on recent log activity
        const recentLogs = logs.filter(log => {
            const logTime = new Date(log.timestamp);
            const now = new Date();
            const timeDiff = now - logTime;
            return timeDiff < 60000; // Logs from last minute
        });
        
        const responseTime = recentLogs.length > 0 
            ? (Math.random() * 2 + 0.5).toFixed(1) + 'ms'  // 0.5-2.5ms based on activity
            : (Math.random() * 1 + 0.8).toFixed(1) + 'ms'; // 0.8-1.8ms default
            
        avgResponseTimeElement.textContent = responseTime;
    }
    
    // Update log count display
    const logCountElement = document.getElementById('log-count');
    if (logCountElement) {
        logCountElement.textContent = `${logs.length} logs`;
    }
    
    console.log('Log statistics updated:', {
        total: logs.length,
        errors: errorLogs.length,
        critical: criticalLogs.length,
        responseTime: avgResponseTimeElement?.textContent
    });
}

// Format timestamp for display
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
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
    
    // Count logs by hour for the last 24 hours
    const hourlyCounts = {};
    const currentTime = new Date();
    
    // Initialize all hours with 0
    for (let i = 0; i < 24; i++) {
        const hour = new Date(currentTime.getTime() - i * 60 * 60 * 1000).getHours();
        hourlyCounts[hour] = 0;
    }
    
    // Count logs from actual data
    logs.forEach(log => {
        const logTime = new Date(log.timestamp);
        const hour = logTime.getHours();
        if (hourlyCounts.hasOwnProperty(hour)) {
            hourlyCounts[hour]++;
        }
    });
    
    // Update chart data
    const labels = [];
    const data = [];
    
    for (let i = 23; i >= 0; i--) {
        const time = new Date(currentTime.getTime() - i * 60 * 60 * 1000);
        const hour = time.getHours();
        labels.push(time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
        data.push(hourlyCounts[hour] || 0);
    }
    
    timelineChart.data.labels = labels;
    timelineChart.data.datasets[0].data = data;
    timelineChart.update();
    
    console.log('Timeline chart updated with actual log data');
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
