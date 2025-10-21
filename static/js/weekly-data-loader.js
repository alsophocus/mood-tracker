/**
 * Weekly data loader following Single Responsibility Principle
 * Responsible only for loading weekly patterns data from API
 */
class WeeklyDataLoader extends DataLoaderInterface {
    
    constructor(baseUrl = '') {
        super();
        this.baseUrl = baseUrl;
        this.endpoint = '/weekly_patterns';
    }
    
    /**
     * Load weekly patterns data
     * 
     * @param {Object} params - Request parameters
     * @param {number} params.year - Year
     * @param {number} params.month - Month
     * @param {number} params.week - Week of month
     * @returns {Promise<Object>} Weekly patterns data
     */
    async loadData(params = {}) {
        try {
            const url = this._buildUrl(params);
            console.log('Loading weekly patterns from:', url);
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Received weekly patterns data:', data);
            
            return this._validateResponse(data);
            
        } catch (error) {
            console.error('Failed to load weekly patterns:', error);
            throw new Error(`Data loading failed: ${error.message}`);
        }
    }
    
    /**
     * Load current week data (no parameters)
     * 
     * @returns {Promise<Object>} Current week data
     */
    async loadCurrentWeek() {
        return this.loadData(); // No parameters = current week
    }
    
    /**
     * Build URL with query parameters
     * @private
     */
    _buildUrl(params) {
        const url = new URL(this.endpoint, window.location.origin);
        
        if (params.year) url.searchParams.set('year', params.year);
        if (params.month) url.searchParams.set('month', params.month);
        if (params.week) url.searchParams.set('week', params.week);
        
        return url.toString();
    }
    
    /**
     * Validate API response
     * @private
     */
    _validateResponse(data) {
        if (!data) {
            throw new Error('Empty response from server');
        }
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Ensure required fields exist
        return {
            data: data.data || [],
            labels: data.labels || data.days || [],
            days: data.days || data.labels || [],
            period: data.period || 'Weekly Patterns',
            ...data
        };
    }
    
    /**
     * Validate request parameters
     * 
     * @param {Object} params - Parameters to validate
     * @returns {boolean} Are parameters valid
     */
    validateParams(params) {
        if (!params.year || !params.month || !params.week) {
            return false;
        }
        
        const year = parseInt(params.year);
        const month = parseInt(params.month);
        const week = parseInt(params.week);
        
        return year >= 2020 && year <= 2030 &&
               month >= 1 && month <= 12 &&
               week >= 1 && week <= 5;
    }
}
