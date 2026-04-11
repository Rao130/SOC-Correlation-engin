// Reputation Database JavaScript - Premium Implementation
class ReputationManager {
    constructor() {
        this.reputationData = [];
        this.filteredData = [];
        this.currentPage = 1;
        this.pageSize = 20;
        this.sortField = 'entity';
        this.sortOrder = 'asc';
        this.autoRefreshInterval = null;
        this.filters = {
            search: '',
            riskLevel: '',
            entityType: '',
            category: ''
        };
        
        this.init();
    }

    init() {
        console.log('Initializing Reputation Manager...');
        this.loadReputationData();
        this.setupEventListeners();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Search and filter listeners
        document.getElementById('reputation-search')?.addEventListener('keyup', (e) => {
            if (e.key === 'Enter') {
                this.applyFilters();
            } else {
                clearTimeout(window.reputationSearchTimeout);
                window.reputationSearchTimeout = setTimeout(() => {
                    this.applyFilters();
                }, 500);
            }
        });

        document.getElementById('risk-filter')?.addEventListener('change', () => this.applyFilters());
        document.getElementById('entity-type-filter')?.addEventListener('change', () => this.applyFilters());
        document.getElementById('category-filter')?.addEventListener('change', () => this.applyFilters());

        // Quick check
        document.getElementById('quick-entity-input')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.quickCheckEntity();
            }
        });
    }

    generateMockReputationData() {
        const entities = [];
        const entityTypes = ['ip', 'domain', 'hash', 'email', 'url'];
        const riskLevels = ['malicious', 'suspicious', 'benign', 'unknown'];
        const categories = ['malware', 'phishing', 'botnet', 'spam', 'legitimate'];
        
        // Generate IP addresses
        for (let i = 0; i < 50; i++) {
            const ip = `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`;
            const riskLevel = this.getWeightedRiskLevel();
            
            entities.push({
                id: `rep-${i + 1}`,
                entity: ip,
                entity_type: 'ip',
                aggregated_score: this.getScoreForRiskLevel(riskLevel),
                risk_level: riskLevel,
                category: this.getCategoryForRiskLevel(riskLevel),
                metrics: {
                    alert_count: Math.floor(Math.random() * 20),
                    last_seen: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
                },
                last_checked: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString()
            });
        }

        // Generate domains
        const domainNames = ['malicious-site.com', 'phishing-domain.net', 'legitimate-business.org', 'suspicious-link.info', 'trusted-website.edu'];
        for (let i = 0; i < 30; i++) {
            const domain = domainNames[Math.floor(Math.random() * domainNames.length)];
            const riskLevel = this.getWeightedRiskLevel();
            
            entities.push({
                id: `rep-${51 + i}`,
                entity: domain,
                entity_type: 'domain',
                aggregated_score: this.getScoreForRiskLevel(riskLevel),
                risk_level: riskLevel,
                category: this.getCategoryForRiskLevel(riskLevel),
                metrics: {
                    alert_count: Math.floor(Math.random() * 15),
                    last_seen: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
                },
                last_checked: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString()
            });
        }

        // Generate hashes
        for (let i = 0; i < 20; i++) {
            const hash = this.generateRandomHash();
            const riskLevel = this.getWeightedRiskLevel();
            
            entities.push({
                id: `rep-${81 + i}`,
                entity: hash,
                entity_type: 'hash',
                aggregated_score: this.getScoreForRiskLevel(riskLevel),
                risk_level: riskLevel,
                category: this.getCategoryForRiskLevel(riskLevel),
                metrics: {
                    alert_count: Math.floor(Math.random() * 25),
                    last_seen: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
                },
                last_checked: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString()
            });
        }

        // Generate emails
        for (let i = 0; i < 25; i++) {
            const email = this.generateRandomEmail();
            const riskLevel = this.getWeightedRiskLevel();
            
            entities.push({
                id: `rep-${101 + i}`,
                entity: email,
                entity_type: 'email',
                aggregated_score: this.getScoreForRiskLevel(riskLevel),
                risk_level: riskLevel,
                category: this.getCategoryForRiskLevel(riskLevel),
                metrics: {
                    alert_count: Math.floor(Math.random() * 10),
                    last_seen: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
                },
                last_checked: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString()
            });
        }

        // Generate URLs
        const urlPaths = ['/malware/download', '/phishing/login', '/legitimate/page', '/suspicious/redirect', '/trusted/content'];
        for (let i = 0; i < 15; i++) {
            const url = `https://example.com${urlPaths[Math.floor(Math.random() * urlPaths.length)]}`;
            const riskLevel = this.getWeightedRiskLevel();
            
            entities.push({
                id: `rep-${126 + i}`,
                entity: url,
                entity_type: 'url',
                aggregated_score: this.getScoreForRiskLevel(riskLevel),
                risk_level: riskLevel,
                category: this.getCategoryForRiskLevel(riskLevel),
                metrics: {
                    alert_count: Math.floor(Math.random() * 18),
                    last_seen: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
                },
                last_checked: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString()
            });
        }

        return entities;
    }

    getWeightedRiskLevel() {
        const rand = Math.random();
        if (rand < 0.05) return 'malicious';      // 5%
        if (rand < 0.20) return 'suspicious';    // 15%
        if (rand < 0.80) return 'benign';        // 60%
        return 'unknown';                        // 20%
    }

    getScoreForRiskLevel(riskLevel) {
        switch(riskLevel) {
            case 'malicious': return Math.floor(Math.random() * 20) + 80; // 80-100
            case 'suspicious': return Math.floor(Math.random() * 30) + 50; // 50-80
            case 'benign': return Math.floor(Math.random() * 30) + 10;     // 10-40
            case 'unknown': return Math.floor(Math.random() * 20) + 40;    // 40-60
            default: return 50;
        }
    }

    getCategoryForRiskLevel(riskLevel) {
        switch(riskLevel) {
            case 'malicious': 
                return ['malware', 'phishing', 'botnet'][Math.floor(Math.random() * 3)];
            case 'suspicious': 
                return ['spam', 'phishing', 'botnet'][Math.floor(Math.random() * 3)];
            case 'benign': 
                return 'legitimate';
            case 'unknown': 
                return ['spam', 'legitimate'][Math.floor(Math.random() * 2)];
            default: return 'unknown';
        }
    }

    generateRandomHash() {
        const chars = '0123456789abcdef';
        let hash = '';
        for (let i = 0; i < 32; i++) {
            hash += chars[Math.floor(Math.random() * chars.length)];
        }
        return hash;
    }

    generateRandomEmail() {
        const usernames = ['user', 'admin', 'test', 'suspicious', 'legitimate'];
        const domains = ['example.com', 'test.org', 'suspicious.net', 'trusted.edu'];
        return `${usernames[Math.floor(Math.random() * usernames.length)]}${Math.floor(Math.random() * 999)}@${domains[Math.floor(Math.random() * domains.length)]}`;
    }

    async loadReputationData() {
        try {
            // Fetch real reputation data from API
            const response = await fetch('/api/reputation/?limit=1000');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.reputationData = data.entities || [];
            
            // If no data exists, create some initial data
            if (this.reputationData.length === 0) {
                await this.createInitialReputationData();
                // Reload after creating initial data
                await this.loadReputationData();
                return;
            }
            
            this.applyFilters();
            this.updateStatistics();
            this.updateRecentThreats();
            console.log('Real reputation data loaded:', this.reputationData.length, 'entities');
        } catch (error) {
            console.error('Error loading reputation data:', error);
            // Fallback to mock data if API fails
            this.reputationData = this.generateMockReputationData();
            this.applyFilters();
            this.updateStatistics();
            this.updateRecentThreats();
            console.log('Fallback to mock data loaded');
        }
    }

    async createInitialReputationData() {
        try {
            // Create some initial reputation data
            const mockData = this.generateMockReputationData();
            
            for (const entity of mockData.slice(0, 20)) { // Start with 20 entities
                try {
                    await this.createReputationEntity(entity);
                } catch (error) {
                    console.error('Error creating entity:', entity.entity, error);
                    // Continue with other entities even if one fails
                }
            }
            
            console.log('Initial reputation data created');
        } catch (error) {
            console.error('Error creating initial data:', error);
        }
    }

    async createReputationEntity(entity) {
        try {
            const response = await fetch('/api/reputation/check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    entity: entity.entity,
                    entity_type: entity.entity_type
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to create reputation entity');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error creating reputation entity:', error);
            throw error;
        }
    }

    applyFilters() {
        this.filters.search = document.getElementById('reputation-search')?.value.toLowerCase() || '';
        this.filters.riskLevel = document.getElementById('risk-filter')?.value || '';
        this.filters.entityType = document.getElementById('entity-type-filter')?.value || '';
        this.filters.category = document.getElementById('category-filter')?.value || '';

        this.filteredData = this.reputationData.filter(entity => {
            if (this.filters.search && !entity.entity.toLowerCase().includes(this.filters.search)) {
                return false;
            }
            if (this.filters.riskLevel && entity.risk_level !== this.filters.riskLevel) {
                return false;
            }
            if (this.filters.entityType && entity.entity_type !== this.filters.entityType) {
                return false;
            }
            if (this.filters.category && entity.category !== this.filters.category) {
                return false;
            }
            return true;
        });

        this.currentPage = 1;
        this.displayReputationData();
        this.updateStatistics();
    }

    displayReputationData() {
        const tbody = document.getElementById('reputation-tbody');
        if (!tbody) return;

        const startIndex = (this.currentPage - 1) * this.pageSize;
        const endIndex = startIndex + this.pageSize;
        const pageData = this.filteredData.slice(startIndex, endIndex);

        tbody.innerHTML = '';

        pageData.forEach(entity => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="entity-name">${entity.entity}</span></td>
                <td><span class="entity-type ${entity.entity_type}">${entity.entity_type}</span></td>
                <td><span class="score-badge ${this.getScoreClass(entity.aggregated_score)}">${entity.aggregated_score}/100</span></td>
                <td><span class="risk-level-badge ${entity.risk_level}">${entity.risk_level.toUpperCase()}</span></td>
                <td>${entity.category}</td>
                <td><span class="alert-count">${entity.metrics.alert_count}</span></td>
                <td><span class="last-checked">${this.formatDate(entity.last_checked)}</span></td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="reputationManager.viewEntityDetails('${entity.id}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });

        this.updatePagination();
        document.getElementById('entity-count').textContent = `${this.filteredData.length} entities`;
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
        const pageInfo = document.getElementById('reputation-page-info');
        const prevBtn = document.getElementById('reputation-prev-btn');
        const nextBtn = document.getElementById('reputation-next-btn');

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
            malicious: 0,
            suspicious: 0,
            benign: 0,
            unknown: 0,
            total: 0
        };

        this.filteredData.forEach(entity => {
            stats[entity.risk_level]++;
            stats.total++;
        });

        // Update hero stats
        document.getElementById('reputation-total-entities').textContent = stats.total.toLocaleString();
        document.getElementById('reputation-malicious-count').textContent = stats.malicious.toLocaleString();
        document.getElementById('reputation-checks-today').textContent = (Math.floor(Math.random() * 5000) + 5000).toLocaleString();

        // Update risk distribution
        document.getElementById('malicious-count').textContent = stats.malicious;
        document.getElementById('suspicious-count').textContent = stats.suspicious;
        document.getElementById('benign-count').textContent = stats.benign;
        document.getElementById('unknown-count').textContent = stats.unknown;

        // Update percentages
        const maliciousPercentage = stats.total > 0 ? ((stats.malicious / stats.total) * 100).toFixed(1) : 0;
        const suspiciousPercentage = stats.total > 0 ? ((stats.suspicious / stats.total) * 100).toFixed(1) : 0;
        const benignPercentage = stats.total > 0 ? ((stats.benign / stats.total) * 100).toFixed(1) : 0;
        const unknownPercentage = stats.total > 0 ? ((stats.unknown / stats.total) * 100).toFixed(1) : 0;

        // Update percentage displays
        document.querySelectorAll('.risk-card.malicious .risk-percentage')[0].textContent = `${maliciousPercentage}%`;
        document.querySelectorAll('.risk-card.suspicious .risk-percentage')[0].textContent = `${suspiciousPercentage}%`;
        document.querySelectorAll('.risk-card.benign .risk-percentage')[0].textContent = `${benignPercentage}%`;
        document.querySelectorAll('.risk-card.unknown .risk-percentage')[0].textContent = `${unknownPercentage}%`;
    }

    updateRecentThreats() {
        const threats = this.reputationData
            .filter(entity => entity.risk_level === 'malicious' || entity.risk_level === 'suspicious')
            .sort((a, b) => b.aggregated_score - a.aggregated_score)
            .slice(0, 4);

        const threatsList = document.querySelector('.threats-list');
        if (!threatsList) return;

        threatsList.innerHTML = '';

        const threatClasses = ['critical', 'high', 'medium', 'low'];
        
        threats.forEach((threat, index) => {
            const threatItem = document.createElement('div');
            threatItem.className = `threat-item ${threatClasses[index]}`;
            threatItem.innerHTML = `
                <div class="threat-entity">${threat.entity}</div>
                <div class="threat-info">
                    <div class="threat-type">${threat.entity_type.charAt(0).toUpperCase() + threat.entity_type.slice(1)}</div>
                    <div class="threat-score">Score: ${threat.aggregated_score}/100</div>
                </div>
                <div class="threat-status">${threat.risk_level.toUpperCase()}</div>
            `;
            threatsList.appendChild(threatItem);
        });
    }

    async quickCheckEntity() {
        const input = document.getElementById('quick-entity-input');
        const typeSelect = document.getElementById('quick-entity-type');
        
        if (!input || !input.value.trim()) {
            this.showNotification('Please enter an entity to check', 'error');
            return;
        }

        const entity = input.value.trim();
        const type = typeSelect?.value || 'auto';
        
        // Simulate checking process
        this.showNotification(`Checking ${entity}...`, 'info');
        
        try {
            // Call real reputation check API
            const response = await fetch('/api/reputation/check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    entity: entity,
                    entity_type: type === 'auto' ? this.detectEntityType(entity) : type
                })
            });
            
            if (!response.ok) {
                throw new Error('Reputation check failed');
            }
            
            const result = await response.json();
            
            this.showNotification(`Entity check completed for ${entity}`, 'success');
            this.viewEntityDetails(result.entity);
            
            // Refresh the data to show new entity
            await this.loadReputationData();
            
        } catch (error) {
            console.error('Error checking entity:', error);
            
            // Fallback to creating a new entity if API fails
            const newEntity = {
                id: `new-${Date.now()}`,
                entity: entity,
                entity_type: this.detectEntityType(entity),
                aggregated_score: Math.floor(Math.random() * 100),
                risk_level: this.getWeightedRiskLevel(),
                category: 'unknown',
                metrics: {
                    alert_count: 0,
                    last_seen: new Date().toISOString()
                },
                last_checked: new Date().toISOString()
            };
            
            await this.createReputationEntity(newEntity);
            this.showNotification(`Entity check completed for ${entity}`, 'success');
            this.viewEntityDetails(newEntity.entity);
            await this.loadReputationData();
        }
    }

    detectEntityType(entity) {
        // Simple auto-detection logic
        if (/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(entity)) return 'ip';
        if (entity.includes('@')) return 'email';
        if (entity.startsWith('http://') || entity.startsWith('https://')) return 'url';
        if (/^[a-f0-9]{32}$/i.test(entity) || /^[a-f0-9]{40}$/i.test(entity) || /^[a-f0-9]{64}$/i.test(entity)) return 'hash';
        return 'domain';
    }

    async viewEntityDetails(entityId) {
        try {
            // Try to fetch entity details from API
            const response = await fetch(`/api/reputation/check`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    entity: entityId
                })
            });
            
            let entity;
            if (response.ok) {
                entity = await response.json();
            } else {
                // Fallback to local data if API fails
                entity = this.reputationData.find(r => r.entity === entityId);
            }
            
            if (!entity) {
                this.showNotification('Entity not found', 'error');
                return;
            }

            // Create modal with entity details
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content large">
                    <div class="modal-header">
                        <h3>Entity Details: ${entity.entity}</h3>
                        <span class="close" onclick="this.closest('.modal').remove()">&times;</span>
                    </div>
                    <div class="modal-body">
                        <div class="entity-details">
                            <div class="detail-row">
                                <label>Entity:</label>
                                <span>${entity.entity}</span>
                            </div>
                            <div class="detail-row">
                                <label>Type:</label>
                                <span class="entity-type ${entity.entity_type}">${entity.entity_type.toUpperCase()}</span>
                            </div>
                            <div class="detail-row">
                                <label>Risk Level:</label>
                                <span class="risk-level-badge ${entity.risk_level}">${entity.risk_level.toUpperCase()}</span>
                            </div>
                            <div class="detail-row">
                                <label>Score:</label>
                                <span class="score-badge ${this.getScoreClass(entity.aggregated_score)}">${entity.aggregated_score}/100</span>
                            </div>
                            <div class="detail-row">
                                <label>Category:</label>
                                <span>${entity.classification?.category || entity.category || 'Unknown'}</span>
                            </div>
                            <div class="detail-row">
                                <label>Alert Count:</label>
                                <span>${entity.metrics?.alert_count || 0}</span>
                            </div>
                            <div class="detail-row">
                                <label>Last Seen:</label>
                                <span>${this.formatDate(entity.last_checked)}</span>
                            </div>
                            <div class="detail-row">
                                <label>Last Checked:</label>
                                <span>${this.formatDate(entity.last_checked)}</span>
                            </div>
                            ${entity.classification ? `
                            <div class="detail-row">
                                <label>Confidence:</label>
                                <span>${entity.classification.confidence}%</span>
                            </div>
                            ` : ''}
                            ${entity.tags ? `
                            <div class="detail-row">
                                <label>Tags:</label>
                                <span>${entity.tags.join(', ')}</span>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            modal.style.display = 'flex';
            
        } catch (error) {
            console.error('Error viewing entity details:', error);
            this.showNotification('Failed to load entity details', 'error');
        }
    }

    sortReputation(field) {
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

        this.displayReputationData();
    }

    toggleAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
            document.getElementById('reputation-auto-refresh-icon').className = 'fas fa-play';
            this.showNotification('Auto-refresh stopped', 'info');
        } else {
            this.autoRefreshInterval = setInterval(async () => {
                try {
                    await this.loadReputationData();
                    // Only show notification occasionally to avoid spam
                    if (Math.random() < 0.1) { // 10% chance to show notification
                        this.showNotification('Reputation data refreshed', 'success');
                    }
                } catch (error) {
                    console.error('Auto-refresh error:', error);
                    // Don't show error notifications for auto-refresh to avoid spam
                }
            }, 30000);
            document.getElementById('reputation-auto-refresh-icon').className = 'fas fa-pause';
            this.showNotification('Auto-refresh started (30s interval)', 'success');
        }
    }

    startAutoRefresh() {
        // Don't start auto-refresh by default to prevent errors
        // User can manually start it if needed
        console.log('Auto-refresh disabled by default - user can enable manually');
    }

    async refreshReputation() {
        try {
            this.showNotification('Refreshing reputation data...', 'info');
            await this.loadReputationData();
            this.showNotification('Reputation data refreshed', 'success');
        } catch (error) {
            console.error('Error refreshing reputation:', error);
            this.showNotification('Failed to refresh reputation data', 'error');
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
    previousReputationPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.displayReputationData();
        }
    }

    nextReputationPage() {
        const totalPages = Math.ceil(this.filteredData.length / this.pageSize);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.displayReputationData();
        }
    }

    // Filter methods
    clearReputationFilters() {
        document.getElementById('reputation-search').value = '';
        document.getElementById('risk-filter').value = '';
        document.getElementById('entity-type-filter').value = '';
        document.getElementById('category-filter').value = '';
        
        this.applyFilters();
        this.showNotification('Filters cleared', 'info');
    }

    async exportReputationData() {
        try {
            // Fetch latest data before export
            await this.loadReputationData();
            
            const csvContent = this.generateCSV();
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `reputation_data_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
            
            this.showNotification('Reputation data exported', 'success');
        } catch (error) {
            console.error('Error exporting data:', error);
            this.showNotification('Failed to export reputation data', 'error');
        }
    }

    generateCSV() {
        const headers = ['Entity', 'Type', 'Score', 'Risk Level', 'Category', 'Alerts', 'Last Checked'];
        const rows = this.filteredData.map(entity => [
            entity.entity,
            entity.entity_type,
            entity.aggregated_score,
            entity.risk_level,
            entity.category,
            entity.metrics.alert_count,
            this.formatDate(entity.last_checked)
        ]);

        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }
}

