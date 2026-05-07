// Maps JavaScript - Interactive Global Threat Map
let mapWebSocket = null;
let threatData = [];
let mapInitialized = false;

// Initialize maps page
document.addEventListener('DOMContentLoaded', function() {
    console.log('🗺️ Maps.js loaded - DOM ready');
    
    setTimeout(() => {
        initializeMapsPage();
        initMapsWebSocket();
    }, 1000);
});

// Also initialize when maps section is shown
window.addEventListener('load', function() {
    console.log('🗺️ Window fully loaded - checking maps section...');
    
    setTimeout(() => {
        const mapsSection = document.getElementById('maps-section');
        if (mapsSection) {
            console.log('🗺️ Maps section found, initializing...');
            initializeMapsPage();
        }
    }, 1500);
});

function initializeMapsPage() {
    console.log('🗺️ Initializing maps page...');
    
    // Load initial map data
    loadMapData();
    
    // Load geographic distribution
    loadGeographicDistribution();
    
    // Load threat statistics
    loadMapStatistics();
    
    // Start auto-refresh
    startMapAutoRefresh();
    
    console.log('🗺️ Maps page initialized');
}

async function loadMapData() {
    try {
        console.log('🗺️ Loading map threat data...');
        
        const response = await fetch('/api/maps/threats');
        if (response.ok) {
            const data = await response.json();
            threatData = data.threats || [];
            console.log(`🗺️ Loaded ${threatData.length} threats for map`);
            
            // Update threat indicators on map
            updateThreatIndicators();
            
            // Update map statistics
            updateMapStatistics(null);
        } else {
            console.error('🗺️ Failed to load map data:', response.status);
        }
    } catch (error) {
        console.error('🗺️ Error loading map data:', error);
    }
}

async function loadGeographicDistribution() {
    try {
        console.log('🗺️ Loading geographic distribution...');
        
        const response = await fetch('/api/maps/threats/summary');
        if (response.ok) {
            const summary = await response.json();
            updateGeographicTable(summary);
        } else {
            console.error('🗺️ Failed to load geographic distribution:', response.status);
        }
    } catch (error) {
        console.error('🗺️ Error loading geographic distribution:', error);
    }
}

async function loadMapStatistics() {
    try {
        console.log('🗺️ Loading map statistics...');
        
        const response = await fetch('/api/maps/threats/summary');
        if (response.ok) {
            const stats = await response.json();
            updateMapStatistics(stats);
        } else {
            console.error('🗺️ Failed to load map statistics:', response.status);
        }
    } catch (error) {
        console.error('🗺️ Error loading map statistics:', error);
    }
}

function updateThreatIndicators() {
    console.log('🗺️ Updating threat indicators...');
    
    // Clear existing indicators
    const indicatorsContainer = document.querySelector('.threat-indicators');
    if (indicatorsContainer) {
        indicatorsContainer.innerHTML = '';
        
        // Add new threat indicators
        threatData.forEach(threat => {
            const indicator = document.createElement('div');
            indicator.className = `threat-indicator ${threat.severity}`;
            indicator.style.position = 'absolute';
            
            // Convert lat/lng to percentage positions on map
            const lat = threat.latitude || 0;
            const lon = threat.longitude || 0;
            
            // Simple conversion (this would need proper map projection in real implementation)
            const top = ((90 - lat) / 180) * 100;
            const left = ((lon + 180) / 360) * 100;
            
            indicator.style.top = `${top}%`;
            indicator.style.left = `${left}%`;
            indicator.style.color = getSeverityColor(threat.severity);
            indicator.style.fontSize = '1.5rem';
            indicator.style.cursor = 'pointer';
            indicator.style.pointerEvents = 'auto';
            indicator.title = `${threat.severity?.toUpperCase()} Threat - ${threat.country || 'Unknown'}: ${threat.threat_type || 'Unknown'}`;
            
            // Add click handler
            indicator.addEventListener('click', () => showThreatDetails(threat));
            
            indicatorsContainer.appendChild(indicator);
        });
        
        console.log(`🗺️ Added ${threatData.length} threat indicators to map`);
    }
}

