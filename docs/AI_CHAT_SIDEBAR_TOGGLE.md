# AI Chat Sidebar Toggle Functionality

## Overview

The AI Chat interface now includes the same collapsible sidebar functionality as the main dashboard, allowing users to toggle the sidebar on and off for better screen space management.

## Features

### 🎛️ **Toggle Controls**

1. **Sidebar Toggle Button**: Located in the top-right corner of the AI Chat sidebar header
2. **Floating Toggle Button**: Appears when sidebar is hidden (top-left corner)
3. **Keyboard Shortcut**: `Ctrl+B` (or `Cmd+B` on Mac) to toggle sidebar

### 🎨 **Visual Feedback**

- **Smooth Animations**: 300ms cubic-bezier transitions
- **Icon Rotation**: ChevronLeft icon rotates when sidebar is hidden/shown
- **Hover Effects**: Buttons scale and change color on hover
- **Tooltips**: Show keyboard shortcuts on hover

### 📱 **Responsive Design**

- **Desktop**: 280px sidebar width
- **Tablet**: 260px sidebar width
- **Large Screens**: 300px sidebar width
- **Mobile**: Full-width sidebar with improved touch targets

## Implementation Details

### Components Updated

#### **AIChatLayout.tsx**
```typescript
const [sidebarVisible, setSidebarVisible] = useState(true);

const toggleSidebar = useCallback(() => {
  setSidebarVisible(prev => !prev);
}, []);

// Keyboard shortcut handling
useEffect(() => {
  const handleKeyDown = (event: KeyboardEvent) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'b') {
      event.preventDefault();
      toggleSidebar();
    }
  };
  // Event listener setup...
}, [toggleSidebar]);
```

#### **AIChatSidebar.tsx**
```typescript
interface AIChatSidebarProps {
  isVisible: boolean;
  onToggle: () => void;
  onPromptSelect: (prompt: string) => void;
  // ... other props
}

// Toggle button in header
<button 
  className="sidebar-toggle-btn"
  onClick={onToggle}
  aria-label={isVisible ? 'Hide sidebar' : 'Show sidebar'}
  title={`${isVisible ? 'Hide' : 'Show'} sidebar (Ctrl+B)`}
>
  <ChevronLeft 
    size={20} 
    className={`toggle-icon ${isVisible ? 'rotate' : ''}`}
  />
</button>
```

### CSS Classes

#### **Layout Classes**
- `.ai-chat-layout`: Main container
- `.sidebar-visible`: When sidebar is shown
- `.sidebar-hidden`: When sidebar is hidden
- `.ai-chat-container`: Content area
- `.ai-chat-main`: Main chat area

#### **Sidebar Classes**
- `.ai-chat-sidebar`: Sidebar container
- `.sidebar-header-content`: Header with toggle button
- `.sidebar-title-section`: Title and icon area
- `.sidebar-toggle-btn`: Toggle button styling
- `.toggle-icon`: ChevronLeft icon with rotation

#### **Animation Classes**
- `.floating-toggle-btn`: Floating toggle button
- `.fadeIn`: Animation for floating button appearance

## Usage

### Method 1: Click Toggle Button
1. Click the chevron button (←) in the AI Chat sidebar header
2. Sidebar slides out/in with smooth animation
3. Main chat area adjusts automatically

### Method 2: Keyboard Shortcut
1. Press `Ctrl+B` (Windows/Linux) or `Cmd+B` (Mac)
2. Sidebar toggles instantly
3. Works from anywhere in the AI Chat interface

### Method 3: Floating Button
1. When sidebar is hidden, a floating button appears
2. Click the floating button to show sidebar
3. Button disappears when sidebar is visible

## Visual Design

### **Toggle Button Styling**
- **Background**: Light blue with transparency
- **Border**: Subtle blue border
- **Hover**: Scale effect and color change
- **Icon**: ChevronLeft with rotation animation

### **Floating Button**
- **Position**: Fixed top-left corner
- **Style**: Gradient background with shadow
- **Animation**: Fade-in effect when appearing
- **Responsive**: Smaller on mobile devices

### **Animations**
- **Transition**: 300ms cubic-bezier easing
- **Transform**: Smooth slide in/out
- **Rotation**: Icon rotates 180 degrees
- **Scale**: Hover effects with smooth scaling

## Accessibility

### **ARIA Support**
- `aria-label`: Descriptive labels for screen readers
- `title`: Tooltips with keyboard shortcuts
- **Focus management**: Proper tab navigation

### **Keyboard Navigation**
- **Tab order**: Logical navigation flow
- **Enter/Space**: Activate buttons
- **Escape**: Can be added for additional control

### **Screen Reader Support**
- **State announcements**: Sidebar visibility changes
- **Descriptive labels**: Clear button purposes
- **Semantic structure**: Proper heading hierarchy

## Browser Support

- **Chrome**: Full support
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support
- **Mobile browsers**: Responsive design

## Performance

- **Hardware acceleration**: Transform-based animations
- **Efficient reflows**: Minimal layout recalculations
- **Memory management**: Proper event listener cleanup
- **Responsive**: Optimized for different screen sizes

## Integration with Existing Features

### **AI Chat Functionality**
- **Preserves all existing features**: Prompt selection, file handling
- **Maintains state**: Chat history and session data
- **Seamless integration**: No disruption to AI interactions

### **Navigation Items**
- **Home**: Overview of data and workflows
- **Files**: Recent files and datasets
- **Workflows**: Active workflows and status
- **Connectors**: Connected data sources
- **Vendors**: Vendor datasets
- **Pipelines**: Data processing pipelines
- **Dashboard**: Key metrics and visualizations

## Future Enhancements

### **Planned Features**
- **Persistent state**: Remember sidebar state across sessions
- **Custom animations**: User-configurable transition speeds
- **Multiple layouts**: Different sidebar configurations
- **Auto-hide**: Auto-hide on small screens
- **Touch gestures**: Swipe to toggle on mobile

### **Potential Improvements**
- **Keyboard shortcuts**: Additional shortcuts for different actions
- **Themes**: Different visual themes for sidebar
- **Animations**: More sophisticated animation options
- **Accessibility**: Enhanced screen reader support

## Testing

### **Manual Testing Checklist**
- [ ] Toggle button works correctly
- [ ] Keyboard shortcut functions properly
- [ ] Floating button appears when sidebar is hidden
- [ ] Animations are smooth and responsive
- [ ] Tooltips show correct information
- [ ] Mobile responsiveness works
- [ ] Accessibility features function

### **Automated Testing**
```typescript
// Example test cases
describe('AI Chat Sidebar Toggle', () => {
  it('should toggle sidebar visibility', () => {
    // Test implementation
  });
  
  it('should respond to keyboard shortcuts', () => {
    // Test implementation
  });
  
  it('should show floating button when hidden', () => {
    // Test implementation
  });
});
```

## Troubleshooting

### **Common Issues**
1. **Sidebar not toggling**: Check event listener cleanup
2. **Animation glitches**: Verify CSS transitions
3. **Keyboard not working**: Check modifier key detection
4. **Mobile issues**: Test responsive breakpoints

### **Debug Steps**
1. Check browser console for errors
2. Verify CSS classes are applied correctly
3. Test keyboard event handling
4. Validate accessibility features

The AI Chat sidebar toggle functionality provides the same user experience as the main dashboard, ensuring consistency across the application while maintaining all existing AI Chat features. 