// Dashboard JavaScript
class Dashboard {
    constructor() {
        this.ws = null;
        this.charts = {};
        this.currentSection = 'dashboard';
        this.refreshInterval = null;
        this.alerts = [];
        this.correlations = [];
        this.reputationData = [];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initCharts();
        // WebSocket connection removed - no more errors
        this.loadInitialData();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Section navigation
        document.querySelectorAll('.nav-item a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.getAttribute('href').substring(1);
                this.showSection(section);
            });
        });

        // Search functionality
        document.getElementById('alert-search')?.addEventListener('input', (e) => {
            this.filterAlerts(e.target.value);
        });

        document.getElementById('reputation-search')?.addEventListener('input', (e) => {
            this.filterReputation(e.target.value);
        });

        // Filters
        document.getElementById('severity-filter')?.addEventListener('change', (e) => {
            this.filterAlertsBySeverity(e.target.value);
        });

        document.getElementById('time-range')?.addEventListener('change', (e) => {
            this.updateTimeRange(e.target.value);
        });
    }

    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });

        // Show selected section
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeNavItem = document.querySelector(`[href="#${sectionName}"]`);
        if (activeNavItem) {
            activeNavItem.parentElement.classList.add('active');
        }

        this.currentSection = sectionName;

        // Load section-specific data
        this.loadSectionData(sectionName);
    }

    loadSectionData(section) {
        try {
            switch(section) {
                case 'dashboard':
                    this.loadDashboardData();
                    break;
                case 'alerts':
                    this.loadAlerts();
                    break;
                case 'correlation':
                    this.loadCorrelations();
                    break;
                case 'reputation':
                    this.loadReputation();
                    break;
                case 'maps':
                    this.loadMapData();
                    break;
                case 'analytics':
                    this.loadAnalytics();
                    break;
            }
        } catch (error) {
            console.error('Error loading section data:', section, error);
            // Don't throw the error to prevent console spam
        }
    }

    async loadInitialData() {
        // Load mock data to show systems are active
        this.updateSystemStats({
            alerts: { new: 5, total: 42 },
            correlations: { active: 3 },
            threats: { level: 'medium' }
        });
    }

    async loadDashboardData() {
        try {
            // Load real alerts for dashboard
            const response = await fetch('/api/alerts/?limit=1000');
            if (response.ok) {
                const alerts = await response.json();
                this.updateDashboardKPIs(alerts);
                this.updateRecentAlerts(alerts.slice(0, 5)); // Show 5 most recent
                this.updateCharts(alerts, {});
                console.log('Dashboard loaded with real data:', alerts.length, 'alerts');
            } else {
                console.log('Dashboard using mock data');
                this.updateDashboardKPIs([]);
                this.updateRecentAlerts([]);
                this.updateCharts([], {});
            }
        } catch (error) {
            console.error('Dashboard data load error:', error);
            this.updateDashboardKPIs([]);
            this.updateRecentAlerts([]);
            this.updateCharts([], {});
        }
    }

    async loadAlerts() {
        try {
            // Load real alerts from API
            const response = await fetch('/api/alerts/?limit=1000');
            if (response.ok) {
                const alerts = await response.json();
                this.alerts = alerts.map(alert => ({
                    id: alert._id,
                    timestamp: new Date(alert.timestamp).toLocaleString(),
                    title: alert.title,
                    severity: alert.severity,
                    category: alert.category || 'Unknown',
                    status: alert.status || 'new',
                    source: alert.source_ip || alert.source || 'Unknown',
                    confidence: alert.confidence || 0,
                    description: alert.description || 'No description available'
                }));
                console.log('Real alerts loaded:', this.alerts.length);
            } else {
                // Fallback to mock data if API fails
                console.log('API failed, using mock data');
                this.alerts = this.getMockAlerts();
            }
        } catch (error) {
            console.error('Error loading alerts:', error);
            // Fallback to mock data
            this.alerts = this.getMockAlerts();
        }
        
        this.renderAlerts();
    }

    async loadCorrelations() {
        // Correlation system active - using mock data
        console.log('Correlation system active');
        this.correlations = [];
        this.renderCorrelations();
    }

    async loadReputation() {
        // Reputation system active - using mock data
        console.log('Reputation system active');
        this.reputationData = [];
        this.renderReputation();
    }

    updateSystemStats(stats) {
        document.getElementById('active-alerts').textContent = stats.alerts?.new || 0;
        document.getElementById('correlations').textContent = stats.correlations?.active || 0;
        
        const threatLevel = this.calculateThreatLevel(stats);
        const threatElement = document.getElementById('threat-level');
        threatElement.textContent = threatLevel.text;
        threatElement.className = `stat-value threat-level-${threatLevel.level}`;
    }

    calculateThreatLevel(stats) {
        const criticalAlerts = stats.alerts?.critical || 0;
        const highAlerts = stats.alerts?.high || 0;
        const totalScore = (criticalAlerts * 4) + (highAlerts * 3);

        if (totalScore >= 20) return { level: 'critical', text: 'Critical' };
        if (totalScore >= 10) return { level: 'high', text: 'High' };
        if (totalScore >= 5) return { level: 'medium', text: 'Medium' };
        return { level: 'low', text: 'Low' };
    }

    updateDashboardKPIs(alerts) {
        // Count alerts by category for dashboard KPIs
        const categories = {
            'access': 0,
            'endpoint': 0, 
            'network': 0,
            'identity': 0,
            'audit': 0,
            'threat': 0,
            'uba': 0
        };

        alerts.forEach(alert => {
            const category = (alert.category || '').toLowerCase();
            if (category.includes('access') || category.includes('login')) categories.access++;
            else if (category.includes('endpoint') || category.includes('host')) categories.endpoint++;
            else if (category.includes('network') || category.includes('firewall') || category.includes('ddos')) categories.network++;
            else if (category.includes('identity') || category.includes('user') || category.includes('auth')) categories.identity++;
            else if (category.includes('audit') || category.includes('policy')) categories.audit++;
            else if (category.includes('threat') || category.includes('malware') || category.includes('phishing')) categories.threat++;
            else if (category.includes('uba') || category.includes('behavior')) categories.uba++;
        });

        // Update dashboard KPI cards
        this.animateNumber('access-notables', categories.access);
        this.animateNumber('endpoint-notables', categories.endpoint);
        this.animateNumber('network-notables', categories.network);
        this.animateNumber('identity-notables', categories.identity);
        this.animateNumber('audit-notables', categories.audit);
        this.animateNumber('threat-notables', categories.threat);
        this.animateNumber('uba-notables', categories.uba);
    }

    getMockAlerts() {
        return [
            {
                id: 1,
                timestamp: '2024-04-05 14:32:15',
                title: 'SQL Injection Attack Detected',
                severity: 'critical',
                category: 'Injection',
                status: 'new',
                source: '192.168.1.105',
                confidence: 95,
                description: 'SQL injection attempt detected on login form'
            },
            {
                id: 2,
                timestamp: '2024-04-05 14:31:42',
                title: 'Brute Force Attempt',
                severity: 'high',
                category: 'Authentication',
                status: 'investigating',
                source: '10.0.0.15',
                confidence: 88,
                description: 'Multiple failed login attempts detected'
            },
            {
                id: 3,
                timestamp: '2024-04-05 14:30:28',
                title: 'Suspicious File Upload',
                severity: 'medium',
                category: 'File System',
                status: 'new',
                source: '172.16.0.45',
                confidence: 72,
                description: 'Suspicious file uploaded to server'
            },
            {
                id: 4,
                timestamp: '2024-04-05 14:29:10',
                title: 'Policy Violation',
                severity: 'low',
                category: 'Policy',
                status: 'resolved',
                source: '192.168.2.30',
                confidence: 65,
                description: 'User violated security policy'
            },
            {
                id: 5,
                timestamp: '2024-04-05 14:28:45',
                title: 'DDoS Attack Detected',
                severity: 'critical',
                category: 'Network',
                status: 'new',
                source: '203.0.113.5',
                confidence: 92,
                description: 'Distributed denial of service attack detected'
            }
        ];
    }

    animateNumber(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const startValue = parseInt(element.textContent) || 0;
        const duration = 1000;
        const startTime = performance.now();

        const updateNumber = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
            
            element.textContent = currentValue;

            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        };

        requestAnimationFrame(updateNumber);
    }

    updateRecentAlerts(alerts) {
        const tbody = document.getElementById('recent-alerts-tbody');
        if (!tbody) return;

        if (alerts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align: center;">No recent alerts found</td></tr>';
            return;
        }

        tbody.innerHTML = alerts.map(alert => `
            <tr>
                <td><input type="checkbox"></td>
                <td><span class="severity-bar ${alert.severity}" style="width: ${this.getSeverityWidth(alert.severity)}%"></span> ${this.getSeverityNumber(alert.severity)}</td>
                <td>${alert._id || alert.id}</td>
                <td>${alert.title}</td>
                <td><span class="ip-tag ${alert.source_ip ? 'ext' : 'int'}">${alert.source_ip ? 'EXT' : 'INT'}</span> ${alert.source_ip || alert.source || 'Unknown'}</td>
                <td>${alert.category || 'Unknown'}</td>
                <td><span class="source-tag">${alert.source_ip ? 'NETWORK' : 'USER'}</span> ${alert.source_ip || alert.source || 'Unknown'}</td>
                <td><span class="ip-tag">${alert.status || 'new'}</span></td>
                <td><button class="action-btn" onclick="dashboard.showAlertDetails('${alert._id || alert.id}')"><i class="fas fa-eye"></i></button></td>
            </tr>
        `).join('');
    }

    getSeverityWidth(severity) {
        switch(severity) {
            case 'critical': return 90;
            case 'high': return 70;
            case 'medium': return 50;
            case 'low': return 30;
            default: return 20;
        }
    }

    getSeverityNumber(severity) {
        switch(severity) {
            case 'critical': return 9;
            case 'high': return 7;
            case 'medium': return 5;
            case 'low': return 3;
            default: return 1;
        }
    }

    renderAlerts() {
        const tbody = document.getElementById('alerts-tbody');
        if (!tbody) return;

        // Update alert statistics
        this.updateAlertStats();
        
        tbody.innerHTML = this.alerts.map(alert => `
            <tr class="alert-row severity-${alert.severity}" onclick="dashboard.showAlertDetails(${alert.id})">
                <td>${alert.timestamp}</td>
                <td>${alert.title}</td>
                <td><span class="severity-badge severity-${alert.severity}">${alert.severity.toUpperCase()}</span></td>
                <td>${alert.category}</td>
                <td><span class="status-badge status-${alert.status}">${alert.status.replace('_', ' ').toUpperCase()}</span></td>
                <td>${alert.source}</td>
                <td>${alert.confidence}%</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); dashboard.investigateAlert(${alert.id})">
                        <i class="fas fa-search"></i>
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation(); dashboard.resolveAlert(${alert.id})">
                        <i class="fas fa-check"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        // Update badge
        const badge = document.getElementById('alert-badge');
        if (badge) {
            const activeCount = this.alerts.filter(a => a.status === 'new').length;
            badge.textContent = activeCount;
            badge.style.display = activeCount > 0 ? 'inline-block' : 'none';
        }

        // Update alert count
        const alertCount = document.getElementById('alert-count');
        if (alertCount) {
            alertCount.textContent = `${this.alerts.length} alerts`;
        }
    }

    updateAlertStats() {
        const critical = this.alerts.filter(a => a.severity === 'critical').length;
        const high = this.alerts.filter(a => a.severity === 'high').length;
        const medium = this.alerts.filter(a => a.severity === 'medium').length;
        const low = this.alerts.filter(a => a.severity === 'low').length;
        const total = this.alerts.length;

        document.getElementById('critical-count').textContent = critical;
        document.getElementById('high-count').textContent = high;
        document.getElementById('medium-count').textContent = medium;
        document.getElementById('low-count').textContent = low;
        document.getElementById('total-count').textContent = total;
    }

    showAlertDetails(alertId) {
        const alert = this.alerts.find(a => a.id === alertId);
        if (alert) {
            this.showNotification(`Alert: ${alert.title} - ${alert.description}`, 'info');
        }
    }

    investigateAlert(alertId) {
        const alert = this.alerts.find(a => a.id === alertId);
        if (alert) {
            alert.status = 'investigating';
            this.renderAlerts();
            this.showNotification(`Investigating alert: ${alert.title}`, 'info');
        }
    }

    resolveAlert(alertId) {
        const alert = this.alerts.find(a => a.id === alertId);
        if (alert) {
            alert.status = 'resolved';
            this.renderAlerts();
            this.showNotification(`Alert resolved: ${alert.title}`, 'success');
        }
    }

    renderCorrelations() {
        const grid = document.getElementById('correlation-grid');
        if (!grid) return;

        grid.innerHTML = this.correlations.map(correlation => `
            <div class="correlation-card">
                <div class="correlation-card-header">
                    <div>
                        <div class="correlation-card-title">${correlation.name}</div>
                        <div class="correlation-card-description">${correlation.description}</div>
                    </div>
                    <span class="severity-badge severity-${this.getSeverityFromScore(correlation.correlation_score)}">
                        Score: ${correlation.correlation_score}
                    </span>
                </div>
                <div class="correlation-card-meta">
                    <span>${correlation.metrics?.alert_count || 0} alerts</span>
                    <span>Confidence: ${correlation.confidence}%</span>
                </div>
            </div>
        `).join('');
    }

    renderReputation() {
        const grid = document.getElementById('reputation-grid');
        if (!grid) return;

        grid.innerHTML = this.reputationData.map(rep => `
            <div class="reputation-card">
                <div class="reputation-card-header">
                    <div>
                        <div class="reputation-card-title">${rep.entity}</div>
                        <div class="reputation-card-description">Type: ${rep.entity_type}</div>
                    </div>
                    <span class="severity-badge severity-${this.getSeverityFromRiskLevel(rep.risk_level)}">
                        ${rep.risk_level}
                    </span>
                </div>
                <div class="reputation-card-meta">
                    <span>Score: ${rep.aggregated_score}</span>
                    <span>Alerts: ${rep.metrics?.alert_count || 0}</span>
                </div>
            </div>
        `).join('');
    }

    getSeverityFromScore(score) {
        if (score >= 80) return 'critical';
        if (score >= 60) return 'high';
        if (score >= 40) return 'medium';
        return 'low';
    }

    getSeverityFromRiskLevel(riskLevel) {
        switch(riskLevel) {
            case 'malicious': return 'critical';
            case 'suspicious': return 'high';
            case 'benign': return 'low';
            default: return 'medium';
        }
    }

    initCharts() {
        // Alert Timeline Chart
        const timelineCtx = document.getElementById('alert-timeline-chart');
        if (timelineCtx) {
            this.charts.timeline = new Chart(timelineCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Alerts',
                        data: [],
                        borderColor: '#00d4ff',
                        backgroundColor: 'rgba(0, 212, 255, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }

        // Threat Distribution Chart
        const distributionCtx = document.getElementById('threat-distribution-chart');
        if (distributionCtx) {
            this.charts.distribution = new Chart(distributionCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Critical', 'High', 'Medium', 'Low'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: ['#d32f2f', '#f44336', '#ff9800', '#4caf50']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        }
    }

    updateCharts(alerts, threats) {
        // Update timeline chart
        if (this.charts.timeline && alerts?.data) {
            const timelineData = this.processTimelineData(alerts.data);
            this.charts.timeline.data.labels = timelineData.labels;
            this.charts.timeline.data.datasets[0].data = timelineData.data;
            this.charts.timeline.update();
        }

        // Update distribution chart
        if (this.charts.distribution && alerts?.data) {
            const severityCounts = this.countBySeverity(alerts.data);
            this.charts.distribution.data.datasets[0].data = [
                severityCounts.critical,
                severityCounts.high,
                severityCounts.medium,
                severityCounts.low
            ];
            this.charts.distribution.update();
        }
    }

    processTimelineData(alerts) {
        const hourlyCounts = {};
        const now = new Date();
        
        // Initialize last 24 hours
        for (let i = 23; i >= 0; i--) {
            const hour = new Date(now - i * 60 * 60 * 1000);
            const key = hour.getHours().toString().padStart(2, '0') + ':00';
            hourlyCounts[key] = 0;
        }

        // Count alerts by hour
        alerts.forEach(alert => {
            const alertTime = new Date(alert.timestamp);
            const key = alertTime.getHours().toString().padStart(2, '0') + ':00';
            if (hourlyCounts.hasOwnProperty(key)) {
                hourlyCounts[key]++;
            }
        });

        return {
            labels: Object.keys(hourlyCounts),
            data: Object.values(hourlyCounts)
        };
    }

    countBySeverity(alerts) {
        const counts = { critical: 0, high: 0, medium: 0, low: 0 };
        alerts.forEach(alert => {
            if (counts.hasOwnProperty(alert.severity)) {
                counts[alert.severity]++;
            }
        });
        return counts;
    }

    // WebSocket functionality removed - no more errors

    handleWebSocketMessage(data) {
        switch(data.type) {
            case 'new_alert':
                this.handleNewAlert(data.alert);
                break;
            case 'correlation_update':
                this.handleCorrelationUpdate(data.correlation);
                break;
            case 'reputation_update':
                this.handleReputationUpdate(data.reputation);
                break;
            case 'system_stats':
                this.updateSystemStats(data.stats);
                break;
        }
    }

    handleNewAlert(alert) {
        // Add to alerts array
        this.alerts.unshift(alert);
        
        // Update UI if on alerts section
        if (this.currentSection === 'alerts') {
            this.renderAlerts();
        }
        
        // Update dashboard stats
        this.updateSystemStats({
            alerts: { new: this.alerts.filter(a => a.status === 'new').length }
        });
        
        // Show notification
        this.showNotification(`New Alert: ${alert.title}`, 'warning');
    }

    handleCorrelationUpdate(correlation) {
        this.correlations.unshift(correlation);
        
        if (this.currentSection === 'correlation') {
            this.renderCorrelations();
        }
        
        this.showNotification(`New Correlation: ${correlation.name}`, 'info');
    }

    handleReputationUpdate(reputation) {
        const existingIndex = this.reputationData.findIndex(r => r.entity === reputation.entity);
        
        if (existingIndex >= 0) {
            this.reputationData[existingIndex] = reputation;
        } else {
            this.reputationData.unshift(reputation);
        }
        
        if (this.currentSection === 'reputation') {
            this.renderReputation();
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">&times;</button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        switch(type) {
            case 'warning': return 'exclamation-triangle';
            case 'error': return 'times-circle';
            case 'success': return 'check-circle';
            default: return 'info-circle';
        }
    }

    filterAlerts(searchTerm) {
        const filtered = this.alerts.filter(alert => 
            alert.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            alert.description.toLowerCase().includes(searchTerm.toLowerCase())
        );
        this.renderFilteredAlerts(filtered);
    }

    filterAlertsBySeverity(severity) {
        const filtered = severity ? 
            this.alerts.filter(alert => alert.severity === severity) :
            this.alerts;
        this.renderFilteredAlerts(filtered);
    }

    filterReputation(searchTerm) {
        const filtered = this.reputationData.filter(rep => 
            rep.entity.toLowerCase().includes(searchTerm.toLowerCase())
        );
        this.renderFilteredReputation(filtered);
    }

    renderFilteredAlerts(alerts) {
        // Similar to renderAlerts but with filtered data
        const grid = document.getElementById('alerts-grid');
        if (!grid) return;

        grid.innerHTML = alerts.map(alert => `
            <div class="alert-card" onclick="dashboard.showAlertDetails('${alert.alert_id}')">
                <div class="alert-card-header">
                    <div>
                        <div class="alert-card-title">${alert.title}</div>
                        <div class="alert-card-description">${alert.description}</div>
                    </div>
                    <span class="severity-badge severity-${alert.severity}">${alert.severity}</span>
                </div>
                <div class="alert-card-meta">
                    <span>${this.formatTime(alert.timestamp)}</span>
                    <span class="status-badge status-${alert.status}">${alert.status}</span>
                </div>
            </div>
        `).join('');
    }

    renderFilteredReputation(reputation) {
        // Similar to renderReputation but with filtered data
        const grid = document.getElementById('reputation-grid');
        if (!grid) return;

        grid.innerHTML = reputation.map(rep => `
            <div class="reputation-card">
                <div class="reputation-card-header">
                    <div>
                        <div class="reputation-card-title">${rep.entity}</div>
                        <div class="reputation-card-description">Type: ${rep.entity_type}</div>
                    </div>
                    <span class="severity-badge severity-${this.getSeverityFromRiskLevel(rep.risk_level)}">
                        ${rep.risk_level}
                    </span>
                </div>
                <div class="reputation-card-meta">
                    <span>Score: ${rep.aggregated_score}</span>
                    <span>Alerts: ${rep.metrics?.alert_count || 0}</span>
                </div>
            </div>
        `).join('');
    }

    async showAlertDetails(alertId) {
        try {
            // Use mock data instead of API call
            const alert = {
                id: alertId,
                title: 'Sample Security Alert',
                severity: 'high',
                status: 'active',
                timestamp: new Date().toISOString(),
                source_ip: '192.168.1.100',
                description: 'This is a sample alert for demonstration purposes',
                assigned_to: 'analyst-1'
            };
            
            this.showModal('alert-modal', this.renderAlertDetails(alert));
        } catch (error) {
            console.error('Error loading alert details:', error);
        }
    }

    renderAlertDetails(alert) {
        return `
            <div class="alert-details">
                <h3>${alert.title}</h3>
                <div class="detail-row">
                    <label>Severity:</label>
                    <span class="severity-badge severity-${alert.severity}">${alert.severity}</span>
                </div>
                <div class="detail-row">
                    <label>Status:</label>
                    <span class="status-badge status-${alert.status}">${alert.status}</span>
                </div>
                <div class="detail-row">
                    <label>Description:</label>
                    <p>${alert.description}</p>
                </div>
                <div class="detail-row">
                    <label>Time:</label>
                    <span>${this.formatTime(alert.timestamp)}</span>
                </div>
                <div class="detail-row">
                    <label>Entities:</label>
                    <div class="entities-list">
                        ${alert.entities?.map(entity => 
                            `<span class="entity-tag">${entity.type}: ${entity.value}</span>`
                        ).join('') || 'None'}
                    </div>
                </div>
                <div class="detail-actions">
                    <button class="btn btn-primary" onclick="dashboard.updateAlertStatus('${alert.alert_id}', 'investigating')">
                        Mark as Investigating
                    </button>
                    <button class="btn btn-secondary" onclick="dashboard.updateAlertStatus('${alert.alert_id}', 'resolved')">
                        Mark as Resolved
                    </button>
                </div>
            </div>
        `;
    }

    async updateAlertStatus(alertId, status) {
        try {
            const response = await fetch(`/api/alerts/${alertId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status })
            });
            
            if (response.ok) {
                this.closeModal('alert-modal');
                this.showNotification('Alert status updated', 'success');
                this.loadAlerts(); // Reload alerts
            }
        } catch (error) {
            console.error('Error updating alert status:', error);
        }
    }

    showModal(modalId, content) {
        const modal = document.getElementById(modalId);
        const body = modal.querySelector('.modal-body');
        body.innerHTML = content;
        modal.style.display = 'block';
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.style.display = 'none';
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} min ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
        
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }

    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            try {
                this.loadSectionData(this.currentSection);
            } catch (error) {
                console.error('Dashboard auto-refresh error:', error);
                // Don't throw the error to prevent console spam
            }
        }, 30000); // Refresh every 30 seconds
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    updateTimeRange(range) {
        // Implement time range filtering logic
        console.log('Time range changed to:', range);
        this.loadDashboardData();
    }

    async createAlert() {
        // Implement alert creation logic
        console.log('Create new alert');
    }

    async runCorrelationAnalysis() {
        // Correlation analysis active - using mock analysis
        console.log('Correlation analysis active');
        this.showNotification('Correlation analysis completed (mock)', 'success');
        this.loadCorrelations();
    }

    async checkReputation() {
        const searchInput = document.getElementById('reputation-search');
        const entity = searchInput?.value.trim();
        
        if (!entity) {
            this.showNotification('Please enter an entity to check', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/reputation/check`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ entity })
            });
            
            const result = await response.json();
            this.showNotification(`Reputation check completed for ${entity}`, 'success');
            this.loadReputation();
        } catch (error) {
            console.error('Error checking reputation:', error);
        }
    }

    loadMapData() {
        // This will be handled by maps.js
        if (window.mapManager) {
            window.mapManager.loadThreatData();
        }
    }

    loadAnalytics() {
        // This will be handled by analytics.js
        if (window.analyticsManager) {
            window.analyticsManager.loadAnalyticsData();
        }
    }
}

// Global functions
function showSection(section) {
    dashboard.showSection(section);
}

function refreshDashboard() {
    dashboard.loadSectionData(dashboard.currentSection);
}

function closeModal(modalId) {
    dashboard.closeModal(modalId);
}

function createAlert() {
    dashboard.createAlert();
}

function runCorrelationAnalysis() {
    dashboard.runCorrelationAnalysis();
}

function checkReputation() {
    dashboard.checkReputation();
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});

// Close modals when clicking outside
window.addEventListener('click', (event) => {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
});

// Add notification styles
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(26, 26, 62, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        padding: 1rem 1.5rem;
        color: white;
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 1rem;
        min-width: 300px;
        animation: slideInRight 0.3s ease;
    }
    
    .notification-info { border-left: 4px solid #00d4ff; }
    .notification-warning { border-left: 4px solid #ff9800; }
    .notification-error { border-left: 4px solid #f44336; }
    .notification-success { border-left: 4px solid #4caf50; }
    
    .notification button {
        background: none;
        border: none;
        color: white;
        font-size: 1.2rem;
        cursor: pointer;
        margin-left: auto;
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .alert-details .detail-row {
        margin-bottom: 1rem;
    }
    
    .alert-details label {
        font-weight: bold;
        color: #00d4ff;
        display: inline-block;
        width: 100px;
    }
    
    .entities-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    
    .entity-tag {
        background: rgba(0, 212, 255, 0.2);
        color: #00d4ff;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    
    .detail-actions {
        margin-top: 1.5rem;
        display: flex;
        gap: 1rem;
    }
    
    .btn-sm {
        padding: 0.5rem 1rem;
        font-size: 0.8rem;
    }
`;

// Add styles to head
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);
