/**
 * Chart interfaces following SOLID principles
 * Interface Segregation Principle - Separate interfaces for different responsibilities
 */

/**
 * Interface for data processing operations
 */
class DataProcessorInterface {
    processData(rawData) {
        throw new Error('processData method must be implemented');
    }
}

/**
 * Interface for chart rendering operations
 */
class ChartRendererInterface {
    render(chartElement, data, options) {
        throw new Error('render method must be implemented');
    }
    
    update(chart, data) {
        throw new Error('update method must be implemented');
    }
    
    destroy(chart) {
        throw new Error('destroy method must be implemented');
    }
}

/**
 * Interface for data loading operations
 */
class DataLoaderInterface {
    loadData(params) {
        throw new Error('loadData method must be implemented');
    }
}

/**
 * Interface for chart configuration
 */
class ChartConfigInterface {
    getConfiguration(data, options) {
        throw new Error('getConfiguration method must be implemented');
    }
}
