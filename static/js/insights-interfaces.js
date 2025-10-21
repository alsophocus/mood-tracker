/**
 * SOLID-compliant interfaces for insights dashboard
 * Interface Segregation Principle - specific interfaces for different concerns
 */

// Data loading interface
class InsightsDataLoaderInterface {
    async loadDashboardData() { throw new Error('Must implement loadDashboardData'); }
    async loadInsights() { throw new Error('Must implement loadInsights'); }
    async loadTrends(period) { throw new Error('Must implement loadTrends'); }
    async loadCorrelations() { throw new Error('Must implement loadCorrelations'); }
}

// UI rendering interface
class InsightsRendererInterface {
    renderInsights(insights) { throw new Error('Must implement renderInsights'); }
    renderTrends(trends) { throw new Error('Must implement renderTrends'); }
    renderCorrelations(correlations) { throw new Error('Must implement renderCorrelations'); }
    showLoading() { throw new Error('Must implement showLoading'); }
    hideLoading() { throw new Error('Must implement hideLoading'); }
}

// Theme management interface
class InsightsThemeManagerInterface {
    toggleTheme() { throw new Error('Must implement toggleTheme'); }
    initializeTheme() { throw new Error('Must implement initializeTheme'); }
}
