# Material Design 3 (Material You) Pattern Documentation

## Overview
This document outlines the complete Material Design 3 implementation patterns used in the Mood Tracker application, including color systems, typography, animations, and component patterns.

## 🎨 Color System

### Light Theme Colors
```css
:root {
    /* Primary Colors */
    --md-sys-color-primary: #6750a4;
    --md-sys-color-on-primary: #ffffff;
    --md-sys-color-primary-container: #eaddff;
    --md-sys-color-on-primary-container: #21005d;
    
    /* Secondary Colors */
    --md-sys-color-secondary: #625b71;
    --md-sys-color-on-secondary: #ffffff;
    --md-sys-color-secondary-container: #e8def8;
    --md-sys-color-on-secondary-container: #1d192b;
    
    /* Tertiary Colors */
    --md-sys-color-tertiary: #7d5260;
    --md-sys-color-on-tertiary: #ffffff;
    --md-sys-color-tertiary-container: #ffd8e4;
    --md-sys-color-on-tertiary-container: #31111d;
    
    /* Surface Colors */
    --md-sys-color-background: #fffbfe;
    --md-sys-color-on-background: #1c1b1f;
    --md-sys-color-surface: #fffbfe;
    --md-sys-color-on-surface: #1c1b1f;
    --md-sys-color-surface-variant: #e7e0ec;
    --md-sys-color-on-surface-variant: #49454f;
    
    /* Surface Container Hierarchy */
    --md-sys-color-surface-container-lowest: #ffffff;
    --md-sys-color-surface-container-low: #f7f2fa;
    --md-sys-color-surface-container: #f3edf7;
    --md-sys-color-surface-container-high: #ece6f0;
    --md-sys-color-surface-container-highest: #e6e0e9;
}
```

### Dark Theme Colors
```css
[data-theme="dark"] {
    --md-sys-color-primary: #d0bcff;
    --md-sys-color-on-primary: #381e72;
    --md-sys-color-primary-container: #4f378b;
    --md-sys-color-on-primary-container: #eaddff;
    
    --md-sys-color-background: #10090d;
    --md-sys-color-on-background: #e6e0e9;
    --md-sys-color-surface: #10090d;
    --md-sys-color-on-surface: #e6e0e9;
    
    --md-sys-color-surface-container-lowest: #0b0509;
    --md-sys-color-surface-container-low: #1c1b1f;
    --md-sys-color-surface-container: #201f23;
    --md-sys-color-surface-container-high: #2b2930;
    --md-sys-color-surface-container-highest: #36343b;
}
```

## 📝 Typography Scale

### Font Stack
```css
body {
    font-family: 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
}
```

### Typography Classes
```css
.display-large {
    font-size: 57px;
    font-weight: 400;
    line-height: 64px;
    letter-spacing: -0.25px;
}

.headline-large {
    font-size: 32px;
    font-weight: 400;
    line-height: 40px;
    letter-spacing: 0px;
}

.title-large {
    font-size: 22px;
    font-weight: 400;
    line-height: 28px;
    letter-spacing: 0px;
}

.body-large {
    font-size: 16px;
    font-weight: 400;
    line-height: 24px;
    letter-spacing: 0.5px;
}

.body-medium {
    font-size: 14px;
    font-weight: 400;
    line-height: 20px;
    letter-spacing: 0.25px;
}

.label-large {
    font-size: 14px;
    font-weight: 500;
    line-height: 20px;
    letter-spacing: 0.1px;
}
```

## 🎭 Shape System

### Corner Radius Tokens
```css
:root {
    --md-sys-shape-corner-none: 0px;
    --md-sys-shape-corner-extra-small: 4px;
    --md-sys-shape-corner-small: 8px;
    --md-sys-shape-corner-medium: 12px;
    --md-sys-shape-corner-large: 16px;
    --md-sys-shape-corner-extra-large: 28px;
    --md-sys-shape-corner-full: 50%;
}
```

### Expressive Asymmetric Shapes
```css
:root {
    --md-sys-shape-asymmetric-1: 4px 16px 4px 16px;
    --md-sys-shape-asymmetric-2: 8px 24px 8px 24px;
    --md-sys-shape-asymmetric-3: 12px 28px 12px 28px;
}
```

## 🏗️ Elevation System

