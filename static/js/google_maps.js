// Google Maps-like Interface JavaScript
class GoogleMapsInterface {
    constructor() {
        this.map = null;
        this.markers = [];
        this.currentZoom = 10;
        this.currentLat = 40.7128;
        this.currentLng = -74.0060;
        this.mapType = 'threat';
        this.layers = {
            threats: true,
            correlations: false,
            reputation: false,
            traffic: false
        };
        this.threatData = [];
        this.isFullscreen = false;
        this.is3D = false;
        
        this.init();
    }

    init() {
        console.log('Initializing Google Maps-like Interface...');
        this.initializeMap();
        this.loadThreatData();
        this.setupEventListeners();
        this.startRealTimeUpdates();
    }

    initializeMap() {
        const mapContainer = document.getElementById('google-style-map');
        if (!mapContainer) {
            console.error('Map container not found');
            return;
        }

        // Ensure container has proper dimensions
        if (mapContainer.offsetWidth === 0 || mapContainer.offsetHeight === 0) {
            // Wait for container to be ready
            setTimeout(() => this.initializeMap(), 100);
            return;
        }

        // Create a simple canvas-based map
        this.map = {
            container: mapContainer,
            canvas: document.createElement('canvas'),
            ctx: null,
            width: mapContainer.offsetWidth,
            height: mapContainer.offsetHeight
        };

        // Setup canvas
        this.map.canvas.width = this.map.width;
        this.map.canvas.height = this.map.height;
        this.map.ctx = this.map.canvas.getContext('2d');
        
        // Clear any existing content
        mapContainer.innerHTML = '';
        mapContainer.appendChild(this.map.canvas);

        // Draw initial map
        this.drawMap();
        
        // Add click handler
        this.map.canvas.addEventListener('click', this.handleMapClick.bind(this));
        
        // Add drag handler
        this.setupMapDragging();
        
        // Add wheel handler for zoom
        this.setupMapZooming();
        
        // Handle window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });
        
        console.log('Map initialized successfully');
    }

    drawMap() {
        const ctx = this.map.ctx;
        const width = this.map.width;
        const height = this.map.height;

        // Clear canvas
        ctx.clearRect(0, 0, width, height);

        // Draw background based on map type
        this.drawMapBackground(ctx, width, height);

        // Draw grid
        this.drawGrid(ctx, width, height);

        // Draw layers
        if (this.layers.threats) this.drawThreatLayer(ctx, width, height);
        if (this.layers.correlations) this.drawCorrelationLayer(ctx, width, height);
        if (this.layers.reputation) this.drawReputationLayer(ctx, width, height);
        if (this.layers.traffic) this.drawTrafficLayer(ctx, width, height);

        // Draw markers
        this.drawMarkers(ctx, width, height);

        // Draw compass
        this.drawCompass(ctx, width, height);
    }

    drawMapBackground(ctx, width, height) {
        switch (this.mapType) {
            case 'threat':
                // Threat map - dark blue gradient with threat zones
                const gradient = ctx.createLinearGradient(0, 0, width, height);
                gradient.addColorStop(0, '#1a237e');
                gradient.addColorStop(0.5, '#283593');
                gradient.addColorStop(1, '#3949ab');
                ctx.fillStyle = gradient;
                ctx.fillRect(0, 0, width, height);
                
                // Add some texture
                for (let i = 0; i < 50; i++) {
                    ctx.fillStyle = `rgba(26, 35, 126, ${Math.random() * 0.3})`;
                    ctx.fillRect(
                        Math.random() * width,
                        Math.random() * height,
                        Math.random() * 100 + 20,
                        Math.random() * 100 + 20
                    );
                }
                break;
                
            case 'satellite':
                // Satellite view - dark green/brown
                ctx.fillStyle = '#2d5016';
                ctx.fillRect(0, 0, width, height);
                // Add some texture
                for (let i = 0; i < 100; i++) {
                    ctx.fillStyle = `rgba(45, 80, 22, ${Math.random() * 0.3})`;
                    ctx.fillRect(
                        Math.random() * width,
                        Math.random() * height,
                        Math.random() * 50 + 10,
                        Math.random() * 50 + 10
                    );
                }
                break;
                
            case 'terrain':
                // Terrain view - elevation map
                const terrainGradient = ctx.createRadialGradient(width/2, height/2, 0, width/2, height/2, Math.max(width, height)/2);
                terrainGradient.addColorStop(0, '#f5f5dc');
                terrainGradient.addColorStop(0.5, '#d4a574');
                terrainGradient.addColorStop(1, '#8b7355');
                ctx.fillStyle = terrainGradient;
                ctx.fillRect(0, 0, width, height);
                break;
                
            case 'heatmap':
                // Heatmap view - red/yellow gradient
                const heatGradient = ctx.createLinearGradient(0, 0, width, height);
                heatGradient.addColorStop(0, 'rgba(255, 0, 0, 0.4)');
                heatGradient.addColorStop(0.5, 'rgba(255, 255, 0, 0.4)');
                heatGradient.addColorStop(1, 'rgba(255, 0, 0, 0.4)');
                ctx.fillStyle = heatGradient;
                ctx.fillRect(0, 0, width, height);
                break;
                
            default:
                ctx.fillStyle = '#1a237e';
                ctx.fillRect(0, 0, width, height);
        }
    }

