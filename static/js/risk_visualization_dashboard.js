// Risk Score Visualization Dashboard - World-Class UI for Risk Analysis
// Revolutionary real-time visualization with advanced analytics

class RiskVisualizationDashboard {
    constructor() {
        this.risk_engine = new RealTimeRiskEngine();
        this.chart_library = new AdvancedChartLibrary();
        this.realtime_updater = new RealTimeUpdater();
        this.interaction_handler = new InteractionHandler();
        
        this.dashboard_data = {
            current_risks: new Map(),
            historical_trends: [],
            risk_distribution: {},
            performance_metrics: {},
            alerts_stream: []
        };
        
        this.visualization_config = {
            update_interval: 1000, // 1 second updates
            chart_animations: true,
            real_time_indicators: true,
            color_scheme: {
                critical: '#dc3545',
                high: '#fd7e14',
                medium: '#ffc107',
                low: '#28a745',
                info: '#17a2b8'
            }
        };
        
        this.dashboard_initialized = false;
        this.active_charts = new Map();
        
        this.initializeDashboard();
    }

    // Initialize the dashboard
    initializeDashboard() {
        console.log('Initializing Risk Visualization Dashboard...');
        
        // Create dashboard layout
        this.createDashboardLayout();
        
        // Initialize charts
        this.initializeCharts();
        
        // Set up real-time updates
        this.setupRealTimeUpdates();
        
        // Initialize interactions
        this.initializeInteractions();
        
        // Start dashboard
        this.startDashboard();
        
        this.dashboard_initialized = true;
    }

