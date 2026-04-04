// Advanced Analytics and Visualization System
class AdvancedAnalytics {
    constructor() {
        this.charts = {};
        this.visualizations = {};
        this.currentDashboard = null;
        this.realtimeData = {};
        this.filters = {};
    }

    async init() {
        try {
            // Initialize advanced charts
            this.initializeAdvancedCharts();
            
            // Load dashboard data
            await this.loadDashboardData();
            
            // Setup real-time updates
            this.setupRealtimeUpdates();
            
            // Setup event listeners
            this.setupEventListeners();
            
            console.log('Advanced Analytics initialized');
        } catch (error) {
            console.error('Error initializing analytics:', error);
        }
    }

    initializeAdvancedCharts() {
        // Initialize advanced chart types
        this.charts.threatHeatmap = this.createThreatHeatmap();
        this.charts.attackTimeline = this.createAttackTimeline();
        this.charts.entityNetwork = this.createEntityNetwork();
        this.charts.patternAnalysis = this.createPatternAnalysis();
        this.charts.complianceMatrix = this.createComplianceMatrix();
        this.charts.performanceMetrics = this.createPerformanceMetrics();
        this.charts.threatLifecycle = this.createThreatLifecycle();
    }

    createThreatHeatmap() {
        const ctx = document.getElementById('threat-heatmap-canvas');
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'heatmap',
            data: {
                datasets: [{
                    label: 'Threat Intensity',
                    data: [],
                    backgroundColor: (context) => {
                        const value = context.dataset.data[context.dataIndex];
                        if (value > 80) return 'rgba(211, 47, 47, 0.8)';
                        if (value > 60) return 'rgba(244, 67, 54, 0.8)';
                        if (value > 40) return 'rgba(255, 152, 0, 0.8)';
                        return 'rgba(76, 175, 80, 0.8)';
                    },
                    borderColor: 'rgba(255, 255, 255, 0.3)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.dataset.data[context.dataIndex];
                                return `Intensity: ${value.toFixed(1)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: {
                            display: true,
                            text: 'Geographic Region'
                        }
                    },
                    y: {
                        type: 'linear',
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Threat Intensity'
                        }
                    }
                }
            }
        });
    }

    createAttackTimeline() {
        const ctx = document.getElementById('attack-timeline-canvas');
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Attack Volume',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Critical Attacks',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.4,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'hour',
                            displayFormats: {
                                hour: 'HH:mm'
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Attacks'
                        }
                    }
                }
            }
        });
    }

    createEntityNetwork() {
        const ctx = document.getElementById('entity-network-canvas');
        if (!ctx) return null;

        // Create a network visualization (simplified for demo)
        return {
            canvas: ctx,
            nodes: [],
            edges: [],
            render: function() {
                // Simple network rendering
                const canvas = this.canvas;
                const ctx = canvas.getContext('2d');
                
                // Clear canvas
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Draw edges
                ctx.strokeStyle = '#666';
                ctx.lineWidth = 1;
                this.edges.forEach(edge => {
                    const sourceNode = this.nodes.find(n => n.id === edge.source);
                    const targetNode = this.nodes.find(n => n.id === edge.target);
                    
                    if (sourceNode && targetNode) {
                        ctx.beginPath();
                        ctx.moveTo(sourceNode.x, sourceNode.y);
                        ctx.lineTo(targetNode.x, targetNode.y);
                        ctx.stroke();
                    }
                });
                
                // Draw nodes
                this.nodes.forEach(node => {
                    ctx.fillStyle = this.getNodeColor(node.riskLevel);
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, node.size, 0, 2 * Math.PI);
                    ctx.fill();
                    
                    // Draw node label
                    ctx.fillStyle = '#fff';
                    ctx.font = '10px Arial';
                    ctx.textAlign = 'center';
                    ctx.fillText(node.label, node.x, node.y + 3);
                });
            },
            updateData: function(nodes, edges) {
                this.nodes = nodes;
                this.edges = edges;
                this.render();
            }
        };
    }

    createPatternAnalysis() {
        const ctx = document.getElementById('pattern-analysis-canvas');
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Frequency', 'Confidence', 'Risk Level', 'Impact', 'Detection Rate'],
                datasets: [{
                    label: 'Pattern Analysis',
                    data: [0, 0, 0, 0, 0],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    pointBackgroundColor: 'rgb(255, 99, 132)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(255, 99, 132)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 100
                    }
                }
            }
        });
    }

    createComplianceMatrix() {
        const ctx = document.getElementById('compliance-matrix-canvas');
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Access Control', 'Audit Trail', 'Data Protection', 'Network Security'],
                datasets: [{
                    label: 'ISO 27001',
                    data: [85, 88, 92, 78],
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: 'rgb(54, 162, 235)',
                    borderWidth: 1
                }, {
                    label: 'GDPR',
                    data: [92, 95, 88, 85],
                    backgroundColor: 'rgba(75, 192, 192, 0.8)',
                    borderColor: 'rgb(75, 192, 192)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Compliance Score (%)'
                        }
                    }
                }
            }
        });
    }

    createPerformanceMetrics() {
        const ctx = document.getElementById('performance-metrics-canvas');
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'MTTR (minutes)',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    yAxisID: 'y'
                }, {
                    label: 'Response Time (ms)',
                    data: [],
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'hour'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'MTTR (min)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Response Time (ms)'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });
    }

    createThreatLifecycle() {
        const ctx = document.getElementById('threat-lifecycle-canvas');
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Detection', 'Analysis', 'Containment', 'Eradication'],
                datasets: [{
                    data: [25, 35, 20, 15],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 152, 0, 0.8)',
                        'rgba(75, 192, 192, 0.8)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                }
            }
        });
    }

    async loadDashboardData() {
        try {
            // Load threat heatmap data
            await this.loadThreatHeatmap();
            
            // Load attack timeline data
            await this.loadAttackTimeline();
            
            // Load entity network data
            await this.loadEntityNetwork();
            
            // Load pattern analysis data
            await this.loadPatternAnalysis();
            
            // Load compliance matrix data
            await this.loadComplianceMatrix();
            
            // Load performance metrics
            await this.loadPerformanceMetrics();
            
            // Load threat lifecycle data
            await this.loadThreatLifecycle();
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async loadThreatHeatmap() {
        try {
            const response = await fetch('/api/analytics/threat-heatmap');
            const data = await response.json();
            
            if (this.charts.threatHeatmap) {
                this.updateThreatHeatmap(data);
            }
        } catch (error) {
            console.error('Error loading threat heatmap:', error);
        }
    }

    async loadAttackTimeline() {
        try {
            const response = await fetch('/api/analytics/attack-timeline');
            const data = await response.json();
            
            if (this.charts.attackTimeline) {
                this.updateAttackTimeline(data);
            }
        } catch (error) {
            console.error('Error loading attack timeline:', error);
        }
    }

    async loadEntityNetwork() {
        try {
            const response = await fetch('/api/analytics/entity-network');
            const data = await response.json();
            
            if (this.charts.entityNetwork) {
                this.updateEntityNetwork(data);
            }
        } catch (error) {
            console.error('Error loading entity network:', error);
        }
    }

    async loadPatternAnalysis() {
        try {
            const response = await fetch('/api/analytics/pattern-analysis');
            const data = await response.json();
            
            if (this.charts.patternAnalysis) {
                this.updatePatternAnalysis(data);
            }
        } catch (error) {
            console.error('Error loading pattern analysis:', error);
        }
    }

    async loadComplianceMatrix() {
        try {
            const response = await fetch('/api/analytics/compliance-matrix');
            const data = await response.json();
            
            if (this.charts.complianceMatrix) {
                this.updateComplianceMatrix(data);
            }
        } catch (error) {
            console.error('Error loading compliance matrix:', error);
        }
    }

    async loadPerformanceMetrics() {
        try {
            const response = await fetch('/api/analytics/performance-metrics');
            const data = await response.json();
            
            if (this.charts.performanceMetrics) {
                this.updatePerformanceMetrics(data);
            }
        } catch (error) {
            console.error('Error loading performance metrics:', error);
        }
    }

    async loadThreatLifecycle() {
        try {
            const response = await fetch('/api/analytics/threat-lifecycle');
            const data = await response.json();
            
            if (this.charts.threatLifecycle) {
                this.updateThreatLifecycle(data);
            }
        } catch (error) {
            console.error('Error loading threat lifecycle:', error);
        }
    }

    updateThreatHeatmap(data) {
        const chart = this.charts.threatHeatmap;
        if (!chart) return;

        // Update heatmap data
        chart.data.datasets[0].data = data.data.heatmap_data.map(point => ({
            x: point.center[0],
            y: point.center[1],
            v: point.intensity
        }));
        
        chart.update();
    }

    updateAttackTimeline(data) {
        const chart = this.charts.attackTimeline;
        if (!chart) return;

        // Update timeline data
        chart.data.labels = data.data.grouped_data.map(item => item.time_bucket);
        chart.data.datasets[0].data = data.data.grouped_data.map(item => item.events.length);
        
        chart.update();
    }

    updateEntityNetwork(data) {
        const network = this.charts.entityNetwork;
        if (!network) return;

        // Update network data
        network.updateData(data.data.nodes, data.data.edges);
    }

    updatePatternAnalysis(data) {
        const chart = this.charts.patternAnalysis;
        if (!chart) return;

        // Update pattern analysis data
        chart.data.datasets[0].data = data.data.pattern_analysis.map(pattern => ({
            axis: pattern.pattern_id,
            value: pattern.confidence * 100
        }));
        
        chart.update();
    }

    updateComplianceMatrix(data) {
        const chart = this.charts.complianceMatrix;
        if (!chart) return;

        // Update compliance matrix data
        const frameworks = Object.keys(data.data.compliance_matrix);
        chart.data.labels = frameworks;
        chart.data.datasets = frameworks.map(framework => ({
            label: framework,
            data: Object.values(data.data.compliance_matrix[framework]).map(control => control.score)
        }));
        
        chart.update();
    }

    updatePerformanceMetrics(data) {
        const chart = this.charts.performanceMetrics;
        if (!chart) return;

        // Update performance metrics
        chart.data.labels = data.data.time_ranges;
        chart.data.datasets[0].data = data.data.performance_data.mttr;
        chart.data.datasets[1].data = data.data.performance_data.response_time;
        
        chart.update();
    }

    updateThreatLifecycle(data) {
        const chart = this.charts.threatLifecycle;
        if (!chart) return;

        // Update threat lifecycle data
        chart.data.datasets[0].data = data.data.threats.map(threat => 
            Object.values(data.data.stages).indexOf(threat.current_stage)
        );
        
        chart.update();
    }

    getNodeColor(riskLevel) {
        const colors = {
            'critical': '#d32f2f',
            'high': '#f44336',
            'medium': '#ff9800',
            'low': '#4caf50'
        };
        return colors[riskLevel] || '#666';
    }

    setupRealtimeUpdates() {
        // Set up WebSocket connection for real-time updates
        if (window.wsManager) {
            window.wsManager.addMessageHandler('analytics_update', (data) => {
                this.handleRealtimeUpdate(data);
            });
        }
    }

    handleRealtimeUpdate(data) {
        try {
            switch (data.type) {
                case 'threat_heatmap':
                    this.updateThreatHeatmap(data);
                    break;
                case 'attack_timeline':
                    this.updateAttackTimeline(data);
                    break;
                case 'entity_network':
                    this.updateEntityNetwork(data);
                    break;
                case 'pattern_analysis':
                    this.updatePatternAnalysis(data);
                    break;
                case 'compliance_matrix':
                    this.updateComplianceMatrix(data);
                    break;
                case 'performance_metrics':
                    this.updatePerformanceMetrics(data);
                    break;
                case 'threat_lifecycle':
                    this.updateThreatLifecycle(data);
                    break;
            }
        } catch (error) {
            console.error('Error handling real-time update:', error);
        }
    }

    setupEventListeners() {
        // Dashboard type switcher
        const dashboardSelector = document.getElementById('dashboard-type-selector');
        if (dashboardSelector) {
            dashboardSelector.addEventListener('change', (e) => {
                this.switchDashboard(e.target.value);
            });
        }

        // Time range selector
        const timeRangeSelector = document.getElementById('time-range-selector');
        if (timeRangeSelector) {
            timeRangeSelector.addEventListener('change', (e) => {
                this.updateTimeRange(e.target.value);
            });
        }

        // Export functionality
        const exportButtons = document.querySelectorAll('.export-btn');
        exportButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.exportVisualization(e.target.dataset.vizType, e.target.dataset.format);
            });
        });

        // Filter controls
        const filterControls = document.querySelectorAll('.filter-control');
        filterControls.forEach(control => {
            control.addEventListener('change', (e) => {
                this.applyFilter(e.target.dataset.filter, e.target.value);
            });
        });
    }

    async switchDashboard(type) {
        try {
            this.currentDashboard = type;
            
            // Load dashboard data
            const response = await fetch(`/api/analytics/dashboards/${type}`);
            const data = await response.json();
            
            // Update dashboard content
            this.updateDashboardContent(data.dashboard);
            
        } catch (error) {
            console.error('Error switching dashboard:', error);
        }
    }

    updateTimeRange(range) {
        this.filters.timeRange = range;
        this.refreshAllCharts();
    }

    applyFilter(filterType, filterValue) {
        this.filters[filterType] = filterValue;
        this.refreshAllCharts();
    }

    refreshAllCharts() {
        // Refresh all charts with current filters
        this.loadDashboardData();
    }

    updateDashboardContent(dashboard) {
        const content = document.getElementById('dashboard-content');
        if (!content) return;

        // Update dashboard widgets
        let html = '';
        
        dashboard.widgets.forEach(widget => {
            html += this.renderWidget(widget);
        });
        
        content.innerHTML = html;
    }

    renderWidget(widget) {
        switch (widget.type) {
            case 'kpi_grid':
                return this.renderKPIGrid(widget.data);
            case 'threat_overview':
                return this.renderThreatOverview(widget.data);
            case 'compliance_status':
                return this.renderComplianceStatus(widget.data);
            default:
                return `<div class="widget-placeholder">Widget: ${widget.type}</div>`;
        }
    }

    renderKPIGrid(data) {
        return `
            <div class="kpi-grid">
                <div class="kpi-card">
                    <h3>MTTR</h3>
                    <div class="kpi-value">${data.mttr}m</div>
                </div>
                <div class="kpi-card">
                    <h3>Response Time</h3>
                    <div class="kpi-value">${data.response_time}ms</div>
                </div>
                <div class="kpi-card">
                    <h3>Throughput</h3>
                    <div class="kpi-value">${data.throughput}</div>
                </div>
                <div class="kpi-card">
                    <h3>SLA Breach Rate</h3>
                    <div class="kpi-value">${data.sla_breach_rate}%</div>
                </div>
            </div>
        `;
    }

    renderThreatOverview(data) {
        return `
            <div class="threat-overview">
                <h3>Threat Landscape</h3>
                <div class="threat-stats">
                    <div class="threat-stat">
                        <span class="threat-label">Total:</span>
                        <span class="threat-value">${data.total}</span>
                    </div>
                    <div class="threat-stat">
                        <span class="threat-label">Critical:</span>
                        <span class="threat-value critical">${data.critical}</span>
                    </div>
                    <div class="threat-stat">
                        <span class="threat-label">High:</span>
                        <span class="threat-value high">${data.high}</span>
                    </div>
                    <div class="threat-stat">
                        <span class="threat-label">Medium:</span>
                        <span class="threat-value medium">${data.medium}</span>
                    </div>
                    <div class="threat-stat">
                        <span class="threat-label">Low:</span>
                        <span class="threat-value low">${data.low}</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderComplianceStatus(data) {
        return `
            <div class="compliance-status">
                <h3>Compliance Status</h3>
                <div class="compliance-grid">
                    <div class="compliance-item">
                        <span class="compliance-label">ISO 27001:</span>
                        <span class="compliance-score">${data.iso_compliance}%</span>
                    </div>
                    <div class="compliance-item">
                        <span class="compliance-label">GDPR:</span>
                        <span class="compliance-score">${data.gdpr_compliance}%</span>
                    </div>
                    <div class="compliance-item">
                        <span class="compliance-label">PCI DSS:</span>
                        <span class="compliance-score">${data.pci_dss_compliance}%</span>
                    </div>
                </div>
            </div>
        `;
    }

    async exportVisualization(vizType, format) {
        try {
            const response = await fetch(`/api/analytics/export/${vizType}?format=${format}`);
            const data = await response.json();
            
            // Create download link
            const blob = new Blob([JSON.stringify(data.export_data, null, 2)], {
                type: format === 'csv' ? 'text/csv' : 'application/json'
            });
            
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `analytics_${vizType}_${new Date().toISOString().split('T')[0]}.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Error exporting visualization:', error);
        }
    }

    // Export for global access
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = AdvancedAnalytics;
    }
}

// Initialize advanced analytics when page loads
document.addEventListener('DOMContentLoaded', () => {
    if (typeof Chart !== 'undefined') {
        window.advancedAnalytics = new AdvancedAnalytics();
        window.advancedAnalytics.init();
    } else {
        console.error('Chart.js library not loaded for advanced analytics');
    }
});
