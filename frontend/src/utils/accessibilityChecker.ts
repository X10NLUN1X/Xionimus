/**
 * Accessibility Checker Utility
 * 
 * Runtime checks for common accessibility issues (dev mode only)
 */

type A11yIssue = {
  type: 'error' | 'warning';
  element: HTMLElement;
  message: string;
  rule: string;
};

class AccessibilityChecker {
  private issues: A11yIssue[] = [];
  private enabled: boolean;

  constructor() {
    this.enabled = import.meta.env.DEV;
  }

  /**
   * Check all accessibility issues on the page
   */
  checkPage(): A11yIssue[] {
    if (!this.enabled) return [];

    this.issues = [];

    this.checkImages();
    this.checkButtons();
    this.checkLinks();
    this.checkForms();
    this.checkHeadings();
    this.checkARIA();
    this.checkKeyboardAccessibility();

    if (this.issues.length > 0) {
      console.group('🔍 Accessibility Issues Found');
      this.issues.forEach((issue) => {
        const level = issue.type === 'error' ? console.error : console.warn;
        level(`[${issue.rule}] ${issue.message}`, issue.element);
      });
      console.groupEnd();
    } else {
      console.log('✅ No accessibility issues found');
    }

    return this.issues;
  }

  /**
   * Check images for alt text
   */
  private checkImages(): void {
    const images = document.querySelectorAll('img');
    images.forEach((img) => {
      if (!img.hasAttribute('alt')) {
        this.addIssue('error', img, 'Image missing alt attribute', 'img-alt');
      } else if (img.getAttribute('alt') === '' && !img.getAttribute('role')) {
        // Empty alt is OK for decorative images
        const isDecorative = img.hasAttribute('role') && img.getAttribute('role') === 'presentation';
        if (!isDecorative && img.parentElement?.tagName !== 'BUTTON') {
          this.addIssue('warning', img, 'Image has empty alt text - ensure this is decorative', 'img-alt-empty');
        }
      }
    });
  }

  /**
   * Check buttons for accessible names
   */
  private checkButtons(): void {
    const buttons = document.querySelectorAll('button');
    buttons.forEach((button) => {
      const hasText = button.textContent?.trim();
      const hasAriaLabel = button.hasAttribute('aria-label');
      const hasAriaLabelledBy = button.hasAttribute('aria-labelledby');

      if (!hasText && !hasAriaLabel && !hasAriaLabelledBy) {
        this.addIssue('error', button, 'Button has no accessible name', 'button-name');
      }
    });
  }

  /**
   * Check links for accessibility
   */
  private checkLinks(): void {
    const links = document.querySelectorAll('a');
    links.forEach((link) => {
      const hasHref = link.hasAttribute('href');
      const hasText = link.textContent?.trim();
      const hasAriaLabel = link.hasAttribute('aria-label');

      if (!hasHref && !link.hasAttribute('role')) {
        this.addIssue('warning', link, 'Link without href should have role="button"', 'link-href');
      }

      if (!hasText && !hasAriaLabel) {
        this.addIssue('error', link, 'Link has no accessible name', 'link-name');
      }

      // Check for generic link text
      const genericTexts = ['click here', 'read more', 'link', 'here'];
      if (hasText && genericTexts.includes(hasText.toLowerCase())) {
        this.addIssue('warning', link, `Generic link text: "${hasText}" - provide more context`, 'link-generic');
      }
    });
  }

  /**
   * Check form inputs
   */
  private checkForms(): void {
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach((input) => {
      const hasLabel = input.hasAttribute('aria-label') || 
                      input.hasAttribute('aria-labelledby') ||
                      document.querySelector(`label[for="${input.id}"]`);

      if (!hasLabel && input.getAttribute('type') !== 'hidden') {
        this.addIssue('error', input as HTMLElement, 'Form input missing label', 'form-label');
      }
    });
  }

