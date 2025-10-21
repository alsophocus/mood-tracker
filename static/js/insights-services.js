/**
 * SOLID-compliant service implementations for insights dashboard
 * Single Responsibility Principle - each class handles one specific concern
 */

// Data loading service - Single Responsibility
class InsightsDataLoader extends InsightsDataLoaderInterface {
    async loadDashboardData() {
        const response = await fetch('/insights/api/dashboard-data');
        return await response.json();
    }

    async loadInsights() {
        const response = await fetch('/insights/api/insights');
        return await response.json();
    }

    async loadTrends(period = 'month') {
        const response = await fetch(`/insights/api/trends/${period}`);
        return await response.json();
    }

    async loadCorrelations() {
        const response = await fetch('/insights/api/correlations');
        return await response.json();
    }
}

// UI rendering service - Single Responsibility
class InsightsRenderer extends InsightsRendererInterface {
    renderInsights(insights) {
        const container = document.getElementById('insightsGrid');
        container.innerHTML = '';

        if (!insights || insights.length === 0) {
            container.innerHTML = '<p style="grid-column: 1 / -1; text-align: center; color: var(--md-sys-color-on-surface-variant);">No insights available yet. Keep tracking your mood!</p>';
            return;
        }

        insights.forEach((insight, index) => {
            const card = this._createInsightCard(insight, index);
            container.appendChild(card);
        });
    }

    renderTrends(trends) {
        const container = document.getElementById('trendsGrid');
        container.innerHTML = '';

        if (!trends || !trends.success) {
            container.innerHTML = '<p class="body-medium" style="grid-column: 1 / -1; text-align: center; color: var(--md-sys-color-on-surface-variant);">Unable to load trends. Please add some mood entries first.</p>';
            return;
        }

        const trendData = [
            { label: 'Average Mood', value: `${trends.average_mood || 0}/7`, icon: 'mood' },
            { label: 'Stability', value: `${trends.stability || 0}/10`, icon: 'timeline' },
            { label: 'Trend', value: trends.trend_direction || 'unknown', icon: 'trending_up' },
            { label: 'Entries', value: trends.total_entries || 0, icon: 'edit_note' }
        ];

        trendData.forEach(item => {
            const card = this._createTrendCard(item);
            container.appendChild(card);
        });
    }

    renderCorrelations(correlations) {
        const container = document.getElementById('correlationsList');
        container.innerHTML = '';

        if (!correlations || correlations.length === 0) {
            container.innerHTML = '<p class="body-medium" style="text-align: center; color: var(--md-sys-color-on-surface-variant);">No trigger correlations found yet. Try adding triggers to your mood entries!</p>';
            return;
        }

        correlations.slice(0, 10).forEach(correlation => {
            const item = this._createCorrelationItem(correlation);
            container.appendChild(item);
        });
    }

    showLoading() {
        document.getElementById('loadingState').style.display = 'block';
        document.getElementById('dashboardContent').style.display = 'none';
    }

    hideLoading() {
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('dashboardContent').style.display = 'block';
    }

    _createInsightCard(insight, index) {
        const card = document.createElement('div');
        card.className = `insight-card ${insight.type}`;
        card.style.animationDelay = `${index * 0.1}s`;

        const icon = this._getInsightIcon(insight.type);
        
        card.innerHTML = `
            <div class="insight-header">
                <div class="insight-icon">
                    <i class="fas ${icon}"></i>
                </div>
                <div class="insight-title title-medium">${insight.title}</div>
            </div>
            <div class="insight-message body-medium">${insight.message}</div>
        `;

        return card;
    }

    _createTrendCard(item) {
        const card = document.createElement('div');
        card.className = 'trend-card';
        
        card.innerHTML = `
            <div class="trend-value">${item.value}</div>
            <div class="trend-label">${item.label}</div>
        `;

        return card;
    }

    _createCorrelationItem(correlation) {
        const item = document.createElement('div');
        item.className = 'correlation-item';
        
        item.innerHTML = `
            <div class="correlation-tag">
                <i class="fas fa-tag"></i>
                <span class="body-medium">${correlation.tag} (${correlation.frequency}x)</span>
            </div>
            <div class="correlation-impact ${correlation.impact.toLowerCase()}">
                ${correlation.impact} (${correlation.average_mood}/7)
            </div>
        `;

        return item;
    }

    _getInsightIcon(type) {
        const iconMap = {
            positive: 'fa-thumbs-up',
            warning: 'fa-exclamation-triangle',
            suggestion: 'fa-lightbulb',
            pattern: 'fa-chart-line',
            error: 'fa-exclamation-circle'
        };
        return iconMap[type] || 'fa-info-circle';
    }
}

// Theme management service - Single Responsibility
class InsightsThemeManager extends InsightsThemeManagerInterface {
    toggleTheme() {
        // This is now handled by the global toggleTheme function in the HTML
        // to match the main page exactly
        if (window.toggleTheme) {
            window.toggleTheme();
        }
    }

    initializeTheme() {
        // This is now handled by the global initializeTheme function in the HTML
        // to match the main page exactly
        if (window.initializeTheme) {
            window.initializeTheme();
        }
    }
}
