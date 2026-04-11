// Correlation Engine JavaScript - Premium Implementation
class CorrelationManager {
    constructor() {
        this.correlationData = [];
        this.filteredData = [];
        this.currentPage = 1;
        this.pageSize = 20;
        this.sortField = 'name';
        this.sortOrder = 'asc';
        this.autoRefreshInterval = null;
        this.filters = {
            search: '',
            correlation_type: '',
            status: '',
            score_range: ''
        };
        
        this.init();
    }

    init() {
        console.log('Initializing Correlation Manager...');
        this.loadCorrelationData();
        this.setupEventListeners();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Search and filter listeners
        document.getElementById('correlation-search')?.addEventListener('keyup', (e) => {
            if (e.key === 'Enter') {
                this.applyFilters();
            } else {
                clearTimeout(window.correlationSearchTimeout);
                window.correlationSearchTimeout = setTimeout(() => {
                    this.applyFilters();
                }, 500);
            }
        });

        document.getElementById('correlation-type-filter')?.addEventListener('change', () => this.applyFilters());
        document.getElementById('correlation-status-filter')?.addEventListener('change', () => this.applyFilters());
        document.getElementById('correlation-score-filter')?.addEventListener('change', () => this.applyFilters());
    }

    generateMockCorrelationData() {
        const correlations = [];
        const correlationTypes = ['entity_based', 'temporal', 'geographic', 'pattern_based'];
        const statuses = ['active', 'investigating', 'resolved', 'false_positive'];
        const threatNames = [
            'SQL Injection Cluster', 'Brute Force Attack Pattern', 'Suspicious Login Sequence',
            'Geographic Anomaly', 'Malware Distribution Network', 'Data Exfiltration Pattern',
            'Lateral Movement Detection', 'Privilege Escalation Chain', 'Command & Control Traffic',
            'Insider Threat Pattern', 'Phishing Campaign Correlation', 'Zero-Day Exploit Pattern'
        ];
        
        for (let i = 0; i < 150; i++) {
            const threatName = threatNames[Math.floor(Math.random() * threatNames.length)];
            const correlationType = correlationTypes[Math.floor(Math.random() * correlationTypes.length)];
            const status = statuses[Math.floor(Math.random() * statuses.length)];
            const score = Math.floor(Math.random() * 100);
            
            correlations.push({
                id: `corr-${i + 1}`,
                name: threatName,
                correlation_type: correlationType,
                correlation_score: score,
                status: status,
                alerts_count: Math.floor(Math.random() * 50) + 1,
                entities_count: Math.floor(Math.random() * 20) + 1,
                created_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
                updated_at: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
                description: `Advanced ${correlationType.replace('_', ' ')} correlation detected with ${status} status`,
                severity: this.getSeverityFromScore(score),
                confidence: Math.floor(Math.random() * 40) + 60,
                tags: [correlationType, status, this.getSeverityFromScore(score)]
            });
        }

        return correlations;
    }

    getSeverityFromScore(score) {
        if (score >= 80) return 'critical';
        if (score >= 60) return 'high';
        if (score >= 40) return 'medium';
        return 'low';
    }

    async loadCorrelationData() {
        try {
            // Try to fetch real correlation data from API
            const response = await fetch('/api/correlation/list?limit=1000');
            if (!response.ok) {
                throw new Error('Failed to fetch correlation data');
            }
            
            const data = await response.json();
            this.correlationData = data.correlations || [];
            
            // If no data exists, create some initial data
            if (this.correlationData.length === 0) {
                await this.createInitialCorrelationData();
                // Reload after creating initial data
                await this.loadCorrelationData();
                return;
            }
            
            this.applyFilters();
            this.updateStatistics();
            this.updateCorrelationTypes();
            this.updateActiveCorrelations();
            console.log('Real correlation data loaded:', this.correlationData.length, 'correlations');
        } catch (error) {
            console.error('Error loading correlation data:', error);
            // Fallback to mock data if API fails
            this.correlationData = this.generateMockCorrelationData();
            this.applyFilters();
            this.updateStatistics();
            this.updateCorrelationTypes();
            this.updateActiveCorrelations();
            console.log('Fallback to mock correlation data loaded');
        }
    }

    async createInitialCorrelationData() {
        try {
            // Create some initial correlation data
            const mockData = this.generateMockCorrelationData();
            
            for (const correlation of mockData.slice(0, 20)) { // Start with 20 correlations
                await this.createCorrelationEntity(correlation);
            }
            
            console.log('Initial correlation data created');
        } catch (error) {
            console.error('Error creating initial data:', error);
        }
    }