### Elevation Tokens
```css
:root {
    --md-sys-elevation-level0: 0px 0px 0px 0px rgba(0, 0, 0, 0.2);
    --md-sys-elevation-level1: 0px 2px 1px -1px rgba(0, 0, 0, 0.2), 
                               0px 1px 1px 0px rgba(0, 0, 0, 0.14), 
                               0px 1px 3px 0px rgba(0, 0, 0, 0.12);
    --md-sys-elevation-level2: 0px 3px 1px -2px rgba(0, 0, 0, 0.2), 
                               0px 2px 2px 0px rgba(0, 0, 0, 0.14), 
                               0px 1px 5px 0px rgba(0, 0, 0, 0.12);
    --md-sys-elevation-level3: 0px 3px 3px -2px rgba(0, 0, 0, 0.2), 
                               0px 3px 4px 0px rgba(0, 0, 0, 0.14), 
                               0px 1px 8px 0px rgba(0, 0, 0, 0.12);
}
```

## 🎬 Motion System

### Easing Curves
```css
:root {
    --md-sys-motion-easing-standard: cubic-bezier(0.2, 0, 0, 1);
    --md-sys-motion-easing-emphasized: cubic-bezier(0.2, 0, 0, 1);
    --md-sys-motion-easing-emphasized-accelerate: cubic-bezier(0.3, 0, 0.8, 0.15);
    --md-sys-motion-easing-emphasized-decelerate: cubic-bezier(0.05, 0.7, 0.1, 1);
}
```

### Duration Tokens
```css
:root {
    --md-sys-motion-duration-short1: 50ms;
    --md-sys-motion-duration-short2: 100ms;
    --md-sys-motion-duration-short3: 150ms;
    --md-sys-motion-duration-short4: 200ms;
    --md-sys-motion-duration-medium1: 250ms;
    --md-sys-motion-duration-medium2: 300ms;
    --md-sys-motion-duration-medium3: 350ms;
    --md-sys-motion-duration-medium4: 400ms;
    --md-sys-motion-duration-long1: 450ms;
    --md-sys-motion-duration-long2: 500ms;
}
```

## 🧩 Component Patterns

### Material Design 3 Cards
```css
.md-card {
    background-color: var(--md-sys-color-surface-container);
    color: var(--md-sys-color-on-surface);
    border-radius: var(--md-sys-shape-corner-extra-large);
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: var(--md-sys-elevation-level1);
    transition: all var(--md-sys-motion-duration-medium2) var(--md-sys-motion-easing-emphasized);
    position: relative;
    overflow: hidden;
}

.md-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, var(--md-sys-color-primary) 0%, transparent 50%);
    opacity: 0;
    transition: opacity var(--md-sys-motion-duration-medium1) var(--md-sys-motion-easing-standard);
}

.md-card:hover {
    box-shadow: var(--md-sys-elevation-level3);
    transform: translateY(-4px) scale(1.02);
}

.md-card:hover::before {
    opacity: 0.03;
}
```

### Expressive Mood Cards
```css
.mood-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 16px;
    background-color: var(--md-sys-color-surface-container-high);
    border: 1px solid var(--md-sys-color-outline-variant);
    border-radius: var(--md-sys-shape-asymmetric-1);
    cursor: pointer;
    transition: all var(--md-sys-motion-duration-medium2) var(--md-sys-motion-easing-emphasized);
    min-height: 100px;
    position: relative;
    overflow: hidden;
    transform-origin: center;
}

.mood-card:hover {
    transform: translateY(-8px) rotate(2deg) scale(1.05);
    box-shadow: var(--md-sys-elevation-level4);
    border-radius: var(--md-sys-shape-asymmetric-2);
}

.mood-card.selected {
    background-color: var(--md-sys-color-primary-container);
    color: var(--md-sys-color-on-primary-container);
    border-color: var(--md-sys-color-primary);
    border-radius: var(--md-sys-shape-asymmetric-3);
    transform: translateY(-6px) scale(1.08);
    box-shadow: var(--md-sys-elevation-level5);
}
```

### Material Design 3 Buttons
```css
.md-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 10px 24px;
    border-radius: var(--md-sys-shape-corner-large);
    font-size: 14px;
    font-weight: 500;
    text-decoration: none;
    border: none;
    cursor: pointer;
    transition: all var(--md-sys-motion-duration-medium1) var(--md-sys-motion-easing-emphasized);
    min-height: 40px;
    position: relative;
    overflow: hidden;
}

.md-button::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: currentColor;
    opacity: 0;
    transition: opacity var(--md-sys-motion-duration-short3) var(--md-sys-motion-easing-standard);
}

.md-button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: var(--md-sys-elevation-level2);
}

.md-button:hover::before {
    opacity: var(--md-sys-state-hover-opacity);
}

.md-button-filled {
    background-color: var(--md-sys-color-primary);
    color: var(--md-sys-color-on-primary);
}

.md-button-outlined {
    background-color: transparent;
    color: var(--md-sys-color-primary);
    border: 1px solid var(--md-sys-color-outline);
}
```

