/**
 * SOLID-compliant service implementations for Recent Moods Carousel
 * Single Responsibility Principle - each class handles one specific concern
 */

// Data management service - Single Responsibility
class CarouselDataService extends CarouselDataInterface {
    constructor(apiClient) {
        super();
        this.apiClient = apiClient; // Dependency Injection
        this.moodColors = {
            'very bad': '#D32F2F',
            'bad': '#F57C00', 
            'slightly bad': '#FF9800',
            'neutral': '#6750A4',
            'slightly well': '#388E3C',
            'well': '#2E7D32',
            'very well': '#1B5E20'
        };
        this.moodEmojis = {
            'very bad': '😢',
            'bad': '😞',
            'slightly bad': '😕',
            'neutral': '😐',
            'slightly well': '🙂',
            'well': '😊',
            'very well': '😄'
        };
    }

    async loadMoodData() {
        try {
            const response = await this.apiClient.get('/recent_moods?limit=15');
            return response.moods || [];
        } catch (error) {
            console.error('Error loading mood data:', error);
            return [];
        }
    }

    formatMoodCard(mood) {
        return {
            id: mood.id,
            emoji: this.getMoodEmoji(mood.mood),
            mood: mood.mood,
            color: this.getMoodColor(mood.mood),
            date: this._formatDate(mood.date),
            time: this._formatTime(mood.timestamp),
            notes: this._truncateNotes(mood.notes)
        };
    }

    getMoodColor(moodLevel) {
        return this.moodColors[moodLevel] || this.moodColors['neutral'];
    }

    getMoodEmoji(moodLevel) {
        return this.moodEmojis[moodLevel] || this.moodEmojis['neutral'];
    }

    _formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric' 
        });
    }

    _formatTime(timestamp) {
        if (!timestamp) return '';
        const time = new Date(timestamp);
        return time.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
    }

    _truncateNotes(notes) {
        if (!notes) return '';
        return notes.length > 50 ? notes.substring(0, 47) + '...' : notes;
    }
}

// Animation service - Single Responsibility
class CarouselAnimationService extends CarouselAnimationInterface {
    constructor(container) {
        super();
        this.container = container;
        this.scrollInterval = null;
        this.isPlaying = true;
        this.scrollSpeed = 3000; // 3 seconds
        this.isPaused = false;
    }

    startAutoScroll() {
        if (this.scrollInterval) return;
        
        this.scrollInterval = setInterval(() => {
            if (!this.isPaused) {
                this.scrollToNext();
            }
        }, this.scrollSpeed);
        this.isPlaying = true;
    }

    stopAutoScroll() {
        if (this.scrollInterval) {
            clearInterval(this.scrollInterval);
            this.scrollInterval = null;
        }
        this.isPlaying = false;
    }

    pauseAutoScroll() {
        this.isPaused = true;
    }

    resumeAutoScroll() {
        this.isPaused = false;
    }

    scrollToNext() {
        const scrollContainer = this.container.querySelector('.carousel-scroll-container');
        if (!scrollContainer) return;

        const cardWidth = 280; // Card width + gap
        const maxScroll = scrollContainer.scrollWidth - scrollContainer.clientWidth;
        
        if (scrollContainer.scrollLeft >= maxScroll) {
            // Reset to beginning with smooth transition
            scrollContainer.scrollTo({ left: 0, behavior: 'smooth' });
        } else {
            scrollContainer.scrollBy({ left: cardWidth, behavior: 'smooth' });
        }
    }

    scrollToPrevious() {
        const scrollContainer = this.container.querySelector('.carousel-scroll-container');
        if (!scrollContainer) return;

        const cardWidth = 280;
        
        if (scrollContainer.scrollLeft <= 0) {
            // Go to end
            const maxScroll = scrollContainer.scrollWidth - scrollContainer.clientWidth;
            scrollContainer.scrollTo({ left: maxScroll, behavior: 'smooth' });
        } else {
            scrollContainer.scrollBy({ left: -cardWidth, behavior: 'smooth' });
        }
    }
}

