/**
 * SOLID-compliant main controller
 * Dependency Inversion Principle - depends on abstractions, not concretions
 * Open/Closed Principle - can be extended without modification
 */

class MoodTriggersController {
    constructor(tagManager, themeManager, apiClient, notificationManager, formManager) {
        // Dependency Inversion - inject dependencies
        this.tagManager = tagManager;
        this.themeManager = themeManager;
        this.apiClient = apiClient;
        this.notificationManager = notificationManager;
        this.formManager = formManager;
    }

    // Single Responsibility - only coordinates between services
    async initialize() {
        this.themeManager.initializeTheme();
        this.tagManager.initializeCategories();
        this._bindEvents();
    }

    async saveContext() {
        try {
            if (!this.formManager.validateForm()) {
                this.notificationManager.showError('Please fill in required fields');
                return;
            }

            const contextData = {
                tags: this.tagManager.getSelectedTags(),
                context: this.formManager.getFormData()
            };

            this._animateSaveButton();
            
            const result = await this.apiClient.saveContext(contextData);
            
            if (result.success) {
                this.notificationManager.showSuccess('✅ Context saved successfully!');
                this._clearFormData();
            } else {
                this.notificationManager.showError('❌ Failed to save: ' + result.error);
            }
        } catch (error) {
            console.error('Save error:', error);
            this.notificationManager.showError('❌ Error saving context');
        }
    }

    toggleTheme() {
        this.themeManager.toggleTheme();
    }

    addCustomTag() {
        const tagName = prompt('Enter custom tag name:');
        if (tagName && tagName.trim()) {
            // Extend functionality without modifying existing code
            this._addCustomTagToCategory(tagName.trim(), 'emotions');
        }
    }

    // Private methods - implementation details
    _bindEvents() {
        // Global functions for onclick handlers
        window.toggleTheme = () => this.toggleTheme();
        window.saveMoodContext = () => this.saveContext();
        window.addCustomTag = () => this.addCustomTag();
    }

    _animateSaveButton() {
        const saveButton = document.querySelector('.save-button');
        saveButton.style.transform = 'scale(0.95)';
        setTimeout(() => {
            saveButton.style.transform = 'scale(1)';
        }, 150);
    }

    _clearFormData() {
        this.tagManager.clearSelectedTags();
        this.formManager.clearForm();
    }

    _addCustomTagToCategory(tagName, category) {
        const categoryContainer = document.getElementById(`${category}Tags`);
        const tagChip = document.createElement('div');
        tagChip.className = 'tag-chip';
        tagChip.setAttribute('data-tag', tagName);
        tagChip.onclick = () => this.tagManager.toggleTag(tagName, category, '#C62828');
        tagChip.innerHTML = `
            <span class="material-icons">tag</span>
            ${tagName}
        `;
        categoryContainer.appendChild(tagChip);
    }
}

// Factory pattern for creating controller with dependencies
class MoodTriggersFactory {
    static create() {
        // Dependency Injection - create all dependencies
        const tagManager = new TagManager();
        const themeManager = new ThemeManager();
        const apiClient = new ApiClient();
        const notificationManager = new NotificationManager();
        const formManager = new FormManager();

        // Return controller with injected dependencies
        return new MoodTriggersController(
            tagManager,
            themeManager,
            apiClient,
            notificationManager,
            formManager
        );
    }
}

// Global instances for backward compatibility
let tagManager, themeManager, controller;

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    controller = MoodTriggersFactory.create();
    controller.initialize();
    
    // Expose for onclick handlers
    tagManager = controller.tagManager;
    themeManager = controller.themeManager;
});
