# Responsive Design Quick Reference

## Breakpoints

```css
/* Desktop First */
Default: > 1024px (Desktop)

/* Tablet */
@media (max-width: 1024px)

/* Mobile */
@media (max-width: 768px)

/* Small Mobile */
@media (max-width: 480px)

/* Extra Small Mobile */
@media (max-width: 360px)
```

## Component Behavior by Screen Size

### Navigation Bar
| Screen Size | Behavior |
|------------|----------|
| Desktop (>1024px) | Full nav with icons + text, user location visible |
| Tablet (768-1024px) | Full nav with icons + text |
| Mobile (<768px) | Icons only, hidden user info |

### Feature Buttons
| Screen Size | Layout |
|------------|--------|
| Desktop (>1024px) | Horizontal grid (3 columns) |
| Tablet (768-1024px) | Horizontal grid (2-3 columns) |
| Mobile (<768px) | Vertical stack (1 column) |

### Modal Dialogs
| Screen Size | Width | Padding |
|------------|-------|---------|
| Desktop (>1024px) | 450px max | 30px |
| Tablet (768-1024px) | 90% | 25px |
| Mobile (<768px) | 95% | 20px |

### Text Input Controls
| Screen Size | Layout |
|------------|--------|
| Desktop (>1024px) | Horizontal (button + language selector) |
| Mobile (<768px) | Vertical stack (full-width) |

### Landing Page Hero
| Screen Size | Title Size | Button Layout |
|------------|-----------|---------------|
| Desktop (>1024px) | 4.5rem | Horizontal |
| Tablet (768-1024px) | 3rem | Horizontal |
| Mobile (<768px) | 2.5rem | Vertical (full-width) |
| Small Mobile (<480px) | 2rem | Vertical (full-width) |

### Profile Page
| Screen Size | Grid Layout |
|------------|-------------|
| Desktop (>1024px) | 2 columns (main + sidebar) |
| Tablet (768-1024px) | 1 column |
| Mobile (<768px) | 1 column (stacked) |

### Community Page
| Screen Size | Reports Grid | Tabs |
|------------|--------------|------|
| Desktop (>1024px) | Multi-column | Full (icon + text) |
| Tablet (768-1024px) | 2 columns | Full (icon + text) |
| Mobile (<768px) | 1 column | Scrollable (icon only) |

## Font Sizes

### Headings
```css
/* Desktop */
h1: 2.5rem - 4.5rem
h2: 2rem - 3rem
h3: 1.5rem - 2rem

/* Mobile */
h1: 1.5rem - 2.5rem
h2: 1.5rem - 2rem
h3: 1.1rem - 1.5rem
```

### Body Text
```css
/* Desktop */
body: 1rem (16px)
small: 0.875rem (14px)

/* Mobile */
body: 0.9rem - 1rem (14-16px)
small: 0.8rem - 0.85rem (13-14px)
```

## Spacing

### Padding
```css
/* Desktop */
Container: 40px
Card: 30-40px
Button: 12-16px

/* Mobile */
Container: 15-20px
Card: 16-20px
Button: 10-14px
```

### Margins
```css
/* Desktop */
Section: 40-60px
Element: 20-30px

/* Mobile */
Section: 20-30px
Element: 15-20px
```

## Touch Targets

### Minimum Sizes (Mobile)
```css
Buttons: 44px x 44px (minimum)
Icons: 24px x 24px
Input fields: 44px height
```

## Grid Layouts

### Feature Buttons
```css
/* Desktop */
grid-template-columns: repeat(3, 1fr)

/* Tablet */
grid-template-columns: repeat(2, 1fr)

/* Mobile */
grid-template-columns: 1fr
```

### Reports/Cards
```css
/* Desktop */
grid-template-columns: repeat(auto-fill, minmax(350px, 1fr))

/* Mobile */
grid-template-columns: 1fr
```

## Common Responsive Patterns

### Stack on Mobile
```css
/* Desktop: Horizontal */
.container {
  display: flex;
  flex-direction: row;
  gap: 20px;
}

/* Mobile: Vertical */
@media (max-width: 768px) {
  .container {
    flex-direction: column;
    gap: 15px;
  }
}
```

### Full Width on Mobile
```css
/* Desktop: Fixed width */
.element {
  width: 450px;
}

/* Mobile: Full width */
@media (max-width: 768px) {
  .element {
    width: 100%;
  }
}
```

### Hide on Mobile
```css
/* Desktop: Visible */
.desktop-only {
  display: block;
}

/* Mobile: Hidden */
@media (max-width: 768px) {
  .desktop-only {
    display: none;
  }
}
```

## Testing Checklist

- [ ] Test on Chrome DevTools (all device sizes)
- [ ] Test on actual mobile device
- [ ] Test on tablet
- [ ] Test landscape and portrait orientations
- [ ] Verify touch targets are adequate (44px minimum)
- [ ] Check text readability
- [ ] Verify no horizontal scrolling
- [ ] Test all interactive elements
- [ ] Check modal scrolling
- [ ] Verify navigation functionality

## Browser DevTools Shortcuts

- **Chrome/Edge:** F12 or Ctrl+Shift+I
- **Firefox:** F12 or Ctrl+Shift+I
- **Safari:** Cmd+Option+I (Mac)

Toggle device toolbar:
- **Chrome/Edge/Firefox:** Ctrl+Shift+M
- **Safari:** Cmd+Shift+M (Mac)
