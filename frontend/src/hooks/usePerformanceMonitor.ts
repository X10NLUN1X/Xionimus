/**
 * Performance Monitoring Hook
 * 
 * Tracks and reports performance metrics for the application
 */

import { useEffect } from 'react';

interface PerformanceMetrics {
  name: string;
  duration: number;
  timestamp: number;
}

class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: PerformanceMetrics[] = [];
  private enabled: boolean = false;

  private constructor() {
    // Check if we're in development mode
    this.enabled = import.meta.env.DEV;
  }

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  measure(name: string, startMark: string, endMark: string) {
    if (!this.enabled) return;

    try {
      performance.measure(name, startMark, endMark);
      const measure = performance.getEntriesByName(name)[0];
      
      this.metrics.push({
        name,
        duration: measure.duration,
        timestamp: Date.now(),
      });

      // Log to console in dev
      if (measure.duration > 1000) {
        console.warn(`⚠️ Slow performance: ${name} took ${measure.duration.toFixed(2)}ms`);
      } else if (measure.duration > 100) {
        console.log(`📊 ${name}: ${measure.duration.toFixed(2)}ms`);
      }
    } catch (error) {
      console.error('Performance measurement failed:', error);
    }
  }

  mark(name: string) {
    if (!this.enabled) return;
    performance.mark(name);
  }

  getMetrics(): PerformanceMetrics[] {
    return this.metrics;
  }

  clearMetrics() {
    this.metrics = [];
    performance.clearMarks();
    performance.clearMeasures();
  }

  reportWebVitals() {
    if (!this.enabled || typeof window === 'undefined') return;

    // Report Core Web Vitals
    if ('web-vital' in window) {
      // @ts-ignore
      import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
        getCLS(console.log);
        getFID(console.log);
        getFCP(console.log);
        getLCP(console.log);
        getTTFB(console.log);
      });
    }
  }
}

/**
 * Hook to measure component render performance
 */
export function usePerformanceMonitor(componentName: string) {
  const monitor = PerformanceMonitor.getInstance();

  useEffect(() => {
    const startMark = `${componentName}-start`;
    const endMark = `${componentName}-end`;
    const measureName = `${componentName}-render`;

    monitor.mark(startMark);

    return () => {
      monitor.mark(endMark);
      monitor.measure(measureName, startMark, endMark);
    };
  }, [componentName, monitor]);
}

/**
 * Hook to track page load performance
 */
export function usePageLoadPerformance() {
  useEffect(() => {
    const monitor = PerformanceMonitor.getInstance();

    if (typeof window !== 'undefined' && window.performance) {
      // Wait for page to fully load
      window.addEventListener('load', () => {
        setTimeout(() => {
          const perfData = window.performance.timing;
          const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
          const connectTime = perfData.responseEnd - perfData.requestStart;
          const renderTime = perfData.domComplete - perfData.domLoading;

          console.log('📊 Page Load Metrics:');
          console.log(`  Total Load Time: ${pageLoadTime}ms`);
          console.log(`  Server Response: ${connectTime}ms`);
          console.log(`  DOM Render: ${renderTime}ms`);

          // Report if slow
          if (pageLoadTime > 3000) {
            console.warn('⚠️ Slow page load detected!');
          }

          // Report Web Vitals
          monitor.reportWebVitals();
        }, 0);
      });
    }
  }, []);
}

/**
 * Performance measurement utility
 */
export const performance = {
  start: (label: string) => {
    PerformanceMonitor.getInstance().mark(`${label}-start`);
  },
  
  end: (label: string) => {
    const monitor = PerformanceMonitor.getInstance();
    monitor.mark(`${label}-end`);
    monitor.measure(label, `${label}-start`, `${label}-end`);
  },

  getMetrics: () => {
    return PerformanceMonitor.getInstance().getMetrics();
  },

  clear: () => {
    PerformanceMonitor.getInstance().clearMetrics();
  },
};

export default usePerformanceMonitor;