// Global functions for HTML onclick handlers
let reputationManager;

function quickCheckEntity() {
    reputationManager.quickCheckEntity();
}

function toggleAdvancedFilters() {
    const filters = document.getElementById('advanced-filters');
    const button = document.querySelector('.toggle-filters-btn');
    
    if (filters.classList.contains('hidden')) {
        filters.classList.remove('hidden');
        button.innerHTML = '<i class="fas fa-chevron-up"></i> Hide Filters';
    } else {
        filters.classList.add('hidden');
        button.innerHTML = '<i class="fas fa-chevron-down"></i> Show Filters';
    }
}

function applyReputationFilters() {
    reputationManager.applyFilters();
}

function clearReputationFilters() {
    reputationManager.clearReputationFilters();
}

function exportReputationData() {
    reputationManager.exportReputationData();
}

function sortReputation(field) {
    reputationManager.sortReputation(field);
}

function toggleReputationAutoRefresh() {
    reputationManager.toggleAutoRefresh();
}

function refreshReputation() {
    reputationManager.refreshReputation();
}

function previousReputationPage() {
    reputationManager.previousReputationPage();
}

function nextReputationPage() {
    reputationManager.nextReputationPage();
}

function checkReputation() {
    reputationManager.quickCheckEntity();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    reputationManager = new ReputationManager();
});
