/**
 * SOLID-compliant carousel controller
 * Single Responsibility - handles only carousel UI logic
 * Dependency Inversion - depends on abstractions
 */

class CarouselController {
    constructor(apiClient, container) {
        this.apiClient = apiClient;
        this.container = container;
        this.currentIndex = 0;
        this.moods = [];
        this.autoScrollInterval = null;
        this.isPlaying = true;
        this.scrollSpeed = 3000; // 3 seconds
    }

    async initialize() {
        try {
            const response = await this.apiClient.getCarouselMoods();
            if (response.success) {
                this.moods = response.moods;
                this.render();
                this.bindEvents();
                this.startAutoScroll();
            }
        } catch (error) {
            console.error('Carousel initialization failed:', error);
        }
    }

    render() {
        if (this.moods.length === 0) {
            this.container.innerHTML = '<div class="carousel-empty">No mood entries yet</div>';
            return;
        }

        this.container.innerHTML = `
            <div class="carousel-header">
                <h3 class="carousel-title">Recent Moods</h3>
                <div class="carousel-controls">
                    <button class="carousel-btn" id="prevBtn">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                    <button class="carousel-btn" id="playPauseBtn">
                        <i class="fas fa-${this.isPlaying ? 'pause' : 'play'}"></i>
                    </button>
                    <button class="carousel-btn" id="nextBtn">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
            </div>
            <div class="carousel-track-container">
                <div class="carousel-track" id="carouselTrack">
                    ${this.moods.map((mood, index) => this.createMoodCard(mood, index)).join('')}
                </div>
            </div>
        `;
    }

    createMoodCard(mood, index) {
        return `
            <div class="mood-carousel-card" style="--mood-color: ${mood.color}" data-index="${index}">
                <div class="mood-card-emoji">${mood.emoji}</div>
                <div class="mood-card-content">
                    <div class="mood-card-mood">${mood.mood}</div>
                    <div class="mood-card-datetime">${mood.date} ${mood.time}</div>
                    ${mood.notes ? `<div class="mood-card-notes">${mood.notes}</div>` : ''}
                    ${mood.triggers ? `<div class="mood-card-triggers">${mood.triggers}</div>` : ''}
                </div>
            </div>
        `;
    }

    bindEvents() {
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const playPauseBtn = document.getElementById('playPauseBtn');

        prevBtn?.addEventListener('click', () => this.previousSlide());
        nextBtn?.addEventListener('click', () => this.nextSlide());
        playPauseBtn?.addEventListener('click', () => this.togglePlayPause());

        // Pause on hover
        this.container.addEventListener('mouseenter', () => this.pauseAutoScroll());
        this.container.addEventListener('mouseleave', () => {
            if (this.isPlaying) this.startAutoScroll();
        });
    }

    nextSlide() {
        this.currentIndex = (this.currentIndex + 1) % Math.max(1, this.moods.length - 2);
        this.updateCarouselPosition();
    }

    previousSlide() {
        this.currentIndex = this.currentIndex === 0 ? Math.max(0, this.moods.length - 3) : this.currentIndex - 1;
        this.updateCarouselPosition();
    }

    updateCarouselPosition() {
        const track = document.getElementById('carouselTrack');
        if (track) {
            const translateX = -this.currentIndex * (280 + 16); // card width + gap
            track.style.transform = `translateX(${translateX}px)`;
        }
    }

    startAutoScroll() {
        this.clearAutoScroll();
        if (this.moods.length > 3) {
            this.autoScrollInterval = setInterval(() => this.nextSlide(), this.scrollSpeed);
        }
    }

    pauseAutoScroll() {
        this.clearAutoScroll();
    }

    clearAutoScroll() {
        if (this.autoScrollInterval) {
            clearInterval(this.autoScrollInterval);
            this.autoScrollInterval = null;
        }
    }

    togglePlayPause() {
        this.isPlaying = !this.isPlaying;
        const icon = document.querySelector('#playPauseBtn i');
        if (icon) {
            icon.className = `fas fa-${this.isPlaying ? 'pause' : 'play'}`;
        }
        
        if (this.isPlaying) {
            this.startAutoScroll();
        } else {
            this.pauseAutoScroll();
        }
    }
}

// API Client for carousel
class CarouselApiClient {
    async getCarouselMoods() {
        const response = await fetch('/api/carousel/recent-moods');
        return await response.json();
    }
}

// Factory for creating carousel
class CarouselFactory {
    static create(containerId) {
        const container = document.getElementById(containerId);
        const apiClient = new CarouselApiClient();
        return new CarouselController(apiClient, container);
    }
}