    drawGrid(ctx, width, height) {
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
        ctx.lineWidth = 1;
        
        // Draw vertical lines
        for (let x = 0; x < width; x += 50) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height);
            ctx.stroke();
        }
        
        // Draw horizontal lines
        for (let y = 0; y < height; y += 50) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
        }
    }

    drawThreatLayer(ctx, width, height) {
        // Draw threat zones
        this.threatData.forEach(threat => {
            const x = this.lngToX(threat.lng, width);
            const y = this.latToY(threat.lat, height);
            
            // Draw threat radius
            const radius = threat.severity === 'critical' ? 40 : threat.severity === 'high' ? 30 : 20;
            const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
            
            if (threat.severity === 'critical') {
                gradient.addColorStop(0, 'rgba(255, 0, 0, 0.8)');
                gradient.addColorStop(0.5, 'rgba(255, 71, 87, 0.5)');
                gradient.addColorStop(1, 'rgba(255, 71, 87, 0.1)');
            } else if (threat.severity === 'high') {
                gradient.addColorStop(0, 'rgba(255, 165, 0, 0.8)');
                gradient.addColorStop(0.5, 'rgba(255, 165, 2, 0.5)');
                gradient.addColorStop(1, 'rgba(255, 165, 2, 0.1)');
            } else {
                gradient.addColorStop(0, 'rgba(255, 255, 0, 0.8)');
                gradient.addColorStop(0.5, 'rgba(255, 221, 89, 0.5)');
                gradient.addColorStop(1, 'rgba(255, 221, 89, 0.1)');
            }
            
            ctx.fillStyle = gradient;
            ctx.fillRect(x - radius, y - radius, radius * 2, radius * 2);
        });
    }

    drawCorrelationLayer(ctx, width, height) {
        // Draw correlation lines
        ctx.strokeStyle = 'rgba(0, 212, 255, 0.5)';
        ctx.lineWidth = 2;
        
        // Draw some sample correlation lines
        for (let i = 0; i < 5; i++) {
            const x1 = Math.random() * width;
            const y1 = Math.random() * height;
            const x2 = Math.random() * width;
            const y2 = Math.random() * height;
            
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();
            
            // Draw connection points
            ctx.fillStyle = 'rgba(0, 212, 255, 0.8)';
            ctx.beginPath();
            ctx.arc(x1, y1, 3, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(x2, y2, 3, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    drawReputationLayer(ctx, width, height) {
        // Draw reputation zones
        const zones = [
            { x: width * 0.2, y: height * 0.3, radius: 40, color: 'rgba(255, 0, 0, 0.3)' }, // Malicious
            { x: width * 0.7, y: height * 0.6, radius: 35, color: 'rgba(255, 165, 0, 0.3)' }, // Suspicious
            { x: width * 0.5, y: height * 0.8, radius: 45, color: 'rgba(0, 255, 0, 0.3)' }, // Benign
        ];
        
        zones.forEach(zone => {
            ctx.fillStyle = zone.color;
            ctx.beginPath();
            ctx.arc(zone.x, zone.y, zone.radius, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    drawTrafficLayer(ctx, width, height) {
        // Draw traffic flow
        ctx.strokeStyle = 'rgba(255, 255, 0, 0.6)';
        ctx.lineWidth = 3;
        
        // Draw traffic lines
        for (let i = 0; i < 8; i++) {
            const startX = Math.random() * width;
            const startY = Math.random() * height;
            const endX = Math.random() * width;
            const endY = Math.random() * height;
            
            // Draw curved line
            ctx.beginPath();
            ctx.moveTo(startX, startY);
            const cpX = (startX + endX) / 2 + (Math.random() - 0.5) * 100;
            const cpY = (startY + endY) / 2 + (Math.random() - 0.5) * 100;
            ctx.quadraticCurveTo(cpX, cpY, endX, endY);
            ctx.stroke();
        }
    }

    drawMarkers(ctx, width, height) {
        this.threatData.forEach(threat => {
            const x = this.lngToX(threat.lng, width);
            const y = this.latToY(threat.lat, height);
            
            // Draw marker pin
            this.drawPin(ctx, x, y, threat.severity);
        });
    }

    drawPin(ctx, x, y, severity) {
        // Draw pin shadow
        ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        ctx.beginPath();
        ctx.arc(x + 2, y - 8, 8, Math.PI, 0);
        ctx.lineTo(x - 6, y - 8);
        ctx.lineTo(x + 2, y + 7);
        ctx.lineTo(x + 10, y - 8);
        ctx.closePath();
        ctx.fill();
        
        // Draw pin body
        if (severity === 'critical') {
            ctx.fillStyle = '#ff4757';
            ctx.strokeStyle = '#ff6b6b';
        } else if (severity === 'high') {
            ctx.fillStyle = '#ffa502';
            ctx.strokeStyle = '#ff7675';
        } else {
            ctx.fillStyle = '#ffdd59';
            ctx.strokeStyle = '#ffeaa7';
        }
        
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(x, y - 10, 10, Math.PI, 0);
        ctx.lineTo(x - 10, y - 10);
        ctx.lineTo(x, y + 8);
        ctx.lineTo(x + 10, y - 10);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        
        // Draw pin center
        ctx.fillStyle = '#fff';
        ctx.beginPath();
        ctx.arc(x, y - 10, 4, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw inner circle
        if (severity === 'critical') {
            ctx.fillStyle = '#ff4757';
        } else if (severity === 'high') {
            ctx.fillStyle = '#ffa502';
        } else {
            ctx.fillStyle = '#ffdd59';
        }
        ctx.beginPath();
        ctx.arc(x, y - 10, 2, 0, Math.PI * 2);
        ctx.fill();
    }

    drawCompass(ctx, width, height) {
        const compassX = width - 50;
        const compassY = 50;
        const compassRadius = 25;
        
        // Draw compass circle
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(compassX, compassY, compassRadius, 0, Math.PI * 2);
        ctx.stroke();
        
        // Draw compass needle
        ctx.strokeStyle = '#ff4757';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(compassX, compassY);
        ctx.lineTo(compassX, compassY - compassRadius + 5);
        ctx.stroke();
        
        // Draw N
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('N', compassX, compassY - compassRadius - 5);
    }

    handleResize() {
        if (!this.map || !this.map.container) return;
        
        // Update dimensions
        this.map.width = this.map.container.offsetWidth;
        this.map.height = this.map.container.offsetHeight;
        this.map.canvas.width = this.map.width;
        this.map.canvas.height = this.map.height;
        
        // Redraw map
        this.drawMap();
    }

    lngToX(lng, width) {
        // Convert longitude to X coordinate
        return ((lng + 180) / 360) * width;
    }

    latToY(lat, height) {
        // Convert latitude to Y coordinate
        return ((90 - lat) / 180) * height;
    }

    setupMapDragging() {
        let isDragging = false;
        let startX, startY;
        let startLat, startLng;

        this.map.canvas.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            startLat = this.currentLat;
            startLng = this.currentLng;
            this.map.canvas.style.cursor = 'grabbing';
        });

        this.map.canvas.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;
            
            // Update center coordinates
            this.currentLng = startLng - (deltaX / this.map.width) * 360;
            this.currentLat = startLat + (deltaY / this.map.height) * 180;
            
            // Update display
            this.updateCoordinates();
            this.drawMap();
        });

        this.map.canvas.addEventListener('mouseup', () => {
            isDragging = false;
            this.map.canvas.style.cursor = 'grab';
        });

        this.map.canvas.addEventListener('mouseleave', () => {
            isDragging = false;
            this.map.canvas.style.cursor = 'grab';
        });

        this.map.canvas.style.cursor = 'grab';
    }

    setupMapZooming() {
        this.map.canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            
            const delta = e.deltaY > 0 ? -1 : 1;
            const newZoom = Math.max(1, Math.min(20, this.currentZoom + delta));
            
            if (newZoom !== this.currentZoom) {
                this.currentZoom = newZoom;
                this.updateZoomLevel();
                this.drawMap();
            }
        });
    }

    handleMapClick(e) {
        const rect = this.map.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Convert to lat/lng
        const lng = (x / this.map.width) * 360 - 180;
        const lat = 90 - (y / this.map.height) * 180;
        
        // Check if clicked on a threat
        const clickedThreat = this.threatData.find(threat => {
            const threatX = this.lngToX(threat.lng, this.map.width);
            const threatY = this.latToY(threat.lat, this.map.height);
            const distance = Math.sqrt(Math.pow(x - threatX, 2) + Math.pow(y - threatY, 2));
            return distance < 15;
        });
        
        if (clickedThreat) {
            this.showThreatDetails(clickedThreat);
        }
    }

    loadThreatData() {
        // Generate mock threat data
        this.threatData = [
            { id: 1, name: 'Critical Threat Alpha', lat: 40.7128, lng: -74.0060, severity: 'critical', type: 'malware', source: 'US', time: '2 mins ago', status: 'active', description: 'Critical malware detected in New York area with high infection rate' },
            { id: 2, name: 'High Risk Beta', lat: 51.5074, lng: -0.1278, severity: 'high', type: 'phishing', source: 'UK', time: '5 mins ago', status: 'investigating', description: 'Phishing campaign targeting financial institutions in London' },
            { id: 3, name: 'Medium Threat Gamma', lat: 35.6762, lng: 139.6503, severity: 'medium', type: 'botnet', source: 'JP', time: '10 mins ago', status: 'monitoring', description: 'Botnet activity detected in Tokyo region' },
            { id: 4, name: 'Critical Threat Delta', lat: 48.8566, lng: 2.3522, severity: 'critical', type: 'ransomware', source: 'FR', time: '1 min ago', status: 'active', description: 'Ransomware attack in Paris affecting multiple organizations' },
            { id: 5, name: 'Low Risk Epsilon', lat: -33.8688, lng: 151.2093, severity: 'low', type: 'exploit', source: 'AU', time: '15 mins ago', status: 'resolved', description: 'Exploit attempt blocked in Sydney' },
            { id: 6, name: 'High Threat Zeta', lat: 55.7558, lng: 37.6173, severity: 'high', type: 'ddos', source: 'RU', time: '3 mins ago', status: 'active', description: 'DDoS attack targeting Moscow infrastructure' },
            { id: 7, name: 'Medium Threat Eta', lat: 19.4326, lng: -99.1332, severity: 'medium', type: 'malware', source: 'MX', time: '8 mins ago', status: 'investigating', description: 'Malware variant spreading in Mexico City' },
            { id: 8, name: 'Critical Threat Theta', lat: 28.6139, lng: 77.2090, severity: 'critical', type: 'apt', source: 'IN', time: '4 mins ago', status: 'active', description: 'Advanced persistent threat detected in New Delhi' }
        ];
        
        this.updateThreatStatistics();
        this.updateRecentThreats();
    }

    updateThreatStatistics() {
        const stats = {
            critical: this.threatData.filter(t => t.severity === 'critical').length,
            high: this.threatData.filter(t => t.severity === 'high').length,
            medium: this.threatData.filter(t => t.severity === 'medium').length,
            total: this.threatData.length,
            countries: new Set(this.threatData.map(t => t.source)).size
        };
        
        document.getElementById('critical-threats-count').textContent = stats.critical;
        document.getElementById('high-threats-count').textContent = stats.high;
        document.getElementById('medium-threats-count').textContent = stats.medium;
        document.getElementById('total-threats-count').textContent = stats.total;
        document.getElementById('countries-count').textContent = stats.countries;
    }

    updateRecentThreats() {
        const threatsList = document.getElementById('recent-threats-list');
        if (!threatsList) return;
        
        threatsList.innerHTML = '';
        
        const recentThreats = this.threatData.slice(0, 5);
        recentThreats.forEach(threat => {
            const threatItem = document.createElement('div');
            threatItem.className = 'threat-item';
            threatItem.innerHTML = `
                <div class="threat-item-icon ${threat.severity}">
                    ${threat.severity === 'critical' ? '🚨' : threat.severity === 'high' ? '⚠️' : '🔶'}
                </div>
                <div class="threat-item-info">
                    <div class="threat-item-title">${threat.name}</div>
                    <div class="threat-item-time">${threat.time} • ${threat.source}</div>
                </div>
            `;
            
            threatItem.addEventListener('click', () => this.showThreatDetails(threat));
            threatsList.appendChild(threatItem);
        });
    }

    showThreatDetails(threat) {
        const modal = document.getElementById('threat-details-modal');
        if (!modal) return;
        
        // Update modal content
        document.getElementById('modal-threat-title').textContent = threat.name;
        document.getElementById('modal-threat-type').textContent = threat.type;
        document.getElementById('modal-threat-severity').textContent = threat.severity;
        document.getElementById('modal-threat-source').textContent = threat.source;
        document.getElementById('modal-threat-location').textContent = `${threat.lat.toFixed(4)}, ${threat.lng.toFixed(4)}`;
        document.getElementById('modal-threat-time').textContent = threat.time;
        document.getElementById('modal-threat-status').textContent = threat.status;
        document.getElementById('modal-threat-description').textContent = threat.description;
        
        // Show modal
        modal.classList.add('show');
    }

    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('maps-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }
    }

    handleSearch(query) {
        if (!query) return;
        
        // Simple search implementation
        const results = this.threatData.filter(threat => 
            threat.name.toLowerCase().includes(query.toLowerCase()) ||
            threat.type.toLowerCase().includes(query.toLowerCase()) ||
            threat.source.toLowerCase().includes(query.toLowerCase())
        );
        
        console.log('Search results:', results);
        // Could show search results in a dropdown
    }

    updateCoordinates() {
        document.getElementById('current-lat').textContent = this.currentLat.toFixed(4);
        document.getElementById('current-lng').textContent = this.currentLng.toFixed(4);
    }

    updateZoomLevel() {
        document.getElementById('current-zoom').textContent = this.currentZoom;
    }

    updateMapType(type) {
        this.mapType = type;
        document.getElementById('current-map-type').textContent = type.charAt(0).toUpperCase() + type.slice(1);
        this.drawMap();
    }

    startRealTimeUpdates() {
        // Update threat data every 30 seconds
        setInterval(() => {
            this.loadThreatData();
            this.drawMap();
        }, 30000);
    }
}

// Global functions for map controls
let googleMapsInterface;

function zoomIn() {
    if (googleMapsInterface) {
        googleMapsInterface.currentZoom = Math.min(20, googleMapsInterface.currentZoom + 1);
        googleMapsInterface.updateZoomLevel();
        googleMapsInterface.drawMap();
    }
}

function zoomOut() {
    if (googleMapsInterface) {
        googleMapsInterface.currentZoom = Math.max(1, googleMapsInterface.currentZoom - 1);
        googleMapsInterface.updateZoomLevel();
        googleMapsInterface.drawMap();
    }
}

function changeMapType(type) {
    if (googleMapsInterface) {
        // Update button states
        document.querySelectorAll('.map-type-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-type="${type}"]`).classList.add('active');
        
        googleMapsInterface.updateMapType(type);
    }
}

function toggleLayer(layer) {
    if (googleMapsInterface) {
        googleMapsInterface.layers[layer] = !googleMapsInterface.layers[layer];
        
        // Update button states
        const btn = document.querySelector(`[data-layer="${layer}"]`);
        if (btn) {
            btn.classList.toggle('active');
        }
        
        googleMapsInterface.drawMap();
    }
}

function toggleFullscreen() {
    if (googleMapsInterface) {
        const container = document.querySelector('.google-maps-container');
        if (!document.fullscreenElement) {
            container.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }
}

function toggle3DView() {
    if (googleMapsInterface) {
        googleMapsInterface.is3D = !googleMapsInterface.is3D;
        // Could implement 3D view here
        console.log('3D view toggled:', googleMapsInterface.is3D);
    }
}

function measureDistance() {
    if (googleMapsInterface) {
        // Could implement distance measurement tool
        console.log('Distance measurement tool activated');
    }
}

function getCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
            if (googleMapsInterface) {
                googleMapsInterface.currentLat = position.coords.latitude;
                googleMapsInterface.currentLng = position.coords.longitude;
                googleMapsInterface.updateCoordinates();
                googleMapsInterface.drawMap();
            }
        }, (error) => {
            console.error('Error getting location:', error);
        });
    }
}

function searchMaps() {
    const searchInput = document.getElementById('maps-search');
    if (searchInput && googleMapsInterface) {
        googleMapsInterface.handleSearch(searchInput.value);
    }
}

function toggleVoiceSearch() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById('maps-search').value = transcript;
            searchMaps();
        };
        
        recognition.start();
    } else {
        console.log('Speech recognition not supported');
    }
}

function showThreatFeed() {
    console.log('Threat feed activated');
}

function showAlertZones() {
    console.log('Alert zones activated');
}

function showSafeZones() {
    console.log('Safe zones activated');
}

function showActivityHeatmap() {
    changeMapType('heatmap');
}

function closeThreatModal() {
    const modal = document.getElementById('threat-details-modal');
    if (modal) {
        modal.classList.remove('show');
    }
}

function investigateThreat() {
    console.log('Investigating threat...');
    closeThreatModal();
}

function blockThreat() {
    console.log('Blocking threat...');
    closeThreatModal();
}

function shareThreat() {
    console.log('Sharing threat...');
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    googleMapsInterface = new GoogleMapsInterface();
    window.googleMapsInterface = googleMapsInterface;
});
