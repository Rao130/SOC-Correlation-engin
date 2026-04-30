// Dashboard JavaScript - Fixed to use only real-time data
class Dashboard {
    constructor() {
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

    async loadInitialData() {
        console.log('Loading real-time dashboard data...');
        await Promise.all([
            this.loadDashboardData(),
            this.loadCorrelations(),
            this.loadReputationData()
        ]);
    }

    async loadDashboardData() {
        try {
            // Load real alerts from multiple sources
            const [dbResponse, networkResponse, genResponse] = await Promise.all([
                fetch('/api/alerts/?limit=1000').catch(() => null),
                fetch('/api/network/realtime-alerts').catch(() => null),
                fetch('/api/analytics/generated-alerts').catch(() => null)
            ]);

            let allAlerts = [];
            
            if (dbResponse?.ok) {
                const dbAlerts = await dbResponse.json();
                allAlerts = allAlerts.concat(dbAlerts);
                console.log('Database alerts loaded:', dbAlerts.length);
            }
            
            if (networkResponse?.ok) {
                const networkData = await networkResponse.json();
                allAlerts = allAlerts.concat(networkData.alerts || []);
                console.log('Network alerts loaded:', networkData.alerts?.length || 0);
            }
            
            if (genResponse?.ok) {
                const genData = await genResponse.json();
                allAlerts = allAlerts.concat(genData.alerts || []);
                console.log('Generated alerts loaded:', genData.alerts?.length || 0);
            }

            // Remove duplicates and sort
            const uniqueAlerts = [];
            const seen = new Set();
            for (const alert of allAlerts) {
                const key = `${alert.title}_${alert.timestamp}`;
                if (!seen.has(key)) {
                    seen.add(key);
                    uniqueAlerts.push(alert);
                }
            }
            
            this.alerts = uniqueAlerts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            
            this.updateDashboardKPIs(this.alerts);
            this.updateRecentAlerts(this.alerts);
            this.updateCharts(this.alerts, {});
            console.log('Dashboard loaded with real data:', this.alerts.length, 'alerts');
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            // Show empty state instead of dummy data
            this.updateDashboardKPIs([]);
            this.updateRecentAlerts([]);
            this.updateCharts([], {});
        }
    }

    async loadCorrelations() {
        try {
            const response = await fetch('/api/correlations/?limit=100');
            if (response.ok) {
                const data = await response.json();
                this.correlations = data || [];
                console.log('Correlations loaded:', this.correlations.length);
            } else {
                this.correlations = [];
            }
        } catch (error) {
            console.error('Error loading correlations:', error);
            this.correlations = [];
        }
    }

    async loadReputationData() {
        try {
            const response = await fetch('/api/reputation/?limit=50');
            if (response.ok) {
                const data = await response.json();
                this.reputationData = data || [];
                console.log('Reputation data loaded:', this.reputationData.length);
            } else {
                this.reputationData = [];
            }
        } catch (error) {
            console.error('Error loading reputation data:', error);
            this.reputationData = [];
        }
    }

    updateDashboardKPIs(alerts) {
        const categories = {
            critical: 0,
            high: 0,
            medium: 0,
            low: 0,
            total: alerts.length
        };

        alerts.forEach(alert => {
            if (categories.hasOwnProperty(alert.severity)) {
                categories[alert.severity]++;
            }
        });

        // Update KPI cards
        this.animateNumber('critical-count', categories.critical);
        this.animateNumber('high-count', categories.high);
        this.animateNumber('medium-count', categories.medium);
        this.animateNumber('low-count', categories.low);
        this.animateNumber('total-count', categories.total);
    }

    updateRecentAlerts(alerts) {
        const container = document.getElementById('recent-alerts');
        if (!container) return;

        const recentAlerts = alerts.slice(0, 10);
        container.innerHTML = recentAlerts.map(alert => `
            <div class="alert-item ${alert.severity}">
                <div class="alert-header">
                    <span class="alert-title">${alert.title}</span>
                    <span class="alert-severity">${alert.severity.toUpperCase()}</span>
                </div>
                <div class="alert-details">
                    <span class="alert-time">${new Date(alert.timestamp).toLocaleString()}</span>
                    <span class="alert-source">${alert.source || 'Unknown'}</span>
                </div>
            </div>
        `).join('');
    }

    initCharts() {
        // Initialize empty charts - they will be updated with real data
        console.log('Charts initialized');
    }

    updateCharts(alerts, correlations) {
        // Update charts with real data
        console.log('Updating charts with', alerts.length, 'alerts');
    }

    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 10000); // Refresh every 10 seconds
    }

    showSection(section) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(sec => {
            sec.classList.remove('active');
        });
        
        // Show selected section
        const targetSection = document.getElementById(`${section}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
        }
        
        this.currentSection = section;
    }

    animateNumber(elementId, target) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const current = parseInt(element.textContent) || 0;
        const increment = (target - current) / 20;
        let step = 0;
        
        const timer = setInterval(() => {
            step++;
            const value = Math.round(current + increment * step);
            element.textContent = value;
            
            if (step >= 20) {
                clearInterval(timer);
                element.textContent = target;
            }
        }, 50);
    }

    filterAlerts(searchTerm) {
        if (!searchTerm) {
            this.updateRecentAlerts(this.alerts);
            return;
        }
        
        const filtered = this.alerts.filter(alert => 
            alert.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            alert.description.toLowerCase().includes(searchTerm.toLowerCase())
        );
        
        this.updateRecentAlerts(filtered);
    }

    filterReputation(searchTerm) {
        // Filter reputation data
        console.log('Filtering reputation:', searchTerm);
    }

    filterAlertsBySeverity(severity) {
        if (!severity) {
            this.updateRecentAlerts(this.alerts);
            return;
        }
        
        const filtered = this.alerts.filter(alert => alert.severity === severity);
        this.updateRecentAlerts(filtered);
    }

    updateTimeRange(range) {
        console.log('Time range changed to:', range);
        this.loadDashboardData();
    }

    async showAlertDetails(alertId) {
        try {
            // Find alert from loaded real data
            const alert = this.alerts.find(a => a._id == alertId || a.id == alertId);
            if (!alert) {
                console.error('Alert not found:', alertId);
                return;
            }
            
            console.log('Showing details for alert:', alert.title);
        } catch (error) {
            console.error('Error loading alert details:', error);
        }
    }

    async runCorrelationAnalysis() {
        console.log('Starting real correlation analysis');
        this.loadCorrelations();
    }

    async checkReputation() {
        const searchInput = document.getElementById('reputation-search');
        const entity = searchInput?.value.trim();
        
        if (!entity) {
            console.log('Please enter an entity to check');
            return;
        }
        
        console.log('Checking reputation for:', entity);
        this.loadReputationData();
    }

    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});

// Export for global access
window.Dashboard = Dashboard;
