// Simple Logs JavaScript - Basic functionality
console.log('📋 logs_simple.js loaded');

// Global variables
let currentLogs = [];
let logsWs = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('📋 DOM ready - initializing logs...');
    
    // Check if logs section exists
    const logsSection = document.getElementById('logs-section');
    if (logsSection) {
        console.log('✅ logs-section found');
        setTimeout(loadLogs, 1000);
    } else {
        console.log('❌ logs-section not found');
    }
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
    
    // Update navigation
    document.querySelectorAll('.nav-tab').forEach(item => {
        item.classList.remove('active');
    });
    
    const activeNavItem = document.querySelector(`[onclick*="showSection('${section}')"]`);
    if (activeNavItem) {
        activeNavItem.classList.add('active');
    }
    
    // Load logs if logs section
    if (section === 'logs') {
        console.log('📋 Loading logs section...');
        loadLogs();
        initLogsWebSocket();
    }
};

// Load logs from API
async function loadLogs() {
    try {
        console.log('🔄 Loading logs from API...');
        
        const response = await fetch('/api/logs?limit=100');
        let logs = [];
        
        if (response.ok) {
            logs = await response.json();
            console.log(`✅ Loaded ${logs.length} logs from API`);
        } else {
            console.error('❌ API response not OK:', response.status);
            logs = [];
        }
        
        // Store globally
        currentLogs = logs;
        
        // Sort logs by timestamp (newest first)
        logs.sort((a, b) => {
            const timeA = new Date(a.timestamp || '');
            const timeB = new Date(b.timestamp || '');
            return timeB - timeA;
        });
        
        // Display logs
        displayLogs(logs);
        
    } catch (error) {
        console.error('❌ Error loading logs:', error);
        displayLogs([]);
    }
}

// Display logs in table
function displayLogs(logs) {
    console.log(`📋 Displaying ${logs.length} logs`);
    
    const tbody = document.getElementById('logs-tbody');
    if (!tbody) {
        console.error('❌ logs-tbody not found');
        return;
    }
    
    tbody.innerHTML = '';
    
    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No logs available</td></tr>';
        return;
    }
    
    logs.forEach((log, index) => {
        const row = document.createElement('tr');
        
        const timestamp = log.timestamp ? new Date(log.timestamp).toLocaleString() : 'N/A';
        const level = log.level || 'INFO';
        const message = log.message || 'No message';
        const module = log.module || 'system';
        const ip = log.ip_address || 'N/A';
        
        row.innerHTML = `
            <td>${timestamp}</td>
            <td><span class="level-badge level-${level.toLowerCase()}">${level}</span></td>
            <td>${module}</td>
            <td>${message}</td>
            <td>${ip}</td>
            <td>
                <button class="btn btn-sm btn-info" onclick="showLogDetails(${index})">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
    
    console.log('✅ Logs displayed successfully');
}

// Initialize WebSocket for real-time updates
function initLogsWebSocket() {
    try {
        // Close existing connection if any
        if (logsWs) {
            console.log('🔌 Closing existing WebSocket connection');
            logsWs.close();
            logsWs = null;
        }
        
        // Prevent multiple connections
        if (window.logsWsConnecting) {
            console.log('🔌 WebSocket connection already in progress');
            return;
        }
        
        window.logsWsConnecting = true;
        
        const clientId = 'logs_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const wsUrl = `ws://${window.location.hostname}:8000/ws/${clientId}`;
        
        console.log('🔌 Connecting WebSocket:', wsUrl);
        logsWs = new WebSocket(wsUrl);
        
        logsWs.onopen = function() {
            console.log('✅ WebSocket connected');
            window.logsWsConnecting = false;
            logsWs.send(JSON.stringify({type: 'get_logs'}));
        };
        
        logsWs.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                console.log('📨 WebSocket message:', data.type);
                
                if (data.type === 'new_log' && data.log) {
                    // Add new log to beginning
                    currentLogs.unshift(data.log);
                    if (currentLogs.length > 1000) {
                        currentLogs = currentLogs.slice(0, 1000);
                    }
                    displayLogs(currentLogs);
                } else if (data.type === 'logs_response' && data.logs) {
                    currentLogs = data.logs;
                    displayLogs(currentLogs);
                }
            } catch (error) {
                console.error('❌ WebSocket message error:', error);
            }
        };
        
        logsWs.onclose = function(event) {
            console.log('❌ WebSocket disconnected', event.code, event.reason);
            window.logsWsConnecting = false;
            logsWs = null;
        };
        
        logsWs.onerror = function(error) {
            console.error('❌ WebSocket error:', error);
            window.logsWsConnecting = false;
        };
        
    } catch (error) {
        console.error('❌ Failed to initialize WebSocket:', error);
    }
}

// Show log details
function showLogDetails(index) {
    const log = currentLogs[index];
    if (log) {
        alert(`Log Details:\n\nTimestamp: ${log.timestamp}\nLevel: ${log.level}\nModule: ${log.module}\nMessage: ${log.message}\nIP: ${log.ip_address}`);
    }
}

// Auto-refresh logs
setInterval(() => {
    if (document.getElementById('logs-section')?.classList.contains('active')) {
        console.log('🔄 Auto-refreshing logs...');
        loadLogs();
    }
}, 30000); // Every 30 seconds

console.log('📋 logs_simple.js initialization complete');