### Floating Action Button (FAB)
```css
.md-fab {
    position: fixed;
    bottom: 24px;
    right: 24px;
    width: 56px;
    height: 56px;
    border-radius: var(--md-sys-shape-corner-large);
    background-color: var(--md-sys-color-primary-container);
    color: var(--md-sys-color-on-primary-container);
    border: none;
    cursor: pointer;
    box-shadow: var(--md-sys-elevation-level3);
    transition: all var(--md-sys-motion-duration-medium3) var(--md-sys-motion-easing-emphasized);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    z-index: 1000;
}

.md-fab:hover {
    transform: scale(1.1) rotate(5deg);
    box-shadow: var(--md-sys-elevation-level4);
    border-radius: var(--md-sys-shape-corner-extra-large);
}

.md-fab:active {
    transform: scale(0.95) rotate(-2deg);
    transition-duration: var(--md-sys-motion-duration-short2);
}
```

### Text Fields
```css
.md-text-field {
    position: relative;
    margin-bottom: 16px;
}

.md-text-field-input {
    width: 100%;
    padding: 16px;
    border: 1px solid var(--md-sys-color-outline);
    border-radius: var(--md-sys-shape-corner-extra-small);
    background-color: var(--md-sys-color-surface);
    color: var(--md-sys-color-on-surface);
    font-size: 16px;
    transition: all var(--md-sys-motion-duration-medium1) var(--md-sys-motion-easing-emphasized);
    font-family: 'Roboto', sans-serif;
}

.md-text-field-input:focus {
    outline: none;
    border-color: var(--md-sys-color-primary);
    border-width: 2px;
    transform: scale(1.02);
    box-shadow: 0 0 0 8px rgba(103, 80, 164, 0.1);
}

.md-text-field-label {
    position: absolute;
    left: 16px;
    top: 16px;
    color: var(--md-sys-color-on-surface-variant);
    font-size: 16px;
    transition: all var(--md-sys-motion-duration-medium1) var(--md-sys-motion-easing-emphasized);
    pointer-events: none;
    background-color: var(--md-sys-color-surface);
    padding: 0 4px;
    transform-origin: left center;
}

.md-text-field-input:focus + .md-text-field-label,
.md-text-field-input:not(:placeholder-shown) + .md-text-field-label {
    top: -8px;
    font-size: 12px;
    color: var(--md-sys-color-primary);
    transform: scale(0.9) translateY(-2px);
}
```

## 🎨 State Layers

### State Layer Opacity Values
```css
:root {
    --md-sys-state-hover-opacity: 0.08;
    --md-sys-state-focus-opacity: 0.12;
    --md-sys-state-pressed-opacity: 0.12;
    --md-sys-state-dragged-opacity: 0.16;
}
```

### State Layer Implementation
```css
.interactive-element::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: currentColor;
    opacity: 0;
    transition: opacity var(--md-sys-motion-duration-short3) var(--md-sys-motion-easing-standard);
}

.interactive-element:hover::before {
    opacity: var(--md-sys-state-hover-opacity);
}

.interactive-element:focus::before {
    opacity: var(--md-sys-state-focus-opacity);
}

.interactive-element:active::before {
    opacity: var(--md-sys-state-pressed-opacity);
}
```

## 🎭 Animations

### Entrance Animations
```css
@keyframes md-fade-in-up {
    from {
        opacity: 0;
        transform: translateY(24px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@keyframes md-fade-in-scale {
    from {
        opacity: 0;
        transform: scale(0.8) rotate(-5deg);
    }
    to {
        opacity: 1;
        transform: scale(1) rotate(0deg);
    }
}

.md-card {
    animation: md-fade-in-up var(--md-sys-motion-duration-long2) var(--md-sys-motion-easing-emphasized);
}

.mood-card {
    animation: md-fade-in-scale var(--md-sys-motion-duration-medium4) var(--md-sys-motion-easing-emphasized);
}

/* Staggered animation delays */
.mood-card:nth-child(1) { animation-delay: 0ms; }
.mood-card:nth-child(2) { animation-delay: 50ms; }
.mood-card:nth-child(3) { animation-delay: 100ms; }
.mood-card:nth-child(4) { animation-delay: 150ms; }
.mood-card:nth-child(5) { animation-delay: 200ms; }
.mood-card:nth-child(6) { animation-delay: 250ms; }
.mood-card:nth-child(7) { animation-delay: 300ms; }
```