  /**
   * Check heading structure
   */
  private checkHeadings(): void {
    const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
    
    if (headings.length === 0) {
      return;
    }

    // Check for h1
    const h1Count = headings.filter(h => h.tagName === 'H1').length;
    if (h1Count === 0) {
      this.addIssue('warning', document.body, 'Page missing h1 heading', 'heading-h1');
    } else if (h1Count > 1) {
      this.addIssue('warning', document.body, 'Page has multiple h1 headings', 'heading-h1-multiple');
    }

    // Check for heading level skips
    let prevLevel = 0;
    headings.forEach((heading) => {
      const level = parseInt(heading.tagName.charAt(1));
      if (prevLevel > 0 && level > prevLevel + 1) {
        this.addIssue('warning', heading as HTMLElement, 
          `Heading level skip: h${prevLevel} to h${level}`, 'heading-skip');
      }
      prevLevel = level;
    });
  }

  /**
   * Check ARIA usage
   */
  private checkARIA(): void {
    // Check for invalid ARIA attributes
    const elementsWithARIA = document.querySelectorAll('[aria-label], [aria-labelledby], [role]');
    elementsWithARIA.forEach((element) => {
      // Check for empty aria-label
      const ariaLabel = element.getAttribute('aria-label');
      if (ariaLabel !== null && ariaLabel.trim() === '') {
        this.addIssue('error', element as HTMLElement, 'Empty aria-label', 'aria-empty');
      }

      // Check for invalid roles
      const role = element.getAttribute('role');
      const validRoles = [
        'alert', 'alertdialog', 'application', 'article', 'banner', 'button',
        'checkbox', 'columnheader', 'combobox', 'complementary', 'contentinfo',
        'definition', 'dialog', 'directory', 'document', 'feed', 'figure',
        'form', 'grid', 'gridcell', 'group', 'heading', 'img', 'link', 'list',
        'listbox', 'listitem', 'log', 'main', 'marquee', 'math', 'menu',
        'menubar', 'menuitem', 'menuitemcheckbox', 'menuitemradio', 'navigation',
        'none', 'note', 'option', 'presentation', 'progressbar', 'radio',
        'radiogroup', 'region', 'row', 'rowgroup', 'rowheader', 'scrollbar',
        'search', 'searchbox', 'separator', 'slider', 'spinbutton', 'status',
        'switch', 'tab', 'table', 'tablist', 'tabpanel', 'term', 'textbox',
        'timer', 'toolbar', 'tooltip', 'tree', 'treegrid', 'treeitem'
      ];

      if (role && !validRoles.includes(role)) {
        this.addIssue('error', element as HTMLElement, `Invalid ARIA role: ${role}`, 'aria-role-invalid');
      }
    });
  }

  /**
   * Check keyboard accessibility
   */
  private checkKeyboardAccessibility(): void {
    // Check for interactive elements without tabindex
    const interactiveElements = document.querySelectorAll('[onclick]:not(button):not(a)');
    interactiveElements.forEach((element) => {
      if (!element.hasAttribute('tabindex') && !element.hasAttribute('role')) {
        this.addIssue('warning', element as HTMLElement, 
          'Interactive element should have tabindex and role', 'keyboard-interactive');
      }
    });
  }

  /**
   * Add an issue to the list
   */
  private addIssue(type: 'error' | 'warning', element: HTMLElement, message: string, rule: string): void {
    this.issues.push({ type, element, message, rule });
  }

  /**
   * Get summary of issues
   */
  getSummary(): { errors: number; warnings: number } {
    return {
      errors: this.issues.filter(i => i.type === 'error').length,
      warnings: this.issues.filter(i => i.type === 'warning').length,
    };
  }
}

// Export singleton instance
export const accessibilityChecker = new AccessibilityChecker();

/**
 * Run accessibility check (dev mode only)
 */
export function checkAccessibility(): A11yIssue[] {
  return accessibilityChecker.checkPage();
}

/**
 * Auto-check on page load in dev mode
 */
if (import.meta.env.DEV && typeof window !== 'undefined') {
  window.addEventListener('load', () => {
    setTimeout(() => {
      checkAccessibility();
    }, 1000);
  });
}

export default accessibilityChecker;
