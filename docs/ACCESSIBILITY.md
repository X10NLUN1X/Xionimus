# ♿ Accessibility (a11y) Guide

## Overview

Xionimus AI ist committed zu Web Accessibility und folgt WCAG 2.1 Level AA Standards.

## 🎯 Accessibility Features

### 1. Keyboard Navigation

**Implementiert**:
- ✅ Full keyboard navigation (Tab, Shift+Tab)
- ✅ Skip links für schnellen Zugriff
- ✅ Focus management für Dialogs
- ✅ Keyboard shortcuts mit ARIA announcements

**Tastaturkürzel**:
```
Tab              - Navigate forward
Shift + Tab      - Navigate backward
Enter/Space      - Activate buttons
Esc              - Close dialogs/modals
```

### 2. Screen Reader Support

**ARIA Labels**:
- Alle interaktiven Elemente haben accessible names
- Formulare haben Labels
- Buttons haben descriptive text oder aria-label
- Images haben alt text

**Live Regions**:
```typescript
import { useScreenReaderAnnouncement } from '@/hooks/useAccessibility';

const announce = useScreenReaderAnnouncement();
announce('Message sent successfully', 'polite');
```

### 3. Focus Management

**Skip Links**:
```tsx
import { SkipLinks } from '@/components/SkipLink';

<SkipLinks />
// Provides "Skip to main content" link
```

**Focus Trap** (for modals):
```typescript
import { useFocusTrap } from '@/hooks/useAccessibility';

const ref = useFocusTrap(isModalOpen);
<div ref={ref}>Modal content</div>
```

**Auto Focus**:
```typescript
import { useFocusOnMount } from '@/hooks/useAccessibility';

const ref = useFocusOnMount();
<input ref={ref} />
```

### 4. Visual Design

**Color Contrast**:
- Text meets WCAG AA standards (4.5:1 ratio)
- Interactive elements have sufficient contrast
- Focus indicators visible (2px outline)

**Responsive Text**:
- Minimum font size: 14px
- Scalable text (supports 200% zoom)
- No fixed pixel heights for text containers

**Motion**:
```css
/* Respects prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### 5. Touch Targets

**Minimum Size**: 44x44 pixels
```css
button, a, input {
  min-height: 44px;
  min-width: 44px;
}
```

## 🛠️ Development Tools

### Accessibility Checker (Dev Mode)

Automatische Prüfung beim Page Load:
```typescript
import { checkAccessibility } from '@/utils/accessibilityChecker';

// Manual check
const issues = checkAccessibility();
console.log(issues);
```

**Checked Rules**:
- Images without alt text
- Buttons without accessible names
- Links without text or href
- Forms without labels
- Heading structure
- Invalid ARIA usage
- Keyboard accessibility

### Hooks

```typescript
import {
  useFocusOnMount,
  useFocusTrap,
  useScreenReaderAnnouncement,
  useAccessibleKeyboardShortcut,
  useReducedMotion,
  useSkipLink,
} from '@/hooks/useAccessibility';
```

### CSS Utilities

```css
/* Screen reader only */
.sr-only { /* visually hidden */ }

/* Screen reader only (focusable) */
.sr-only-focusable { /* hidden until focused */ }

/* Focus visible */
.focus-visible-outline:focus-visible { /* custom focus ring */ }
```

## 📋 Accessibility Checklist

### For Developers

**Before Committing**:
- [ ] All images have alt text
- [ ] All buttons have accessible names
- [ ] All forms have labels
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] Color contrast sufficient
- [ ] No console accessibility warnings

**For New Components**:
- [ ] Semantic HTML used
- [ ] ARIA attributes added where needed
- [ ] Keyboard navigation implemented
- [ ] Focus management handled
- [ ] Screen reader tested
- [ ] Color contrast verified

### For Designers

**Design Considerations**:
- [ ] Color contrast ratios meet WCAG AA
- [ ] Focus indicators designed
- [ ] Touch targets minimum 44x44px
- [ ] Text is scalable (no fixed heights)
- [ ] Interactive states visible
- [ ] Reduced motion considered

## 🧪 Testing

### Manual Testing

**Keyboard Navigation**:
1. Unplug mouse
2. Use Tab to navigate
3. Verify all interactive elements reachable
4. Check focus indicators visible

**Screen Reader**:
1. Enable screen reader (NVDA/JAWS/VoiceOver)
2. Navigate through page
3. Verify all content announced correctly
4. Test interactive elements

**Zoom**:
1. Zoom to 200%
2. Verify layout doesn't break
3. Check text is readable
4. Verify functionality intact

### Automated Testing

**Browser Extensions**:
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WAVE](https://wave.webaim.org/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)

**Command Line**:
```bash
# Run Lighthouse
lighthouse http://localhost:3000 --view

