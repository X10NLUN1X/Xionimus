/**
 * Performance Monitor
 * Tracks frontend performance metrics and reports issues
 */

class PerformanceMonitor {
  private metrics: Map<string, number[]> = new Map()
  private isMonitoring: boolean = false
  private backendUrl: string = ''

  constructor() {
    // Get backend URL from env
    this.backendUrl = import.meta.env.VITE_BACKEND_URL || 
                      import.meta.env.REACT_APP_BACKEND_URL || 
                      'http://localhost:8001'
  }

  /**
   * Start monitoring input latency
   */
  measureInputLatency() {
    const input = document.querySelector('textarea')
    if (!input) {
      console.warn('⚠️ Input element not found for performance monitoring')
      return
    }

    let startTime: number
    
    input.addEventListener('keydown', () => {
      startTime = performance.now()
    })

    input.addEventListener('keyup', () => {
      const latency = performance.now() - startTime
      this.recordMetric('input_latency', latency)

      // Alert on high latency
      if (latency > 100) {
        console.warn(`⚠️ High input latency: ${latency.toFixed(2)}ms`)
        this.reportToBackend('input_lag', {
          latency,
          messageCount: this.getMessageCount(),
        })
      }
    })
  }

  /**
   * Measure component render time
   */
  measureRenderTime(componentName: string) {
    const start = performance.now()
    
    return () => {
      const duration = performance.now() - start
      this.recordMetric(`render_${componentName}`, duration)

      if (duration > 50) {
        console.warn(`⚠️ Slow render: ${componentName} took ${duration.toFixed(2)}ms`)
      }
    }
  }

  /**
   * Get current message count
   */
  getMessageCount(): number {
    const messages = document.querySelectorAll('[role="log"] > div > div')
    return messages.length
  }

  /**
   * Get DOM node count
   */
  getDOMNodeCount(): number {
    return document.querySelectorAll('*').length
  }

  /**
   * Get memory usage (Chrome only)
   */
  getMemoryUsage(): number {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      return memory.usedJSHeapSize / 1024 / 1024 // MB
    }
    return 0
  }

  /**
   * Record a metric value
   */
  recordMetric(name: string, value: number) {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, [])
    }

    const values = this.metrics.get(name)!
    values.push(value)

    // Keep last 100 measurements only
    if (values.length > 100) {
      values.shift()
    }
  }

  /**
   * Get average of a metric
   */
  getAverageMetric(name: string): number {
    const values = this.metrics.get(name) || []
    if (values.length === 0) return 0
    return values.reduce((a, b) => a + b, 0) / values.length
  }

  /**
   * Get all metrics summary
   */
  getMetricsSummary() {
    const summary: Record<string, any> = {}
    
    this.metrics.forEach((values, name) => {
      summary[name] = {
        avg: this.getAverageMetric(name),
        min: Math.min(...values),
        max: Math.max(...values),
        count: values.length,
      }
    })

    return summary
  }

  /**
   * Report issue to backend
   */
  async reportToBackend(event: string, data: any) {
    try {
      await fetch(`${this.backendUrl}/api/metrics/performance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event,
          timestamp: Date.now(),
          userAgent: navigator.userAgent,
          ...data,
        }),
      })
    } catch (error) {
      console.error('Failed to report metrics:', error)
    }
  }

  /**
   * Start monitoring
   */
  startMonitoring() {
    if (this.isMonitoring) {
      console.warn('Performance monitoring already started')
      return
    }

    this.isMonitoring = true
    console.log('📊 Performance monitoring started')

    // Wait for DOM to be ready
    setTimeout(() => {
      this.measureInputLatency()
    }, 1000)

    // Periodic reporting
    setInterval(() => {
      const avgInputLatency = this.getAverageMetric('input_latency')
      const messageCount = this.getMessageCount()
      const domNodes = this.getDOMNodeCount()
      const memoryUsage = this.getMemoryUsage()

      const metrics = {
        avgInputLatency: avgInputLatency.toFixed(2) + 'ms',
        messageCount,
        domNodes,
        memoryUsage: memoryUsage.toFixed(2) + 'MB',
      }

      console.log('📊 Performance Metrics:', metrics)

      // Alert on degradation
      if (avgInputLatency > 100) {
        console.error('🚨 Performance degradation detected!')
        this.reportToBackend('performance_degradation', {
          ...metrics,
          summary: this.getMetricsSummary(),
        })
      }
    }, 30000) // Every 30 seconds
  }

  /**
   * Stop monitoring
   */
  stopMonitoring() {
    this.isMonitoring = false
    console.log('📊 Performance monitoring stopped')
  }
}

// Singleton instance
export const perfMonitor = new PerformanceMonitor()

/**
 * Memory Monitor
 * Detects memory leaks
 */
class MemoryMonitor {
  private baseline: number = 0
  private isMonitoring: boolean = false

  start() {
    if (this.isMonitoring) return
    
    if (!('memory' in performance)) {
      console.warn('⚠️ Memory monitoring not available (Chrome only)')
      return
    }

    this.isMonitoring = true
    const memory = (performance as any).memory
    this.baseline = memory.usedJSHeapSize

    console.log('💾 Memory monitoring started')
    console.log(`   Baseline: ${(this.baseline / 1024 / 1024).toFixed(2)} MB`)

    setInterval(() => {
      const current = memory.usedJSHeapSize
      const growthMB = (current - this.baseline) / 1024 / 1024
      
      console.log(`💾 Memory Growth: ${growthMB.toFixed(2)} MB`)

      // Alert on potential leak (>100MB growth)
      if (growthMB > 100) {
        console.error('🚨 Potential Memory Leak Detected!')
        perfMonitor.reportToBackend('memory_leak', {
          baseline: this.baseline,
          current,
          growthMB: growthMB.toFixed(2),
        })
      }
    }, 60000) // Every 60 seconds
  }

  stop() {
    this.isMonitoring = false
    console.log('💾 Memory monitoring stopped')
  }
}

export const memMonitor = new MemoryMonitor()