function updateGeographicTable(summary) {
    console.log('🗺️ Updating geographic distribution table...');
    
    const tbody = document.getElementById('geo-tbody');
    if (tbody) {
        tbody.innerHTML = '';
        
        // Create sample geographic data based on summary
        const countries = [
            { name: 'United States', flag: '🇺🇸', threat_level: 'Critical', attacks: summary.critical_threats || 0, sources: 45, target: 'Web Server Cluster', last_activity: '2 mins ago' },
            { name: 'China', flag: '🇨🇳', threat_level: 'High', attacks: summary.high_threats || 0, sources: 32, target: 'Database Server', last_activity: '5 mins ago' },
            { name: 'Russia', flag: '🇷🇺', threat_level: 'High', attacks: summary.high_threats || 0, sources: 28, target: 'API Gateway', last_activity: '3 mins ago' },
            { name: 'North Korea', flag: '🇰🇵', threat_level: 'Medium', attacks: summary.medium_threats || 0, sources: 15, target: 'File Server', last_activity: '8 mins ago' },
            { name: 'Iran', flag: '🇮🇷', threat_level: 'Medium', attacks: summary.medium_threats || 0, sources: 12, target: 'Email Server', last_activity: '12 mins ago' }
        ];
        
        countries.forEach(country => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${country.flag} ${country.name}</td>
                <td><span class="ip-tag ${country.threat_level.toLowerCase()}">${country.threat_level}</span></td>
                <td>${country.attacks}</td>
                <td>${country.sources}</td>
                <td>${country.target}</td>
                <td>${country.last_activity}</td>
            `;
            tbody.appendChild(row);
        });
        
        console.log('🗺️ Geographic distribution table updated');
    }
}

function updateMapStatistics(stats) {
    console.log('🗺️ Updating map statistics...');
    
    // Update KPI cards
    const activeThreatsEl = document.getElementById('map-active-threats');
    if (activeThreatsEl) {
        const threatCount = stats?.total_threats || threatData.length || 0;
        activeThreatsEl.textContent = threatCount;
    }
    
    const countriesEl = document.getElementById('map-countries');
    if (countriesEl) {
        const countryCount = stats?.top_countries?.length || 5;
        countriesEl.textContent = countryCount;
    }
    
    const sourcesEl = document.getElementById('map-sources');
    if (sourcesEl) {
        sourcesEl.textContent = Math.floor(Math.random() * 50) + 20; // Mock data
    }
    
    const targetsEl = document.getElementById('map-targets');
    if (targetsEl) {
        targetsEl.textContent = Math.floor(Math.random() * 15) + 5; // Mock data
    }
    
    console.log('🗺️ Map statistics updated');
}

function getSeverityColor(severity) {
    const colors = {
        'critical': 'var(--status-critical)',
        'high': 'var(--status-high)',
        'medium': 'var(--status-medium)',
        'low': 'var(--status-low)'
    };
    return colors[severity] || 'var(--status-low)';
}

function showThreatDetails(threat) {
    console.log('🗺️ Showing threat details:', threat);
    
    // Create modal or popup with threat details
    const modal = document.createElement('div');
    modal.className = 'threat-details-modal';
    modal.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        padding: 1.5rem;
        z-index: 1000;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        max-width: 400px;
    `;
    
    modal.innerHTML = `
        <h3 style="margin: 0 0 1rem 0; color: var(--text-primary);">
            <i class="fas fa-exclamation-triangle" style="color: ${getSeverityColor(threat.severity)};"></i>
            ${threat.threat_type?.toUpperCase() || 'UNKNOWN'} THREAT
        </h3>
        <div style="color: var(--text-secondary);">
            <p><strong>Location:</strong> ${threat.city || 'Unknown'}, ${threat.country || 'Unknown'}</p>
            <p><strong>Severity:</strong> <span style="color: ${getSeverityColor(threat.severity)}">${threat.severity?.toUpperCase()}</span></p>
            <p><strong>Threat Actor:</strong> ${threat.threat_actor || 'Unknown'}</p>
            <p><strong>Confidence:</strong> ${threat.confidence || 0}%</p>
            <p><strong>Affected Assets:</strong> ${threat.affected_assets || 0}</p>
            <p><strong>First Seen:</strong> ${new Date(threat.first_seen).toLocaleString()}</p>
        </div>
        <button onclick="this.parentElement.remove()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 0.25rem; color: var(--text-primary); cursor: pointer;">Close</button>
    `;
    
    document.body.appendChild(modal);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (modal.parentElement) {
            modal.remove();
        }
    }, 10000);
}

