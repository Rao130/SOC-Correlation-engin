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
        this.activeFilters = {};
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        
        // Delay chart initialization to ensure DOM is fully loaded
        setTimeout(() => {
            this.initCharts();
            this.loadInitialData();
            // Auto-load alerts when dashboard initializes
            this.loadAlerts();
        }, 100);
        
        this.initWebSocket(); // Add WebSocket for real-time updates
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Section navigation
        document.querySelectorAll('.nav-tab').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.getAttribute('onclick').match(/showSection\('([^']+)'\)/);
                if (section && section[1]) {
                    this.showSection(section[1]);
                }
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
        document.querySelectorAll('.nav-tab').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeNavItem = document.querySelector(`[onclick*="showSection('${sectionName}')"]`);
        if (activeNavItem) {
            activeNavItem.classList.add('active');
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
        // Load real-time system stats
        try {
            const response = await fetch('/api/realtime-status');
            if (response.ok) {
                const stats = await response.json();
                this.updateSystemStats({
                    alerts: { new: stats.data_ingestion?.buffer_size || 0, total: stats.data_ingestion?.correlation_processing?.alert_buffer_size || 0 },
                    correlations: { active: stats.data_ingestion?.correlation_processing?.active || false },
                    threats: { level: 'medium' }
                });
            } else {
                // Fallback to minimal stats
                this.updateSystemStats({
                    alerts: { new: 0, total: 0 },
                    correlations: { active: false },
                    threats: { level: 'medium' }
                });
            }
        } catch (error) {
            console.error('Error loading system stats:', error);
            // Fallback to minimal stats
            this.updateSystemStats({
                alerts: { new: 0, total: 0 },
                correlations: { active: false },
                threats: { level: 'medium' }
            });
        }
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
        console.log('🔄 Starting to load alerts...');
        
        try {
            // Load real alerts from API
            console.log('📡 Fetching alerts from API...');
            const response = await fetch('/api/alerts/?limit=1000');
            console.log('📡 API Response status:', response.status);
            
            if (response.ok) {
                const alerts = await response.json();
                console.log('📊 Raw alerts received:', alerts.length);
                
                this.alerts = alerts.map(alert => ({
                    id: alert._id, // Use MongoDB _id as primary ID
                    _id: alert._id, // Keep MongoDB _id for API calls
                    alert_id: alert.alert_id, // Keep original alert_id for reference
                    timestamp: new Date(alert.timestamp).toLocaleString(),
                    rawTimestamp: new Date(alert.timestamp), // Keep original timestamp for sorting
                    title: alert.title,
                    severity: alert.severity,
                    category: alert.category || 'Unknown',
                    status: alert.status || 'new',
                    source: alert.source_ip || alert.source || 'Unknown',
                    confidence: alert.confidence || 0,
                    description: alert.description || 'No description available'
                })).sort((a, b) => b.rawTimestamp - a.rawTimestamp); // Sort by newest first
                
                console.log('✅ Real alerts loaded and processed:', this.alerts.length);
                console.log('📋 Sample alert:', this.alerts[0]);
            } else {
                // API failed - show empty state
                console.log('❌ API failed, showing empty state');
                console.log('API Error:', response.statusText);
                this.alerts = [];
                console.log('📊 Empty alerts loaded');
            }
        } catch (error) {
            console.error('❌ Error loading alerts:', error);
            // Show empty state on error
            this.alerts = [];
            console.log('📊 Empty alerts loaded due to error');
        }
        
        console.log('🎨 Rendering alerts...');
        // Render alerts (all alerts initially)
        this.renderFilteredAlerts(this.alerts);
    }

    async loadCorrelations() {
        try {
            // Load real correlations from API
            console.log('Loading real correlations...');
            const response = await fetch('/api/correlations/?limit=100');
            if (response.ok) {
                const correlations = await response.json();
                this.correlations = correlations.map(corr => ({
                    id: corr._id,
                    name: corr.name,
                    type: corr.correlation_type,
                    score: corr.correlation_score,
                    status: corr.status,
                    alert_count: corr.alert_count,
                    created_at: new Date(corr.created_at).toLocaleString()
                }));
                console.log('✅ Real correlations loaded:', this.correlations.length);
            } else {
                console.log('❌ API failed, showing empty correlations');
                this.correlations = [];
            }
        } catch (error) {
            console.error('❌ Error loading correlations:', error);
            this.correlations = [];
        }
        this.renderCorrelations();
    }

    async loadReputation() {
        try {
            // Load real reputation data from API
            console.log('Loading real reputation data...');
            const response = await fetch('/api/reputation/');
            if (response.ok) {
                const reputationData = await response.json();
                this.reputationData = reputationData.map(rep => ({
                    id: rep._id,
                    entity: rep.entity,
                    entity_type: rep.entity_type,
                    reputation_score: rep.reputation_score,
                    risk_level: rep.risk_level,
                    sources: rep.sources || [],
                    created_at: new Date(rep.created_at).toLocaleString()
                }));
                console.log('✅ Real reputation data loaded:', this.reputationData.length);
            } else {
                console.log('❌ API failed, showing empty reputation data');
                this.reputationData = [];
            }
        } catch (error) {
            console.error('❌ Error loading reputation data:', error);
            this.reputationData = [];
        }
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
        // Return empty array - no mock data
        return [];
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

    destroyExistingCharts() {
        console.log('🗑️ Destroying existing charts...');
        
        // Destroy all existing charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                try {
                    chart.destroy();
                    console.log('✅ Chart destroyed');
                } catch (error) {
                    console.warn('⚠️ Error destroying chart:', error);
                }
            }
        });
        
        // Clear charts object
        this.charts = {};
        
        // Clean up all canvas elements to prevent reuse error
        const canvasElements = document.querySelectorAll('canvas');
        canvasElements.forEach(canvas => {
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
            // Remove and recreate canvas to ensure clean state
            const parent = canvas.parentNode;
            if (parent) {
                const newCanvas = document.createElement('canvas');
                newCanvas.id = canvas.id;
                newCanvas.width = canvas.width;
                newCanvas.height = canvas.height;
                parent.replaceChild(newCanvas, canvas);
            }
        });
        
        console.log('🗑️ All charts destroyed and canvas cleaned');
    }

    initWebSocket() {
        try {
            const clientId = 'dashboard_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            const wsUrl = `ws://${window.location.hostname}:8000/ws/${clientId}`;
            
            console.log('🔌 Connecting WebSocket for real-time updates:', wsUrl);
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('✅ WebSocket connected for real-time updates');
                
                // Request initial data
                this.ws.send(JSON.stringify({
                    type: 'request_alerts',
                    limit: 1000
                }));
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('WebSocket message parse error:', error);
                }
            };
            
            this.ws.onclose = () => {
                console.log('❌ WebSocket disconnected');
                // Reconnect after 5 seconds
                setTimeout(() => {
                    this.initWebSocket();
                }, 5000);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
        }
    }

    handleWebSocketMessage(data) {
        console.log('📨 WebSocket message received:', data.type);
        
        switch(data.type) {
            case 'initial_data':
                console.log('📊 Received initial data via WebSocket');
                if (data.recent_alerts && Array.isArray(data.recent_alerts)) {
                    this.alerts = data.recent_alerts;
                    this.updateCharts(this.alerts, {});
                    this.updateDashboardKPIs(this.alerts);
                    this.updateRecentAlerts(this.alerts.slice(0, 5));
                }
                break;
                
            case 'new_alert':
                console.log('🚨 New alert received:', data.alert?.title);
                if (data.alert) {
                    // Add new alert to the beginning
                    this.alerts.unshift(data.alert);
                    
                    // Keep only last 1000 alerts
                    if (this.alerts.length > 1000) {
                        this.alerts = this.alerts.slice(0, 1000);
                    }
                    
                    // Update charts immediately
                    this.updateCharts(this.alerts, {});
                    this.updateDashboardKPIs(this.alerts);
                    this.updateRecentAlerts(this.alerts.slice(0, 5));
                    
                    // Show notification
                    this.showNotification(`New Alert: ${data.alert.title}`, 'warning');
                }
                break;
                
            case 'alerts_response':
                console.log('📋 Alerts response received');
                if (data.alerts && Array.isArray(data.alerts)) {
                    this.alerts = data.alerts;
                    this.updateCharts(this.alerts, {});
                    this.updateDashboardKPIs(this.alerts);
                    this.updateRecentAlerts(this.alerts.slice(0, 5));
                }
                break;
                
            case 'analytics_update':
                console.log('📈 Analytics update received');
                // Refresh data when analytics update comes
                this.loadInitialData();
                break;
                
            case 'metrics_update':
                console.log('📊 Metrics update received');
                // Refresh data when metrics update comes
                this.loadInitialData();
                break;
                
            case 'pong':
                // Heartbeat response - do nothing
                break;
                
            default:
                console.log('🔍 Unknown WebSocket message type:', data.type, data);
        }
    }

    initCharts() {
        console.log('🚀 Initializing charts...');
        console.log('Chart.js available:', typeof Chart !== 'undefined');
        console.log('Chart object:', Chart);
        
        // Destroy existing charts first to prevent canvas reuse error
        this.destroyExistingCharts();
        
        // Check if Chart is loaded
        if (typeof Chart === 'undefined') {
            console.error('❌ Chart.js is not loaded! Waiting...');
            // Wait for Chart to load
            setTimeout(() => this.initCharts(), 1000);
            return;
        }
        
        console.log('✅ Chart.js loaded successfully');
        
        // Offenses by Magnitude Chart
        console.log('📊 Looking for magnitudeChart canvas...');
        const magnitudeCtx = document.getElementById('magnitudeChart');
        console.log('magnitudeChart element:', magnitudeCtx);
        
        if (magnitudeCtx) {
            try {
                console.log('🎨 Creating magnitude chart with Chart:', Chart);
                const chartConfig = {
                    type: 'bar',
                    data: {
                        labels: ['Critical', 'High', 'Medium', 'Low'],
                        datasets: [{
                            label: 'Alert Count',
                            data: [0, 0, 0, 0],
                            backgroundColor: [
                                '#ff4444',
                                '#ff9800',
                                '#ffeb3b',
                                '#4caf50'
                            ]
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
                };
                
                this.charts.magnitude = new Chart(magnitudeCtx, chartConfig);
                console.log('✅ Magnitude chart created successfully');
            } catch (error) {
                console.error('❌ Error creating magnitude chart:', error);
                console.error('Error details:', error.message, error.stack);
            }
        } else {
            console.warn('⚠️ magnitudeChart canvas not found');
        }

        // Offenses by Assignee Chart
        console.log('📊 Looking for assigneeChart canvas...');
        const assigneeCtx = document.getElementById('assigneeChart');
        console.log('assigneeChart element:', assigneeCtx);
        
        if (assigneeCtx) {
            try {
                this.charts.assignee = new Chart(assigneeCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Analyst 1', 'Analyst 2', 'Analyst 3', 'Unassigned'],
                        datasets: [{
                            data: [0, 0, 0, 0],
                            backgroundColor: [
                                '#00d4ff',
                                '#ff6b6b',
                                '#4ecdc4',
                                '#95a5a6'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
                console.log('✅ Assignee chart created successfully');
            } catch (error) {
                console.error('❌ Error creating assignee chart:', error);
            }
        } else {
            console.warn('⚠️ assigneeChart canvas not found');
        }

        // Offenses by Type Chart
        console.log('📊 Looking for typeChart canvas...');
        const typeCtx = document.getElementById('typeChart');
        console.log('typeChart element:', typeCtx);
        
        if (typeCtx) {
            try {
                this.charts.type = new Chart(typeCtx, {
                    type: 'pie',
                    data: {
                        labels: ['Malware', 'Phishing', 'Network', 'Policy', 'Other'],
                        datasets: [{
                            data: [0, 0, 0, 0, 0],
                            backgroundColor: [
                                '#e74c3c',
                                '#f39c12',
                                '#3498db',
                                '#2ecc71',
                                '#9b59b6'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
                console.log('✅ Type chart created successfully');
            } catch (error) {
                console.error('❌ Error creating type chart:', error);
            }
        } else {
            console.warn('⚠️ typeChart canvas not found');
        }

        // Notable Events by Urgency Chart
        console.log('📊 Looking for urgencyChart canvas...');
        const urgencyCtx = document.getElementById('urgencyChart');
        console.log('urgencyChart element:', urgencyCtx);
        
        if (urgencyCtx) {
            try {
                this.charts.urgency = new Chart(urgencyCtx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Critical',
                            data: [],
                            borderColor: '#ff4444',
                            backgroundColor: 'rgba(255, 68, 68, 0.1)',
                            tension: 0.4
                        }, {
                            label: 'High',
                            data: [],
                            borderColor: '#ff9800',
                            backgroundColor: 'rgba(255, 152, 0, 0.1)',
                            tension: 0.4
                        }, {
                            label: 'Medium',
                            data: [],
                            borderColor: '#ffeb3b',
                            backgroundColor: 'rgba(255, 235, 59, 0.1)',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'top' }
                        },
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
                console.log('✅ Urgency chart created successfully');
            } catch (error) {
                console.error('❌ Error creating urgency chart:', error);
            }
        } else {
            console.warn('⚠️ urgencyChart canvas not found');
        }

        // Notable Events Over Time Chart
        console.log('📊 Looking for timeChart canvas...');
        const timeCtx = document.getElementById('timeChart');
        console.log('timeChart element:', timeCtx);
        
        if (timeCtx) {
            try {
                this.charts.time = new Chart(timeCtx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Total Alerts',
                            data: [],
                            borderColor: '#00d4ff',
                            backgroundColor: 'rgba(0, 212, 255, 0.1)',
                            fill: true,
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
                console.log('✅ Time chart created successfully');
            } catch (error) {
                console.error('❌ Error creating time chart:', error);
            }
        } else {
            console.warn('⚠️ timeChart canvas not found');
        }
        
        console.log('🎯 Chart initialization complete. Total charts:', Object.keys(this.charts).length);
    }

    updateCharts(alerts, threats) {
        if (!alerts || !Array.isArray(alerts)) {
            console.warn('Invalid alerts data for charts');
            return;
        }

        console.log('Updating charts with', alerts.length, 'alerts');

        // Update magnitude chart
        if (this.charts.magnitude) {
            const severityCounts = this.countBySeverity(alerts);
            this.charts.magnitude.data.datasets[0].data = [
                severityCounts.critical,
                severityCounts.high,
                severityCounts.medium,
                severityCounts.low
            ];
            this.charts.magnitude.update();
        }

        // Update assignee chart (mock data for now)
        if (this.charts.assignee) {
            this.charts.assignee.data.datasets[0].data = [
                Math.floor(alerts.length * 0.3),
                Math.floor(alerts.length * 0.25),
                Math.floor(alerts.length * 0.2),
                Math.floor(alerts.length * 0.25)
            ];
            this.charts.assignee.update();
        }

        // Update type chart
        if (this.charts.type) {
            const categoryCounts = this.countByCategory(alerts);
            this.charts.type.data.datasets[0].data = [
                categoryCounts.malware || 0,
                categoryCounts.phishing || 0,
                categoryCounts.network || 0,
                categoryCounts.policy || 0,
                categoryCounts.other || 0
            ];
            this.charts.type.update();
        }

        // Update urgency chart (timeline data)
        if (this.charts.urgency) {
            const timelineData = this.processTimelineData(alerts);
            this.charts.urgency.data.labels = timelineData.labels;
            
            // Update each severity dataset
            const severityTimeline = this.processSeverityTimeline(alerts);
            this.charts.urgency.data.datasets[0].data = severityTimeline.critical;
            this.charts.urgency.data.datasets[1].data = severityTimeline.high;
            this.charts.urgency.data.datasets[2].data = severityTimeline.medium;
            this.charts.urgency.update();
        }

        // Update time chart
        if (this.charts.time) {
            const timelineData = this.processTimelineData(alerts);
            this.charts.time.data.labels = timelineData.labels;
            this.charts.time.data.datasets[0].data = timelineData.data;
            this.charts.time.update();
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
            const severity = (alert.severity || '').toLowerCase();
            if (counts.hasOwnProperty(severity)) {
                counts[severity]++;
            }
        });
        return counts;
    }

    countByCategory(alerts) {
        const counts = { malware: 0, phishing: 0, network: 0, policy: 0, other: 0 };
        alerts.forEach(alert => {
            const category = (alert.category || '').toLowerCase();
            if (category.includes('malware') || category.includes('virus')) {
                counts.malware++;
            } else if (category.includes('phish') || category.includes('spam')) {
                counts.phishing++;
            } else if (category.includes('network') || category.includes('ddos') || category.includes('firewall')) {
                counts.network++;
            } else if (category.includes('policy') || category.includes('audit')) {
                counts.policy++;
            } else {
                counts.other++;
            }
        });
        return counts;
    }

    processSeverityTimeline(alerts) {
        const hourlyData = {
            critical: new Array(24).fill(0),
            high: new Array(24).fill(0),
            medium: new Array(24).fill(0)
        };
        
        alerts.forEach(alert => {
            const alertTime = new Date(alert.timestamp);
            const hour = alertTime.getHours();
            const severity = (alert.severity || '').toLowerCase();
            
            if (severity === 'critical') hourlyData.critical[hour]++;
            else if (severity === 'high') hourlyData.high[hour]++;
            else if (severity === 'medium') hourlyData.medium[hour]++;
        });
        
        return hourlyData;
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
            this.renderFilteredAlerts(this.alerts);
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

    clearAllFilters() {
        // Clear all active filters
        this.activeFilters = {};
        
        // Clear all filter checkboxes
        document.querySelectorAll('.filter-checkbox input').forEach(checkbox => {
            checkbox.checked = false;
        });
        
        // Clear applied filters display
        const appliedFiltersDiv = document.getElementById('applied-filters');
        if (appliedFiltersDiv) {
            appliedFiltersDiv.innerHTML = '';
        }
        
        // Reset dropdown filters
        const severityFilter = document.getElementById('severity-filter');
        const statusFilter = document.getElementById('status-filter');
        if (severityFilter) severityFilter.value = '';
        if (statusFilter) statusFilter.value = '';
        
        // Clear search
        const searchInput = document.getElementById('alert-search');
        if (searchInput) searchInput.value = '';
        
        // Render all alerts
        this.renderFilteredAlerts(this.alerts);
    }

    applyFilter(filterType, filterValue) {
        console.log(`🔍 Applying filter: ${filterType} = ${filterValue}`);
        console.log(`📊 Current alerts count: ${this.alerts ? this.alerts.length : 0}`);
        
        // Store active filters
        if (!this.activeFilters) {
            this.activeFilters = {};
        }
        
        // Toggle filter if already exists
        if (this.activeFilters[filterType] === filterValue) {
            delete this.activeFilters[filterType];
            console.log(`❌ Removed filter: ${filterType}`);
        } else {
            this.activeFilters[filterType] = filterValue;
            console.log(`✅ Added filter: ${filterType} = ${filterValue}`);
        }
        
        console.log(`🎯 Active filters:`, this.activeFilters);
        
        // Apply all active filters
        this.applyAllFilters();
    }

    applyAllFilters() {
        console.log(`🔄 Applying all filters...`);
        console.log(`📋 Total alerts before filtering: ${this.alerts ? this.alerts.length : 0}`);
        
        let filtered = this.alerts;
        
        // Apply severity filter
        if (this.activeFilters && this.activeFilters.severity) {
            const beforeSeverity = filtered.length;
            filtered = filtered.filter(alert => alert.severity === this.activeFilters.severity);
            console.log(`🎯 Severity filter (${this.activeFilters.severity}): ${beforeSeverity} → ${filtered.length}`);
        }
        
        // Apply status filter
        if (this.activeFilters && this.activeFilters.status) {
            const beforeStatus = filtered.length;
            filtered = filtered.filter(alert => alert.status === this.activeFilters.status);
            console.log(`📊 Status filter (${this.activeFilters.status}): ${beforeStatus} → ${filtered.length}`);
        }
        
        // Apply category filter
        if (this.activeFilters && this.activeFilters.category) {
            const beforeCategory = filtered.length;
            filtered = filtered.filter(alert => alert.category === this.activeFilters.category);
            console.log(`🏷️ Category filter (${this.activeFilters.category}): ${beforeCategory} → ${filtered.length}`);
        }
        
        console.log(`✅ Final filtered alerts: ${filtered.length}`);
        
        // Update applied filters display
        this.updateAppliedFiltersDisplay();
        
        // Render filtered alerts
        this.renderFilteredAlerts(filtered);
    }

    updateAppliedFiltersDisplay() {
        const appliedFiltersDiv = document.getElementById('applied-filters');
        if (!appliedFiltersDiv) return;
        
        appliedFiltersDiv.innerHTML = '';
        
        if (this.activeFilters && Object.keys(this.activeFilters).length > 0) {
            Object.entries(this.activeFilters).forEach(([filterType, filterValue]) => {
                const filterTag = document.createElement('span');
                filterTag.className = 'applied-filter-tag';
                filterTag.innerHTML = `
                    ${filterType}: ${filterValue}
                    <button onclick="window.dashboard.removeFilter('${filterType}')" class="remove-filter">×</button>
                `;
                appliedFiltersDiv.appendChild(filterTag);
            });
        }
    }

    removeFilter(filterType) {
        if (this.activeFilters && this.activeFilters[filterType]) {
            delete this.activeFilters[filterType];
            
            // Uncheck the corresponding checkbox
            const checkbox = document.querySelector(`input[onchange*="applyFilter('${filterType}'"]`);
            if (checkbox) {
                checkbox.checked = false;
            }
            
            this.applyAllFilters();
        }
    }

    applyFilters() {
        const severityFilter = document.getElementById('severity-filter')?.value;
        const statusFilter = document.getElementById('status-filter')?.value;
        const searchTerm = document.getElementById('alert-search')?.value;
        
        let filtered = this.alerts;
        
        if (severityFilter) {
            filtered = filtered.filter(alert => alert.severity === severityFilter);
        }
        
        if (statusFilter) {
            filtered = filtered.filter(alert => alert.status === statusFilter);
        }
        
        if (searchTerm) {
            filtered = filtered.filter(alert => 
                alert.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                alert.description.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }
        
        this.renderFilteredAlerts(filtered);
    }

    toggleAutoRefresh() {
        const icon = document.getElementById('auto-refresh-icon');
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
            icon.className = 'fas fa-play';
        } else {
            this.refreshInterval = setInterval(() => {
                this.loadAlerts();
            }, 30000); // Refresh every 30 seconds
            icon.className = 'fas fa-pause';
        }
    }

    previousAlertPage() {
        console.log('Previous page functionality');
    }

    nextAlertPage() {
        console.log('Next page functionality');
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
        console.log(`🎨 Rendering filtered alerts: ${alerts ? alerts.length : 0} alerts`);
        
        // Render filtered alerts in table format
        const tbody = document.getElementById('alerts-tbody');
        if (!tbody) {
            console.error('❌ alerts-tbody not found!');
            return;
        }

        console.log('✅ alerts-tbody element found');

        if (!alerts || alerts.length === 0) {
            console.log('📭 No alerts to display, showing empty message');
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No alerts found</td></tr>';
            return;
        }

        console.log(`📊 Building HTML for ${alerts.length} alerts...`);
        
        const html = alerts.map((alert, index) => {
            // Ensure alert has a valid ID for action buttons
            const alertId = alert._id || alert.alert_id || alert.id || `alert_${index}`;
            
            return `
            <tr>
                <td>${this.formatTime(alert.timestamp)}</td>
                <td>${alert.title || 'N/A'}</td>
                <td><span class="severity-badge severity-${alert.severity}">${alert.severity}</span></td>
                <td>${alert.category || 'N/A'}</td>
                <td><span class="status-badge status-${alert.status}">${alert.status}</span></td>
                <td>${alert.source || 'N/A'}</td>
                <td>${alert.confidence || 'N/A'}</td>
                <td>
                    <button class="action-btn" onclick="viewAlertDetails('${alertId}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn" onclick="updateAlertStatus('${alertId}', 'investigating')">
                        <i class="fas fa-search"></i>
                    </button>
                </td>
            </tr>
        `;
        }).join('');
        
        console.log('📝 Setting innerHTML...');
        tbody.innerHTML = html;
        console.log('✅ Alerts rendered successfully!');
        
        // Update alert count
        const alertCount = document.getElementById('alert-count');
        if (alertCount) {
            alertCount.textContent = `${alerts.length} alerts`;
            console.log(`📈 Updated alert count: ${alerts.length}`);
        } else {
            console.log('⚠️ alert-count element not found');
        }
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
            // Find alert from current alerts array
            const alert = this.alerts.find(a => a._id === alertId || a.alert_id === alertId || a.id === alertId);
            
            if (alert) {
                this.showModal('alert-modal', this.renderAlertDetails(alert));
            } else {
                // Fallback to API call if not found in current array
                const response = await fetch(`/api/alerts/${alertId}`);
                if (response.ok) {
                    const alertData = await response.json();
                    this.showModal('alert-modal', this.renderAlertDetails(alertData));
                } else {
                    this.showNotification('Alert not found', 'error');
                }
            }
        } catch (error) {
            console.error('Error loading alert details:', error);
            this.showNotification('Error loading alert details', 'error');
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
            console.log(`🔄 Updating alert ${alertId} to status: ${status}`);
            
            // Find alert in local array first
            const alertIndex = this.alerts.findIndex(a => 
                a._id === alertId || 
                a.alert_id === alertId || 
                a.id === alertId ||
                `alert_${this.alerts.indexOf(a)}` === alertId
            );
            
            if (alertIndex === -1) {
                console.error('❌ Alert not found in local array');
                this.showNotification('Alert not found', 'error');
                return;
            }
            
            const alert = this.alerts[alertIndex];
            // Use MongoDB _id for API calls (not alert_id)
            const realAlertId = alert._id || alert.id;
            
            if (!realAlertId || realAlertId.startsWith('alert_')) {
                // For alerts without real ID, only update local state
                console.log('📝 Updating local alert status (no real ID)');
                alert.status = status;
                this.renderFilteredAlerts(this.alerts);
                this.closeModal('alert-modal');
                this.showNotification(`Alert marked as ${status} (local)`, 'success');
                return;
            }
            
            const response = await fetch(`/api/alerts/${realAlertId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status })
            });
            
            if (response.ok) {
                // Update local alerts array immediately for instant feedback
                alert.status = status;
                this.renderFilteredAlerts(this.alerts);
                
                this.closeModal('alert-modal');
                this.showNotification(`Alert marked as ${status}`, 'success');
                console.log(`✅ Alert status updated successfully`);
            } else {
                const errorText = await response.text();
                console.error('❌ Failed to update alert status:', errorText);
                this.showNotification('Failed to update alert status', 'error');
            }
        } catch (error) {
            console.error('❌ Error updating alert status:', error);
            this.showNotification('Error updating alert status', 'error');
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
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new Dashboard();
    console.log('🎯 Dashboard initialized and exposed globally');
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

// Global functions for HTML onclick handlers
function showSection(sectionName) {
    if (window.dashboard) {
        window.dashboard.showSection(sectionName);
    }
}

function refreshDashboard() {
    if (window.dashboard) {
        window.dashboard.loadDashboardData();
    }
}

function clearAllFilters() {
    if (window.dashboard) {
        window.dashboard.clearAllFilters();
    }
}

function applyFilter(filterType, filterValue) {
    if (window.dashboard) {
        window.dashboard.applyFilter(filterType, filterValue);
    }
}

function toggleAccordion(element) {
    element.classList.toggle('active');
    const content = element.nextElementSibling;
    if (content.style.display === 'block') {
        content.style.display = 'none';
    } else {
        content.style.display = 'block';
    }
}

function createAlert() {
    dashboard.createAlert();
}

function refreshRecentOffenses() {
    if (window.dashboard) {
        window.dashboard.loadDashboardData();
    }
}

function toggleColumns() {
    console.log('Toggle columns functionality');
}

function toggleDropdown() {
    const dropdown = document.getElementById('actions-menu');
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
}

function bulkAssign() {
    console.log('Bulk assign functionality');
}

function bulkResolve() {
    console.log('Bulk resolve functionality');
}

function bulkInvestigate() {
    console.log('Bulk investigate functionality');
}

function exportSelected() {
    console.log('Export selected functionality');
}

function bulkDelete() {
    console.log('Bulk delete functionality');
}

function applyFilters() {
    if (window.dashboard) {
        window.dashboard.applyFilters();
    }
}

function refreshAlerts() {
    if (window.dashboard) {
        window.dashboard.loadAlerts();
    }
}

function toggleAutoRefresh() {
    if (window.dashboard) {
        window.dashboard.toggleAutoRefresh();
    }
}

function exportAlerts() {
    console.log('Export alerts functionality');
}

function previousAlertPage() {
    if (window.dashboard) {
        window.dashboard.previousAlertPage();
    }
}

function nextAlertPage() {
    if (window.dashboard) {
        window.dashboard.nextAlertPage();
    }
}
