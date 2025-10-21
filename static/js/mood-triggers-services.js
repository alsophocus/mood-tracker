/**
 * SOLID-compliant service implementations
 * Single Responsibility Principle - each class handles one specific concern
 */

// Theme management - Single Responsibility
class ThemeManager extends ThemeManagerInterface {
    constructor() {
        super();
        this.themeIcon = null;
    }

    toggleTheme() {
        const body = document.body;
        const isDark = body.getAttribute('data-theme') === 'dark';
        
        if (isDark) {
            body.removeAttribute('data-theme');
            this.themeIcon.textContent = 'light_mode';
            localStorage.setItem('theme', 'light');
        } else {
            body.setAttribute('data-theme', 'dark');
            this.themeIcon.textContent = 'dark_mode';
            localStorage.setItem('theme', 'dark');
        }
    }

    initializeTheme() {
        this.themeIcon = document.getElementById('themeIcon');
        const savedTheme = localStorage.getItem('theme');
        
        if (savedTheme === 'dark') {
            document.body.setAttribute('data-theme', 'dark');
            this.themeIcon.textContent = 'dark_mode';
        } else {
            this.themeIcon.textContent = 'light_mode';
        }
    }
}

// Tag management - Single Responsibility
class TagManager extends TagManagerInterface {
    constructor() {
        super();
        this.selectedTags = new Set();
        this.tagCategories = {
            work: { icon: 'work', color: '#D32F2F' },
            health: { icon: 'fitness_center', color: '#388E3C' },
            social: { icon: 'group', color: '#7B1FA2' },
            activities: { icon: 'local_activity', color: '#0288D1' },
            environment: { icon: 'wb_sunny', color: '#00796B' },
            emotions: { icon: 'psychology', color: '#C62828' }
        };
        this.defaultTags = {
            work: ['work', 'meeting', 'deadline', 'project'],
            health: ['exercise', 'sleep', 'food', 'medication'],
            social: ['family', 'friends', 'party', 'date'],
            activities: ['music', 'reading', 'gaming', 'cooking'],
            environment: ['weather', 'home', 'outdoors', 'travel'],
            emotions: ['stress', 'relaxation', 'excitement', 'anxiety']
        };
    }

    initializeCategories() {
        const container = document.getElementById('tagCategories');
        
        Object.entries(this.tagCategories).forEach(([category, config]) => {
            const categoryCard = this._createCategoryCard(category, config);
            container.appendChild(categoryCard);
        });
    }

    toggleTag(tag, category, color) {
        const tagElement = document.querySelector(`[data-tag="${tag}"]`);
        
        if (this.selectedTags.has(tag)) {
            this.selectedTags.delete(tag);
            tagElement.classList.remove('selected');
        } else {
            this.selectedTags.add(tag);
            tagElement.classList.add('selected');
            this._addRippleEffect(tagElement);
        }
        
        this._updateSelectedTagsList();
    }

    getSelectedTags() {
        return Array.from(this.selectedTags);
    }

    clearSelectedTags() {
        this.selectedTags.clear();
        document.querySelectorAll('.tag-chip.selected').forEach(chip => {
            chip.classList.remove('selected');
        });
        this._updateSelectedTagsList();
    }

    _createCategoryCard(category, config) {
        const categoryCard = document.createElement('div');
        categoryCard.className = 'category-card';
        
        categoryCard.innerHTML = `
            <div class="category-header">
                <div class="category-icon" style="background-color: ${config.color}20; color: ${config.color};">
                    <span class="material-icons">${config.icon}</span>
                </div>
                <h3 class="category-title">${category}</h3>
            </div>
            <div class="tags-grid" id="${category}Tags">
                ${this.defaultTags[category].map(tag => `
                    <div class="tag-chip" onclick="tagManager.toggleTag('${tag}', '${category}', '${config.color}')" data-tag="${tag}">
                        <span class="material-icons">${this._getTagIcon(tag)}</span>
                        ${tag}
                    </div>
                `).join('')}
            </div>
        `;
        
        return categoryCard;
    }

    _getTagIcon(tag) {
        const iconMap = {
            work: 'work', meeting: 'groups', deadline: 'schedule', project: 'assignment',
            exercise: 'fitness_center', sleep: 'bedtime', food: 'restaurant', medication: 'medication',
            family: 'family_restroom', friends: 'group', party: 'celebration', date: 'favorite',
            music: 'music_note', reading: 'menu_book', gaming: 'sports_esports', cooking: 'restaurant_menu',
            weather: 'wb_sunny', home: 'home', outdoors: 'park', travel: 'flight',
            stress: 'psychology', relaxation: 'spa', excitement: 'star', anxiety: 'psychology_alt'
        };
        return iconMap[tag] || 'tag';
    }

    _addRippleEffect(element) {
        element.classList.add('ripple');
        setTimeout(() => element.classList.remove('ripple'), 300);
    }

    _updateSelectedTagsList() {
        const container = document.getElementById('selectedTagsList');
        container.innerHTML = '';
        
        this.selectedTags.forEach(tag => {
            const tagChip = document.createElement('div');
            tagChip.className = 'tag-chip selected';
            tagChip.innerHTML = `
                <span class="material-icons">${this._getTagIcon(tag)}</span>
                ${tag}
                <span class="material-icons" onclick="tagManager.removeTag('${tag}')" style="cursor: pointer; font-size: 16px;">close</span>
            `;
            container.appendChild(tagChip);
        });
    }

    removeTag(tag) {
        this.selectedTags.delete(tag);
        document.querySelector(`[data-tag="${tag}"]`).classList.remove('selected');
        this._updateSelectedTagsList();
    }
}

// API client - Single Responsibility
class ApiClient extends ApiClientInterface {
    async saveContext(data) {
        const response = await fetch('/api/mood-context', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await response.json();
    }

    async getTags() {
        const response = await fetch('/api/tags');
        return await response.json();
    }
}

// Notification system - Single Responsibility
class NotificationManager extends NotificationInterface {
    showSuccess(message) {
        this._showSnackbar(message, 'success');
    }

    showError(message) {
        this._showSnackbar(message, 'error');
    }

    _showSnackbar(message, type) {
        const snackbar = document.createElement('div');
        snackbar.style.cssText = `
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--md-sys-color-surface-variant);
            color: var(--md-sys-color-on-surface-variant);
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            font-size: 0.875rem;
            font-weight: 500;
        `;
        snackbar.textContent = message;
        document.body.appendChild(snackbar);
        
        setTimeout(() => snackbar.remove(), 3000);
    }
}

// Form management - Single Responsibility
class FormManager extends FormManagerInterface {
    getFormData() {
        return {
            location: document.getElementById('location').value,
            activity: document.getElementById('activity').value,
            weather: document.getElementById('weather').value,
            notes: document.getElementById('notes').value
        };
    }

    clearForm() {
        document.getElementById('location').value = '';
        document.getElementById('activity').value = '';
        document.getElementById('weather').value = '';
        document.getElementById('notes').value = '';
    }

    validateForm() {
        // Basic validation - can be extended
        return true;
    }
}