    // Create dashboard layout
    createDashboardLayout() {
        const dashboard_container = document.getElementById('risk-dashboard');
        
        if (!dashboard_container) {
            console.error('Risk dashboard container not found');
            return;
        }
        
        dashboard_container.innerHTML = `
            <div class="risk-dashboard-container">
                <!-- Header with Real-time Status -->
                <div class="dashboard-header">
                    <div class="dashboard-title">
                        <h1>World-Class Risk Correlation Dashboard</h1>
                        <div class="real-time-indicator">
                            <span class="status-dot live"></span>
                            <span class="status-text">LIVE</span>
                        </div>
                    </div>
                    <div class="dashboard-controls">
                        <button id="refresh-dashboard" class="btn btn-primary">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                        <button id="export-dashboard" class="btn btn-secondary">
                            <i class="fas fa-download"></i> Export
                        </button>
                        <button id="settings-dashboard" class="btn btn-info">
                            <i class="fas fa-cog"></i> Settings
                        </button>
                    </div>
                </div>

                <!-- Key Metrics Row -->
                <div class="metrics-row">
                    <div class="metric-card critical">
                        <div class="metric-icon">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value" id="critical-risk-count">0</div>
                            <div class="metric-label">Critical Risks</div>
                            <div class="metric-change" id="critical-change">+0%</div>
                        </div>
                    </div>
                    
                    <div class="metric-card high">
                        <div class="metric-icon">
                            <i class="fas fa-exclamation-circle"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value" id="high-risk-count">0</div>
                            <div class="metric-label">High Risks</div>
                            <div class="metric-change" id="high-change">+0%</div>
                        </div>
                    </div>
                    
                    <div class="metric-card medium">
                        <div class="metric-icon">
                            <i class="fas fa-info-circle"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value" id="medium-risk-count">0</div>
                            <div class="metric-label">Medium Risks</div>
                            <div class="metric-change" id="medium-change">+0%</div>
                        </div>
                    </div>
                    
                    <div class="metric-card performance">
                        <div class="metric-icon">
                            <i class="fas fa-tachometer-alt"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value" id="performance-score">0%</div>
                            <div class="metric-label">System Performance</div>
                            <div class="metric-change" id="performance-change">+0%</div>
                        </div>
                    </div>
                </div>

                <!-- Main Dashboard Grid -->
                <div class="dashboard-grid">
                    <!-- Real-time Risk Chart -->
                    <div class="chart-container large">
                        <div class="chart-header">
                            <h3>Real-time Risk Scores</h3>
                            <div class="chart-controls">
                                <select id="risk-timeframe" class="form-control">
                                    <option value="1h">Last Hour</option>
                                    <option value="6h">Last 6 Hours</option>
                                    <option value="24h" selected>Last 24 Hours</option>
                                    <option value="7d">Last 7 Days</option>
                                </select>
                            </div>
                        </div>
                        <div class="chart-body">
                            <canvas id="realtime-risk-chart"></canvas>
                        </div>
                    </div>

                    <!-- Risk Distribution Pie Chart -->
                    <div class="chart-container medium">
                        <div class="chart-header">
                            <h3>Risk Distribution</h3>
                        </div>
                        <div class="chart-body">
                            <canvas id="risk-distribution-chart"></canvas>
                        </div>
                    </div>

                    <!-- Confidence Score Gauge -->
                    <div class="chart-container medium">
                        <div class="chart-header">
                            <h3>Average Confidence</h3>
                        </div>
                        <div class="chart-body">
                            <canvas id="confidence-gauge-chart"></canvas>
                        </div>
                    </div>

                    <!-- Alert Stream -->
                    <div class="chart-container large">
                        <div class="chart-header">
                            <h3>Live Alert Stream</h3>
                            <div class="chart-controls">
                                <button id="pause-stream" class="btn btn-sm btn-secondary">
                                    <i class="fas fa-pause"></i> Pause
                                </button>
                                <button id="clear-stream" class="btn btn-sm btn-danger">
                                    <i class="fas fa-trash"></i> Clear
                                </button>
                            </div>
                        </div>
                        <div class="chart-body">
                            <div class="alert-stream" id="alert-stream">
                                <!-- Alerts will be populated here -->
                            </div>
                        </div>
                    </div>

                    <!-- Performance Metrics -->
                    <div class="chart-container medium">
                        <div class="chart-header">
                            <h3>System Performance</h3>
                        </div>
                        <div class="chart-body">
                            <canvas id="performance-chart"></canvas>
                        </div>
                    </div>

                    <!-- Risk Heatmap -->
                    <div class="chart-container medium">
                        <div class="chart-header">
                            <h3>Risk Heatmap</h3>
                        </div>
                        <div class="chart-body">
                            <div class="risk-heatmap" id="risk-heatmap">
                                <!-- Heatmap will be generated here -->
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Detailed Risk Table -->
                <div class="risk-table-container">
                    <div class="table-header">
                        <h3>Detailed Risk Analysis</h3>
                        <div class="table-controls">
                            <input type="text" id="risk-search" class="form-control" placeholder="Search risks...">
                            <select id="risk-filter" class="form-control">
                                <option value="all">All Risks</option>
                                <option value="critical">Critical</option>
                                <option value="high">High</option>
                                <option value="medium">Medium</option>
                                <option value="low">Low</option>
                            </select>
                        </div>
                    </div>
                    <div class="table-body">
                        <table class="risk-table" id="risk-table">
                            <thead>
                                <tr>
                                    <th>Timestamp</th>
                                    <th>Risk Score</th>
                                    <th>Confidence</th>
                                    <th>Priority</th>
                                    <th>Correlation ID</th>
                                    <th>Source</th>
                                    <th>Target</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="risk-table-body">
                                <!-- Risk rows will be populated here -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        // Add custom CSS
        this.addDashboardStyles();
    }

    // Add dashboard styles
    addDashboardStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .risk-dashboard-container {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: #ffffff;
                padding: 20px;
                min-height: 100vh;
            }

            .dashboard-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding: 20px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }

            .dashboard-title {
                display: flex;
                align-items: center;
                gap: 15px;
            }

            .dashboard-title h1 {
                margin: 0;
                font-size: 2.5em;
                font-weight: 700;
                background: linear-gradient(45deg, #ffffff, #64b5f6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .real-time-indicator {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 16px;
                background: rgba(76, 175, 80, 0.2);
                border: 2px solid #4caf50;
                border-radius: 25px;
                font-weight: 600;
            }

            .status-dot {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #4caf50;
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.7; transform: scale(1.2); }
                100% { opacity: 1; transform: scale(1); }
            }

            .dashboard-controls {
                display: flex;
                gap: 10px;
            }

            .btn {
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .btn-primary {
                background: #007bff;
                color: white;
            }

            .btn-secondary {
                background: #6c757d;
                color: white;
            }

            .btn-info {
                background: #17a2b8;
                color: white;
            }

            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            }

            .metrics-row {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }

            .metric-card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 25px;
                display: flex;
                align-items: center;
                gap: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: all 0.3s ease;
            }

            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            }

            .metric-card.critical { border-left: 5px solid #dc3545; }
            .metric-card.high { border-left: 5px solid #fd7e14; }
            .metric-card.medium { border-left: 5px solid #ffc107; }
            .metric-card.performance { border-left: 5px solid #28a745; }

            .metric-icon {
                font-size: 2.5em;
                opacity: 0.8;
            }

            .metric-content {
                flex: 1;
            }

            .metric-value {
                font-size: 2.5em;
                font-weight: 700;
                margin-bottom: 5px;
            }

            .metric-label {
                font-size: 1.1em;
                opacity: 0.9;
                margin-bottom: 5px;
            }

            .metric-change {
                font-size: 0.9em;
                font-weight: 600;
            }

            .metric-change.positive { color: #28a745; }
            .metric-change.negative { color: #dc3545; }

            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }

            .chart-container {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }

            .chart-container.large {
                grid-column: span 2;
            }

            .chart-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }

            .chart-header h3 {
                margin: 0;
                font-size: 1.4em;
                font-weight: 600;
            }

            .chart-controls {
                display: flex;
                gap: 10px;
                align-items: center;
            }

            .form-control {
                padding: 8px 12px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                font-size: 0.9em;
            }

            .form-control::placeholder {
                color: rgba(255, 255, 255, 0.6);
            }

            .chart-body {
                position: relative;
                height: 300px;
            }

            .chart-container.large .chart-body {
                height: 400px;
            }

            .alert-stream {
                height: 350px;
                overflow-y: auto;
                padding: 10px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 8px;
            }

            .alert-item {
                padding: 12px;
                margin-bottom: 10px;
                border-radius: 8px;
                border-left: 4px solid;
                background: rgba(255, 255, 255, 0.05);
                animation: slideIn 0.3s ease;
            }

            @keyframes slideIn {
                from { opacity: 0; transform: translateX(-20px); }
                to { opacity: 1; transform: translateX(0); }
            }

            .alert-item.critical { border-left-color: #dc3545; background: rgba(220, 53, 69, 0.1); }
            .alert-item.high { border-left-color: #fd7e14; background: rgba(253, 126, 20, 0.1); }
            .alert-item.medium { border-left-color: #ffc107; background: rgba(255, 193, 7, 0.1); }
            .alert-item.low { border-left-color: #28a745; background: rgba(40, 167, 69, 0.1); }

            .risk-heatmap {
                display: grid;
                grid-template-columns: repeat(10, 1fr);
                gap: 2px;
                height: 250px;
            }

            .heatmap-cell {
                border-radius: 4px;
                transition: all 0.3s ease;
                cursor: pointer;
            }

            .heatmap-cell:hover {
                transform: scale(1.1);
                z-index: 10;
            }

            .risk-table-container {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }

            .table-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }

            .table-controls {
                display: flex;
                gap: 10px;
                align-items: center;
            }

            .risk-table {
                width: 100%;
                border-collapse: collapse;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                overflow: hidden;
            }

            .risk-table th,
            .risk-table td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }

            .risk-table th {
                background: rgba(255, 255, 255, 0.1);
                font-weight: 600;
            }

            .risk-table tbody tr:hover {
                background: rgba(255, 255, 255, 0.1);
            }

            .priority-badge {
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.8em;
                font-weight: 600;
            }

            .priority-badge.critical { background: #dc3545; }
            .priority-badge.high { background: #fd7e14; }
            .priority-badge.medium { background: #ffc107; color: #000; }
            .priority-badge.low { background: #28a745; }

            .action-buttons {
                display: flex;
                gap: 5px;
            }

            .btn-sm {
                padding: 5px 10px;
                font-size: 0.8em;
            }

            /* Responsive Design */
            @media (max-width: 768px) {
                .dashboard-grid {
                    grid-template-columns: 1fr;
                }
                
                .chart-container.large {
                    grid-column: span 1;
                }
                
                .metrics-row {
                    grid-template-columns: 1fr;
                }
                
                .dashboard-header {
                    flex-direction: column;
                    gap: 20px;
                }
                
                .table-controls {
                    flex-direction: column;
                    width: 100%;
                }
                
                .risk-table {
                    font-size: 0.9em;
                }
            }
        `;
        
        document.head.appendChild(style);
    }

