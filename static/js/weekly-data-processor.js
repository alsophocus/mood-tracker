/**
 * Weekly data processor following Single Responsibility Principle
 * Responsible only for processing weekly mood data
 */
class WeeklyDataProcessor extends DataProcessorInterface {
    
    /**
     * Process weekly mood data for chart display
     * Converts 0 values to null for line breaks
     * 
     * @param {Object} rawData - Raw data from API
     * @returns {Object} Processed data for chart
     */
    processData(rawData) {
        if (!rawData || !rawData.data) {
            return this._getEmptyData();
        }
        
        const processedData = rawData.data.map(value => {
            // Convert 0 (no data) to null for Chart.js line breaks
            // Keep values 1-7 (valid moods) as-is
            return (value === 0) ? null : value;
        });
        
        return {
            ...rawData,
            data: processedData,
            labels: rawData.days || rawData.labels || this._getDefaultLabels()
        };
    }
    
    /**
     * Get default day labels
     * @private
     */
    _getDefaultLabels() {
        return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    }
    
    /**
     * Get empty data structure
     * @private
     */
    _getEmptyData() {
        return {
            labels: this._getDefaultLabels(),
            data: [null, null, null, null, null, null, null],
            period: 'No data available'
        };
    }
    
    /**
     * Validate processed data
     * @param {Object} data - Processed data
     * @returns {boolean} Is data valid
     */
    validateData(data) {
        return data && 
               Array.isArray(data.labels) && 
               Array.isArray(data.data) && 
               data.labels.length === 7 && 
               data.data.length === 7;
    }
}
