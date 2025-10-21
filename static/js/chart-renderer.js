/**
 * Chart renderer following Single Responsibility Principle
 * Responsible only for Chart.js rendering operations
 */
class ChartRenderer extends ChartRendererInterface {
    
    /**
     * Render a new chart
     * 
     * @param {HTMLElement} chartElement - Canvas element
     * @param {Object} data - Chart data
     * @param {Object} options - Chart options
     * @returns {Chart} Chart.js instance
     */
    render(chartElement, data, options = {}) {
        if (!chartElement) {
            throw new Error('Chart element is required');
        }
        
        if (!window.Chart) {
            throw new Error('Chart.js library not loaded');
        }
        
        try {
            const ctx = chartElement.getContext('2d');
            return new Chart(ctx, data);
        } catch (error) {
            console.error('Failed to render chart:', error);
            throw error;
        }
    }
    
    /**
     * Update existing chart with new data
     * 
     * @param {Chart} chart - Chart.js instance
     * @param {Object} data - New chart data
     * @param {Object} options - Update options
     */
    update(chart, data, options = {}) {
        if (!chart) {
            throw new Error('Chart instance is required');
        }
        
        try {
            // Update chart data
            if (data.labels) {
                chart.data.labels = data.labels;
            }
            
            if (data.data && chart.data.datasets[0]) {
                chart.data.datasets[0].data = data.data;
            }
            
            if (data.period && chart.data.datasets[0]) {
                chart.data.datasets[0].label = data.period;
            }
            
            // Update chart with animation control
            const animationMode = options.animation !== undefined ? options.animation : 'none';
            chart.update(animationMode);
            
            // Force render if requested
            if (options.forceRender) {
                chart.render();
            }
            
        } catch (error) {
            console.error('Failed to update chart:', error);
            throw error;
        }
    }
    
    /**
     * Destroy chart instance
     * 
     * @param {Chart} chart - Chart.js instance
     */
    destroy(chart) {
        if (!chart) {
            return;
        }
        
        try {
            chart.destroy();
        } catch (error) {
            console.error('Failed to destroy chart:', error);
        }
    }
    
    /**
     * Check if chart is valid and responsive
     * 
     * @param {Chart} chart - Chart.js instance
     * @returns {boolean} Is chart valid
     */
    isValid(chart) {
        return chart && 
               typeof chart.update === 'function' && 
               typeof chart.destroy === 'function' &&
               chart.canvas &&
               chart.canvas.parentNode;
    }
}
