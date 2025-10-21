/**
 * Weekly chart service following SOLID principles
 * Dependency Inversion Principle - Depends on abstractions, not concrete implementations
 */
class WeeklyChartService {
    
    /**
     * Constructor with dependency injection
     * 
     * @param {DataLoaderInterface} dataLoader - Data loading service
     * @param {DataProcessorInterface} dataProcessor - Data processing service
     * @param {ChartRendererInterface} chartRenderer - Chart rendering service
     * @param {ChartConfigInterface} chartConfig - Chart configuration service
     */
    constructor(dataLoader, dataProcessor, chartRenderer, chartConfig) {
        this.dataLoader = dataLoader;
        this.dataProcessor = dataProcessor;
        this.chartRenderer = chartRenderer;
        this.chartConfig = chartConfig;
        this.chart = null;
        this.chartElement = null;
    }
    
    /**
     * Initialize chart with element
     * 
     * @param {string|HTMLElement} elementId - Chart canvas element or ID
     */
    initialize(elementId) {
        this.chartElement = typeof elementId === 'string' 
            ? document.getElementById(elementId)
            : elementId;
            
        if (!this.chartElement) {
            throw new Error(`Chart element not found: ${elementId}`);
        }
        
        // Create initial empty chart
        this._createChart({
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            data: [null, null, null, null, null, null, null],
            period: 'Loading...'
        });
    }
    
    /**
     * Load and display weekly patterns
     * 
     * @param {Object} params - Request parameters
     * @returns {Promise<void>}
     */
    async loadWeeklyPatterns(params = {}) {
        try {
            // Validate parameters if provided
            if (Object.keys(params).length > 0 && !this.dataLoader.validateParams(params)) {
                throw new Error('Invalid parameters provided');
            }
            
            // Load data
            const rawData = await this.dataLoader.loadData(params);
            
            // Process data
            const processedData = this.dataProcessor.processData(rawData);
            
            // Validate processed data
            if (!this.dataProcessor.validateData(processedData)) {
                throw new Error('Invalid data received from processor');
            }
            
            // Update chart
            this._updateChart(processedData);
            
        } catch (error) {
            console.error('Failed to load weekly patterns:', error);
            this._handleError(error);
        }
    }
    
    /**
     * Load current week patterns
     * 
     * @returns {Promise<void>}
     */
    async loadCurrentWeek() {
        return this.loadWeeklyPatterns(); // No parameters = current week
    }
    
    /**
     * Destroy chart and cleanup
     */
    destroy() {
        if (this.chart) {
            this.chartRenderer.destroy(this.chart);
            this.chart = null;
        }
        this.chartElement = null;
    }
    
    /**
     * Check if service is properly initialized
     * 
     * @returns {boolean} Is initialized
     */
    isInitialized() {
        return this.chartElement !== null;
    }
    
    /**
     * Create new chart
     * @private
     */
    _createChart(data) {
        try {
            // Destroy existing chart
            if (this.chart) {
                this.chartRenderer.destroy(this.chart);
            }
            
            // Get chart configuration
            const config = this.chartConfig.getConfiguration(data);
            
            // Render new chart
            this.chart = this.chartRenderer.render(this.chartElement, config);
            
        } catch (error) {
            console.error('Failed to create chart:', error);
            throw error;
        }
    }
    
    /**
     * Update existing chart
     * @private
     */
    _updateChart(data) {
        try {
            if (!this.chart || !this.chartRenderer.isValid(this.chart)) {
                // Recreate chart if invalid
                this._createChart(data);
                return;
            }
            
            // Update existing chart
            this.chartRenderer.update(this.chart, data, {
                animation: 'none',
                forceRender: true
            });
            
        } catch (error) {
            console.error('Chart update failed, recreating:', error);
            this._createChart(data);
        }
    }
    
    /**
     * Handle errors by showing error state
     * @private
     */
    _handleError(error) {
        const errorData = {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            data: [null, null, null, null, null, null, null],
            period: `Error: ${error.message}`
        };
        
        try {
            this._updateChart(errorData);
        } catch (updateError) {
            console.error('Failed to show error state:', updateError);
        }
    }
}
