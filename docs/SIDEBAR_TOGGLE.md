# Sidebar Toggle Functionality

## Overview

DataWeaver.AI now includes a collapsible sidebar that can be toggled on and off to provide more screen space for the main content area.

## Features

### 🎛️ **Toggle Controls**

1. **Sidebar Toggle Button**: Located in the top-right corner of the sidebar header
2. **Floating Toggle Button**: Appears when sidebar is hidden (top-left corner)
3. **Keyboard Shortcut**: `Ctrl+B` (or `Cmd+B` on Mac) to toggle sidebar

### 🎨 **Visual Feedback**

- **Smooth Animations**: 300ms cubic-bezier transitions
- **Icon Rotation**: Toggle button icon rotates when sidebar is hidden/shown
- **Hover Effects**: Buttons scale and change color on hover
- **Tooltips**: Show keyboard shortcuts on hover

### 📱 **Responsive Design**

- **Desktop**: Full sidebar (320px width)
- **Tablet**: Slightly smaller sidebar (280px width)
- **Mobile**: Full-width sidebar with improved touch targets
- **Large Screens**: Wider sidebar (350px width)

## Usage

### Method 1: Click Toggle Button
1. Click the toggle button (↔️) in the sidebar header
2. Sidebar slides out/in with smooth animation
3. Main content area adjusts automatically

### Method 2: Keyboard Shortcut
1. Press `Ctrl+B` (Windows/Linux) or `Cmd+B` (Mac)
2. Sidebar toggles instantly
3. Works from anywhere in the application

### Method 3: Floating Button
1. When sidebar is hidden, a floating button appears
2. Click the floating button to show sidebar
3. Button disappears when sidebar is visible

## Technical Implementation

### Components

- **SidebarLayout.tsx**: Main container with state management
- **Sidebar.tsx**: Sidebar component with toggle button
- **SidebarLayout.css**: Layout and animation styles
- **Sidebar.css**: Sidebar-specific styles

### State Management

```typescript
const [sidebarVisible, setSidebarVisible] = useState(true);

const toggleSidebar = () => {
  setSidebarVisible(!sidebarVisible);
};
```

### Keyboard Event Handling

```typescript
useEffect(() => {
  const handleKeyDown = (event: KeyboardEvent) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'b') {
      event.preventDefault();
      toggleSidebar();
    }
  };

  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
}, [sidebarVisible]);
```

## CSS Classes

### Layout Classes
- `.app-container`: Main container
- `.sidebar-visible`: When sidebar is shown
- `.sidebar-hidden`: When sidebar is hidden
- `.main-content`: Content area
- `.content-wrapper`: Scrollable content container

### Sidebar Classes
- `.sidebar`: Sidebar container
- `.sidebar-header`: Header section
- `.sidebar-content`: Content section
- `.sidebar-toggle-btn`: Toggle button
- `.toggle-icon`: Toggle icon with rotation

### Animation Classes
- `.floating-toggle-btn`: Floating toggle button
- `.fadeIn`: Animation for floating button appearance

## Accessibility

### ARIA Labels
- `aria-label`: Descriptive labels for screen readers
- `title`: Tooltips with keyboard shortcuts

### Keyboard Navigation
- Tab navigation works for all interactive elements
- Focus management when sidebar toggles
- Escape key support (can be added)

### Screen Reader Support
- Proper heading structure
- Descriptive button labels
- State announcements

## Browser Support

- **Chrome**: Full support
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support
- **Mobile browsers**: Responsive design

## Performance

- **Smooth animations**: Hardware-accelerated transforms
- **Efficient reflows**: Minimal layout recalculations
- **Memory management**: Proper event listener cleanup
- **Responsive**: Optimized for different screen sizes

## Future Enhancements

### Planned Features
- **Persistent state**: Remember sidebar state across sessions
- **Custom animations**: User-configurable transition speeds
- **Multiple layouts**: Different sidebar configurations
- **Drag to resize**: Resizable sidebar width
- **Auto-hide**: Auto-hide on small screens

### Potential Improvements
- **Touch gestures**: Swipe to toggle on mobile
- **Keyboard shortcuts**: Additional shortcuts for different actions
- **Themes**: Different visual themes for sidebar
- **Animations**: More sophisticated animation options 