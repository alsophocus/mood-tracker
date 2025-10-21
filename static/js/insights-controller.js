/**
 * SOLID-compliant main controller for insights dashboard
 * Dependency Inversion Principle - depends on abstractions, not concretions
 * Open/Closed Principle - can be extended without modification
 */

class InsightsDashboardController {
    constructor(dataLoader, renderer, themeManager) {
        // Dependency Inversion - inject dependencies
        this.dataLoader = dataLoader;
        this.renderer = renderer;
        this.themeManager = themeManager;
    }

    // Single Responsibility - only coordinates between services
    async initialize() {
        this.themeManager.initializeTheme();
        this._bindEvents();
        await this.loadDashboard();
    }

    async loadDashboard() {
        try {
            this.renderer.showLoading();
            
            const data = await this.dataLoader.loadDashboardData();
            
            if (data.success) {
                this.renderer.renderTrends(data.trends);
                this.renderer.renderInsights(data.insights);
                this.renderer.renderCorrelations(data.correlations);
            } else {
                this._showError('Failed to load dashboard data: ' + data.error);
            }
            
            this.renderer.hideLoading();
        } catch (error) {
            console.error('Dashboard loading error:', error);
            this._showError('Error loading dashboard');
            this.renderer.hideLoading();
        }
    }

    async refreshInsights() {
        try {
            const data = await this.dataLoader.loadInsights();
            if (data.success) {
                this.renderer.renderInsights(data.insights);
            }
        } catch (error) {
            console.error('Insights refresh error:', error);
        }
    }

    async changeTrendsPeriod(period) {
        try {
            const data = await this.dataLoader.loadTrends(period);
            if (data.success) {
                this.renderer.renderTrends(data.trends);
            }
        } catch (error) {
            console.error('Trends loading error:', error);
        }
    }

    toggleTheme() {
        this.themeManager.toggleTheme();
    }

    // Private methods - implementation details
    _bindEvents() {
        // Global functions for onclick handlers
        window.toggleTheme = () => this.toggleTheme();
        window.refreshInsights = () => this.refreshInsights();
        window.changeTrendsPeriod = (period) => this.changeTrendsPeriod(period);
    }

    _showError(message) {
        // Simple error display - could be enhanced with a notification service
        const container = document.getElementById('insightsGrid');
        container.innerHTML = `
            <div class="insight-card error" style="grid-column: 1 / -1;">
                <div class="insight-header">
                    <div class="insight-icon">
                        <span class="material-icons">error</span>
                    </div>
                    <div class="insight-title">Error</div>
                </div>
                <div class="insight-message">${message}</div>
            </div>
        `;
    }
}

// Factory pattern for creating controller with dependencies
class InsightsDashboardFactory {
    static create() {
        // Dependency Injection - create all dependencies
        const dataLoader = new InsightsDataLoader();
        const renderer = new InsightsRenderer();
        const themeManager = new InsightsThemeManager();

        // Return controller with injected dependencies
        return new InsightsDashboardController(
            dataLoader,
            renderer,
            themeManager
        );
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    const controller = InsightsDashboardFactory.create();
    controller.initialize();
});