function initMapsWebSocket() {
    console.log('🗺️ Initializing maps WebSocket...');
    
    try {
        // Create WebSocket connection
        const wsUrl = `ws://${window.location.host}/ws/maps_${Date.now()}`;
        mapWebSocket = new WebSocket(wsUrl);
        
        mapWebSocket.onopen = function(event) {
            console.log('🗺️ Maps WebSocket connected');
        };
        
        mapWebSocket.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                handleMapsWebSocketMessage(data);
            } catch (error) {
                console.error('🗺️ Error parsing WebSocket message:', error);
            }
        };
        
        mapWebSocket.onclose = function(event) {
            console.log('🗺️ Maps WebSocket disconnected');
            // Try to reconnect after 5 seconds
            setTimeout(initMapsWebSocket, 5000);
        };
        
        mapWebSocket.onerror = function(error) {
            console.error('🗺️ Maps WebSocket error:', error);
        };
        
    } catch (error) {
        console.error('🗺️ Failed to initialize maps WebSocket:', error);
    }
}

function handleMapsWebSocketMessage(data) {
    if (data.type === 'geo_threat') {
        console.log('🗺️ Received new geo threat:', data.data);
        
        // Add new threat to data
        threatData.unshift(data.data);
        
        // Keep only last 50 threats
        if (threatData.length > 50) {
            threatData = threatData.slice(0, 50);
        }
        
        // Update map indicators
        updateThreatIndicators();
        
        // Update statistics
        updateMapStatistics();
        
        // Show notification for critical threats
        if (data.data.severity === 'critical') {
            showThreatNotification(data.data);
        }
    }
}

function showThreatNotification(threat) {
    console.log('🗺️ Showing threat notification for critical threat');
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = 'threat-notification';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--status-critical);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        z-index: 1001;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        max-width: 300px;
        animation: slideInFromRight 0.3s ease-out;
    `;
    
    notification.innerHTML = `
        <h4 style="margin: 0 0 0.5rem 0;">🚨 CRITICAL THREAT DETECTED</h4>
        <p style="margin: 0; font-size: 0.875rem;">
            ${threat.threat_type?.toUpperCase()} in ${threat.city || 'Unknown'}, ${threat.country || 'Unknown'}
        </p>
        <button onclick="this.parentElement.remove()" style="margin-top: 0.5rem; padding: 0.25rem 0.5rem; background: rgba(255,255,255,0.2); border: none; border-radius: 0.25rem; color: white; cursor: pointer; font-size: 0.75rem;">Dismiss</button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 8 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 8000);
}

function startMapAutoRefresh() {
    console.log('🗺️ Starting map auto-refresh...');
    
    // Refresh map data every 30 seconds
    setInterval(() => {
        loadMapData();
        loadGeographicDistribution();
    }, 30000);
}

// Map control functions
function zoomInMap() {
    console.log('🗺️ Zooming in map...');
    // Implement map zoom functionality
}

function zoomOutMap() {
    console.log('🗺️ Zooming out map...');
    // Implement map zoom functionality
}

function resetMap() {
    console.log('🗺️ Resetting map...');
    // Implement map reset functionality
    loadMapData();
}

function refreshMapData() {
    console.log('🗺️ Refreshing map data...');
    loadMapData();
    loadGeographicDistribution();
    loadMapStatistics();
}

// Add CSS animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInFromRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .threat-indicator {
        transition: all 0.2s ease;
        animation: pulse 2s infinite;
    }
    
    .threat-indicator:hover {
        transform: scale(1.2);
        filter: brightness(1.2);
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }
`;
document.head.appendChild(style);

console.log('🗺️ Maps JavaScript loaded successfully');