### Expressive Animations
```css
@keyframes brainPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

.app-bar-title i {
    font-size: 32px;
    animation: brainPulse 2s ease-in-out infinite;
}

@keyframes md-pulse {
    0%, 100% { 
        opacity: 1; 
        transform: scale(1);
    }
    50% { 
        opacity: 0.6; 
        transform: scale(1.05);
    }
}

.status-indicator.checking {
    background-color: #ff9800;
    animation: md-pulse var(--md-sys-motion-duration-extra-long2) var(--md-sys-motion-easing-emphasized) infinite;
}
```

## 🎨 Theme Management

### Theme Toggle Implementation
```css
.theme-switch {
    width: 52px;
    height: 32px;
    background-color: var(--md-sys-color-surface-variant);
    border-radius: var(--md-sys-shape-corner-large);
    border: 2px solid var(--md-sys-color-outline);
    cursor: pointer;
    position: relative;
    transition: all var(--md-sys-motion-duration-medium2) var(--md-sys-motion-easing-emphasized);
    overflow: hidden;
}

.theme-switch::before {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 24px;
    height: 24px;
    background-color: var(--md-sys-color-outline);
    border-radius: var(--md-sys-shape-corner-full);
    transition: all var(--md-sys-motion-duration-medium2) var(--md-sys-motion-easing-emphasized);
    box-shadow: var(--md-sys-elevation-level1);
}

[data-theme="dark"] .theme-switch {
    background-color: var(--md-sys-color-primary);
    border-color: var(--md-sys-color-primary);
}

[data-theme="dark"] .theme-switch::before {
    transform: translateX(20px) rotate(180deg);
    background-color: var(--md-sys-color-on-primary);
}
```

### Theme Transition
```css
.theme-transitioning * {
    transition: background-color 300ms var(--md-sys-motion-easing-emphasized),
               color 300ms var(--md-sys-motion-easing-emphasized),
               border-color 300ms var(--md-sys-motion-easing-emphasized) !important;
}
```

## 📱 Responsive Design

### Breakpoints
```css
@media (max-width: 768px) {
    .container {
        padding: 12px;
    }
    
    .md-grid-2 {
        grid-template-columns: 1fr;
    }
    
    .mood-grid {
        grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
    }
}

@media (max-width: 480px) {
    .mood-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .chart-container {
        height: 200px;
        padding: 12px;
    }
}
```

## ♿ Accessibility

### Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

### High Contrast Support
```css
@media (prefers-contrast: high) {
    .md-card, .mood-card, .md-text-field-input, .md-select {
        border-width: 2px;
    }
}
```

## 🎯 Interactive Elements

### Ripple Effect
```javascript
function createRipple(element, event) {
    const ripple = document.createElement('div');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 600ms cubic-bezier(0.2, 0, 0, 1);
        pointer-events: none;
        z-index: 1000;
    `;
    
    element.style.position = 'relative';
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

@keyframes ripple {
    to {
        transform: scale(2);
        opacity: 0;
    }
}
```

## 🎨 Chart Styling

### Material Design 3 Chart Configuration
```javascript
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: true,
            position: 'top',
            labels: {
                font: {
                    family: 'Roboto',
                    size: 12
                }
            }
        },
        tooltip: {
            enabled: true,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgba(103, 80, 164, 0.8)',
            borderWidth: 1,
            cornerRadius: 8,
            displayColors: false
        }
    },
    scales: {
        y: {
            min: 1,
            max: 7,
            ticks: {
                font: {
                    family: 'Roboto',
                    size: 11
                }
            }
        }
    }
};
```

## 🎭 Component Hierarchy

### Surface Container Hierarchy Usage
- **surface-container-lowest**: Background for floating elements
- **surface-container-low**: Cards and containers
- **surface-container**: Default container background
- **surface-container-high**: Elevated containers
- **surface-container-highest**: Highest elevation containers

### Implementation Example
```css
.status-container {
    background-color: var(--md-sys-color-surface-container-low);
}

.md-card {
    background-color: var(--md-sys-color-surface-container);
}

.mood-card {
    background-color: var(--md-sys-color-surface-container-high);
}

.metric-card {
    background-color: var(--md-sys-color-surface-container-highest);
}
```

This comprehensive Material Design 3 implementation provides a cohesive, accessible, and expressive user interface that adapts to user preferences and system settings while maintaining consistency across all components and interactions.
