// Simple Map Controls with Real-time Updates
class RealTimeMap {
    constructor() {
        this.threats = [];
        this.updateInterval = null;
        this.init();
    }

    init() {
        console.log('Initializing Real-time Map...');
        this.startRealTimeUpdates();
        this.setupEventListeners();
    }

    startRealTimeUpdates() {
        // Update threats every 5 seconds
        this.updateInterval = setInterval(() => {
            this.updateThreats();
        }, 5000);
        
        // Initial load
        this.updateThreats();
    }

    async updateThreats() {
        try {
            // Fetch real alerts from backend
            const response = await fetch('/api/alerts/list?limit=100');
            if (response.ok) {
                const data = await response.json();
                this.threats = data.alerts || [];
                this.updateMapThreats();
            }
        } catch (error) {
            console.log('Using mock threat data for real-time map');
            this.useMockThreats();
        }
    }

    useMockThreats() {
        // Generate dynamic mock threats
        this.threats = [
            {
                id: 1,
                severity: 'critical',
                location: { lat: 40.7128, lng: -74.0060 }, // New York
                title: 'SQL Injection Attack',
                source: '192.168.1.105'
            },
            {
                id: 2,
                severity: 'high',
                location: { lat: 51.5074, lng: -0.1278 }, // London
                title: 'Brute Force Attempt',
                source: '10.0.0.15'
            },
            {
                id: 3,
                severity: 'medium',
                location: { lat: 35.6762, lng: 139.6503 }, // Tokyo
                title: 'Suspicious File Upload',
                source: '172.16.0.45'
            },
            {
                id: 4,
                severity: 'low',
                location: { lat: -33.8688, lng: 151.2093 }, // Sydney
                title: 'Policy Violation',
                source: '192.168.2.30'
            }
        ];
        
        // Add random new threats
        if (Math.random() > 0.7) {
            const newThreat = {
                id: Date.now(),
                severity: ['critical', 'high', 'medium', 'low'][Math.floor(Math.random() * 4)],
                location: { 
                    lat: (Math.random() * 180 - 90), 
                    lng: (Math.random() * 360 - 180) 
                },
                title: ['DDoS Attack', 'Malware Detected', 'Phishing Attempt', 'Unauthorized Access'][Math.floor(Math.random() * 4)],
                source: `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`
            };
            this.threats.push(newThreat);
        }
        
        this.updateMapThreats();
    }

    updateMapThreats() {
        // Remove existing threat indicators
        const existingIndicators = document.querySelectorAll('.threat-indicator');
        existingIndicators.forEach(indicator => indicator.remove());

        // Add new threat indicators
        this.threats.forEach((threat, index) => {
            this.addThreatIndicator(threat, index);
        });

        // Update threat count
        this.updateThreatCount();
    }

    addThreatIndicator(threat, index) {
        const container = document.querySelector('.threat-indicators');
        if (!container) return;

        const indicator = document.createElement('div');
        indicator.className = `threat-indicator ${threat.severity}`;
        indicator.title = `${threat.severity.toUpperCase()} Threat - ${threat.title}\nSource: ${threat.source}`;
        indicator.innerHTML = this.getThreatIcon(threat.severity);
        
        // Random positioning for dynamic effect
        const top = 20 + (index * 15) % 60;
        const left = 10 + (index * 20) % 80;
        indicator.style.cssText = `top: ${top}%; left: ${left}%;`;
        
        // Add click handler
        indicator.addEventListener('click', () => {
            this.showThreatDetails(threat);
        });

        container.appendChild(indicator);
    }

    getThreatIcon(severity) {
        const icons = {
            critical: '<i class="fas fa-exclamation-triangle"></i>',
            high: '<i class="fas fa-shield-alt"></i>',
            medium: '<i class="fas fa-exclamation-circle"></i>',
            low: '<i class="fas fa-info-circle"></i>'
        };
        return icons[severity] || '<i class="fas fa-exclamation"></i>';
    }

    showThreatDetails(threat) {
        const message = `
            <strong>${threat.title}</strong><br>
            Severity: ${threat.severity.toUpperCase()}<br>
            Source: ${threat.source}<br>
            Location: ${threat.location.lat.toFixed(4)}, ${threat.location.lng.toFixed(4)}
        `;
        this.showNotification(message, 'warning');
    }

    updateThreatCount() {
        const counts = {
            critical: this.threats.filter(t => t.severity === 'critical').length,
            high: this.threats.filter(t => t.severity === 'high').length,
            medium: this.threats.filter(t => t.severity === 'medium').length,
            low: this.threats.filter(t => t.severity === 'low').length
        };

        console.log(`Real-time Map Threats: C:${counts.critical} H:${counts.high} M:${counts.medium} L:${counts.low}`);
    }

    showNotification(message, type = 'info') {
        // Create notification
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'warning' ? '#ffa502' : '#00d4ff'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            max-width: 300px;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }

    setupEventListeners() {
        // Listen for real-time updates via WebSocket
        if (window.webSocketIntegration) {
            window.webSocketIntegration.messageHandlers.set('new_threat', (data) => {
                this.threats.push(data.threat);
                this.updateMapThreats();
                this.showNotification(`New threat detected: ${data.threat.title}`, 'warning');
            });
        }
    }

    stop() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Initialize real-time map when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.realTimeMap = new RealTimeMap();
});

// Legacy functions for backward compatibility
function zoomInMap() {
    const iframe = document.querySelector('.map-wrapper iframe');
    if (iframe) {
        iframe.style.transform = 'scale(1.2)';
        setTimeout(() => {
            iframe.style.transform = 'scale(1)';
        }, 300);
    }
}

function zoomOutMap() {
    const iframe = document.querySelector('.map-wrapper iframe');
    if (iframe) {
        iframe.style.transform = 'scale(0.8)';
        setTimeout(() => {
            iframe.style.transform = 'scale(1)';
        }, 300);
    }
}

function resetMap() {
    const iframe = document.querySelector('.map-wrapper iframe');
    if (iframe) {
        iframe.style.transform = 'scale(1)';
        iframe.src = iframe.src;
    }
}

function fullscreenMap() {
    const mapContainer = document.querySelector('.simple-map-container');
    if (mapContainer) {
        if (mapContainer.requestFullscreen) {
            mapContainer.requestFullscreen();
        } else if (mapContainer.webkitRequestFullscreen) {
            mapContainer.webkitRequestFullscreen();
        } else if (mapContainer.msRequestFullscreen) {
            mapContainer.msRequestFullscreen();
        }
    }
}
