/**
 * SOLID-compliant interfaces for Recent Moods Carousel
 * Interface Segregation Principle - specific interfaces for different carousel concerns
 */

// Carousel data management interface
class CarouselDataInterface {
    async loadMoodData() { throw new Error('Must implement loadMoodData'); }
    formatMoodCard(mood) { throw new Error('Must implement formatMoodCard'); }
    getMoodColor(moodLevel) { throw new Error('Must implement getMoodColor'); }
    getMoodEmoji(moodLevel) { throw new Error('Must implement getMoodEmoji'); }
}

// Carousel animation interface
class CarouselAnimationInterface {
    startAutoScroll() { throw new Error('Must implement startAutoScroll'); }
    stopAutoScroll() { throw new Error('Must implement stopAutoScroll'); }
    pauseAutoScroll() { throw new Error('Must implement pauseAutoScroll'); }
    resumeAutoScroll() { throw new Error('Must implement resumeAutoScroll'); }
    scrollToNext() { throw new Error('Must implement scrollToNext'); }
    scrollToPrevious() { throw new Error('Must implement scrollToPrevious'); }
}

// Carousel UI interface
class CarouselUIInterface {
    render(moodData) { throw new Error('Must implement render'); }
    updateControls(isPlaying) { throw new Error('Must implement updateControls'); }
    showLoading() { throw new Error('Must implement showLoading'); }
    hideLoading() { throw new Error('Must implement hideLoading'); }
}

// Carousel event handling interface
class CarouselEventInterface {
    bindEvents() { throw new Error('Must implement bindEvents'); }
    handlePlayPause() { throw new Error('Must implement handlePlayPause'); }
    handleNext() { throw new Error('Must implement handleNext'); }
    handlePrevious() { throw new Error('Must implement handlePrevious'); }
    handleMouseEnter() { throw new Error('Must implement handleMouseEnter'); }
    handleMouseLeave() { throw new Error('Must implement handleMouseLeave'); }
}
