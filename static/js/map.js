// Simple Map - Clean and Working
class SimpleMap {
    constructor() {
        this.threats = [
            {id: 1, name: "DDoS Attack", level: "critical", country: "USA", x: 20, y: 35},
            {id: 2, name: "Malware", level: "high", country: "UK", x: 45, y: 30},
            {id: 3, name: "Phishing", level: "medium", country: "Japan", x: 80, y: 40},
            {id: 4, name: "Data Breach", level: "critical", country: "Australia", x: 85, y: 75},
            {id: 5, name: "Suspicious", level: "low", country: "Russia", x: 55, y: 20}
        ];
        this.init();
    }

    init() {
        this.createMap();
        this.addMarkers();
        this.updateStats();
    }

    createMap() {
        const mapDiv = document.getElementById('simple-map');
        if (!mapDiv) return;

        mapDiv.innerHTML = `
            <div class="simple-map-container">
                <div class="map-canvas">
                    <div class="world-bg"></div>
                    <div class="markers-layer"></div>
                </div>
                <div class="map-header">
                    <h3>🌍 Global Threat Map</h3>
                    <div class="map-stats">
                        <span>🚨 ${this.threats.length} Threats</span>
                        <span>🌍 ${this.threats.length} Countries</span>
                    </div>
                </div>
                <div class="map-controls">
                    <button onclick="zoomIn()">🔍</button>
                    <button onclick="zoomOut()">🔍</button>
                    <button onclick="resetMap()">🏠</button>
                </div>
            </div>
        `;
    }

    addMarkers() {
        const markersLayer = document.querySelector('.markers-layer');
        if (!markersLayer) return;

        markersLayer.innerHTML = this.threats.map(threat => `
            <div class="threat-marker ${threat.level}" 
                 style="left: ${threat.x}%; top: ${threat.y}%"
                 onclick="showThreat(${threat.id})"
                 title="${threat.name}">
                <div class="marker-dot"></div>
            </div>
        `).join('');
    }

    updateStats() {
        const critical = this.threats.filter(t => t.level === 'critical').length;
        const high = this.threats.filter(t => t.level === 'high').length;
        const medium = this.threats.filter(t => t.level === 'medium').length;

        const criticalEl = document.getElementById('critical-threats-count');
        const highEl = document.getElementById('high-threats-count');
        const mediumEl = document.getElementById('medium-threats-count');
        const totalEl = document.getElementById('total-threats-count');
        const countriesEl = document.getElementById('countries-count');

        if (criticalEl) criticalEl.textContent = critical;
        if (highEl) highEl.textContent = high;
        if (mediumEl) mediumEl.textContent = medium;
        if (totalEl) totalEl.textContent = this.threats.length;
        if (countriesEl) countriesEl.textContent = this.threats.length;
    }

    zoomIn() {
        const map = document.querySelector('.world-bg');
        if (map) {
            const scale = parseFloat(map.style.transform.replace('scale(', '').replace(')', '') || '1');
            map.style.transform = `scale(${Math.min(scale + 0.2, 2)})`;
        }
    }

    zoomOut() {
        const map = document.querySelector('.world-bg');
        if (map) {
            const scale = parseFloat(map.style.transform.replace('scale(', '').replace(')', '') || '1');
            map.style.transform = `scale(${Math.max(scale - 0.2, 0.5)})`;
        }
    }

    resetMap() {
        const map = document.querySelector('.world-bg');
        if (map) map.style.transform = 'scale(1)';
    }
}

// Global functions
let simpleMap;

document.addEventListener('DOMContentLoaded', () => {
    simpleMap = new SimpleMap();
});

function zoomIn() { if (simpleMap) simpleMap.zoomIn(); }
function zoomOut() { if (simpleMap) simpleMap.zoomOut(); }
function resetMap() { if (simpleMap) simpleMap.resetMap(); }

function showThreat(id) {
    const threat = simpleMap.threats.find(t => t.id === id);
    if (!threat) return;

    const panel = document.getElementById('threat-details-panel');
    if (panel) {
        document.getElementById('threat-title').textContent = threat.name;
        document.getElementById('threat-description').textContent = `Threat detected in ${threat.country}`;
        document.getElementById('threat-severity').textContent = threat.level.toUpperCase();
        document.getElementById('threat-type').textContent = 'SECURITY ALERT';
        document.getElementById('threat-source').textContent = 'Threat Intel';
        document.getElementById('threat-time').textContent = new Date().toLocaleString();
        panel.classList.add('active');
        window.currentThreat = threat;
    }
}

function closeThreatPanel() {
    const panel = document.getElementById('threat-details-panel');
    if (panel) panel.classList.remove('active');
}

function investigateThreat(id) {
    console.log('Investigating:', id);
    showSection('alerts');
}

function blockThreat() {
    if (window.currentThreat) {
        console.log('Blocked:', window.currentThreat.id);
        closeThreatPanel();
    }
}

function showSection(section) {
    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
    const target = document.getElementById(section + '-section');
    if (target) target.classList.add('active');
}