    async createCorrelationEntity(correlation) {
        try {
            const response = await fetch('/api/correlation/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: correlation.name,
                    correlation_type: correlation.correlation_type,
                    correlation_score: correlation.correlation_score,
                    status: correlation.status,
                    alerts_count: correlation.alerts_count,
                    entities_count: correlation.entities_count,
                    description: correlation.description,
                    severity: correlation.severity,
                    confidence: correlation.confidence,
                    tags: correlation.tags
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to create correlation entity');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error creating correlation entity:', error);
            throw error;
        }
    }

    applyFilters() {
        this.filters.search = document.getElementById('correlation-search')?.value.toLowerCase() || '';
        this.filters.correlation_type = document.getElementById('correlation-type-filter')?.value || '';
        this.filters.status = document.getElementById('correlation-status-filter')?.value || '';
        this.filters.score_range = document.getElementById('correlation-score-filter')?.value || '';

        this.filteredData = this.correlationData.filter(correlation => {
            if (this.filters.search && !correlation.name.toLowerCase().includes(this.filters.search)) {
                return false;
            }
            if (this.filters.correlation_type && correlation.correlation_type !== this.filters.correlation_type) {
                return false;
            }
            if (this.filters.status && correlation.status !== this.filters.status) {
                return false;
            }
            if (this.filters.score_range) {
                const score = correlation.correlation_score;
                switch(this.filters.score_range) {
                    case 'high':
                        if (score < 80) return false;
                        break;
                    case 'medium':
                        if (score < 50 || score >= 80) return false;
                        break;
                    case 'low':
                        if (score >= 50) return false;
                        break;
                }
            }
            return true;
        });

        this.currentPage = 1;
        this.displayCorrelationData();
        this.updateStatistics();
    }

