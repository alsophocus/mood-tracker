/**
 * Weekly chart configuration following Single Responsibility Principle
 * Responsible only for generating Chart.js configuration
 */
class WeeklyChartConfig extends ChartConfigInterface {
    
    /**
     * Get Chart.js configuration for weekly patterns
     * 
     * @param {Object} data - Processed chart data
     * @param {Object} options - Additional options
     * @returns {Object} Chart.js configuration
     */
    getConfiguration(data, options = {}) {
        return {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: data.period || 'Weekly Patterns',
                    data: data.data || [],
                    borderColor: options.borderColor || '#6750A4',
                    backgroundColor: options.backgroundColor || 'rgba(103, 80, 164, 0.1)',
                    tension: options.tension || 0.4,
                    fill: options.fill !== undefined ? options.fill : true,
                    borderWidth: options.borderWidth || 2,
                    pointRadius: options.pointRadius || 4,
                    spanGaps: false  // Don't connect lines across null values
                }]
            },
            options: this._getChartOptions(options)
        };
    }
    
    /**
     * Get chart options configuration
     * @private
     */
    _getChartOptions(customOptions = {}) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 7,
                    min: 0,
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            const moodLabels = {
                                1: 'Very Bad',
                                2: 'Bad', 
                                3: 'Slightly Bad',
                                4: 'Neutral',
                                5: 'Slightly Well',
                                6: 'Well',
                                7: 'Very Well'
                            };
                            return moodLabels[value] || value;
                        }
                    }
                },
                x: {
                    grid: {
                        display: true
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            if (context.parsed.y === null) {
                                return 'No data';
                            }
                            const moodLabels = {
                                1: 'Very Bad',
                                2: 'Bad',
                                3: 'Slightly Bad', 
                                4: 'Neutral',
                                5: 'Slightly Well',
                                6: 'Well',
                                7: 'Very Well'
                            };
                            return `${context.dataset.label}: ${moodLabels[context.parsed.y] || context.parsed.y}`;
                        }
                    }
                }
            },
            ...customOptions
        };
    }
}
