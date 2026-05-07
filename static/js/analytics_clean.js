class AdvancedAnalytics {
    constructor() {
        this.charts = {};
        this.alertsData = [];
        this.isInitialized = false;
    }

    async init() {
        try {
            console.log('Initializing Advanced Analytics...');
            
            // Prevent multiple initializations
            if (this.isInitialized) {
                console.log('Analytics already initialized, cleaning up...');
                this.destroyAllCharts();
            }
            
            // Check if Chart.js is loaded
            if (typeof Chart === 'undefined') {
                console.error('Chart.js not loaded. Waiting for it to load...');
                // Wait for Chart.js to load
                await this.waitForChart();
            }
            
            await this.loadRealData();
            this.initializeBasicCharts();
            this.isInitialized = true;
            console.log('Advanced Analytics initialized with real data');
            
            // Start real-time updates
            this.startRealTimeUpdates();
            
        } catch (error) {
            console.error('Error initializing analytics:', error);
            console.error('Error details:', error.stack);
            // Still try to show something even if initialization fails
            this.showFallbackContent();
        }
    }
    
    async waitForChart() {
        let attempts = 0;
        const maxAttempts = 50;
        
        while (typeof Chart === 'undefined' && attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }
        
        if (typeof Chart === 'undefined') {
            throw new Error('Chart.js failed to load after waiting');
        }
    }

    async loadRealData() {
        try {
            console.log('Loading real network data...');
            
            // Load real-time network monitoring alerts first
            let networkAlerts = [];
            try {
                const networkResponse = await fetch('/api/network/realtime-alerts');
                if (networkResponse.ok) {
                    const networkData = await networkResponse.json();
                    networkAlerts = networkData.alerts || [];
                    console.log('Loaded real-time network alerts:', networkAlerts.length);
                } else {
                    console.warn('Network alerts response not ok:', networkResponse.status);
                }
            } catch (networkError) {
                console.warn('Error loading network alerts:', networkError);
            }
            
            // Load system alerts from database
            let systemAlerts = [];
            try {
                const alertsResponse = await fetch('/api/alerts/?limit=1000');
                if (alertsResponse.ok) {
                    systemAlerts = await alertsResponse.json();
                    console.log('Loaded database alerts:', systemAlerts.length);
                } else {
                    console.warn('System alerts response not ok:', alertsResponse.status);
                }
            } catch (systemError) {
                console.warn('Error loading system alerts:', systemError);
            }
            
            // Load generated security data
            let generatedAlerts = [];
            try {
                const genResponse = await fetch('/api/analytics/generated-alerts');
                if (genResponse.ok) {
                    const genData = await genResponse.json();
                    generatedAlerts = genData.alerts || [];
                    console.log('Loaded generated alerts:', generatedAlerts.length);
                }
            } catch (genError) {
                console.warn('Error loading generated alerts:', genError);
            }
            
            // Combine all alerts with priority to real-time data
            this.alertsData = [...networkAlerts, ...generatedAlerts, ...systemAlerts];
            
            // Remove duplicates based on timestamp and title
            const uniqueAlerts = [];
            const seen = new Set();
            for (const alert of this.alertsData) {
                const key = `${alert.title}_${alert.timestamp}`;
                if (!seen.has(key)) {
                    seen.add(key);
                    uniqueAlerts.push(alert);
                }
            }
            this.alertsData = uniqueAlerts;
            
            // Sort by timestamp (newest first)
            this.alertsData.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            
            // If still no data, create network status alerts
            if (this.alertsData.length === 0) {
                console.log('No alerts found, creating network status alerts...');
                await this.createNetworkStatusAlerts();
            }
            
            console.log('Total unique alerts loaded:', this.alertsData.length);
            
        } catch (error) {
            console.error('Error loading real data:', error);
            console.error('Error stack:', error.stack);
            this.alertsData = [];
            await this.createNetworkStatusAlerts();
        }
    }
    
    async createNetworkStatusAlerts() {
        try {
            console.log('Creating network status alerts...');
            
            // Get current network metrics
            let metrics = null;
            let connections = null;
            let status = null;
            
            try {
                const metricsResponse = await fetch('/api/network/metrics');
                if (metricsResponse.ok) {
                    metrics = await metricsResponse.json();
                    console.log('Network metrics loaded:', metrics);
                }
            } catch (metricsError) {
                console.warn('Error loading network metrics:', metricsError);
            }
            
            try {
                const connectionsResponse = await fetch('/api/network/connections');
                if (connectionsResponse.ok) {
                    connections = await connectionsResponse.json();
                    console.log('Network connections loaded:', connections);
                }
            } catch (connectionsError) {
                console.warn('Error loading network connections:', connectionsError);
            }
            
            try {
                const statusResponse = await fetch('/api/network/status');
                if (statusResponse.ok) {
                    status = await statusResponse.json();
                    console.log('Network status loaded:', status);
                }
            } catch (statusError) {
                console.warn('Error loading network status:', statusError);
            }
            
            // Create comprehensive network status alert
            if (metrics || connections || status) {
                const activeConns = metrics?.active_connections || connections?.total_count || 0;
                const bytesTransferred = (metrics?.bytes_sent || 0) + (metrics?.bytes_recv || 0);
                const monitoringActive = status?.monitoring_active || false;
                
                const networkAlert = {
                    title: "Real-time Network Activity",
                    description: `Monitoring ${activeConns} active connections with ${bytesTransferred > 0 ? 'active' : 'no'} data transfer. Status: ${monitoringActive ? 'Active' : 'Inactive'}`,
                    severity: "low",
                    category: "network_monitoring",
                    source: "Network Monitor",
                    timestamp: new Date().toISOString(),
                    entities: [
                        {"type": "monitor", "value": "system_network"},
                        {"type": "metric", "value": `connections:${activeConns}`},
                        {"type": "metric", "value": `bytes:${bytesTransferred}`}
                    ],
                    context: {
                        "metrics": metrics,
                        "connections_count": activeConns,
                        "monitoring_active": monitoringActive
                    }
                };
                
                this.alertsData.push(networkAlert);
                console.log('Created comprehensive network status alert:', networkAlert);
                
                // If there are actual connections, create alerts for suspicious ones
                if (connections && connections.connections && connections.connections.length > 0) {
                    const suspiciousConnections = connections.connections.filter(conn => 
                        conn.remote_address && !conn.remote_address.includes('127.0.0.1') && 
                        !conn.remote_address.includes('192.168.') && 
                        !conn.remote_address.includes('10.0.')
                    );
                    
                    if (suspiciousConnections.length > 0) {
                        const suspiciousAlert = {
                            title: "External Network Connections Detected",
                            description: `Found ${suspiciousConnections.length} external network connections to ${new Set(suspiciousConnections.map(c => c.remote_address.split(':')[0])).size} unique external IPs`,
                            severity: "medium",
                            category: "network_anomaly",
                            source: "Network Monitor",
                            timestamp: new Date().toISOString(),
                            entities: suspiciousConnections.slice(0, 5).map(conn => ({
                                "type": "ip_address", 
                                "value": conn.remote_address.split(':')[0]
                            }))
                        };
                        
                        this.alertsData.push(suspiciousAlert);
                        console.log('Created external connections alert:', suspiciousAlert);
                    }
                }
                
            } else {
                // Create a default alert if no data available
                const defaultAlert = {
                    title: "Network Monitor Initializing",
                    description: "Network monitoring is starting up. Real-time data will appear here momentarily.",
                    severity: "low",
                    category: "network_monitoring",
                    source: "Real-time Monitor",
                    timestamp: new Date().toISOString(),
                    entities: [
                        {"type": "monitor", "value": "system_network"}
                    ]
                };
                
                this.alertsData.push(defaultAlert);
                console.log('Created default network alert:', defaultAlert);
            }
            
        } catch (error) {
            console.error('Error creating network status alerts:', error);
            console.error('Error stack:', error.stack);
        }
    }

    destroyAllCharts() {
        console.log('Destroying analytics charts only...');
        Object.keys(this.charts).forEach(chartKey => {
            if (this.charts[chartKey]) {
                try {
                    this.charts[chartKey].destroy();
                    console.log(`Destroyed analytics chart: ${chartKey}`);
                } catch (error) {
                    console.warn(`Error destroying analytics chart ${chartKey}:`, error);
                }
                delete this.charts[chartKey];
            }
        });
    }

    initializeBasicCharts() {
        // Destroy all existing charts
        this.destroyAllCharts();
        
        // Create all 4 charts
        this.charts.attackTimeline = this.createAttackTimeline();
        this.charts.sourceAnalysis = this.createSourceAnalysisChart();
        this.charts.hourlyPattern = this.createHourlyPatternChart();
        this.charts.responseTimes = this.createResponseTimesChart();
        
        console.log('All analytics charts initialized');
    }

    createAttackTimeline() {
        try {
            console.log('Creating attack timeline chart...');
            
            const canvas = document.getElementById('attack-timeline-canvas');
            if (!canvas) {
                console.warn('Attack timeline canvas not found');
                this.showFallbackMessage('Chart container not found');
                return null;
            }
            
            // Clear any existing chart on this canvas
            const ctx = canvas.getContext('2d');
            if (!ctx) {
                console.warn('Could not get canvas context');
                this.showFallbackMessage('Could not initialize chart');
                return null;
            }
            
            // Clear the canvas completely
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            if (!this.alertsData.length) {
                console.warn('No alerts data available for chart');
                this.showFallbackMessage('No data available for timeline');
                return null;
            }

            const now = new Date();
            const labels = [];
            const timelineData = [];
            const criticalAttacks = [];

            // Last 24 hour buckets
            const hourlyBuckets = Array(24).fill(0);
            const criticalBuckets = Array(24).fill(0);

            this.alertsData.forEach(alert => {
                try {
                    const alertTime = new Date(alert.timestamp);
                    const diffHours = Math.floor((now - alertTime) / (1000 * 60 * 60));

                    if (diffHours >= 0 && diffHours < 24) {
                        const index = 23 - diffHours;
                        hourlyBuckets[index]++;

                        if (alert.severity === 'critical') {
                            criticalBuckets[index]++;
                        }
                    }
                } catch (alertError) {
                    console.warn('Error processing alert for timeline:', alertError);
                }
            });

            for (let i = 0; i < 24; i++) {
                const time = new Date(now.getTime() - (23 - i) * 60 * 60 * 1000);

                labels.push(time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
                timelineData.push(hourlyBuckets[i]);
                criticalAttacks.push(criticalBuckets[i]);
            }

            // Clear any existing Chart.js instances on this canvas
            Chart.helpers.each(Chart.instances, function(instance){
                if (instance.canvas.id === canvas.id) {
                    instance.destroy();
                }
            });

            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Attack Volume',
                            data: timelineData,
                            borderColor: 'rgb(255, 99, 132)',
                            backgroundColor: 'rgba(255, 99, 132, 0.1)',
                            fill: true,
                            tension: 0.4
                        },
                        {
                            label: 'Critical Attacks',
                            data: criticalAttacks,
                            borderColor: 'rgb(220, 53, 69)',
                            fill: false,
                            tension: 0.3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
            
            console.log('Attack timeline chart created successfully');
            return chart;
            
        } catch (error) {
            console.error('Error creating attack timeline:', error);
            console.error('Error stack:', error.stack);
            this.showFallbackMessage('Error loading timeline chart');
            return null;
        }
    }
    
    createSourceAnalysisChart() {
        try {
            console.log('Creating source analysis chart...');
            
            const canvas = document.getElementById('source-analysis-canvas');
            if (!canvas) {
                console.warn('Source analysis canvas not found');
                return null;
            }
            
            // Extract real sources from alerts
            const sources = {};
            this.alertsData.forEach(alert => {
                const source = alert.source || 'Unknown';
                sources[source] = (sources[source] || 0) + 1;
            });
            
            const sortedSources = Object.entries(sources)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 10);
            
            const ctx = canvas.getContext('2d');
            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: sortedSources.length > 0 ? sortedSources.map(([source]) => source) : ['No Data'],
                    datasets: [{
                        label: 'Alerts',
                        data: sortedSources.length > 0 ? sortedSources.map(([, count]) => count) : [0],
                        backgroundColor: '#3b82f6',
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true },
                        x: { grid: { display: false } }
                    }
                }
            });
            
            console.log('Source analysis chart created successfully');
            return chart;
            
        } catch (error) {
            console.error('Error creating source analysis chart:', error);
            return null;
        }
    }
    
    createHourlyPatternChart() {
        try {
            console.log('Creating hourly pattern chart...');
            
            const canvas = document.getElementById('hourly-pattern-canvas');
            if (!canvas) {
                console.warn('Hourly pattern canvas not found');
                return null;
            }
            
            // Calculate real hourly pattern from alerts
            const hourlyData = new Array(24).fill(0);
            this.alertsData.forEach(alert => {
                if (alert.timestamp) {
                    const hour = new Date(alert.timestamp).getHours();
                    hourlyData[hour]++;
                }
            });
            
            const hourLabels = Array.from({length: 24}, (_, i) => 
                `${i.toString().padStart(2, '0')}:00`
            );
            
            const ctx = canvas.getContext('2d');
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: hourLabels,
                    datasets: [{
                        label: 'Alerts',
                        data: hourlyData,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true },
                        x: { grid: { display: false } }
                    }
                }
            });
            
            console.log('Hourly pattern chart created successfully');
            return chart;
            
        } catch (error) {
            console.error('Error creating hourly pattern chart:', error);
            return null;
        }
    }
    
    createResponseTimesChart() {
        try {
            console.log('Creating response times chart...');
            
            const canvas = document.getElementById('response-times-canvas');
            if (!canvas) {
                console.warn('Response times canvas not found');
                return null;
            }
            
            // Calculate real response times from alerts
            const responseTimeData = new Array(7).fill(0);
            const dayCounts = new Array(7).fill(0);
            
            this.alertsData.forEach(alert => {
                if (alert.timestamp) {
                    const dayOfWeek = new Date(alert.timestamp).getDay(); // 0=Sunday
                    const adjustedDay = dayOfWeek === 0 ? 6 : dayOfWeek - 1; // 0=Monday
                    const responseTime = alert.response_time || 5; // Default 5ms
                    responseTimeData[adjustedDay] += responseTime;
                    dayCounts[adjustedDay]++;
                }
            });
            
            // Calculate averages
            const avgResponseTimes = responseTimeData.map((total, i) => 
                dayCounts[i] > 0 ? Math.round(total / dayCounts[i]) : 0
            );
            
            const ctx = canvas.getContext('2d');
            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Avg Response Time (min)',
                        data: avgResponseTimes,
                        backgroundColor: avgResponseTimes.map(time => 
                            time > 20 ? 'rgba(220, 53, 69, 0.8)' : 
                            time > 10 ? 'rgba(255, 193, 7, 0.8)' : 
                            'rgba(40, 167, 69, 0.8)'
                        ),
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true },
                        x: { grid: { display: false } }
                    }
                }
            });
            
            console.log('Response times chart created successfully');
            return chart;
            
        } catch (error) {
            console.error('Error creating response times chart:', error);
            return null;
        }
    }
    
    startRealTimeUpdates() {
        // Start periodic data refresh
        setInterval(async () => {
            try {
                await this.loadRealData();
                if (this.isInitialized) {
                    this.initializeBasicCharts();
                }
            } catch (error) {
                console.warn('Error during real-time update:', error);
            }
        }, 10000); // Update every 10 seconds
    }
    
    showFallbackMessage(message) {
        const canvas = document.getElementById('attack-timeline-canvas');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#666';
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(message || 'Loading...', canvas.width / 2, canvas.height / 2);
            }
        }
    }
    
    showFallbackContent() {
        console.log('Showing fallback content due to initialization error');
        // Show a simple message instead of failing completely
        this.showFallbackMessage('Analytics initializing...');
    }
}

// INIT
document.addEventListener('DOMContentLoaded', () => {
    // Clean up existing instance if it exists
    if (window.advancedAnalytics) {
        // Destroy all existing charts
        Object.values(window.advancedAnalytics.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
    }
    
    // Initialize with error handling
    try {
        if (typeof Chart !== 'undefined') {
            window.advancedAnalytics = new AdvancedAnalytics();
            window.advancedAnalytics.init();
        } else {
            console.error('Chart.js not loaded');
            // Try to load Chart.js and retry
            setTimeout(() => {
                if (typeof Chart !== 'undefined') {
                    window.advancedAnalytics = new AdvancedAnalytics();
                    window.advancedAnalytics.init();
                } else {
                    console.error('Chart.js still not available after timeout');
                }
            }, 2000);
        }
    } catch (error) {
        console.error('Error during analytics initialization:', error);
        // Show fallback message
        const canvas = document.getElementById('attack-timeline-canvas');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#666';
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('Dashboard loading...', canvas.width / 2, canvas.height / 2);
            }
        }
    }
});