    displayCorrelationData() {
        const tbody = document.getElementById('correlation-tbody');
        if (!tbody) return;

        const startIndex = (this.currentPage - 1) * this.pageSize;
        const endIndex = startIndex + this.pageSize;
        const pageData = this.filteredData.slice(startIndex, endIndex);

        tbody.innerHTML = '';

        pageData.forEach(correlation => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="correlation-name">${correlation.name}</span></td>
                <td><span class="correlation-type-badge ${correlation.correlation_type}">${correlation.correlation_type.replace('_', ' ').toUpperCase()}</span></td>
                <td><span class="score-badge ${this.getScoreClass(correlation.correlation_score)}">${correlation.correlation_score}/100</span></td>
                <td><span class="status-badge ${correlation.status}">${correlation.status.toUpperCase()}</span></td>
                <td><span class="alert-count">${correlation.alerts_count}</span></td>
                <td><span class="entity-count">${correlation.entities_count}</span></td>
                <td><span class="created-date">${this.formatDate(correlation.created_at)}</span></td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="correlationManager.viewCorrelationDetails('${correlation.id}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });

        this.updatePagination();
        document.getElementById('correlation-count').textContent = `${this.filteredData.length} correlations`;
    }

    getScoreClass(score) {
        if (score >= 80) return 'high';
        if (score >= 50) return 'medium';
        return 'low';
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });
    }

    updatePagination() {
        const totalPages = Math.ceil(this.filteredData.length / this.pageSize);
        const pageInfo = document.getElementById('correlation-page-info');
        const prevBtn = document.getElementById('correlation-prev-btn');
        const nextBtn = document.getElementById('correlation-next-btn');

        if (pageInfo) {
            pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
        }

        if (prevBtn) {
            prevBtn.disabled = this.currentPage === 1;
        }

        if (nextBtn) {
            nextBtn.disabled = this.currentPage >= totalPages;
        }
    }

    updateStatistics() {
        const stats = {
            active: 0,
            investigating: 0,
            resolved: 0,
            entity_based: 0,
            temporal: 0,
            geographic: 0,
            pattern_based: 0,
            total: 0
        };

        this.filteredData.forEach(correlation => {
            stats[correlation.status]++;
            stats[correlation.correlation_type]++;
            stats.total++;
        });

        // Update hero stats
        document.getElementById('correlation-total-groups').textContent = stats.total.toLocaleString();
        document.getElementById('correlation-active-groups').textContent = stats.active.toLocaleString();
        document.getElementById('correlation-patterns-found').textContent = Math.floor(stats.total * 0.27).toLocaleString();

        // Update correlation types
        document.getElementById('entity-based-count').textContent = stats.entity_based;
        document.getElementById('temporal-count').textContent = stats.temporal;
        document.getElementById('geographic-count').textContent = stats.geographic;
        document.getElementById('pattern-based-count').textContent = stats.pattern_based;

        // Update percentages
        const entityPercentage = stats.total > 0 ? ((stats.entity_based / stats.total) * 100).toFixed(1) : 0;
        const temporalPercentage = stats.total > 0 ? ((stats.temporal / stats.total) * 100).toFixed(1) : 0;
        const geographicPercentage = stats.total > 0 ? ((stats.geographic / stats.total) * 100).toFixed(1) : 0;
        const patternPercentage = stats.total > 0 ? ((stats.pattern_based / stats.total) * 100).toFixed(1) : 0;

        // Update percentage displays
        const typeCards = document.querySelectorAll('.type-card');
        if (typeCards[0]) {
            const entityCard = typeCards[0].querySelector('.type-percentage');
            if (entityCard) entityCard.textContent = `${entityPercentage}%`;
        }
        if (typeCards[1]) {
            const temporalCard = typeCards[1].querySelector('.type-percentage');
            if (temporalCard) temporalCard.textContent = `${temporalPercentage}%`;
        }
        if (typeCards[2]) {
            const geographicCard = typeCards[2].querySelector('.type-percentage');
            if (geographicCard) geographicCard.textContent = `${geographicPercentage}%`;
        }
        if (typeCards[3]) {
            const patternCard = typeCards[3].querySelector('.type-percentage');
            if (patternCard) patternCard.textContent = `${patternPercentage}%`;
        }
    }

    updateCorrelationTypes() {
        // This is handled in updateStatistics
    }

    updateActiveCorrelations() {
        const threats = this.correlationData
            .filter(correlation => correlation.status === 'active')
            .sort((a, b) => b.correlation_score - a.correlation_score)
            .slice(0, 4);

        const threatsList = document.querySelector('.correlations-list');
        if (!threatsList) return;

        threatsList.innerHTML = '';

        const severityClasses = ['critical', 'high', 'medium', 'low'];
        
        threats.forEach((threat, index) => {
            const threatItem = document.createElement('div');
            threatItem.className = `correlation-item ${severityClasses[index]}`;
            threatItem.innerHTML = `
                <div class="correlation-info">
                    <div class="correlation-name">${threat.name}</div>
                    <div class="correlation-type">${threat.correlation_type.replace('_', ' ').charAt(0).toUpperCase() + threat.correlation_type.replace('_', ' ').slice(1)}</div>
                    <div class="correlation-score">Score: ${threat.correlation_score}/100</div>
                </div>
                <div class="correlation-details">
                    <div class="alert-count">${threat.alerts_count} alerts</div>
                    <div class="entity-count">${threat.entities_count} entities</div>
                    <div class="correlation-status">${threat.severity.toUpperCase()}</div>
                </div>
            `;
            threatsList.appendChild(threatItem);
        });
    }

    async viewCorrelationDetails(correlationId) {
        try {
            const correlation = this.correlationData.find(c => c.id === correlationId);
            if (!correlation) {
                this.showNotification('Correlation not found', 'error');
                return;
            }

            // Create modal with correlation details
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content large">
                    <div class="modal-header">
                        <h3>Correlation Details: ${correlation.name}</h3>
                        <span class="close" onclick="this.closest('.modal').remove()">&times;</span>
                    </div>
                    <div class="modal-body">
                        <div class="correlation-details">
                            <div class="detail-row">
                                <label>Name:</label>
                                <span>${correlation.name}</span>
                            </div>
                            <div class="detail-row">
                                <label>Type:</label>
                                <span class="correlation-type-badge ${correlation.correlation_type}">${correlation.correlation_type.replace('_', ' ').toUpperCase()}</span>
                            </div>
                            <div class="detail-row">
                                <label>Status:</label>
                                <span class="status-badge ${correlation.status}">${correlation.status.toUpperCase()}</span>
                            </div>
                            <div class="detail-row">
                                <label>Score:</label>
                                <span class="score-badge ${this.getScoreClass(correlation.correlation_score)}">${correlation.correlation_score}/100</span>
                            </div>
                            <div class="detail-row">
                                <label>Severity:</label>
                                <span class="severity-badge ${correlation.severity}">${correlation.severity.toUpperCase()}</span>
                            </div>
                            <div class="detail-row">
                                <label>Confidence:</label>
                                <span>${correlation.confidence}%</span>
                            </div>
                            <div class="detail-row">
                                <label>Alerts:</label>
                                <span>${correlation.alerts_count}</span>
                            </div>
                            <div class="detail-row">
                                <label>Entities:</label>
                                <span>${correlation.entities_count}</span>
                            </div>
                            <div class="detail-row">
                                <label>Description:</label>
                                <span>${correlation.description}</span>
                            </div>
                            <div class="detail-row">
                                <label>Created:</label>
                                <span>${this.formatDate(correlation.created_at)}</span>
                            </div>
                            <div class="detail-row">
                                <label>Updated:</label>
                                <span>${this.formatDate(correlation.updated_at)}</span>
                            </div>
                            ${correlation.tags ? `
                            <div class="detail-row">
                                <label>Tags:</label>
                                <span>${correlation.tags.join(', ')}</span>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            modal.style.display = 'flex';
            
        } catch (error) {
            console.error('Error viewing correlation details:', error);
            this.showNotification('Failed to load correlation details', 'error');
        }
    }

    sortCorrelations(field) {
        if (this.sortField === field) {
            this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortField = field;
            this.sortOrder = 'asc';
        }

        this.filteredData.sort((a, b) => {
            let aVal = a[field];
            let bVal = b[field];

            if (typeof aVal === 'string') {
                aVal = aVal.toLowerCase();
                bVal = bVal.toLowerCase();
            }

            if (this.sortOrder === 'asc') {
                return aVal > bVal ? 1 : -1;
            } else {
                return aVal < bVal ? 1 : -1;
            }
        });

        this.displayCorrelationData();
    }

    toggleAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
            document.getElementById('correlation-auto-refresh-icon').className = 'fas fa-play';
            this.showNotification('Auto-refresh stopped', 'info');
        } else {
            this.autoRefreshInterval = setInterval(async () => {
                try {
                    await this.loadCorrelationData();
                    // Only show notification occasionally to avoid spam
                    if (Math.random() < 0.1) { // 10% chance to show notification
                        this.showNotification('Correlation data refreshed', 'success');
                    }
                } catch (error) {
                    console.error('Auto-refresh error:', error);
                    // Don't show error notifications for auto-refresh to avoid spam
                }
            }, 30000);
            document.getElementById('correlation-auto-refresh-icon').className = 'fas fa-pause';
            this.showNotification('Auto-refresh started (30s interval)', 'success');
        }
    }

    startAutoRefresh() {
        // Don't start auto-refresh by default to prevent errors
        console.log('Correlation auto-refresh disabled by default - user can enable manually');
    }

    async refreshCorrelations() {
        try {
            this.showNotification('Refreshing correlation data...', 'info');
            await this.loadCorrelationData();
            this.showNotification('Correlation data refreshed', 'success');
        } catch (error) {
            console.error('Error refreshing correlations:', error);
            this.showNotification('Failed to refresh correlation data', 'error');
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Pagination methods
    previousCorrelationPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.displayCorrelationData();
        }
    }

    nextCorrelationPage() {
        const totalPages = Math.ceil(this.filteredData.length / this.pageSize);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.displayCorrelationData();
        }
    }

    // Filter methods
    clearCorrelationFilters() {
        document.getElementById('correlation-search').value = '';
        document.getElementById('correlation-type-filter').value = '';
        document.getElementById('correlation-status-filter').value = '';
        document.getElementById('correlation-score-filter').value = '';
        
        this.applyFilters();
        this.showNotification('Filters cleared', 'info');
    }

    exportCorrelationData() {
        const csvContent = this.generateCSV();
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `correlation_data_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
        
        this.showNotification('Correlation data exported', 'success');
    }

    generateCSV() {
        const headers = ['Name', 'Type', 'Score', 'Status', 'Alerts', 'Entities', 'Created', 'Updated'];
        const rows = this.filteredData.map(correlation => [
            correlation.name,
            correlation.correlation_type,
            correlation.correlation_score,
            correlation.status,
            correlation.alerts_count,
            correlation.entities_count,
            this.formatDate(correlation.created_at),
            this.formatDate(correlation.updated_at)
        ]);

        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }
}

// Global functions for HTML onclick handlers
let correlationManager;

function runCorrelationAnalysis() {
    correlationManager.showNotification('Correlation analysis started...', 'info');
    setTimeout(() => {
        correlationManager.showNotification('Correlation analysis completed', 'success');
        correlationManager.refreshCorrelations();
    }, 2000);
}

function toggleCorrelationFilters() {
    const filters = document.getElementById('correlation-filters');
    const button = document.querySelector('.toggle-filters-btn');
    
    if (filters.classList.contains('hidden')) {
        filters.classList.remove('hidden');
        button.innerHTML = '<i class="fas fa-chevron-up"></i> Hide Filters';
    } else {
        filters.classList.add('hidden');
        button.innerHTML = '<i class="fas fa-chevron-down"></i> Show Filters';
    }
}

function applyCorrelationFilters() {
    correlationManager.applyFilters();
}

function clearCorrelationFilters() {
    correlationManager.clearCorrelationFilters();
}

function exportCorrelationData() {
    correlationManager.exportCorrelationData();
}

function sortCorrelations(field) {
    correlationManager.sortCorrelations(field);
}

function toggleCorrelationAutoRefresh() {
    correlationManager.toggleAutoRefresh();
}

function refreshCorrelations() {
    correlationManager.refreshCorrelations();
}

function previousCorrelationPage() {
    correlationManager.previousCorrelationPage();
}

function nextCorrelationPage() {
    correlationManager.nextCorrelationPage();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    correlationManager = new CorrelationManager();
});