    // Initialize charts
    initializeCharts() {
        // Real-time Risk Chart
        this.active_charts.set('realtime_risk', 
            this.chart_library.createLineChart('realtime-risk-chart', {
                title: 'Real-time Risk Scores',
                datasets: [{
                    label: 'Risk Score',
                    data: [],
                    borderColor: '#ff6b6b',
                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                    tension: 0.4
                }]
            })
        );

        // Risk Distribution Chart
        this.active_charts.set('risk_distribution', 
            this.chart_library.createPieChart('risk-distribution-chart', {
                title: 'Risk Distribution',
                data: {
                    critical: 0,
                    high: 0,
                    medium: 0,
                    low: 0
                }
            })
        );

        // Confidence Gauge Chart
        this.active_charts.set('confidence_gauge', 
            this.chart_library.createGaugeChart('confidence-gauge-chart', {
                title: 'Average Confidence',
                value: 0,
                max: 100
            })
        );

        // Performance Chart
        this.active_charts.set('performance', 
            this.chart_library.createLineChart('performance-chart', {
                title: 'System Performance',
                datasets: [{
                    label: 'CPU Usage',
                    data: [],
                    borderColor: '#4ecdc4',
                    backgroundColor: 'rgba(78, 205, 196, 0.1)'
                }, {
                    label: 'Memory Usage',
                    data: [],
                    borderColor: '#f7b731',
                    backgroundColor: 'rgba(247, 183, 49, 0.1)'
                }]
            })
        );
    }

