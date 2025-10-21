/**
 * Chart factory following Open/Closed Principle
 * Open for extension (new chart types), closed for modification
 */
class ChartFactory {
    
    /**
     * Create weekly chart service with all dependencies
     * 
     * @param {Object} options - Configuration options
     * @returns {WeeklyChartService} Configured chart service
     */
    static createWeeklyChartService(options = {}) {
        // Create dependencies following Dependency Inversion Principle
        const dataLoader = new WeeklyDataLoader(options.baseUrl);
        const dataProcessor = new WeeklyDataProcessor();
        const chartRenderer = new ChartRenderer();
        const chartConfig = new WeeklyChartConfig();
        
        // Inject dependencies into service
        return new WeeklyChartService(
            dataLoader,
            dataProcessor, 
            chartRenderer,
            chartConfig
        );
    }
    
    /**
     * Create weekly trends chart service (extensible for future)
     * 
     * @param {Object} options - Configuration options
     * @returns {Object} Chart service (placeholder for future implementation)
     */
    static createWeeklyTrendsService(options = {}) {
        // Future implementation for weekly trends
        // Following Open/Closed Principle - can add new chart types without modifying existing code
        throw new Error('Weekly trends service not yet implemented');
    }
    
    /**
     * Create monthly chart service (extensible for future)
     * 
     * @param {Object} options - Configuration options
     * @returns {Object} Chart service (placeholder for future implementation)
     */
    static createMonthlyChartService(options = {}) {
        // Future implementation for monthly charts
        // Following Open/Closed Principle
        throw new Error('Monthly chart service not yet implemented');
    }
    
    /**
     * Register custom chart type (Open/Closed Principle)
     * 
     * @param {string} type - Chart type name
     * @param {Function} factory - Factory function for chart type
     */
    static registerChartType(type, factory) {
        if (!ChartFactory._customTypes) {
            ChartFactory._customTypes = new Map();
        }
        
        ChartFactory._customTypes.set(type, factory);
    }
    
    /**
     * Create custom chart type
     * 
     * @param {string} type - Chart type name
     * @param {Object} options - Configuration options
     * @returns {Object} Chart service
     */
    static createCustomChart(type, options = {}) {
        if (!ChartFactory._customTypes || !ChartFactory._customTypes.has(type)) {
            throw new Error(`Unknown chart type: ${type}`);
        }
        
        const factory = ChartFactory._customTypes.get(type);
        return factory(options);
    }
    
    /**
     * Get available chart types
     * 
     * @returns {Array<string>} Available chart types
     */
    static getAvailableTypes() {
        const builtInTypes = ['weekly', 'weeklyTrends', 'monthly'];
        const customTypes = ChartFactory._customTypes 
            ? Array.from(ChartFactory._customTypes.keys())
            : [];
            
        return [...builtInTypes, ...customTypes];
    }
}
