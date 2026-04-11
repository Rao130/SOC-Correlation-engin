class FreshAnalytics {
    constructor() {
        this.charts = {};
        this.isActive = false;
        this.refreshInterval = null;
        this.refreshRate = 5000; // 5 seconds
    }

    async init() {
        try {
            console.log('Initializing Fresh Analytics System...');
            this.createCleanDashboard();
            // Don't start auto-refresh by default to prevent errors
            // User can enable it manually if needed
            this.isActive = true;
            console.log('Fresh Analytics System Ready! Auto-refresh disabled by default.');
        } catch (error) {
            console.error('Fresh Analytics Error:', error);
        }
    }

    startAutoRefresh() {
        // Clear any existing interval
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(() => {
            try {
                this.refreshData();
            } catch (error) {
                console.error('Analytics auto-refresh error:', error);
                // Don't throw the error to prevent console spam
            }
        }, this.refreshRate); // 30 seconds
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
            console.log('Auto-refresh stopped');
        }
    }

    refreshData() {
        try {
            console.log('Refreshing analytics data...');
            
            // Only update if charts exist
            if (this.charts.securityOverview) {
                this.updateSecurityOverview();
            }
            
            if (this.charts.threatMonitor) {
                this.updateThreatMonitor();
            }
            
            if (this.charts.activityTimeline) {
                this.updateActivityTimeline();
            }
            
            this.updateSystemStatus();
            
            console.log('Analytics data refreshed successfully');
        } catch (error) {
            console.error('Error refreshing analytics data:', error);
            // Don't throw the error to prevent console spam
        }
    }

    updateSecurityOverview() {
        try {
            const chart = this.charts.securityOverview;
            if (!chart) {
                console.log('Security Overview chart not found, skipping update');
                return;
            }

            // Generate new random data
            const newData = [
                Math.floor(Math.random() * 20) + 5,  // Critical
                Math.floor(Math.random() * 40) + 15, // High
                Math.floor(Math.random() * 60) + 30, // Medium
                Math.floor(Math.random() * 80) + 40, // Low
                Math.floor(Math.random() * 100) + 50 // Info
            ];

            if (chart.data && chart.data.datasets && chart.data.datasets[0]) {
                chart.data.datasets[0].data = newData;
                chart.update('none'); // Update without animation for smooth refresh
            }
        } catch (error) {
            console.error('Error updating Security Overview:', error);
            // Don't throw the error to prevent console spam
        }
    }

    updateThreatMonitor() {
        try {
            const chart = this.charts.threatMonitor;
            if (!chart) {
                console.log('Threat Monitor chart not found, skipping update');
                return;
            }

            // Update with new threat data
            if (chart.data && chart.data.datasets && chart.data.datasets[0] && chart.data.datasets[1]) {
                const newThreats = chart.data.datasets[0].data.map(val => 
                    Math.max(5, val + Math.floor(Math.random() * 10) - 5)
                );
                const newCritical = chart.data.datasets[1].data.map(val => 
                    Math.max(0, val + Math.floor(Math.random() * 6) - 3)
                );

                chart.data.datasets[0].data = newThreats;
                chart.data.datasets[1].data = newCritical;
                chart.update('none');
            }
        } catch (error) {
            console.error('Error updating Threat Monitor:', error);
            // Don't throw the error to prevent console spam
        }
    }

    updateActivityTimeline() {
        try {
            const chart = this.charts.activityTimeline;
            if (!chart) {
                console.log('Activity Timeline chart not found, skipping update');
                return;
            }

            // Update activity data
            if (chart.data && chart.data.datasets && chart.data.datasets[0]) {
                const newActivities = chart.data.datasets[0].data.map(val => 
                    Math.max(10, val + Math.floor(Math.random() * 20) - 10)
                );

                chart.data.datasets[0].data = newActivities;
                chart.update('none');
            }
        } catch (error) {
            console.error('Error updating Activity Timeline:', error);
            // Don't throw the error to prevent console spam
        }
    }

    updateSystemStatus() {
        try {
            // Update system status values
            const systemHealth = Math.floor(Math.random() * 5) + 95; // 95-100%
            const activeAlerts = Math.floor(Math.random() * 20) + 15; // 15-35
            const responseTime = (Math.random() * 0.8 + 0.8).toFixed(1); // 0.8-1.6s
            const uptime = (Math.random() * 0.1 + 99.9).toFixed(1); // 99.9-100%

            // Update DOM elements with null checks
            const healthElement = document.querySelector('.status-value.good');
            const alertsElement = document.querySelectorAll('.status-value.warning')[0];
            const responseElement = document.querySelectorAll('.status-value.good')[1];
            const uptimeElement = document.querySelectorAll('.status-value.good')[2];

            if (healthElement) healthElement.textContent = `${systemHealth}%`;
            if (alertsElement) {
                alertsElement.textContent = activeAlerts;
                // Update alert color based on count
                if (activeAlerts > 30) {
                    alertsElement.className = 'status-value critical';
                } else if (activeAlerts > 20) {
                    alertsElement.className = 'status-value warning';
                } else {
                    alertsElement.className = 'status-value good';
                }
            }
            if (responseElement) responseElement.textContent = `${responseTime}s`;
            if (uptimeElement) uptimeElement.textContent = `${uptime}%`;
        } catch (error) {
            console.error('Error updating system status:', error);
            // Don't throw the error to prevent console spam
        }
    }

    createCleanDashboard() {
        // Create only essential charts with clean data
        this.createSecurityOverview();
        this.createThreatMonitor();
        this.createActivityTimeline();
    }

    createSecurityOverview() {
        const ctx = document.getElementById('security-overview-canvas');
        if (!ctx) return;

        const data = {
            labels: ['Critical', 'High', 'Medium', 'Low', 'Info'],
            datasets: [{
                label: 'Security Alerts',
                data: [12, 28, 45, 67, 89],
                backgroundColor: [
                    'rgba(220, 53, 69, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(255, 152, 0, 0.8)',
                    'rgba(23, 162, 184, 0.8)',
                    'rgba(40, 167, 69, 0.8)'
                ],
                borderColor: [
                    'rgb(220, 53, 69)',
                    'rgb(255, 193, 7)',
                    'rgb(255, 152, 0)',
                    'rgb(23, 162, 184)',
                    'rgb(40, 167, 69)'
                ],
                borderWidth: 2
            }]
        };

        this.charts.securityOverview = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#fff',
                            padding: 15,
                            font: { size: 12 }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#00d4ff',
                        borderWidth: 1
                    }
                }
            }
        });
    }

    createThreatMonitor() {
        const ctx = document.getElementById('threat-monitor-canvas');
        if (!ctx) return;

        const hours = Array.from({length: 24}, (_, i) => `${i}:00`);
        const threats = hours.map(() => Math.floor(Math.random() * 50) + 10);
        const critical = hours.map(() => Math.floor(Math.random() * 10));

        this.charts.threatMonitor = new Chart(ctx, {
            type: 'line',
            data: {
                labels: hours,
                datasets: [{
                    label: 'Total Threats',
                    data: threats,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Critical Threats',
                    data: critical,
                    borderColor: 'rgb(220, 53, 69)',
                    backgroundColor: 'rgba(220, 53, 69, 0.2)',
                    tension: 0.3,
                    fill: false,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: { color: '#fff' }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#00d4ff',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: { display: true, text: 'Time (24 Hours)', color: '#fff' },
                        ticks: { color: '#fff', maxRotation: 45 },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: {
                        display: true,
                        title: { display: true, text: 'Threat Count', color: '#fff' },
                        ticks: { color: '#fff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    createActivityTimeline() {
        const ctx = document.getElementById('activity-timeline-canvas');
        if (!ctx) return;

        const activities = ['Login', 'File Access', 'API Call', 'Database', 'Network', 'System'];
        const values = [145, 89, 234, 67, 123, 45];

        this.charts.activityTimeline = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: activities,
                datasets: [{
                    label: 'Activity Count',
                    data: values,
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(153, 102, 255, 0.8)',
                        'rgba(255, 159, 64, 0.8)'
                    ],
                    borderColor: [
                        'rgb(54, 162, 235)',
                        'rgb(255, 99, 132)',
                        'rgb(255, 206, 86)',
                        'rgb(75, 192, 192)',
                        'rgb(153, 102, 255)',
                        'rgb(255, 159, 64)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#00d4ff',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: { display: true, text: 'Activity Type', color: '#fff' },
                        ticks: { color: '#fff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: {
                        display: true,
                        title: { display: true, text: 'Count', color: '#fff' },
                        ticks: { color: '#fff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    destroy() {
        this.stopAutoRefresh();
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
        this.isActive = false;
    }
}

// Global functions for auto-refresh controls
let autoRefreshEnabled = true;

function toggleAutoRefresh() {
    if (window.freshAnalytics) {
        if (autoRefreshEnabled) {
            window.freshAnalytics.stopAutoRefresh();
            document.getElementById('refresh-icon').className = 'fas fa-play';
            autoRefreshEnabled = false;
            console.log('Auto-refresh disabled');
        } else {
            window.freshAnalytics.startAutoRefresh();
            document.getElementById('refresh-icon').className = 'fas fa-pause';
            autoRefreshEnabled = true;
            console.log('Auto-refresh enabled');
        }
    }
}

function refreshAnalyticsNow() {
    if (window.freshAnalytics) {
        window.freshAnalytics.refreshData();
        // Visual feedback
        const icon = document.getElementById('refresh-icon');
        icon.className = 'fas fa-sync-alt fa-spin';
        setTimeout(() => {
            icon.className = autoRefreshEnabled ? 'fas fa-pause' : 'fas fa-play';
        }, 1000);
    }
}

// Initialize Fresh Analytics
document.addEventListener('DOMContentLoaded', () => {
    if (typeof Chart !== 'undefined') {
        window.freshAnalytics = new FreshAnalytics();
        window.freshAnalytics.init();
    }
});