// UI rendering service - Single Responsibility
class CarouselUIService extends CarouselUIInterface {
    constructor(container) {
        super();
        this.container = container;
    }

    render(moodData) {
        const carouselHTML = `
            <div class="carousel-header">
                <div class="carousel-title">
                    <i class="material-icons">history</i>
                    <h3>Recent Moods</h3>
                </div>
                <div class="carousel-controls">
                    <button class="carousel-btn carousel-prev" aria-label="Previous">
                        <i class="material-icons">chevron_left</i>
                    </button>
                    <button class="carousel-btn carousel-play-pause" aria-label="Play/Pause">
                        <i class="material-icons">pause</i>
                    </button>
                    <button class="carousel-btn carousel-next" aria-label="Next">
                        <i class="material-icons">chevron_right</i>
                    </button>
                </div>
            </div>
            <div class="carousel-scroll-container">
                <div class="carousel-track">
                    ${moodData.map(mood => this._createMoodCard(mood)).join('')}
                </div>
            </div>
        `;
        
        this.container.innerHTML = carouselHTML;
    }

    updateControls(isPlaying) {
        const playPauseBtn = this.container.querySelector('.carousel-play-pause i');
        if (playPauseBtn) {
            playPauseBtn.textContent = isPlaying ? 'pause' : 'play_arrow';
        }
    }

    showLoading() {
        this.container.innerHTML = `
            <div class="carousel-loading">
                <div class="loading-spinner"></div>
                <span>Loading recent moods...</span>
            </div>
        `;
    }

    hideLoading() {
        const loading = this.container.querySelector('.carousel-loading');
        if (loading) loading.remove();
    }

    _createMoodCard(mood) {
        return `
            <div class="mood-carousel-card" style="border-left: 4px solid ${mood.color};">
                <div class="mood-card-header">
                    <span class="mood-emoji">${mood.emoji}</span>
                    <div class="mood-info">
                        <span class="mood-name">${mood.mood}</span>
                        <span class="mood-datetime">${mood.date} ${mood.time}</span>
                    </div>
                </div>
                ${mood.notes ? `<div class="mood-notes">${mood.notes}</div>` : ''}
            </div>
        `;
    }
}

// Event handling service - Single Responsibility
class CarouselEventService extends CarouselEventInterface {
    constructor(container, animationService) {
        super();
        this.container = container;
        this.animationService = animationService; // Dependency Injection
    }

    bindEvents() {
        // Play/Pause button
        const playPauseBtn = this.container.querySelector('.carousel-play-pause');
        if (playPauseBtn) {
            playPauseBtn.addEventListener('click', () => this.handlePlayPause());
        }

        // Navigation buttons
        const nextBtn = this.container.querySelector('.carousel-next');
        const prevBtn = this.container.querySelector('.carousel-prev');
        
        if (nextBtn) nextBtn.addEventListener('click', () => this.handleNext());
        if (prevBtn) prevBtn.addEventListener('click', () => this.handlePrevious());

        // Hover to pause
        const scrollContainer = this.container.querySelector('.carousel-scroll-container');
        if (scrollContainer) {
            scrollContainer.addEventListener('mouseenter', () => this.handleMouseEnter());
            scrollContainer.addEventListener('mouseleave', () => this.handleMouseLeave());
        }
    }

    handlePlayPause() {
        if (this.animationService.isPlaying) {
            this.animationService.stopAutoScroll();
        } else {
            this.animationService.startAutoScroll();
        }
        
        // Update UI through the container's UI service
        const event = new CustomEvent('controlsUpdate', { 
            detail: { isPlaying: this.animationService.isPlaying } 
        });
        this.container.dispatchEvent(event);
    }

    handleNext() {
        this.animationService.scrollToNext();
    }

    handlePrevious() {
        this.animationService.scrollToPrevious();
    }

    handleMouseEnter() {
        this.animationService.pauseAutoScroll();
    }

    handleMouseLeave() {
        this.animationService.resumeAutoScroll();
    }
}

// Simple API client for mood data
class CarouselApiClient {
    async get(endpoint) {
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }
}
