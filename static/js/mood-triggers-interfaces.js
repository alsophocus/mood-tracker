/**
 * SOLID-compliant interfaces for mood triggers system
 * Interface Segregation Principle - specific interfaces for different concerns
 */

// Theme management interface
class ThemeManagerInterface {
    toggleTheme() { throw new Error('Must implement toggleTheme'); }
    initializeTheme() { throw new Error('Must implement initializeTheme'); }
}

// Tag management interface
class TagManagerInterface {
    initializeCategories() { throw new Error('Must implement initializeCategories'); }
    toggleTag(tag, category, color) { throw new Error('Must implement toggleTag'); }
    getSelectedTags() { throw new Error('Must implement getSelectedTags'); }
    clearSelectedTags() { throw new Error('Must implement clearSelectedTags'); }
}

// API client interface
class ApiClientInterface {
    saveContext(data) { throw new Error('Must implement saveContext'); }
    getTags() { throw new Error('Must implement getTags'); }
}

// UI notification interface
class NotificationInterface {
    showSuccess(message) { throw new Error('Must implement showSuccess'); }
    showError(message) { throw new Error('Must implement showError'); }
}

// Form management interface
class FormManagerInterface {
    getFormData() { throw new Error('Must implement getFormData'); }
    clearForm() { throw new Error('Must implement clearForm'); }
    validateForm() { throw new Error('Must implement validateForm'); }
}