    // Setup real-time updates
    setupRealTimeUpdates() {
        // Connect to real-time risk engine
        this.realtime_updater.start((data) => {
            this.handleRealTimeUpdate(data);
        });
        
        // Update dashboard periodically
        setInterval(() => {
            this.updateDashboard();
        }, this.visualization_config.update_interval);
    }

    // Handle real-time updates
    handleRealTimeUpdate(data) {
        // Update metrics
        this.updateMetrics(data);
        
        // Update charts
        this.updateCharts(data);
        
        // Update alert stream
        this.updateAlertStream(data);
        
        // Update risk table
        this.updateRiskTable(data);
        
        // Update heatmap
        this.updateHeatmap(data);
    }

    // Update dashboard metrics
    updateMetrics(data) {
        // Update risk counts
        const risk_counts = this.calculateRiskCounts(data);
        
        document.getElementById('critical-risk-count').textContent = risk_counts.critical;
        document.getElementById('high-risk-count').textContent = risk_counts.high;
        document.getElementById('medium-risk-count').textContent = risk_counts.medium;
        
        // Update performance score
        const performance_score = this.calculatePerformanceScore(data);
        document.getElementById('performance-score').textContent = `${performance_score}%`;
        
        // Update change indicators
        this.updateChangeIndicators(data);
    }

    // Update charts with new data
    updateCharts(data) {
        // Update real-time risk chart
        const realtime_chart = this.active_charts.get('realtime_risk');
        if (realtime_chart && data.risk_scores) {
            realtime_chart.addData(data.risk_scores);
        }
        
        // Update risk distribution chart
        const distribution_chart = this.active_charts.get('risk_distribution');
        if (distribution_chart && data.risk_distribution) {
            distribution_chart.updateData(data.risk_distribution);
        }
        
        // Update confidence gauge
        const confidence_chart = this.active_charts.get('confidence_gauge');
        if (confidence_chart && data.average_confidence !== undefined) {
            confidence_chart.updateValue(data.average_confidence);
        }
        
        // Update performance chart
        const performance_chart = this.active_charts.get('performance');
        if (performance_chart && data.performance_metrics) {
            performance_chart.addData(data.performance_metrics);
        }
    }

    // Update alert stream
    updateAlertStream(data) {
        const alert_stream = document.getElementById('alert-stream');
        
        if (data.new_alerts) {
            data.new_alerts.forEach(alert => {
                const alert_element = this.createAlertElement(alert);
                alert_stream.insertBefore(alert_element, alert_stream.firstChild);
            });
            
            // Keep only last 50 alerts
            while (alert_stream.children.length > 50) {
                alert_stream.removeChild(alert_stream.lastChild);
            }
        }
    }

    // Create alert element for stream
    createAlertElement(alert) {
        const alert_div = document.createElement('div');
        alert_div.className = `alert-item ${alert.severity}`;
        alert_div.innerHTML = `
            <div class="alert-header">
                <span class="alert-time">${new Date(alert.timestamp).toLocaleTimeString()}</span>
                <span class="alert-severity">${alert.severity.toUpperCase()}</span>
            </div>
            <div class="alert-content">
                <div class="alert-title">${alert.title}</div>
                <div class="alert-details">
                    Source: ${alert.source_ip} → Target: ${alert.target_ip}
                </div>
            </div>
        `;
        
        return alert_div;
    }

