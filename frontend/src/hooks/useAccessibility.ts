/**
 * Accessibility Hooks
 * 
 * Utilities for improving application accessibility
 */

import { useEffect, useRef, RefObject } from 'react';

/**
 * Hook to manage focus on mount
 * Useful for dialogs, modals, and page transitions
 */
export function useFocusOnMount<T extends HTMLElement>(): RefObject<T> {
  const ref = useRef<T>(null);

  useEffect(() => {
    if (ref.current) {
      ref.current.focus();
    }
  }, []);

  return ref;
}

/**
 * Hook to trap focus within a container
 * Essential for modal dialogs and menus
 */
export function useFocusTrap<T extends HTMLElement>(isActive: boolean): RefObject<T> {
  const ref = useRef<T>(null);

  useEffect(() => {
    if (!isActive || !ref.current) return;

    const container = ref.current;
    const focusableElements = container.querySelectorAll<HTMLElement>(
      'a[href], button, textarea, input, select, [tabindex]:not([tabindex="-1"])'
    );

    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    };

    container.addEventListener('keydown', handleTabKey);
    firstElement.focus();

    return () => {
      container.removeEventListener('keydown', handleTabKey);
    };
  }, [isActive]);

  return ref;
}

/**
 * Hook to announce screen reader messages
 * Uses aria-live regions
 */
export function useScreenReaderAnnouncement() {
  const announce = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;

    document.body.appendChild(announcement);

    // Remove after announcement
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  };

  return announce;
}

/**
 * Hook for keyboard shortcuts with accessibility support
 */
export function useAccessibleKeyboardShortcut(
  key: string,
  callback: () => void,
  options: {
    ctrl?: boolean;
    shift?: boolean;
    alt?: boolean;
    description?: string;
  } = {}
) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const matchesModifiers =
        (!options.ctrl || e.ctrlKey || e.metaKey) &&
        (!options.shift || e.shiftKey) &&
        (!options.alt || e.altKey);

      if (e.key.toLowerCase() === key.toLowerCase() && matchesModifiers) {
        e.preventDefault();
        callback();
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [key, callback, options]);
}

/**
 * Hook to detect reduced motion preference
 */
export function useReducedMotion(): boolean {
  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  return prefersReducedMotion;
}

/**
 * Hook to manage skip links
 */
export function useSkipLink(targetId: string) {
  const skipToContent = () => {
    const target = document.getElementById(targetId);
    if (target) {
      target.setAttribute('tabindex', '-1');
      target.focus();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return skipToContent;
}

/**
 * Accessibility utility functions
 */
export const a11y = {
  /**
   * Generate unique IDs for ARIA relationships
   */
  generateId: (prefix: string): string => {
    return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
  },

  /**
   * Check if element is visible to screen readers
   */
  isVisibleToScreenReader: (element: HTMLElement): boolean => {
    const style = window.getComputedStyle(element);
    return (
      style.display !== 'none' &&
      style.visibility !== 'hidden' &&
      !element.hasAttribute('aria-hidden')
    );
  },

  /**
   * Get accessible name of element
   */
  getAccessibleName: (element: HTMLElement): string => {
    return (
      element.getAttribute('aria-label') ||
      element.getAttribute('aria-labelledby') ||
      element.textContent ||
      ''
    );
  },
};

export default {
  useFocusOnMount,
  useFocusTrap,
  useScreenReaderAnnouncement,
  useAccessibleKeyboardShortcut,
  useReducedMotion,
  useSkipLink,
  a11y,
};