# Pa11y
npx pa11y http://localhost:3000
```

### Testing with Real Users

**Best Practice**:
- Test with actual assistive technology users
- Gather feedback on pain points
- Iterate based on real usage

## 📚 WCAG 2.1 Compliance

### Level A (Minimum)

✅ **1.1.1** Non-text Content - Alt text for images  
✅ **1.3.1** Info and Relationships - Semantic HTML  
✅ **1.4.1** Use of Color - Not sole indicator  
✅ **2.1.1** Keyboard - Full keyboard access  
✅ **2.1.2** No Keyboard Trap - Can escape  
✅ **2.4.1** Bypass Blocks - Skip links  
✅ **2.4.2** Page Titled - Meaningful titles  
✅ **3.1.1** Language of Page - lang attribute  
✅ **4.1.1** Parsing - Valid HTML  
✅ **4.1.2** Name, Role, Value - ARIA

### Level AA (Target)

✅ **1.4.3** Contrast (Minimum) - 4.5:1 ratio  
✅ **1.4.5** Images of Text - Avoid when possible  
✅ **2.4.5** Multiple Ways - Navigation options  
✅ **2.4.6** Headings and Labels - Descriptive  
✅ **2.4.7** Focus Visible - Clear indicators  
✅ **3.2.3** Consistent Navigation - Predictable  
✅ **3.2.4** Consistent Identification - Uniform  
⚠️ **3.3.3** Error Suggestion - Implement more  
⚠️ **3.3.4** Error Prevention - Add confirmation  

## 🔧 Implementation Examples

### Accessible Button

```tsx
// ✅ Good
<button
  aria-label="Send message"
  onClick={handleSend}
>
  <SendIcon />
</button>

// ❌ Bad
<div onClick={handleSend}>
  <SendIcon />
</div>
```

### Accessible Form

```tsx
// ✅ Good
<label htmlFor="email">Email</label>
<input
  id="email"
  type="email"
  aria-required="true"
  aria-invalid={hasError}
  aria-describedby={hasError ? "email-error" : undefined}
/>
{hasError && (
  <span id="email-error" role="alert">
    Please enter a valid email
  </span>
)}

// ❌ Bad
<input type="email" placeholder="Email" />
```

### Accessible Modal

```tsx
import { useFocusTrap } from '@/hooks/useAccessibility';

function Modal({ isOpen, onClose }) {
  const ref = useFocusTrap(isOpen);
  
  return (
    <div
      ref={ref}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <h2 id="modal-title">Modal Title</h2>
      <button onClick={onClose} aria-label="Close modal">×</button>
      {/* content */}
    </div>
  );
}
```

### Accessible Navigation

```tsx
<nav aria-label="Main navigation" id="navigation">
  <ul>
    <li><a href="/" aria-current={isHome ? "page" : undefined}>Home</a></li>
    <li><a href="/settings">Settings</a></li>
  </ul>
</nav>
```

## 🚨 Common Mistakes to Avoid

### ❌ Don't

```tsx
// Missing alt text
<img src="logo.png" />

// Non-semantic click handler
<div onClick={handleClick}>Click me</div>

// Empty button
<button><Icon /></button>

// No label
<input type="text" placeholder="Name" />

// Color as only indicator
<span style={{ color: 'red' }}>Error</span>
```

### ✅ Do

```tsx
// With alt text
<img src="logo.png" alt="Company Logo" />

// Semantic button
<button onClick={handleClick}>Click me</button>

// Button with aria-label
<button aria-label="Close"><Icon /></button>

// With label
<label htmlFor="name">Name</label>
<input id="name" type="text" />

// Error with icon and text
<span role="alert">
  <ErrorIcon aria-hidden="true" />
  <span>Error: Invalid input</span>
</span>
```

## 📊 Metrics & Goals

### Current Score
- **Lighthouse Accessibility**: Target 95+
- **axe Issues**: Target 0
- **Keyboard Navigation**: 100% coverage
- **Screen Reader Compatibility**: Major SRs supported

### Monitoring
```bash
# Run accessibility audit
yarn test:a11y

# Check in CI/CD
lighthouse --only-categories=accessibility
```

## 🔄 Continuous Improvement

### Monthly Tasks
- [ ] Run automated accessibility audit
- [ ] Review new WCAG updates
- [ ] Test with screen readers
- [ ] Gather user feedback
- [ ] Update documentation

### Before Release
- [ ] Full keyboard navigation test
- [ ] Screen reader test (min 2 SRs)
- [ ] Color contrast verification
- [ ] Lighthouse audit (>95 score)
- [ ] Manual checklist completion

## 📚 Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [A11y Project](https://www.a11yproject.com/)
- [WebAIM](https://webaim.org/)
- [Inclusive Components](https://inclusive-components.design/)

---

**Version**: 1.0  
**Last Updated**: January 2025  
**WCAG Level**: AA (Target)  
**Status**: In Progress