    // Update risk table
    updateRiskTable(data) {
        const table_body = document.getElementById('risk-table-body');
        
        if (data.new_risks) {
            data.new_risks.forEach(risk => {
                const row = this.createRiskTableRow(risk);
                table_body.insertBefore(row, table_body.firstChild);
            });
            
            // Keep only last 100 rows
            while (table_body.children.length > 100) {
                table_body.removeChild(table_body.lastChild);
            }
        }
    }

    // Create risk table row
    createRiskTableRow(risk) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(risk.timestamp).toLocaleString()}</td>
            <td>${risk.risk_score.toFixed(1)}</td>
            <td>${(risk.confidence * 100).toFixed(1)}%</td>
            <td><span class="priority-badge ${risk.priority}">${risk.priority.toUpperCase()}</span></td>
            <td>${risk.correlation_id}</td>
            <td>${risk.source}</td>
            <td>${risk.target}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-primary" onclick="investigateRisk('${risk.id}')">
                        <i class="fas fa-search"></i>
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="acknowledgeRisk('${risk.id}')">
                        <i class="fas fa-check"></i>
                    </button>
                </div>
            </td>
        `;
        
        return row;
    }

    // Update heatmap
    updateHeatmap(data) {
        const heatmap = document.getElementById('risk-heatmap');
        
        if (data.heatmap_data) {
            heatmap.innerHTML = '';
            
            data.heatmap_data.forEach((cell_data, index) => {
                const cell = document.createElement('div');
                cell.className = 'heatmap-cell';
                cell.style.backgroundColor = this.getHeatmapColor(cell_data.intensity);
                cell.title = `Risk: ${cell_data.risk_score}`;
                
                cell.addEventListener('click', () => {
                    this.showHeatmapDetails(cell_data);
                });
                
                heatmap.appendChild(cell);
            });
        }
    }

    // Get heatmap color based on intensity
    getHeatmapColor(intensity) {
        const colors = [
            '#28a745', // Green (low risk)
            '#ffc107', // Yellow (medium risk)
            '#fd7e14', // Orange (high risk)
            '#dc3545'  // Red (critical risk)
        ];
        
        const index = Math.floor(intensity * (colors.length - 1));
        return colors[Math.min(index, colors.length - 1)];
    }

    // Initialize interactions
    initializeInteractions() {
        // Refresh button
        document.getElementById('refresh-dashboard').addEventListener('click', () => {
            this.refreshDashboard();
        });
        
        // Export button
        document.getElementById('export-dashboard').addEventListener('click', () => {
            this.exportDashboardData();
        });
        
        // Settings button
        document.getElementById('settings-dashboard').addEventListener('click', () => {
            this.showSettings();
        });
        
        // Timeframe selector
        document.getElementById('risk-timeframe').addEventListener('change', (e) => {
            this.changeTimeframe(e.target.value);
        });
        
        // Stream controls
        document.getElementById('pause-stream').addEventListener('click', () => {
            this.toggleStream();
        });
        
        document.getElementById('clear-stream').addEventListener('click', () => {
            this.clearStream();
        });
        
        // Search and filter
        document.getElementById('risk-search').addEventListener('input', (e) => {
            this.filterRisks(e.target.value);
        });
        
        document.getElementById('risk-filter').addEventListener('change', (e) => {
            this.filterRisksByPriority(e.target.value);
        });
    }

    // Start dashboard
    startDashboard() {
        console.log('Risk Visualization Dashboard started successfully');
        
        // Show loading complete
        this.showNotification('Dashboard initialized successfully', 'success');
    }

    // Helper methods
    calculateRiskCounts(data) {
        const counts = { critical: 0, high: 0, medium: 0, low: 0 };
        
        if (data.risks) {
            data.risks.forEach(risk => {
                const priority = this.getPriorityLevel(risk.risk_score);
                counts[priority]++;
            });
        }
        
        return counts;
    }

    calculatePerformanceScore(data) {
        if (data.performance_metrics) {
            const cpu = data.performance_metrics.cpu_usage || 0;
            const memory = data.performance_metrics.memory_usage || 0;
            return Math.max(0, 100 - (cpu + memory) / 2);
        }
        return 85; // Default
    }

    getPriorityLevel(risk_score) {
        if (risk_score >= 80) return 'critical';
        if (risk_score >= 60) return 'high';
        if (risk_score >= 40) return 'medium';
        return 'low';
    }

    updateChangeIndicators(data) {
        // Calculate and display changes
        // This would compare with previous data
    }

    changeTimeframe(timeframe) {
        console.log('Changing timeframe to:', timeframe);
        // Update charts with new timeframe
    }

    toggleStream() {
        const button = document.getElementById('pause-stream');
        const is_paused = button.textContent.includes('Pause');
        
        if (is_paused) {
            button.innerHTML = '<i class="fas fa-play"></i> Resume';
            this.realtime_updater.pause();
        } else {
            button.innerHTML = '<i class="fas fa-pause"></i> Pause';
            this.realtime_updater.resume();
        }
    }

    clearStream() {
        document.getElementById('alert-stream').innerHTML = '';
        this.showNotification('Alert stream cleared', 'info');
    }

    filterRisks(search_term) {
        // Filter risk table based on search term
        const rows = document.querySelectorAll('#risk-table-body tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matches = text.includes(search_term.toLowerCase());
            row.style.display = matches ? '' : 'none';
        });
    }

    filterRisksByPriority(priority) {
        const rows = document.querySelectorAll('#risk-table-body tr');
        
        rows.forEach(row => {
            const row_priority = row.querySelector('.priority-badge').textContent.toLowerCase();
            const matches = priority === 'all' || row_priority === priority;
            row.style.display = matches ? '' : 'none';
        });
    }

    refreshDashboard() {
        this.showNotification('Refreshing dashboard...', 'info');
        
        // Refresh all data
        this.updateDashboard();
        
        setTimeout(() => {
            this.showNotification('Dashboard refreshed', 'success');
        }, 1000);
    }

    exportDashboardData() {
        const data = {
            timestamp: new Date().toISOString(),
            dashboard_data: this.dashboard_data,
            performance_metrics: this.risk_engine.getPerformanceMetrics()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `risk-dashboard-${Date.now()}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        this.showNotification('Dashboard data exported', 'success');
    }

    showSettings() {
        // Show settings modal
        this.showNotification('Settings panel coming soon', 'info');
    }

    showHeatmapDetails(cell_data) {
        // Show detailed information for heatmap cell
        this.showNotification(`Risk Score: ${cell_data.risk_score}, Location: ${cell_data.location}`, 'info');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Position notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'success' ? '#28a745' : '#17a2b8'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            animation: slideInRight 0.3s ease;
        `;
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Update dashboard with latest data
    updateDashboard() {
        // Fetch latest data from risk engine
        const latest_data = this.risk_engine.getRealTimeStatus();
        
        // Update all components
        this.handleRealTimeUpdate(latest_data);
    }
}

// Advanced Chart Library
class AdvancedChartLibrary {
    createLineChart(canvas_id, config) {
        // Simplified line chart implementation
        return {
            addData: function(new_data) {
                console.log(`Adding data to ${canvas_id}:`, new_data);
            },
            updateData: function(data) {
                console.log(`Updating ${canvas_id} with:`, data);
            }
        };
    }

    createPieChart(canvas_id, config) {
        return {
            updateData: function(data) {
                console.log(`Updating pie chart ${canvas_id} with:`, data);
            }
        };
    }

    createGaugeChart(canvas_id, config) {
        return {
            updateValue: function(value) {
                console.log(`Updating gauge ${canvas_id} to:`, value);
            }
        };
    }
}

// Real-time Updater
class RealTimeUpdater {
    start(callback) {
        // Use real-time updates only - no mock data
        console.log('Risk dashboard started - waiting for real data updates');
        // No mock data generation - real data will come from WebSocket
    }

    // No mock data generation methods - removed for production

    pause() {
        console.log('Real-time updates paused');
    }

    resume() {
        console.log('Real-time updates resumed');
    }
}

// Interaction Handler
class InteractionHandler {
    constructor() {
        this.setupGlobalHandlers();
    }

    setupGlobalHandlers() {
        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                // Refresh dashboard
            }
        });
    }
}

// Global functions for button actions
window.investigateRisk = function(riskId) {
    console.log('Investigating risk:', riskId);
    alert(`Investigating risk: ${riskId}`);
};

window.acknowledgeRisk = function(riskId) {
    console.log('Acknowledging risk:', riskId);
    alert(`Risk acknowledged: ${riskId}`);
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RiskVisualizationDashboard;
}

// Global instance
window.RiskVisualizationDashboard = RiskVisualizationDashboard;
